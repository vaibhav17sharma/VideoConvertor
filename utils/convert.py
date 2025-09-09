import os
import subprocess
from pathlib import Path
from tqdm import tqdm

def convert_to_webm(input_path, output_path):
    """Convert video to WebM using VP9 codec"""
    command = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-c:v", "libvpx-vp9",
        "-crf", "30",
        "-b:v", "0",
        "-c:a", "libopus",
        "-auto-alt-ref", "4",
        str(output_path)
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error converting {input_path}: {result.stderr}")
        return False
    return True

def find_video_files(directory):
    """Find video files in directory"""
    video_extensions = {".mp4", ".mov", ".avi", ".mkv"}
    return [f for f in Path(directory).rglob("*") if f.suffix.lower() in video_extensions]

def main():
    print("Starting video to WebM batch conversion...")
    
    input_dir = Path("./videos")
    output_dir = Path("./converted")
    output_dir.mkdir(exist_ok=True)
    
    if not input_dir.exists():
        print(f"Input directory {input_dir} not found!")
        return
    
    video_files = find_video_files(input_dir)
    
    if not video_files:
        print("No video files found!")
        return
    
    print(f"Found {len(video_files)} video(s)")
    
    for video_file in tqdm(video_files, desc="Converting"):
        output_file = output_dir / (video_file.stem + ".webm")
        
        if output_file.exists():
            tqdm.write(f"Skipping {video_file.name} (already exists)")
            continue
        
        if convert_to_webm(video_file, output_file):
            tqdm.write(f"✅ Converted: {video_file.name}")
        else:
            tqdm.write(f"❌ Failed: {video_file.name}")

if __name__ == "__main__":
    main()