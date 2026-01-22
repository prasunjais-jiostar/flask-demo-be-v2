# Quick Start - RunPod Deployment (Python 3.10)

## One-Line Deploy (Automated Script)

```bash
# On RunPod terminal, run this single command:
curl -o runpod-deploy.sh https://raw.githubusercontent.com/your-repo/flask-demo-be/main/runpod-deploy.sh && chmod +x runpod-deploy.sh && ./runpod-deploy.sh
```

---

## Manual Deploy (5 Minutes)

### 1. Create RunPod Pod
- Go to: https://www.runpod.io/console/pods
- Click "Deploy" → Choose CPU or GPU
- **Expose HTTP Ports**: `8000`
- Click "Deploy"

### 2. Copy-Paste This Into RunPod Terminal

```bash
# Install Python 3.10
apt-get update && apt-get install -y python3.10 python3.10-venv python3-pip screen

# Create project directory
mkdir -p /workspace/flask-demo-be && cd /workspace/flask-demo-be

# Create main.py
cat > main.py << 'EOF'
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

@app.route('/generate-script', methods=['POST'])
def generate_script():
    return jsonify({'status': 'success', 'message': 'Script generated successfully', 'data': {'script_id': 'script_12345', 'script_content': 'This is a sample generated script', 'timestamp': datetime.now().isoformat()}}), 200

@app.route('/trigger-video-gen', methods=['POST'])
def trigger_video_gen():
    return jsonify({'status': 'success', 'message': 'Video generation triggered successfully', 'data': {'job_id': 'job_67890', 'video_id': 'video_abcde', 'status': 'processing', 'timestamp': datetime.now().isoformat()}}), 200

@app.route('/get-job-status', methods=['GET'])
def get_job_status():
    job_id = request.args.get('job_id', 'job_67890')
    return jsonify({'status': 'success', 'message': 'Job status retrieved successfully', 'data': {'job_id': job_id, 'status': 'completed', 'progress': 100, 'result': 'Video generation completed successfully', 'timestamp': datetime.now().isoformat()}}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
EOF

# Setup and run
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
screen -dmS flask-app bash -c "gunicorn -w 4 -b 0.0.0.0:8000 main:app"

echo "✅ Deployment complete!"
echo "Access your app at: https://$(hostname | cut -d'-' -f1)-8000.proxy.runpod.net/health"
```

### 3. Test Your Endpoints

```bash
# Get your RunPod URL (replace <pod-id> with your actual pod ID)
export URL="https://<pod-id>-8000.proxy.runpod.net"

# Test
curl $URL/health
curl -X POST $URL/generate-script
curl -X POST $URL/trigger-video-gen
curl "$URL/get-job-status?job_id=test123"
```

---

## Useful Commands

```bash
# Check if app is running
ps aux | grep gunicorn

# View logs in screen
screen -r flask-app

# Restart app
screen -X -S flask-app quit
cd /workspace/flask-demo-be && source venv/bin/activate
screen -dmS flask-app bash -c "gunicorn -w 4 -b 0.0.0.0:8000 main:app"

# Check port
lsof -i :8000
```

---

## Upload Your Own Files (from local machine)

```bash
# From your local machine (replace placeholders):
scp -P <runpod-port> -r /Users/prasunj/Documents/jiostar/personal/flask-demo-be/* root@<pod-id>.runpod.io:/workspace/flask-demo-be/
```

---

## Full Documentation
- [RUNPOD_DEPLOYMENT_PYTHON.md](RUNPOD_DEPLOYMENT_PYTHON.md) - Complete guide
- [README.md](README.md) - Project overview
