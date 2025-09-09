# Video to WebM Converter

A modern web-based video converter that converts MP4, MOV, AVI, and MKV files to WebM format using VP9 codec with Opus audio.

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
│   └── convert.py     # Simple CLI converter
├── docs/              # Documentation
│   ├── README.md      # Detailed documentation
│   └── Dockerfile     # Container setup
├── videos/            # Input directory (auto-created)
└── converted/         # Output directory (auto-created)
```

## Features

- Convert MP4, MOV, AVI, MKV to WebM (VP9 + Opus)
- Batch conversion (up to 10 files, 500MB total)
- Real-time file size comparison and savings
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

- **Video Codec:** VP9 (libvpx-vp9)
- **Audio Codec:** Opus (libopus)
- **Quality:** CRF 30 (high quality)
- **Mode:** Variable bitrate for optimal compression

---

**Created by Vaibhav Sharma with ❤️**