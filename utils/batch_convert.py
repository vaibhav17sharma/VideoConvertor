import os
import subprocess
from tqdm import tqdm
from pathlib import Path

INPUT_DIR = Path("./videos")
OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Video file extensions to look for
VIDEO_EXTENSIONS = {".mp4", ".mov"}

def find_video_files(directory):
    """Recursively find video files in a directory."""
    return [f for f in directory.rglob("*") if f.suffix.lower() in VIDEO_EXTENSIONS]

def convert_to_lossless_webm(input_path: Path, output_path: Path):
    """Convert the video to lossless WebM using VP9 codec."""
    command = [
        "ffmpeg",
        "-i", str(input_path),
        "-c:v", "libvpx-vp9",
        "-crf", "30",  # Adjust CRF for high quality (lower value = higher quality)
        "-b:v", "0",  # VP9 codec for lossless
        "-c:a", "libopus",
        "-auto-alt-ref", "4",      # Use Opus for audio
        str(output_path)
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"\n[ERROR] Failed to convert {input_path}")
        print(result.stderr)
        return False
    return True


def main():
    video_files = find_video_files(INPUT_DIR)

    if not video_files:
        print("No .mp4 or .mov files found in", INPUT_DIR)
        return

    print(f"Found {len(video_files)} video(s). Starting conversion...\n")

    for video_file in tqdm(video_files, desc="Converting", unit="file"):
        relative_path = video_file.relative_to(INPUT_DIR)
        output_file = OUTPUT_DIR / relative_path.with_suffix(".webm")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.exists():
            tqdm.write(f"Skipping {relative_path} (already converted)")
            continue

        success = convert_to_lossless_webm(video_file, output_file)
        if success:
            tqdm.write(f"✅ Converted: {relative_path}")
        else:
            tqdm.write(f"❌ Failed: {relative_path}")

if __name__ == "__main__":
    main()
