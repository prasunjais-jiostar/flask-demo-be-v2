# Flask Demo Backend - Setup Summary

## ✅ What Has Been Created

### Flask Application
- **main.py**: Flask server with 4 endpoints:
  - `POST /generate-script` - Returns hardcoded script generation response
  - `POST /trigger-video-gen` - Returns hardcoded video generation response
  - `GET /get-job-status` - Returns hardcoded job status response
  - `GET /health` - Health check endpoint

### Dependencies
- **requirements.txt**: Contains Flask 3.0.0, gunicorn 21.2.0, Werkzeug 3.0.1

### Setup Scripts
- **setup.sh**: Local development setup (creates venv, installs dependencies)
- **runpod-deploy.sh**: Automated RunPod deployment script

### Documentation
- **README.md**: Main project documentation with all deployment options
- **QUICKSTART.md**: Quick reference for fast RunPod deployment
- **RUNPOD_DEPLOYMENT_PYTHON.md**: Complete Python 3.10 deployment guide (no Docker)
- **RUNPOD_DEPLOYMENT.md**: Docker-based deployment options

### Docker Files (Optional)
- **Dockerfile**: For containerized deployment
- **docker-compose.yml**: For Docker Compose deployment
- **.dockerignore**: Docker ignore patterns

---

## 🚀 How to Deploy on RunPod (3 Options)

### Option 1: Automated Script (Easiest) ⭐

1. Create RunPod Pod (CPU or GPU) with port 8000 exposed
2. Open web terminal
3. Run:
   ```bash
   wget https://raw.githubusercontent.com/your-repo/flask-demo-be/main/runpod-deploy.sh
   chmod +x runpod-deploy.sh
   ./runpod-deploy.sh
   ```
4. Done! Access at: `https://<pod-id>-8000.proxy.runpod.net`

### Option 2: Manual Copy-Paste (5 minutes)

See **[QUICKSTART.md](QUICKSTART.md)** for step-by-step commands to copy-paste.

### Option 3: File Upload

1. Create RunPod Pod with port 8000 exposed
2. From your local machine:
   ```bash
   scp -P <port> -r /Users/prasunj/Documents/jiostar/personal/flask-demo-be/* root@<pod-id>.runpod.io:/workspace/flask-demo-be/
   ```
3. SSH into pod and run:
   ```bash
   cd /workspace/flask-demo-be
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   screen -dmS flask-app bash -c "gunicorn -w 4 -b 0.0.0.0:8000 main:app"
   ```

---

## 💻 Local Development

### Setup (One-time)
```bash
cd /Users/prasunj/Documents/jiostar/personal/flask-demo-be
./setup.sh
```

### Run Server
```bash
source venv/bin/activate
python main.py
```

### Test Locally
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/generate-script
curl -X POST http://localhost:8000/trigger-video-gen
curl "http://localhost:8000/get-job-status?job_id=test123"
```

---

## 📋 Next Steps

1. **Deploy to RunPod**: Follow one of the 3 options above
2. **Test Your Endpoints**: Use curl or Postman
3. **Monitor**: Check logs with `journalctl -u flask-demo -f` (if using systemd)
4. **Customize**: Update endpoints in main.py for your actual use case
5. **Add Features**:
   - Database integration
   - Authentication (JWT/API keys)
   - Rate limiting
   - Logging
   - Error handling

---

## 📚 Documentation Index

| File | Purpose |
|------|---------|
| [README.md](README.md) | Main documentation, overview, local setup |
| [QUICKSTART.md](QUICKSTART.md) | Fast deployment commands for RunPod |
| [RUNPOD_DEPLOYMENT_PYTHON.md](RUNPOD_DEPLOYMENT_PYTHON.md) | Complete Python deployment guide ⭐ |
| [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md) | Docker deployment options |

---

## 🔍 Key Files

| File | Description |
|------|-------------|
| `main.py` | Flask application (modify this for your logic) |
| `requirements.txt` | Python dependencies |
| `setup.sh` | Local setup script |
| `runpod-deploy.sh` | RunPod auto-deployment script |

---

## ⚡ Quick Commands Reference

```bash
# Local Development
./setup.sh                          # Initial setup
source venv/bin/activate           # Activate venv
python main.py                     # Run dev server
gunicorn -w 4 -b 0.0.0.0:8000 main:app  # Run with gunicorn

# RunPod Management (after deployment)
systemctl status flask-demo        # Check status
systemctl restart flask-demo       # Restart app
journalctl -u flask-demo -f        # View logs
ps aux | grep gunicorn            # Check processes
lsof -i :8000                     # Check port

# Testing
curl http://localhost:8000/health                    # Local
curl https://<pod-id>-8000.proxy.runpod.net/health  # RunPod
```

---

## 💰 RunPod Cost Estimates

- **CPU Pod (Spot)**: ~$0.05-0.10/hour
- **CPU Pod (On-Demand)**: ~$0.15-0.30/hour
- **Small GPU Pod**: ~$0.20-0.50/hour
- **Large GPU Pod**: $1.00-$5.00+/hour

**Tip**: Use CPU pods for basic Flask apps, GPU only if needed for ML inference.

---

## 🆘 Troubleshooting

### Can't connect to endpoint
- Check port 8000 is exposed in RunPod settings
- Verify app is running: `ps aux | grep gunicorn`
- Check binding: `netstat -tlnp | grep 8000` (should show `0.0.0.0:8000`)

### App won't start
- Check logs: `journalctl -u flask-demo -xe`
- Test manually: `python main.py`
- Verify Python: `python3.10 --version`

### Need to update code
```bash
cd /workspace/flask-demo-be
# Edit main.py or upload new version
systemctl restart flask-demo
```

---

## ✨ You're All Set!

Your Flask application is ready to deploy on RunPod with Python 3.10. Choose your preferred deployment method and follow the respective guide.

**Questions?** Check the detailed documentation in the files above.
