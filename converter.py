#!/usr/bin/env python3
import subprocess
import sys
import os
import webbrowser
import threading
import time
import platform

def setup_venv_and_install():
    """Create venv and install packages (Mac/Linux)"""
    import venv
    
    venv_path = 'venv'
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
    
    # Get venv python and pip paths
    if platform.system() == 'Windows':
        python_exe = os.path.join(venv_path, 'Scripts', 'python')
        pip_exe = os.path.join(venv_path, 'Scripts', 'pip')
    else:
        python_exe = os.path.join(venv_path, 'bin', 'python')
        pip_exe = os.path.join(venv_path, 'bin', 'pip')
    
    requirements = ['Flask', 'tqdm']
    
    print("Installing dependencies in virtual environment...")
    for req in requirements:
        print(f"Installing {req}...")
        try:
            subprocess.check_call([pip_exe, 'install', req])
        except subprocess.CalledProcessError:
            print(f"Failed to install {req}")
            return None
    
    return python_exe

def install_requirements():
    """Install required packages (Windows fallback)"""
    requirements = ['Flask', 'tqdm']
    
    print("Installing dependencies...")
    for req in requirements:
        print(f"Installing {req}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
        except subprocess.CalledProcessError:
            print(f"Failed to install {req}")
            return False
    return True

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def cleanup_old_files():
    """Remove files older than 2 hours from converted folder"""
    current_time = time.time()
    if os.path.exists('converted'):
        for filename in os.listdir('converted'):
            filepath = os.path.join('converted', filename)
            if os.path.isfile(filepath) and current_time - os.path.getctime(filepath) > 7200:
                try:
                    os.remove(filepath)
                except:
                    pass

def cleanup_files():
    """Background cleanup task"""
    while True:
        time.sleep(3600)  # Wait 1 hour
        cleanup_old_files()

def main():
    print("Video to WebM Converter")
    print("=" * 30)
    print(f"Running on {platform.system()} {platform.release()}")
    print()
    
    # Check ffmpeg
    if not check_ffmpeg():
        print("ERROR: ffmpeg not found!")
        print("Please install ffmpeg:")
        if platform.system() == 'Darwin':
            print("  brew install ffmpeg")
        elif platform.system() == 'Linux':
            print("  sudo apt install ffmpeg  # Ubuntu/Debian")
            print("  sudo yum install ffmpeg  # CentOS/RHEL")
        else:
            print("  Download from: https://ffmpeg.org/download.html")
        input("Press Enter to exit...")
        return
    
    # Check if packages are installed
    try:
        import flask
        import tqdm
    except ImportError:
        print("Installing required packages...")
        
        # Use venv on Mac/Linux, direct install on Windows
        if platform.system() in ['Darwin', 'Linux']:
            python_exe = setup_venv_and_install()
            if not python_exe:
                print("Failed to setup environment. Please run manually:")
                print("python3 -m venv venv")
                print("source venv/bin/activate")
                print("pip install Flask tqdm")
                input("Press Enter to exit...")
                return
            
            # Restart with venv python
            print("Restarting with virtual environment...")
            subprocess.call([python_exe, os.path.abspath(__file__)])
            return
        else:
            # Windows - direct install
            if not install_requirements():
                print("Failed to install packages. Please run manually:")
                print("pip install Flask tqdm")
                input("Press Enter to exit...")
                return
    
    # Create required directories
    os.makedirs('converted', exist_ok=True)
    os.makedirs('videos', exist_ok=True)
    
    # Clean old files on startup
    cleanup_old_files()
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_files, daemon=True)
    cleanup_thread.start()
    
    # Import and run Flask app
    try:
        from app import app
        print("Starting video converter...")
        print("Opening browser...")
        
        # Open browser only if not in Docker
        if not os.getenv('DOCKER_ENV'):
            def open_browser():
                time.sleep(1.5)
                webbrowser.open('http://localhost:8080')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.start()
        
        # Use 0.0.0.0 for Docker, 127.0.0.1 for local
        host = '0.0.0.0' if os.getenv('DOCKER_ENV') else '127.0.0.1'
        app.run(host=host, port=8080, debug=False)
        
    except ImportError:
        print("Error: app.py not found in current directory")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == '__main__':
    main()