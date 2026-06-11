# Video Converter

A modern web-based video converter that converts MP4, MOV, AVI, and MKV files to WebM (VP9/Opus) or HLS (m3u8) format. Uses GPU encoding when available, with automatic CPU fallback.

## Quick Start

### Docker (Recommended)
**All Platforms:** 
```bash
docker-compose up -d
```
Or use scripts: `scripts/docker-run.sh` (Mac/Linux) or `scripts/docker-run.bat` (Windows)

### One-Time Desktop Setup
**Windows:** Double-click `scripts/setup_desktop.bat`  
**Mac/Linux:** Double-click `scripts/setup_desktop.sh`

### Direct Run
**Windows:** Double-click `scripts/run.bat`  
**Mac/Linux:** Double-click `scripts/run.sh`

### Manual (if you have Python + FFmpeg)
```bash
python converter.py
```

## Project Structure

```
VideoConvertor/
├── app.py              # Flask web application
├── converter.py        # Main entry point
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container setup
├── scripts/           # Setup and run scripts
│   ├── run.bat        # Windows launcher
│   ├── run.sh         # Mac/Linux launcher
│   ├── setup_desktop.bat
│   ├── setup_desktop.sh
│   └── setup_desktop.py
├── static/            # Web assets
│   ├── style.css      # Application styles
│   └── script.js      # Client-side functionality
├── templates/         # HTML templates
│   └── index.html     # Main interface
├── utils/             # Utility scripts
│   ├── convert.py     # Simple CLI converter
│   ├── webm_convert.py # WebM conversion (GPU→CPU fallback)
│   └── hls_convert.py  # HLS conversion (GPU→CPU fallback)
├── docs/              # Documentation
│   ├── README.md      # Detailed documentation
│   └── Dockerfile     # Container setup
├── videos/            # Input directory (auto-created)
└── converted/         # Output directory (auto-created)
```

## Features

- Convert MP4, MOV, AVI, MKV to **WebM** (VP9 + Opus) or **HLS/m3u8** (H.264 + AAC)
- GPU-accelerated encoding (NVIDIA) with automatic CPU fallback
- Batch conversion (up to 10 files, 500MB total)
- Real-time progress bars and ETA
- Auto-cleanup timer (30 minutes)
- Drag & drop interface
- Cross-platform support (Windows/Mac/Linux)
- Single Page Application (SPA) experience

## System Requirements

### Docker (Easiest)
- Docker and Docker Compose
- No other dependencies needed!

### Local Installation
- Python 3.7+ (auto-detected, installation guidance provided)
- FFmpeg (installation guidance provided)
- Internet connection (for initial dependency installation)

## Sharing

To share with others, provide the entire project folder.

**Recipients:** Double-click `scripts/setup_desktop.bat` (Windows) or `scripts/setup_desktop.sh` (Mac/Linux) for one-time setup, then use the desktop icon!

## Development

- **Flask Backend:** `app.py` - Handles file upload, conversion, and API
- **Frontend:** `static/` - Modern CSS and JavaScript
- **Templates:** `templates/` - Jinja2 HTML templates
- **Entry Point:** `converter.py` - Auto-setup and server launcher
- **CLI Tool:** `utils/convert.py` - Batch conversion utility

## Troubleshooting

### FFmpeg Installation
**macOS:** `brew install ffmpeg`  
**Ubuntu/Debian:** `sudo apt install ffmpeg`  
**Windows:** Download from https://ffmpeg.org/download.html

### Permission Errors
- **Windows**: Run Command Prompt as Administrator
- **Mac/Linux**: Use `sudo python converter.py` if needed

### Dependencies
If dependencies fail to install:
```bash
pip install Flask tqdm
python converter.py
```

## Video Conversion Settings

### WebM
- **Video Codec:** VP9 — GPU: `vp9_nvenc`, CPU fallback: `libvpx-vp9`
- **Audio Codec:** Opus (libopus)
- **Quality:** CRF 30, variable bitrate

### HLS (m3u8)
- **Video Codec:** H.264 — GPU: `h264_nvenc`, CPU fallback: `libx264`
- **Audio Codec:** AAC
- **Segment length:** 10 seconds, VOD playlist

---

**Created by Vaibhav Sharma with ❤️**