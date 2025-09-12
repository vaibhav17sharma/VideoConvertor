#!/bin/bash
cd "$(dirname "$0")/.."

echo "Video Converter"
echo "================"

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg not found, attempting auto-install..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - try homebrew
        if command -v brew &> /dev/null; then
            echo "Installing FFmpeg via Homebrew..."
            brew install ffmpeg
        else
            echo "Homebrew not found. Please install FFmpeg manually:"
            echo "  brew install ffmpeg"
            read -p "Press Enter to exit..."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - try common package managers
        if command -v apt &> /dev/null; then
            echo "Installing FFmpeg via apt..."
            sudo apt update && sudo apt install -y ffmpeg
        elif command -v yum &> /dev/null; then
            echo "Installing FFmpeg via yum..."
            sudo yum install -y ffmpeg
        elif command -v dnf &> /dev/null; then
            echo "Installing FFmpeg via dnf..."
            sudo dnf install -y ffmpeg
        else
            echo "No supported package manager found. Please install FFmpeg manually."
            read -p "Press Enter to exit..."
            exit 1
        fi
    fi
    
    # Check if installation worked
    if ! command -v ffmpeg &> /dev/null; then
        echo "Auto-install failed. Please install FFmpeg manually."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi
echo "Found FFmpeg ✓"

# Check for Python
if command -v python3 &> /dev/null; then
    echo "Found Python3 ✓"
    echo "Starting converter..."
    python3 converter.py
elif command -v python &> /dev/null; then
    echo "Found Python ✓"
    echo "Starting converter..."
    python converter.py
else
    echo "ERROR: Python not found!"
    echo "Please install Python 3.7+"
    read -p "Press Enter to exit..."
    exit 1
fi