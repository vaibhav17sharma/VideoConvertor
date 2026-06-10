import os
import subprocess
import time


def _get_video_duration(input_path):
    command = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(input_path)]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return float(result.stdout.strip())
    except Exception:
        return None


def _run_ffmpeg_with_progress(command, duration, progress_callback):
    start_time = time.time()
    # stderr=DEVNULL prevents the stderr pipe buffer from filling up and deadlocking FFmpeg
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        universal_newlines=True
    )
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output and "out_time_ms=" in output:
            try:
                time_ms = int(output.split("out_time_ms=")[1].strip())
                current_time = time_ms / 1000000
                if duration and current_time > 0:
                    progress = min(current_time / duration, 1.0)
                    elapsed = time.time() - start_time
                    if progress > 0.01:
                        eta_seconds = (elapsed / progress) - elapsed
                        eta_minutes = int(eta_seconds // 60)
                        eta_secs = int(eta_seconds % 60)
                        eta_str = f"{eta_minutes}m {eta_secs}s" if eta_minutes > 0 else f"{eta_secs}s"
                        print(f"  [HLS] Progress: {progress*100:.1f}% — ETA: {eta_str}")
                        if progress_callback:
                            progress_callback({
                                'progress': progress * 100,
                                'eta': eta_str
                            })
            except Exception:
                pass
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)


def convert_video_to_hls(input_path, output_dir, playlist_name="playlist.m3u8", progress_callback=None):
    """Convert video to HLS. Tries GPU (h264_nvenc) first, falls back to CPU (libx264)."""
    print(f"\n{'='*50}")
    print(f"[HLS] Starting conversion: {os.path.basename(str(input_path))}")
    print(f"[HLS] Output dir: {output_dir}")

    duration = _get_video_duration(input_path)
    if duration:
        print(f"[HLS] Video duration: {duration:.2f}s")
    else:
        print(f"[HLS] Warning: could not determine video duration")

    os.makedirs(output_dir, exist_ok=True)

    playlist_path = os.path.join(output_dir, playlist_name)
    segment_pattern = os.path.join(output_dir, "segment_%03d.ts")

    gpu_command = [
        "ffmpeg", "-y", "-progress", "pipe:1",
        "-hwaccel", "cuda",
        "-i", str(input_path),
        "-c:v", "h264_nvenc",
        "-preset", "p4",
        "-c:a", "aac",
        "-hls_time", "10",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", segment_pattern,
        playlist_path
    ]

    cpu_command = [
        "ffmpeg", "-y", "-progress", "pipe:1",
        "-i", str(input_path),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-threads", "0",
        "-c:a", "aac",
        "-hls_time", "10",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", segment_pattern,
        playlist_path
    ]

    try:
        print(f"[HLS] Attempting GPU encoder (h264_nvenc)...")
        _run_ffmpeg_with_progress(gpu_command, duration, progress_callback)
        encoder_used = "GPU (h264_nvenc)"
        print(f"[HLS] GPU conversion succeeded.")
    except Exception as e:
        print(f"[HLS] GPU failed ({e.__class__.__name__}). Falling back to CPU (libx264)...")
        _run_ffmpeg_with_progress(cpu_command, duration, progress_callback)
        encoder_used = "CPU (libx264)"
        print(f"[HLS] CPU conversion succeeded.")

    segment_count = len([f for f in os.listdir(output_dir) if f.endswith('.ts')])
    total_size = sum(
        os.path.getsize(os.path.join(output_dir, f))
        for f in os.listdir(output_dir)
    )

    print(f"[HLS] Done — Encoder: {encoder_used} | Segments: {segment_count} | Size: {total_size/1024:.1f} KB")
    print(f"{'='*50}\n")

    return {
        "encoder_used": encoder_used,
        "playlist": playlist_name,
        "segment_count": segment_count,
        "total_size": total_size,
    }
