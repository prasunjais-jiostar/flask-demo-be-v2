#!/bin/bash

# Flask Demo Backend Setup Script
# This script sets up the virtual environment and installs dependencies

echo "================================================"
echo "Flask Demo Backend - Setup Script"
echo "================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    echo "✓ Virtual environment created successfully"
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

if [ $? -eq 0 ]; then
    echo "✓ Virtual environment activated"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo ""

# Install dependencies
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

echo "================================================"
echo "✅ Setup completed successfully!"
echo "================================================"
echo ""
echo "To start the server:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the development server:"
echo "     python main.py"
echo ""
echo "  3. Or run with gunicorn (production):"
echo "     gunicorn -w 4 -b 0.0.0.0:8000 main:app"
echo ""
echo "Test the endpoints:"
echo "  curl http://localhost:8000/health"
echo "  curl -X POST http://localhost:8000/generate-script"
echo "  curl -X POST http://localhost:8000/trigger-video-gen"
echo "  curl http://localhost:8000/get-job-status?job_id=test123"
echo ""
