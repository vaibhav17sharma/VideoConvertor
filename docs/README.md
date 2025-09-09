# Video to WebM Converter - Documentation

## Overview

This application converts video files (MP4, MOV, AVI, MKV) to WebM format using the VP9 video codec and Opus audio codec. It provides both a web interface and command-line tools for conversion.

## Architecture

### Web Application (`app.py`)
- Flask-based web server
- Handles file uploads and conversions
- Provides REST API endpoints
- Manages temporary file cleanup

### Main Entry Point (`converter.py`)
- Auto-detects and installs dependencies
- Checks for FFmpeg availability
- Launches the web application
- Handles cross-platform compatibility

### Utility Scripts (`utils/`)
- `convert.py`: Command-line batch converter
- Processes entire directories of videos

### Frontend (`static/`, `templates/`)
- Modern responsive web interface
- Drag-and-drop file upload
- Real-time progress tracking
- File size comparison and savings display

## API Endpoints

### `POST /upload`
Handles video file uploads and conversion.

**Parameters:**
- `files`: Multiple video files (multipart/form-data)

**Response (JSON):**
```json
{
  "success": true,
  "files": [
    {
      "filename": "output.webm",
      "original_name": "input.mp4",
      "original_size": 10485760,
      "converted_size": 8388608,
      "savings_percent": 20.0
    }
  ],
  "errors": [],
  "skipped": [],
  "is_batch": false
}
```

### `GET /download/<filename>`
Downloads converted files.

### `GET /download_batch`
Downloads all converted files as a ZIP archive.

## Configuration

### File Limits
- Maximum files per batch: 10
- Maximum total size: 500MB
- Supported formats: MP4, MOV, AVI, MKV

### Conversion Settings
- Video codec: VP9 (libvpx-vp9)
- Audio codec: Opus (libopus)
- CRF: 30 (high quality)
- Variable bitrate optimization

### Cleanup
- Converted files are automatically deleted after 30 minutes
- Temporary files are cleaned up immediately after conversion

## Deployment

### Local Development
```bash
python converter.py
```

### Docker
```bash
docker build -t video-converter .
docker run -p 8080:8080 video-converter
```

### Production
- Use a WSGI server like Gunicorn
- Configure reverse proxy (nginx)
- Set up proper file storage and cleanup
- Configure security settings

## Security Considerations

- File type validation
- File size limits
- Secure filename handling
- Temporary file cleanup
- Input sanitization for FFmpeg commands

## Performance

### Optimization Tips
- Use SSD storage for temporary files
- Ensure adequate RAM for large video files
- Consider GPU acceleration for VP9 encoding
- Implement queue system for high-volume usage

### Monitoring
- Track conversion times
- Monitor disk space usage
- Log conversion errors
- Monitor system resources

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Install FFmpeg system-wide
   - Add FFmpeg to PATH

2. **Permission errors**
   - Check file permissions
   - Run with appropriate privileges

3. **Out of disk space**
   - Monitor converted/ directory
   - Implement disk space checks

4. **Conversion failures**
   - Check FFmpeg logs
   - Validate input file integrity
   - Verify codec support

### Logging
Enable debug logging by setting `debug=True` in `app.py` or using environment variables.