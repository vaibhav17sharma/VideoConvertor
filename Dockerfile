FROM python:3.11

RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libvpx-dev \
    libopus-dev && \
    apt-get clean

# Create app directory
WORKDIR /app

# Copy Python requirements and application files
COPY requirements.txt ./
COPY convert.py ./
COPY videos ./videos

# Create output directory
RUN mkdir -p /app/output

# Install Python dependencies (if any)
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the script
CMD ["python", "Videoconvert.py"]
