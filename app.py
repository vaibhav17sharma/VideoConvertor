from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from flask_socketio import SocketIO, emit
import os
import subprocess
import uuid
import zipfile
from pathlib import Path
from werkzeug.utils import secure_filename
import threading

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
    """Clean up files older than 30 minutes"""
    import time
    current_time = time.time()
    for folder in [CONVERTED_FOLDER]:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath) and current_time - os.path.getctime(filepath) > 1800:
                    try:
                        os.remove(filepath)
                    except:
                        pass

def check_ffmpeg_available():
    """Check if FFmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_video_duration(input_path):
    """Get video duration in seconds"""
    command = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(input_path)]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return None

def convert_to_webm(input_path, output_path, progress_callback=None):
    """Convert video to WebM using VP9 codec with progress tracking"""
    if not check_ffmpeg_available():
        raise Exception("FFmpeg not found. Please install FFmpeg and add it to your PATH.")
    
    # Get video duration for ETA calculation
    duration = get_video_duration(input_path)
    
    command = [
        "ffmpeg", "-y", "-progress", "pipe:1",
        "-i", str(input_path),
        "-c:v", "libvpx-vp9",
        "-crf", "30",
        "-b:v", "0",
        "-c:a", "libopus",
        "-auto-alt-ref", "4",
        str(output_path)
    ]
    
    import time
    start_time = time.time()
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, universal_newlines=True)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        
        if output and "out_time_ms=" in output:
            try:
                # Parse current time in microseconds
                time_ms = int(output.split("out_time_ms=")[1].strip())
                current_time = time_ms / 1000000  # Convert to seconds
                
                if duration and current_time > 0:
                    progress = min(current_time / duration, 1.0)
                    elapsed = time.time() - start_time
                    
                    if progress > 0.01:  # Avoid division by very small numbers
                        eta_seconds = (elapsed / progress) - elapsed
                        eta_minutes = int(eta_seconds // 60)
                        eta_seconds = int(eta_seconds % 60)
                        
                        if progress_callback:
                            progress_callback({
                                'progress': progress * 100,
                                'eta': f"{eta_minutes}m {eta_seconds}s" if eta_minutes > 0 else f"{eta_seconds}s"
                            })
            except:
                pass
    
    return process.returncode == 0

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
            
        try:
            # Save uploaded file temporarily
            temp_path = os.path.join(CONVERTED_FOLDER, f"temp_{uuid.uuid4().hex}_{filename}")
            file.save(temp_path)
            
            original_size = os.path.getsize(temp_path)
            
            # Convert to WebM
            base_name = filename.rsplit('.', 1)[0]
            webm_filename = f"{base_name}.webm"
            webm_path = os.path.join(CONVERTED_FOLDER, webm_filename)
            
            # Progress callback for WebSocket updates
            def progress_callback(data):
                socketio.emit('conversion_progress', {
                    'filename': filename,
                    'progress': data['progress'],
                    'eta': data['eta']
                })
            
            if convert_to_webm(temp_path, webm_path, progress_callback):
                converted_size = os.path.getsize(webm_path)
                savings_percent = ((original_size - converted_size) / original_size) * 100
                
                converted_files.append({
                    'filename': webm_filename,
                    'original_name': filename,
                    'original_size': original_size,
                    'converted_size': converted_size,
                    'savings_percent': savings_percent
                })
            else:
                errors.append(f"{filename}: Conversion failed")
            
            # Clean up temp file
            os.remove(temp_path)
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
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
    
    # Process files similar to AJAX version
    converted_files = []
    errors = []
    
    for file in files:
        if not allowed_file(file.filename):
            continue
            
        filename = secure_filename(file.filename)
        try:
            temp_path = os.path.join(CONVERTED_FOLDER, f"temp_{uuid.uuid4().hex}_{filename}")
            file.save(temp_path)
            
            base_name = filename.rsplit('.', 1)[0]
            webm_filename = f"{base_name}.webm"
            webm_path = os.path.join(CONVERTED_FOLDER, webm_filename)
            
            if convert_to_webm(temp_path, webm_path):
                converted_files.append({'filename': webm_filename})
            
            os.remove(temp_path)
        except Exception as e:
            errors.append(str(e))
    
    if errors:
        for error in errors[:3]:
            flash(f'Error: {error}')
    
    if not converted_files:
        flash('No files were converted successfully')
        return redirect(url_for('index'))
    
    return render_template('index.html', results={'files': converted_files})

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

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 500MB total.')
    return redirect(url_for('index'))

def format_file_size(size_bytes):
    """Format file size in human readable format"""
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