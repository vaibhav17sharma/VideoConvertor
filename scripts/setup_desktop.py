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
    """Create Windows desktop shortcut using VBS script"""
    # Try multiple desktop locations
    desktop_paths = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
        os.environ.get('USERPROFILE', '') + "\\Desktop",
        os.environ.get('USERPROFILE', '') + "\\OneDrive\\Desktop"
    ]
    
    desktop = None
    for path in desktop_paths:
        if os.path.exists(path):
            desktop = path
            break
    
    if not desktop:
        raise Exception("Could not find Desktop folder")
    
    shortcut_path = os.path.join(desktop, "Video Converter.lnk")
    target = os.path.join(project_dir, "scripts", "run.bat")
    working_dir = os.path.join(project_dir, "scripts")
    
    print(f"Creating shortcut at: {shortcut_path}")
    print(f"Target: {target}")
    print(f"Working Directory: {working_dir}")
    
    # Create VBS script to make shortcut
    icon_path = os.path.join(project_dir, "icon.ico")
    if not os.path.exists(icon_path):
        icon_path = target  # Use target as fallback
    
    vbs_script = f'''Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{shortcut_path}")
oLink.TargetPath = "{target}"
oLink.WorkingDirectory = "{working_dir}"
oLink.IconLocation = "{icon_path}"
oLink.Save
'''
    
    # Write and execute VBS script
    vbs_file = "create_shortcut.vbs"
    with open(vbs_file, 'w') as f:
        f.write(vbs_script)
    
    try:
        result = subprocess.run(["cscript", "//nologo", vbs_file], capture_output=True, text=True)
        os.remove(vbs_file)
        if result.returncode == 0:
            print(f"Desktop shortcut created: {shortcut_path}")
            if os.path.exists(shortcut_path):
                print("Shortcut file confirmed to exist")
            else:
                print("Warning: Shortcut creation reported success but file not found")
        else:
            raise Exception(f"VBS script failed: {result.stderr}")
    except Exception as e:
        if os.path.exists(vbs_file):
            os.remove(vbs_file)
        raise e

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
    
    # Add icon if available
    icon_path = project_dir / "icon.icns"
    if icon_path.exists():
        import shutil
        shutil.copy(icon_path, resources_dir / "icon.icns")
        # Update Info.plist to reference icon
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
    <key>CFBundleIconFile</key>
    <string>icon</string>
</dict>
</plist>''')
    
    print(f"Desktop app created: {app_path}")

def create_linux_shortcut(project_dir):
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "VideoConverter.desktop"
    
    # Check for custom icon
    icon_path = project_dir / "icon.png"
    icon = str(icon_path) if icon_path.exists() else "video-x-generic"
    
    shortcut_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Video Converter
Comment=Convert videos to WebM
Exec=python3 "{project_dir}/converter.py"
Path={project_dir}
Icon={icon}
Terminal=false
Categories=AudioVideo;
'''
    
    shortcut_path.write_text(shortcut_content)
    shortcut_path.chmod(0o755)
    
    print(f"Desktop shortcut created: {shortcut_path}")

def main():
    print("Video Converter - Desktop Setup")
    print("=" * 30)
    
    system = platform.system()
    
    try:
        if system == "Windows":
            project_dir = Path(__file__).parent.parent.absolute()
            create_windows_shortcut(project_dir)
        elif system == "Darwin":  # macOS
            project_dir = Path(__file__).parent.parent.absolute()
            create_macos_shortcut(project_dir)
        elif system == "Linux":
            project_dir = Path(__file__).parent.parent.absolute()
            create_linux_shortcut(project_dir)
        else:
            print(f"Unsupported system: {system}")
            return
        
        print("\nSetup complete! You can now:")
        print("1. Find 'Video Converter' on your desktop")
        print("2. Double-click it to start the converter")
        print("3. Delete this folder if you want - the shortcut will still work")
        
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
        print("You can still use the converter by running:")
        if system == "Windows":
            print("  run.bat")
        else:
            print("  ./run.sh")

if __name__ == '__main__':
    main()