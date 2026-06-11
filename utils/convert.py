import os
from pathlib import Path
from tqdm import tqdm

from webm_convert import convert_video_to_webm


def find_video_files(directory):
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

        try:
            result = convert_video_to_webm(str(video_file), str(output_file))
            tqdm.write(f"✅ Converted: {video_file.name} [{result['encoder_used']}]")
        except Exception as e:
            tqdm.write(f"❌ Failed: {video_file.name} — {e}")


if __name__ == "__main__":
    main()
