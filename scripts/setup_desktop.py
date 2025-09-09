#!/usr/bin/env python3
import os
import platform
import subprocess
from pathlib import Path

def create_desktop_shortcut():
    system = platform.system()
    project_dir = Path(__file__).parent.parent.absolute()
    
    if system == "Windows":
        create_windows_shortcut(project_dir)
    elif system == "Darwin":  # macOS
        create_macos_shortcut(project_dir)
    elif system == "Linux":
        create_linux_shortcut(project_dir)
    else:
        print(f"Unsupported system: {system}")

def create_windows_shortcut(project_dir):
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "Video Converter.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = os.path.join(project_dir, "scripts", "run.bat")
        shortcut.WorkingDirectory = str(project_dir)
        shortcut.IconLocation = os.path.join(project_dir, "scripts", "run.bat")
        shortcut.save()
        
        print(f"Desktop shortcut created: {shortcut_path}")
    except ImportError:
        print("Creating manual shortcut...")
        print(f"Create a shortcut to: {project_dir}/scripts/run.bat")

def create_macos_shortcut(project_dir):
    desktop = Path.home() / "Desktop"
    app_name = "Video Converter.app"
    app_path = desktop / app_name
    
    # Create .app bundle structure
    contents_dir = app_path / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    for dir_path in [contents_dir, macos_dir, resources_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create Info.plist
    info_plist = contents_dir / "Info.plist"
    info_plist.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>VideoConverter</string>
    <key>CFBundleIdentifier</key>
    <string>com.videoconverter.app</string>
    <key>CFBundleName</key>
    <string>Video Converter</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>''')
    
    # Create executable script
    executable = macos_dir / "VideoConverter"
    executable.write_text(f'''#!/bin/bash
cd "{project_dir}"
python3 converter.py
''')
    executable.chmod(0o755)
    
    print(f"Desktop app created: {app_path}")

def create_linux_shortcut(project_dir):
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "VideoConverter.desktop"
    
    shortcut_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Video Converter
Comment=Convert videos to WebM
Exec=python3 "{project_dir}/converter.py"
Path={project_dir}
Icon=video-x-generic
Terminal=false
Categories=AudioVideo;
'''
    
    shortcut_path.write_text(shortcut_content)
    shortcut_path.chmod(0o755)
    
    print(f"Desktop shortcut created: {shortcut_path}")

if __name__ == "__main__":
    print("Creating desktop shortcut...")
    create_desktop_shortcut()
    print("Done! You can now run Video Converter from your desktop.")