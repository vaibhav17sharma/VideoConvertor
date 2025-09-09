FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p converted videos

# Set environment variable to indicate Docker environment
ENV DOCKER_ENV=1

# Expose port
EXPOSE 8080

# Run the Flask app directly
CMD ["python", "app.py"]
