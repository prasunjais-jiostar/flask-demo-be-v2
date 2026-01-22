# Flask Demo Backend

A simple Flask server with 3 endpoints for script generation, video generation, and job status tracking.

## Endpoints

### 1. Generate Script
- **URL**: `/generate-script`
- **Method**: `POST`
- **Response**: Hardcoded success response with script details

### 2. Trigger Video Generation
- **URL**: `/trigger-video-gen`
- **Method**: `POST`
- **Response**: Hardcoded success response with job and video details

### 3. Get Job Status
- **URL**: `/get-job-status`
- **Method**: `GET`
- **Query Parameters**: `job_id` (optional)
- **Response**: Hardcoded success response with job status

### 4. Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Response**: Server health status

## Local Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Server
```bash
# Development mode
python main.py

# Production mode with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### 5. Test the Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Generate script
curl -X POST http://localhost:8000/generate-script

# Trigger video generation
curl -X POST http://localhost:8000/trigger-video-gen

# Get job status
curl http://localhost:8000/get-job-status?job_id=job_123
```

## Deploying to RunPod

### Prerequisites
- RunPod account (sign up at https://www.runpod.io/)

### Quick Deployment (Python 3.10 - No Docker Required) ⭐ RECOMMENDED

**See detailed guide**: [RUNPOD_DEPLOYMENT_PYTHON.md](RUNPOD_DEPLOYMENT_PYTHON.md)

**Quick Start:**
1. Create a RunPod Pod (CPU or GPU)
2. Expose port 8000
3. Connect via web terminal or SSH
4. Run the automated deployment script:
   ```bash
   curl -o- https://raw.githubusercontent.com/your-repo/flask-demo-be/main/runpod-deploy.sh | bash
   ```
   Or manually:
   ```bash
   wget https://raw.githubusercontent.com/your-repo/flask-demo-be/main/runpod-deploy.sh
   chmod +x runpod-deploy.sh
   ./runpod-deploy.sh
   ```
5. Access your app at: `https://<pod-id>-8000.proxy.runpod.net`

### Option 1: Deploy Using Docker (Alternative)

**See detailed guide**: [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md)

### Option 2: Deploy Using RunPod Serverless (Recommended for APIs)

1. **Create a Dockerfile** (already included in this project)

2. **Build and Push Docker Image**:
   ```bash
   # Login to Docker Hub (or your preferred registry)
   docker login
   
   # Build the image
   docker build -t yourusername/flask-demo-be:latest .
   
   # Push to registry
   docker push yourusername/flask-demo-be:latest
   ```

3. **Deploy on RunPod**:
   - Go to RunPod Dashboard
   - Click on "Serverless" → "New Endpoint"
   - Configure your endpoint:
     - **Container Image**: `yourusername/flask-demo-be:latest`
     - **Container Disk**: 5 GB minimum
     - **Exposed HTTP Port**: 8000
     - **Advanced Settings**: Add environment variables if needed
   - Click "Deploy"
   - RunPod will provide you with an endpoint URL

For detailed Docker and Serverless deployment instructions, see [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md)

---

## Detailed Deployment Guides

- **[RUNPOD_DEPLOYMENT_PYTHON.md](RUNPOD_DEPLOYMENT_PYTHON.md)** - ⭐ **RECOMMENDED** - Direct Python 3.10 deployment (no Docker required)
- **[RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md)** - Docker-based deployment options (Serverless, Pods, Docker Compose)

### Quick Manual Steps (Python 3.10)

If you prefer to deploy manually instead of using the automated script:

1. Create RunPod Pod with port 8000 exposed
2. Connect via SSH or web terminal
3. Run these commands:
   ```bash
   # Update and install Python 3.10
   apt-get update && apt-get install -y python3.10 python3.10-venv python3-pip screen
   
   # Create project and files
   mkdir -p /workspace/flask-demo-be && cd /workspace/flask-demo-be
   # Upload your files (main.py, requirements.txt) via SCP or create them
   
   # Setup virtual environment
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Run with screen (persistent)
   screen -S flask-app
   gunicorn -w 4 -b 0.0.0.0:8000 main:app
   # Press Ctrl+A then D to detach
   ```

4. Access at: `https://<pod-id>-8000.proxy.runpod.net/health`

For complete detailed instructions, troubleshooting, and best practices, see the deployment guides above.

## Project Structure
```
flask-demo-be/
├── main.py                        # Flask application with 3 endpoints
├── requirements.txt               # Python dependencies
├── setup.sh                       # Local setup script (macOS/Linux)
├── runpod-deploy.sh              # RunPod automated deployment script
├── Dockerfile                     # Docker configuration (optional)
├── docker-compose.yml            # Docker Compose configuration (optional)
├── .dockerignore                 # Docker ignore file
├── .gitignore                    # Git ignore file
├── README.md                     # Main documentation (this file)
├── QUICKSTART.md                 # Quick start guide for RunPod
├── RUNPOD_DEPLOYMENT_PYTHON.md  # Detailed Python deployment guide ⭐
└── RUNPOD_DEPLOYMENT.md         # Docker deployment guide
```
