@echo off
cd ..
echo Video Converter
echo ================

REM Check for FFmpeg first
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo FFmpeg not found!
    echo.
    echo Choose installation method:
    echo 1. Auto-install (requires winget or chocolatey)
    echo 2. Skip and continue (manual install later)
    echo 3. Exit
    set /p choice="Enter choice (1-3): "
    
    if "%choice%"=="1" (
        echo Attempting auto-install...
        
        REM Try winget with timeout
        echo Trying winget...
        timeout /t 2 >nul
        winget install --id=Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements >nul 2>&1
        if %errorlevel% == 0 (
            echo FFmpeg installed via winget ✓
            goto check_ffmpeg_again
        )
        
        REM Try chocolatey with timeout
        echo Trying chocolatey...
        timeout /t 2 >nul
        choco install ffmpeg -y --limit-output >nul 2>&1
        if %errorlevel% == 0 (
            echo FFmpeg installed via chocolatey ✓
            goto check_ffmpeg_again
        )
        
        echo Auto-install failed.
        goto manual_install
    ) else if "%choice%"=="2" (
        echo Skipping FFmpeg check...
        goto check_python
    ) else (
        exit /b 1
    )
    
    :manual_install
    echo Manual installation required:
    echo 1. Download from: https://ffmpeg.org/download.html#build-windows
    echo 2. Extract to C:\ffmpeg
    echo 3. Add C:\ffmpeg\bin to your PATH
    echo 4. Restart this program
    pause
    exit /b 1
    
    :check_ffmpeg_again
    timeout /t 3 >nul
    ffmpeg -version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Installation completed but FFmpeg not in PATH
        echo Please restart command prompt and try again
        pause
        exit /b 1
    )
)
echo Found FFmpeg ✓

:check_python

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