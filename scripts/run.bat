@echo off
cd ..
echo Video Converter
echo ================

REM Check for FFmpeg first
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo FFmpeg not found, attempting auto-install...
    
    REM Try winget first
    winget install --id=Gyan.FFmpeg -e --silent >nul 2>&1
    if %errorlevel% == 0 (
        echo FFmpeg installed via winget ✓
        goto check_ffmpeg_again
    )
    
    REM Try chocolatey
    choco install ffmpeg -y >nul 2>&1
    if %errorlevel% == 0 (
        echo FFmpeg installed via chocolatey ✓
        goto check_ffmpeg_again
    )
    
    echo Auto-install failed. Manual installation required:
    echo 1. Download from: https://ffmpeg.org/download.html#build-windows
    echo 2. Extract to C:\ffmpeg
    echo 3. Add C:\ffmpeg\bin to your PATH
    echo 4. Restart this program
    pause
    exit /b 1
    
    :check_ffmpeg_again
    ffmpeg -version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Installation completed but FFmpeg still not in PATH
        echo Please restart your command prompt and try again
        pause
        exit /b 1
    )
)
echo Found FFmpeg ✓

REM Check for Python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Found Python ✓
    echo Starting converter...
    python converter.py
    cd scripts
    goto end
)

python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo Found Python3 ✓
    echo Starting converter...
    python3 converter.py
    cd scripts
    goto end
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    echo Found Python ✓
    echo Starting converter...
    py converter.py
    cd scripts
    goto end
)

echo ERROR: Python not found!
echo Please install Python from: https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
pause

:end
pause