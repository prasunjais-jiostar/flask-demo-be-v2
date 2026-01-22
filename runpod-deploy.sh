#!/bin/bash

# RunPod Flask App Deployment Script
# This script automates the deployment of Flask app on RunPod with Python 3.10

set -e  # Exit on error

echo "=========================================="
echo "Flask Demo Backend - RunPod Deployment"
echo "=========================================="
echo ""

# Update system
echo "📦 Updating system packages..."
apt-get update -qq && apt-get upgrade -y -qq

# Install Python 3.10 and dependencies
echo "🐍 Installing Python 3.10 and dependencies..."
apt-get install -y -qq python3.10 python3.10-venv python3-pip git curl wget screen

# Verify Python installation
PYTHON_VERSION=$(python3.10 --version)
echo "✓ Python installed: $PYTHON_VERSION"
echo ""

# Create project directory
echo "📁 Creating project directory..."
mkdir -p /workspace/flask-demo-be
cd /workspace/flask-demo-be

# Create main.py
echo "📝 Creating main.py..."
cat > main.py << 'MAINPY'
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

@app.route('/generate-script', methods=['POST'])
def generate_script():
    """
    Endpoint to generate a script.
    Currently returns a hardcoded success response.
    """
    return jsonify({
        'status': 'success',
        'message': 'Script generated successfully',
        'data': {
            'script_id': 'script_12345',
            'script_content': 'This is a sample generated script',
            'timestamp': datetime.now().isoformat()
        }
    }), 200


@app.route('/trigger-video-gen', methods=['POST'])
def trigger_video_gen():
    """
    Endpoint to trigger video generation.
    Currently returns a hardcoded success response.
    """
    return jsonify({
        'status': 'success',
        'message': 'Video generation triggered successfully',
        'data': {
            'job_id': 'job_67890',
            'video_id': 'video_abcde',
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        }
    }), 200


@app.route('/get-job-status', methods=['GET'])
def get_job_status():
    """
    Endpoint to get job status.
    Currently returns a hardcoded success response.
    """
    job_id = request.args.get('job_id', 'job_67890')

    return jsonify({
        'status': 'success',
        'message': 'Job status retrieved successfully',
        'data': {
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'result': 'Video generation completed successfully',
            'timestamp': datetime.now().isoformat()
        }
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    # For production, use a proper WSGI server like gunicorn
    # This is just for development
    app.run(host='0.0.0.0', port=8000, debug=False)
MAINPY

echo "✓ main.py created"

# Create requirements.txt
echo "📝 Creating requirements.txt..."
cat > requirements.txt << 'REQUIREMENTS'
Flask==3.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
REQUIREMENTS

echo "✓ requirements.txt created"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3.10 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "📥 Installing Flask and dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"
echo ""

# Create systemd service
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/flask-demo.service << 'SERVICE'
[Unit]
Description=Flask Demo Backend
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/workspace/flask-demo-be
Environment="PATH=/workspace/flask-demo-be/venv/bin"
ExecStart=/workspace/flask-demo-be/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 main:app --timeout 120 --access-logfile /var/log/flask-access.log --error-logfile /var/log/flask-error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

echo "✓ Systemd service file created"

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Start the service
echo "🚀 Starting Flask application..."
systemctl start flask-demo
systemctl enable flask-demo

# Wait a moment for service to start
sleep 3

# Check status
echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""

# Display service status
if systemctl is-active --quiet flask-demo; then
    echo "✓ Flask app is running successfully!"
    echo ""

    # Try to get the pod ID from hostname
    POD_ID=$(hostname | cut -d'-' -f1)

    echo "📍 Your application is accessible at:"
    echo "   https://${POD_ID}-8000.proxy.runpod.net"
    echo ""
    echo "   (Find exact URL in RunPod dashboard under 'TCP Port Mappings')"
    echo ""

    echo "🧪 Test your endpoints:"
    echo "   curl https://${POD_ID}-8000.proxy.runpod.net/health"
    echo "   curl -X POST https://${POD_ID}-8000.proxy.runpod.net/generate-script"
    echo "   curl -X POST https://${POD_ID}-8000.proxy.runpod.net/trigger-video-gen"
    echo "   curl \"https://${POD_ID}-8000.proxy.runpod.net/get-job-status?job_id=test123\""
    echo ""

    echo "📊 Useful commands:"
    echo "   systemctl status flask-demo     # Check service status"
    echo "   systemctl restart flask-demo    # Restart service"
    echo "   systemctl stop flask-demo       # Stop service"
    echo "   journalctl -u flask-demo -f     # View logs"
    echo "   tail -f /var/log/flask-access.log  # View access logs"
    echo "   tail -f /var/log/flask-error.log   # View error logs"
    echo ""
else
    echo "❌ Flask app failed to start!"
    echo ""
    echo "Check the logs:"
    echo "   journalctl -u flask-demo -xe"
    echo ""
    echo "Or try running manually:"
    echo "   cd /workspace/flask-demo-be"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    exit 1
fi

echo "=========================================="
echo "Deployment script completed successfully!"
echo "=========================================="
