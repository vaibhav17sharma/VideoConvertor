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
                        print(f"  [WebM] Progress: {progress*100:.1f}% — ETA: {eta_str}")
                        if progress_callback:
                            progress_callback({
                                'progress': progress * 100,
                                'eta': eta_str
                            })
            except Exception:
                pass
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)


def convert_video_to_webm(input_path, output_path, progress_callback=None):
    """Convert video to WebM. Tries GPU (vp9_nvenc) first, falls back to CPU (libvpx-vp9)."""
    print(f"\n{'='*50}")
    print(f"[WebM] Starting conversion: {os.path.basename(str(input_path))}")

    duration = _get_video_duration(input_path)
    if duration:
        print(f"[WebM] Video duration: {duration:.2f}s")
    else:
        print(f"[WebM] Warning: could not determine video duration")

    gpu_command = [
        "ffmpeg", "-y", "-progress", "pipe:1",
        "-hwaccel", "cuda",
        "-i", str(input_path),
        "-c:v", "vp9_nvenc",
        "-cq", "30",
        "-c:a", "libopus",
        str(output_path)
    ]

    cpu_command = [
        "ffmpeg", "-y", "-progress", "pipe:1",
        "-i", str(input_path),
        "-c:v", "libvpx-vp9",
        "-crf", "30",
        "-b:v", "0",
        "-c:a", "libopus",
        "-auto-alt-ref", "4",
        str(output_path)
    ]

    try:
        print(f"[WebM] Attempting GPU encoder (vp9_nvenc)...")
        _run_ffmpeg_with_progress(gpu_command, duration, progress_callback)
        encoder_used = "GPU (vp9_nvenc)"
        print(f"[WebM] GPU conversion succeeded.")
    except Exception as e:
        print(f"[WebM] GPU failed ({e.__class__.__name__}). Falling back to CPU (libvpx-vp9)...")
        _run_ffmpeg_with_progress(cpu_command, duration, progress_callback)
        encoder_used = "CPU (libvpx-vp9)"
        print(f"[WebM] CPU conversion succeeded.")

    print(f"[WebM] Done — Encoder: {encoder_used}")
    print(f"{'='*50}\n")

    return {"encoder_used": encoder_used, "output_path": str(output_path)}
