#!/bin/bash
set -e

echo "Creating virtual environment: chatterbox_venv"
python3 -m venv chatterbox_venv

echo "Activating virtual environment..."
source chatterbox_venv/bin/activate

echo "Installing chatterbox-tts and dependencies..."

# First install build dependencies and ensure we get the right pkuseg version
pip install "numpy>=1.25.0,<2.3.0" setuptools wheel cython

# Install spacy-pkuseg first to prevent old pkuseg from being installed
pip install spacy-pkuseg

# Install chatterbox-tts dependencies manually to avoid the pkuseg conflict
pip install \
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
pip install --no-deps chatterbox-tts==0.1.4

echo "Chatterbox-tts installation complete in chatterbox_venv!"
echo "To activate this environment, run: source chatterbox_venv/bin/activate"
