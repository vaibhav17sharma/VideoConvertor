#!/bin/bash
cd "$(dirname "$0")/.."

echo "Building Docker image..."
docker build -t video-converter .

echo "Running Docker container..."
docker run -d \
  --name video-converter \
  -p 8080:8080 \
  -v "$(pwd)/videos:/app/videos" \
  -v "$(pwd)/converted:/app/converted" \
  video-converter

echo "Video Converter is running at http://localhost:8080"
echo "To stop: docker stop video-converter"
echo "To remove: docker rm video-converter"