from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from flask_socketio import SocketIO, emit
import os
import subprocess
import uuid
import zipfile
import shutil
from pathlib import Path
from werkzeug.utils import secure_filename
import threading

from utils.webm_convert import convert_video_to_webm
from utils.hls_convert import convert_video_to_hls

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max total size

CONVERTED_FOLDER = 'converted'
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv'}

os.makedirs(CONVERTED_FOLDER, exist_ok=True)


def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return f'.{ext}' in VIDEO_EXTENSIONS


def cleanup_old_files():
    """Clean up files and HLS directories older than 30 minutes"""
    import time
    current_time = time.time()
    if os.path.exists(CONVERTED_FOLDER):
        for entry in os.listdir(CONVERTED_FOLDER):
            entry_path = os.path.join(CONVERTED_FOLDER, entry)
            try:
                if current_time - os.path.getctime(entry_path) > 1800:
                    if os.path.isfile(entry_path):
                        os.remove(entry_path)
                    elif os.path.isdir(entry_path) and entry.startswith('hls_'):
                        shutil.rmtree(entry_path)
            except Exception:
                pass


def check_ffmpeg_available():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return upload_ajax()
    else:
        return upload_form()


def upload_ajax():
    cleanup_old_files()

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return {'success': False, 'error': 'No files selected'}

    if len(files) > 10:
        return {'success': False, 'error': 'Maximum 10 files allowed per batch'}

    converted_files = []
    errors = []
    skipped = []

    for file in files:
        if not file or not file.filename:
            continue

        if not allowed_file(file.filename):
            skipped.append(file.filename)
            continue

        filename = secure_filename(file.filename)
        if not filename:
            skipped.append(file.filename)
            continue

        temp_path = os.path.join(CONVERTED_FOLDER, f"temp_{uuid.uuid4().hex}_{filename}")
        try:
            file.save(temp_path)
            original_size = os.path.getsize(temp_path)

            base_name = filename.rsplit('.', 1)[0]
            webm_filename = f"{base_name}.webm"
            webm_path = os.path.join(CONVERTED_FOLDER, webm_filename)

            def progress_callback(data):
                socketio.emit('conversion_progress', {
                    'filename': filename,
                    'progress': data['progress'],
                    'eta': data['eta']
                })

            result = convert_video_to_webm(temp_path, webm_path, progress_callback)
            converted_size = os.path.getsize(webm_path)
            savings_percent = ((original_size - converted_size) / original_size) * 100

            converted_files.append({
                'filename': webm_filename,
                'original_name': filename,
                'original_size': original_size,
                'converted_size': converted_size,
                'savings_percent': savings_percent,
                'encoder_used': result['encoder_used'],
            })

        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    if not converted_files:
        return {'success': False, 'error': 'No files were converted successfully'}

    return {
        'success': True,
        'files': converted_files,
        'errors': errors,
        'skipped': skipped,
        'is_batch': len(converted_files) > 1
    }


def upload_form():
    cleanup_old_files()

    if 'files' not in request.files:
        flash('No files selected')
        return redirect(url_for('index'))

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        flash('No files selected')
        return redirect(url_for('index'))

    converted_files = []
    errors = []

    for file in files:
        if not allowed_file(file.filename):
            continue

        filename = secure_filename(file.filename)
        temp_path = os.path.join(CONVERTED_FOLDER, f"temp_{uuid.uuid4().hex}_{filename}")
        try:
            file.save(temp_path)
            base_name = filename.rsplit('.', 1)[0]
            webm_filename = f"{base_name}.webm"
            webm_path = os.path.join(CONVERTED_FOLDER, webm_filename)
            convert_video_to_webm(temp_path, webm_path)
            converted_files.append({'filename': webm_filename})
        except Exception as e:
            errors.append(str(e))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    if errors:
        for error in errors[:3]:
            flash(f'Error: {error}')

    if not converted_files:
        flash('No files were converted successfully')
        return redirect(url_for('index'))

    return render_template('index.html', results={'files': converted_files})


@app.route('/convert-hls', methods=['POST'])
def convert_hls():
    cleanup_old_files()

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return {'success': False, 'error': 'No files selected'}

    if len(files) > 10:
        return {'success': False, 'error': 'Maximum 10 files allowed per batch'}

    jobs = []
    errors = []
    skipped = []

    for file in files:
        if not file or not file.filename:
            continue

        if not allowed_file(file.filename):
            skipped.append(file.filename)
            continue

        filename = secure_filename(file.filename)
        if not filename:
            skipped.append(file.filename)
            continue

        job_id = f"hls_{uuid.uuid4().hex[:12]}"
        temp_path = os.path.join(CONVERTED_FOLDER, f"temp_{uuid.uuid4().hex}_{filename}")
        output_dir = os.path.join(CONVERTED_FOLDER, job_id)

        try:
            file.save(temp_path)

            def progress_callback(data):
                socketio.emit('hls_progress', {
                    'filename': filename,
                    'progress': data['progress'],
                    'eta': data['eta']
                })

            result = convert_video_to_hls(temp_path, output_dir, progress_callback=progress_callback)

            jobs.append({
                'job_id': job_id,
                'original_name': filename,
                'encoder_used': result['encoder_used'],
                'segment_count': result['segment_count'],
                'total_size': result['total_size'],
            })

        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir, ignore_errors=True)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    if not jobs:
        return {'success': False, 'error': 'No files were converted successfully'}

    return {
        'success': True,
        'jobs': jobs,
        'errors': errors,
        'skipped': skipped,
        'is_batch': len(jobs) > 1
    }


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(CONVERTED_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    return redirect(url_for('index'))


@app.route('/download_batch')
def download_batch():
    zip_filename = f'converted_videos_{str(uuid.uuid4())[:8]}.zip'
    zip_path = os.path.join(CONVERTED_FOLDER, zip_filename)

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in os.listdir(CONVERTED_FOLDER):
                if filename.endswith('.webm'):
                    file_path = os.path.join(CONVERTED_FOLDER, filename)
                    zipf.write(file_path, filename)

        return send_file(zip_path, as_attachment=True, download_name=zip_filename)

    except Exception as e:
        flash(f'Error creating zip file: {str(e)}')
        return redirect(url_for('index'))


@app.route('/download-hls/<job_id>')
def download_hls(job_id):
    job_dir = os.path.join(CONVERTED_FOLDER, job_id)
    if not os.path.isdir(job_dir):
        return redirect(url_for('index'))

    zip_filename = f'{job_id}.zip'
    zip_path = os.path.join(CONVERTED_FOLDER, zip_filename)

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for fname in os.listdir(job_dir):
                zipf.write(os.path.join(job_dir, fname), fname)

        return send_file(zip_path, as_attachment=True, download_name=zip_filename)

    except Exception as e:
        flash(f'Error creating zip file: {str(e)}')
        return redirect(url_for('index'))


@app.route('/download-hls-batch')
def download_hls_batch():
    zip_filename = f'hls_batch_{str(uuid.uuid4())[:8]}.zip'
    zip_path = os.path.join(CONVERTED_FOLDER, zip_filename)

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for entry in os.listdir(CONVERTED_FOLDER):
                entry_path = os.path.join(CONVERTED_FOLDER, entry)
                if os.path.isdir(entry_path) and entry.startswith('hls_'):
                    for fname in os.listdir(entry_path):
                        zipf.write(os.path.join(entry_path, fname), os.path.join(entry, fname))

        return send_file(zip_path, as_attachment=True, download_name=zip_filename)

    except Exception as e:
        flash(f'Error creating zip file: {str(e)}')
        return redirect(url_for('index'))


@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 500MB total.')
    return redirect(url_for('index'))


def format_file_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    import math
    size_names = ["B", "KB", "MB", "GB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


app.jinja_env.globals.update(format_file_size=format_file_size)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
