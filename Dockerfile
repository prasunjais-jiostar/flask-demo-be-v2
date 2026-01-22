FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# First install build dependencies and ensure we get the right pkuseg version
RUN --mount=type=ssh,id=github pip install "numpy>=1.25.0,<2.3.0" setuptools wheel cython

# Install spacy-pkuseg first to prevent old pkuseg from being installed
RUN --mount=type=ssh,id=github pip install spacy-pkuseg

# Install chatterbox-tts dependencies manually to avoid the pkuseg conflict
RUN --mount=type=ssh,id=github pip install \
    "librosa==0.11.0" \
    "s3tokenizer" \
    "torch==2.6.0" \
    "torchaudio==2.6.0" \
    "transformers==4.46.3" \
    "diffusers==0.29.0" \
    "resemble-perth==1.0.1" \
    "conformer==0.3.2" \
    "safetensors==0.5.3" \
    "pykakasi==2.3.0" \
    "gradio==5.44.1"

# Now install chatterbox-tts without dependencies since we've installed them manually
RUN --mount=type=ssh,id=github pip install --no-deps chatterbox-tts==0.1.4

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
