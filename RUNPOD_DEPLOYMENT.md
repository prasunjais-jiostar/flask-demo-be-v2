# RunPod Deployment Guide

This guide provides detailed steps to deploy your Flask application on RunPod.

## Prerequisites

1. **RunPod Account**: Sign up at https://www.runpod.io/
2. **Docker Hub Account** (for Option 1): Sign up at https://hub.docker.com/
3. **Your Flask Application**: Already set up in this repository

---

## Option 1: Deploy Using RunPod Serverless (Recommended for APIs)

This is the best option for REST APIs as it auto-scales and you only pay for usage.

### Step 1: Build Docker Image

```bash
# Navigate to project directory
cd /Users/prasunj/Documents/jiostar/personal/flask-demo-be

# Build the Docker image
docker build -t your-dockerhub-username/flask-demo-be:latest .

# Test locally (optional)
docker run -p 8000:8000 your-dockerhub-username/flask-demo-be:latest
# Test: curl http://localhost:8000/health
```

### Step 2: Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push the image
docker push your-dockerhub-username/flask-demo-be:latest
```

### Step 3: Deploy on RunPod Serverless

1. Go to RunPod Dashboard: https://www.runpod.io/console/serverless
2. Click **"New Endpoint"**
3. Fill in the details:
   - **Endpoint Name**: `flask-demo-be`
   - **Container Image**: `your-dockerhub-username/flask-demo-be:latest`
   - **Container Disk**: 5 GB (minimum)
   - **GPU Type**: Select based on needs (can use CPU for basic Flask app)
   - **Max Workers**: 3-5 (adjust based on expected traffic)
   - **Idle Timeout**: 5 seconds
   - **Execution Timeout**: 120 seconds
   - **Advanced Settings**:
     - **Container Start Command**: Leave empty (uses Dockerfile CMD)
     - **HTTP Port**: 8000
     - **Environment Variables**: Add if needed

4. Click **"Deploy"**
5. Wait for deployment (usually 1-2 minutes)
6. Copy your endpoint URL (format: `https://api.runpod.ai/v2/{endpoint_id}/`)

### Step 4: Test Your Serverless Endpoint

RunPod Serverless requires a specific request format:

```bash
# Save your endpoint ID
ENDPOINT_ID="your-endpoint-id"
API_KEY="your-runpod-api-key"

# Health check
curl -X POST https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "input": {
      "method": "GET",
      "endpoint": "/health"
    }
  }'

# Generate script
curl -X POST https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{
    "input": {
      "method": "POST",
      "endpoint": "/generate-script"
    }
  }'
```

---

## Option 2: Deploy Using RunPod Pods (Always-On Server)

This is better if you need a persistent server that's always running.

### Step 1: Create a Pod

1. Go to RunPod Dashboard: https://www.runpod.io/console/pods
2. Click **"Deploy"** or **"+ GPU Pod"** or **"+ CPU Pod"**
3. Select a template:
   - For basic Flask: **"RunPod Pytorch"** or **"Ubuntu"** template
   - Or select any GPU if you plan to add ML features later
4. Configure the pod:
   - **GPU Type**: Select GPU or CPU-only
   - **Container Disk**: 20 GB (recommended)
   - **Volume Disk**: 10 GB (optional, for persistent data)
   - **Expose HTTP Ports**: `8000`
   - **Expose TCP Ports**: `8000,22` (22 for SSH)
   - **Docker Image** (optional): Can use default or specify custom

5. Click **"Deploy On-Demand"** or **"Deploy Spot"**
   - **On-Demand**: More expensive but guaranteed availability
   - **Spot**: Cheaper but can be interrupted

### Step 2: Access Your Pod

1. Once deployed, go to **"My Pods"**
2. Click on your pod
3. Note the **Pod ID** and **Connection Info**

### Step 3: Connect via SSH

```bash
# Get SSH command from RunPod dashboard (under "Connection" tab)
# It will look like this:
ssh root@<pod-id>.runpod.io -p <port> -i ~/.ssh/id_ed25519

# Or use the web terminal in RunPod dashboard
```

### Step 4: Setup Application on Pod

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install required packages
apt-get install -y python3 python3-pip python3-venv git curl

# Create project directory
mkdir -p /workspace/flask-demo-be
cd /workspace/flask-demo-be

# Option A: Clone from Git (if you have a repo)
git clone https://github.com/your-username/flask-demo-be.git .

# Option B: Manual upload (from your local machine)
# Use SCP to upload files:
# scp -P <port> -i ~/.ssh/id_ed25519 -r /Users/prasunj/Documents/jiostar/personal/flask-demo-be/* root@<pod-id>.runpod.io:/workspace/flask-demo-be/

# Option C: Create files manually
# Copy the content of main.py, requirements.txt, etc.
```

### Step 5: Install Dependencies

```bash
# Navigate to project directory
cd /workspace/flask-demo-be

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Run the Application

**Method A: Run with gunicorn (recommended)**

```bash
# Run in foreground (for testing)
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# Run as background daemon
gunicorn -w 4 -b 0.0.0.0:8000 main:app --daemon \
  --access-logfile /var/log/gunicorn-access.log \
  --error-logfile /var/log/gunicorn-error.log
```

**Method B: Run with screen (persistent terminal)**

```bash
# Install screen if not available
apt-get install -y screen

# Start a new screen session
screen -S flask-app

# Run the application
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# Detach from screen: Press Ctrl+A, then D
# Reattach later: screen -r flask-app
```

**Method C: Run with systemd (best for production)**

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
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Start the service
systemctl start flask-demo

# Enable on boot
systemctl enable flask-demo

# Check status
systemctl status flask-demo

# View logs
journalctl -u flask-demo -f
```

### Step 7: Access Your Application

1. Go to RunPod dashboard → Your Pod → "Connection" tab
2. Find the **HTTP Service** section
3. You'll see a URL like: `https://<pod-id>-8000.proxy.runpod.net`
4. Test the endpoints:

```bash
# Replace with your actual RunPod URL
RUNPOD_URL="https://<pod-id>-8000.proxy.runpod.net"

# Health check
curl ${RUNPOD_URL}/health

# Generate script
curl -X POST ${RUNPOD_URL}/generate-script

# Trigger video generation
curl -X POST ${RUNPOD_URL}/trigger-video-gen

# Get job status
curl "${RUNPOD_URL}/get-job-status?job_id=test123"
```

---

## Option 3: Deploy Using Docker Compose on Pod

### Step 1-3: Same as Option 2 (Create pod and SSH)

### Step 4: Install Docker Compose

```bash
# Install docker-compose
apt-get update
apt-get install -y docker-compose

# Or install latest version
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 5: Upload Files and Run

```bash
# Navigate to project directory
cd /workspace/flask-demo-be

# Upload all files (including docker-compose.yml and Dockerfile)
# Use SCP or git clone as shown in Option 2

# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Managing Your Deployment

### Monitoring

```bash
# Check if service is running
ps aux | grep gunicorn

# Check port
netstat -tlnp | grep 8000
# or
lsof -i :8000

# Check logs
tail -f /var/log/gunicorn-access.log
tail -f /var/log/gunicorn-error.log

# System resources
htop  # or top
```

### Updating Your Application

```bash
# SSH into your pod
ssh root@<pod-id>.runpod.io -p <port>

# Navigate to project
cd /workspace/flask-demo-be

# Pull latest changes (if using git)
git pull

# Or upload new files via SCP

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart the service
# If using systemd:
systemctl restart flask-demo

# If using gunicorn daemon:
pkill gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app --daemon

# If using screen:
screen -r flask-app
# Press Ctrl+C to stop
# Then restart: gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Scaling

```bash
# Increase workers for better performance
gunicorn -w 8 -b 0.0.0.0:8000 main:app

# Monitor worker health
watch -n 1 'ps aux | grep gunicorn'
```

---

## Cost Optimization Tips

1. **Use Spot Instances**: 70-80% cheaper than on-demand
2. **Use CPU Pods**: If you don't need GPU, use CPU-only pods
3. **Auto-shutdown**: Configure idle timeout in RunPod settings
4. **Serverless for APIs**: Pay only for actual usage
5. **Monitor Usage**: Check RunPod billing dashboard regularly

---

## Troubleshooting

### Issue: Can't connect to endpoint

**Solution:**
- Verify port 8000 is exposed in RunPod pod settings
- Check if application is running: `ps aux | grep gunicorn`
- Check logs for errors: `tail -f /var/log/gunicorn-error.log`

### Issue: Application crashes

**Solution:**
- Check logs: `systemctl status flask-demo` or `journalctl -u flask-demo`
- Verify dependencies: `pip list`
- Test locally: `python main.py`

### Issue: 502 Bad Gateway

**Solution:**
- Application might not be binding to 0.0.0.0
- Verify with: `netstat -tlnp | grep 8000`
- Should show: `0.0.0.0:8000` not `127.0.0.1:8000`

### Issue: Out of memory

**Solution:**
- Reduce number of workers
- Upgrade to pod with more RAM
- Check memory usage: `free -h`

---

## Security Best Practices

1. **Use Environment Variables**: Store sensitive data in `.env` files
2. **Update Regularly**: Keep dependencies updated
3. **Firewall**: RunPod handles this, but verify exposed ports
4. **HTTPS**: RunPod provides HTTPS through their proxy
5. **Authentication**: Add API key authentication for production
6. **Rate Limiting**: Implement rate limiting for production APIs

---

## Next Steps

1. **Add Authentication**: Implement API key or JWT authentication
2. **Add Database**: Connect to PostgreSQL or MongoDB
3. **Add Logging**: Implement proper logging with log rotation
4. **Add Monitoring**: Use tools like Prometheus + Grafana
5. **Add CI/CD**: Automate deployments with GitHub Actions
6. **Add Tests**: Write unit and integration tests
7. **Documentation**: Generate API docs with Swagger/OpenAPI

---

## Useful Commands Reference

```bash
# Virtual Environment
python3 -m venv venv
source venv/bin/activate
deactivate

# Dependencies
pip install -r requirements.txt
pip freeze > requirements.txt

# Run Application
python main.py
gunicorn -w 4 -b 0.0.0.0:8000 main:app
gunicorn -w 4 -b 0.0.0.0:8000 main:app --daemon

# Process Management
ps aux | grep gunicorn
pkill gunicorn
kill -HUP <pid>  # Graceful reload

# Systemd
systemctl start flask-demo
systemctl stop flask-demo
systemctl restart flask-demo
systemctl status flask-demo
journalctl -u flask-demo -f

# Docker
docker build -t flask-demo-be .
docker run -p 8000:8000 flask-demo-be
docker-compose up -d
docker-compose logs -f
docker-compose down

# Testing
curl http://localhost:8000/health
curl -X POST http://localhost:8000/generate-script
curl -X POST http://localhost:8000/trigger-video-gen
curl "http://localhost:8000/get-job-status?job_id=test123"
```

---

## Support

- RunPod Documentation: https://docs.runpod.io/
- RunPod Discord: https://discord.gg/runpod
- Flask Documentation: https://flask.palletsprojects.com/
- Gunicorn Documentation: https://docs.gunicorn.org/

---

**Good luck with your deployment! 🚀**
