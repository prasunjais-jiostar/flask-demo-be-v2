# RunPod Deployment Guide - Direct Python Installation

This guide shows you how to deploy your Flask application on RunPod using direct Python 3.10 installation (no Docker required).

---

## Quick Start Guide

### Step 1: Create a RunPod Pod

1. **Go to RunPod Dashboard**: https://www.runpod.io/console/pods
2. **Click "Deploy"** → Choose **"CPU Pod"** or **"GPU Pod"**
3. **Select a Template**: Choose **"RunPod Pytorch"** or **"Ubuntu 22.04"**
4. **Configure the Pod**:
   - **GPU Type**: Select CPU-only (cheapest) or any GPU
   - **Container Disk**: 20 GB minimum
   - **Volume Disk**: 10 GB (optional)
   - **Expose HTTP Ports**: `8000`
   - **Expose TCP Ports**: `8000,22`
5. **Click "Deploy On-Demand"** or **"Deploy Spot"** (spot is cheaper)
6. **Wait for deployment** (1-2 minutes)

### Step 2: Connect to Your Pod

1. Go to **"My Pods"** in RunPod dashboard
2. Click on your pod
3. Click **"Connect"** → **"Start Web Terminal"** (easiest)
   - Or use SSH: Copy the SSH command and run it in your local terminal

### Step 3: Install Python 3.10 and Dependencies

```bash
# Update system packages
apt-get update && apt-get upgrade -y

# Install Python 3.10 and required packages
apt-get install -y python3.10 python3.10-venv python3-pip git curl wget

# Verify Python version
python3.10 --version
```

### Step 4: Upload Your Application Files

**Option A: Clone from Git (if you have a GitHub repo)**
```bash
cd /workspace
git clone https://github.com/your-username/flask-demo-be.git
cd flask-demo-be
```

**Option B: Manual File Upload via SCP (from your local machine)**
```bash
# Get SSH details from RunPod dashboard
# Run this from your LOCAL machine (not on RunPod):
scp -P <port> -r /Users/prasunj/Documents/jiostar/personal/flask-demo-be/* root@<pod-id>.runpod.io:/workspace/flask-demo-be/
```

**Option C: Create Files Manually (fastest for testing)**
```bash
# Create project directory
mkdir -p /workspace/flask-demo-be
cd /workspace/flask-demo-be

# Create main.py
cat > main.py << 'EOF'
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

@app.route('/generate-script', methods=['POST'])
def generate_script():
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
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
EOF
```

### Step 5: Set Up Virtual Environment

```bash
# Navigate to project directory
cd /workspace/flask-demo-be

# Create virtual environment with Python 3.10
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Run Your Flask Application

**Method 1: Quick Test (Foreground)**
```bash
# Run with Flask development server (for testing only)
python main.py

# Or run with gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

**Method 2: Run in Background with Screen (Recommended)**
```bash
# Install screen
apt-get install -y screen

# Start a screen session
screen -S flask-app

# Activate venv and run
cd /workspace/flask-demo-be
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# Detach from screen: Press Ctrl+A, then D
# Your app keeps running in background!

# To reattach later:
screen -r flask-app

# To list all screen sessions:
screen -ls
```

**Method 3: Run as Daemon (Alternative)**
```bash
cd /workspace/flask-demo-be
source venv/bin/activate
nohup gunicorn -w 4 -b 0.0.0.0:8000 main:app > /var/log/flask-app.log 2>&1 &

# Check if running
ps aux | grep gunicorn

# View logs
tail -f /var/log/flask-app.log

# Stop the app
pkill gunicorn
```

**Method 4: Systemd Service (Production)**
```bash
# Create systemd service file
cat > /etc/systemd/system/flask-demo.service << 'EOF'
[Unit]
Description=Flask Demo Backend
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/workspace/flask-demo-be
Environment="PATH=/workspace/flask-demo-be/venv/bin"
ExecStart=/workspace/flask-demo-be/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
systemctl daemon-reload
systemctl start flask-demo
systemctl enable flask-demo

# Check status
systemctl status flask-demo

# View logs
journalctl -u flask-demo -f

# Manage service
systemctl stop flask-demo
systemctl restart flask-demo
```

### Step 7: Access Your Application

1. **Go back to RunPod Dashboard** → Your Pod
2. **Find the HTTP Port URL**:
   - Look for "TCP Port Mappings" or "HTTP Services"
   - You'll see: `https://<pod-id>-8000.proxy.runpod.net`
3. **Copy that URL** - this is your public endpoint!

### Step 8: Test Your Endpoints

```bash
# Replace with your actual RunPod URL
export RUNPOD_URL="https://<pod-id>-8000.proxy.runpod.net"

# Test health check
curl $RUNPOD_URL/health

# Test generate-script endpoint
curl -X POST $RUNPOD_URL/generate-script

# Test trigger-video-gen endpoint
curl -X POST $RUNPOD_URL/trigger-video-gen

# Test get-job-status endpoint
curl "$RUNPOD_URL/get-job-status?job_id=test123"
```

---

## Complete Step-by-Step Commands (Copy & Paste)

Here's the complete script you can copy and paste directly into your RunPod terminal:

```bash
#!/bin/bash

# Update system
apt-get update && apt-get upgrade -y

# Install Python 3.10 and dependencies
apt-get install -y python3.10 python3.10-venv python3-pip git curl wget screen

# Create project directory
mkdir -p /workspace/flask-demo-be
cd /workspace/flask-demo-be

# Create main.py
cat > main.py << 'MAINPY'
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

@app.route('/generate-script', methods=['POST'])
def generate_script():
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
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
MAINPY

# Create requirements.txt
cat > requirements.txt << 'REQUIREMENTS'
Flask==3.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
REQUIREMENTS

# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/flask-demo.service << 'SERVICE'
[Unit]
Description=Flask Demo Backend
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/workspace/flask-demo-be
Environment="PATH=/workspace/flask-demo-be/venv/bin"
ExecStart=/workspace/flask-demo-be/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Start the service
systemctl daemon-reload
systemctl start flask-demo
systemctl enable flask-demo

# Check status
echo "=================================="
echo "Flask app is now running!"
echo "=================================="
systemctl status flask-demo

echo ""
echo "Your app is accessible at:"
echo "https://<your-pod-id>-8000.proxy.runpod.net"
echo ""
echo "Find your exact URL in RunPod dashboard under 'TCP Port Mappings'"
```

---

## Managing Your Application

### Check if App is Running
```bash
# Check systemd service
systemctl status flask-demo

# Check process
ps aux | grep gunicorn

# Check port
netstat -tlnp | grep 8000
# or
lsof -i :8000
```

### View Logs
```bash
# Systemd logs
journalctl -u flask-demo -f

# Or if using nohup
tail -f /var/log/flask-app.log

# Or if using screen
screen -r flask-app
```

### Restart Application
```bash
# If using systemd
systemctl restart flask-demo

# If using screen
screen -r flask-app
# Press Ctrl+C to stop
# Then: gunicorn -w 4 -b 0.0.0.0:8000 main:app

# If using nohup/daemon
pkill gunicorn
cd /workspace/flask-demo-be
source venv/bin/activate
nohup gunicorn -w 4 -b 0.0.0.0:8000 main:app > /var/log/flask-app.log 2>&1 &
```

### Update Your Application
```bash
# Navigate to project
cd /workspace/flask-demo-be

# Activate venv
source venv/bin/activate

# Pull latest changes (if using git)
git pull

# Install new dependencies
pip install -r requirements.txt

# Restart service
systemctl restart flask-demo
```

### Stop Application
```bash
# If using systemd
systemctl stop flask-demo

# If using screen
screen -r flask-app
# Press Ctrl+C

# If using nohup
pkill gunicorn
```

---

## Performance Tuning

### Adjust Number of Workers
```bash
# Edit the systemd service
nano /etc/systemd/system/flask-demo.service

# Change the ExecStart line to:
ExecStart=/workspace/flask-demo-be/venv/bin/gunicorn -w 8 -b 0.0.0.0:8000 main:app

# Reload and restart
systemctl daemon-reload
systemctl restart flask-demo
```

**Worker Count Guidelines:**
- CPU-only pods: 2-4 workers
- Small GPU pods: 4-8 workers  
- Large GPU pods: 8-16 workers
- Formula: (2 × CPU cores) + 1

### Enable Access Logging
```bash
# Run with access logs
gunicorn -w 4 -b 0.0.0.0:8000 main:app \
  --access-logfile /var/log/flask-access.log \
  --error-logfile /var/log/flask-error.log

# View logs
tail -f /var/log/flask-access.log
tail -f /var/log/flask-error.log
```

---

## Troubleshooting

### Issue: Can't connect to the endpoint

**Solutions:**
1. Check if app is running: `systemctl status flask-demo`
2. Check if port 8000 is listening: `netstat -tlnp | grep 8000`
3. Verify RunPod exposed port 8000 in pod settings
4. Make sure you're using the correct RunPod proxy URL

### Issue: Application won't start

**Solutions:**
1. Check logs: `journalctl -u flask-demo -xe`
2. Test manually: 
   ```bash
   cd /workspace/flask-demo-be
   source venv/bin/activate
   python main.py
   ```
3. Check Python version: `python3.10 --version`
4. Reinstall dependencies: `pip install -r requirements.txt`

### Issue: 502 Bad Gateway

**Solutions:**
1. App must bind to `0.0.0.0:8000`, not `127.0.0.1:8000`
2. Check: `netstat -tlnp | grep 8000` should show `0.0.0.0:8000`
3. Verify main.py has: `app.run(host='0.0.0.0', port=8000)`

### Issue: Port already in use

**Solutions:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or kill all gunicorn processes
pkill gunicorn

# Then restart your app
systemctl start flask-demo
```

### Issue: Virtual environment issues

**Solutions:**
```bash
# Delete and recreate venv
cd /workspace/flask-demo-be
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Cost Optimization

1. **Use Spot Instances**: 70-80% cheaper (but can be interrupted)
2. **Use CPU Pods**: Much cheaper than GPU for basic Flask apps
3. **Stop Pod When Not Needed**: Stop the pod from RunPod dashboard
4. **Monitor Usage**: Check RunPod billing regularly
5. **Use Smaller Disk**: 20GB is usually enough for basic apps

**Estimated Costs (as of 2026):**
- CPU Pod (Spot): ~$0.05-0.10/hour
- CPU Pod (On-Demand): ~$0.15-0.30/hour
- GPU Pod: Varies by GPU type ($0.20-$2.00+/hour)

---

## Security Best Practices

1. **Change default passwords** if any
2. **Use environment variables** for secrets:
   ```bash
   # Create .env file
   cat > /workspace/flask-demo-be/.env << 'EOF'
   SECRET_KEY=your-secret-key
   DATABASE_URL=your-database-url
   EOF
   
   # Load in Python
   # pip install python-dotenv
   # In main.py: from dotenv import load_dotenv; load_dotenv()
   ```
3. **Don't commit secrets** to git
4. **Use HTTPS** (RunPod provides this automatically)
5. **Add API authentication** for production use

---

## Testing Your Deployment

### Local Testing (before deploying)
```bash
# On your local machine
cd /Users/prasunj/Documents/jiostar/personal/flask-demo-be

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install and run
pip install -r requirements.txt
python main.py

# Test
curl http://localhost:8000/health
```

### Remote Testing (on RunPod)
```bash
# Get your RunPod URL from dashboard
RUNPOD_URL="https://<pod-id>-8000.proxy.runpod.net"

# Test all endpoints
echo "Testing health endpoint..."
curl $RUNPOD_URL/health

echo -e "\nTesting generate-script endpoint..."
curl -X POST $RUNPOD_URL/generate-script

echo -e "\nTesting trigger-video-gen endpoint..."
curl -X POST $RUNPOD_URL/trigger-video-gen

echo -e "\nTesting get-job-status endpoint..."
curl "$RUNPOD_URL/get-job-status?job_id=test123"
```

---

## Useful Commands Reference

```bash
# System Management
systemctl start flask-demo        # Start service
systemctl stop flask-demo         # Stop service
systemctl restart flask-demo      # Restart service
systemctl status flask-demo       # Check status
systemctl enable flask-demo       # Auto-start on boot
journalctl -u flask-demo -f       # View logs

# Process Management
ps aux | grep gunicorn            # List gunicorn processes
pkill gunicorn                    # Kill all gunicorn
kill -HUP <pid>                   # Graceful reload
lsof -i :8000                     # Check port 8000

# Virtual Environment
source venv/bin/activate          # Activate venv
deactivate                        # Deactivate venv
pip list                          # List installed packages
pip freeze > requirements.txt     # Update requirements

# Screen Management
screen -S flask-app               # Create screen session
screen -ls                        # List sessions
screen -r flask-app               # Reattach to session
# Ctrl+A, D                       # Detach from screen
screen -X -S flask-app quit       # Kill screen session

# File Transfer (from local machine)
scp -P <port> -r /path/to/local/* root@<pod-id>.runpod.io:/workspace/flask-demo-be/
```

---

## Next Steps

1. **Add Database**: PostgreSQL, MongoDB, or SQLite
2. **Add Authentication**: JWT tokens or API keys
3. **Add Logging**: Proper structured logging
4. **Add Monitoring**: Health checks and metrics
5. **Add Rate Limiting**: Prevent abuse
6. **Add Tests**: Unit and integration tests
7. **Set up CI/CD**: GitHub Actions for auto-deployment
8. **Add API Documentation**: Swagger/OpenAPI

---

## Support Resources

- **RunPod Documentation**: https://docs.runpod.io/
- **RunPod Discord**: https://discord.gg/runpod
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Gunicorn Documentation**: https://docs.gunicorn.org/

---

## Summary Checklist

✅ Create RunPod pod with port 8000 exposed  
✅ Install Python 3.10 and dependencies  
✅ Upload/create application files  
✅ Create and activate virtual environment  
✅ Install Flask and gunicorn  
✅ Run application with gunicorn  
✅ Set up systemd service (optional but recommended)  
✅ Get RunPod proxy URL from dashboard  
✅ Test all endpoints  
✅ Monitor logs and performance  

**You're all set! 🚀**
