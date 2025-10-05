# 🚀 AI Content Studio - Deployment Guide

**Version:** 1.0.0  
**Last Updated:** October 4, 2025  
**Deployment Status:** Production Ready

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Environment Setup](#environment-setup)
4. [Local Docker Deployment](#local-docker-deployment)
5. [Cloud Deployment Options](#cloud-deployment-options)
6. [Troubleshooting](#troubleshooting)
7. [Post-Deployment Verification](#post-deployment-verification)

---

## 🎯 Prerequisites

### Required Software

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
  - Download from: https://www.docker.com/products/docker-desktop
- **Git** (for cloning repository)
- **API Keys** (see Environment Setup)

### Required API Keys

| Service | Purpose | Cost | Get Key From |
|---------|---------|------|--------------|
| OpenAI | GPT-4 text generation + DALL-E images | Pay-as-you-go | https://platform.openai.com/api-keys |
| Tavily | Web research & fact-checking | Free tier: 1000/month | https://app.tavily.com/ |

### System Requirements

**Minimum:**
- 2 CPU cores
- 4 GB RAM
- 5 GB disk space

**Recommended:**
- 4 CPU cores
- 8 GB RAM
- 10 GB disk space

---

## ⚡ Quick Start

Get AI Content Studio running in **5 minutes**:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/ai_content_studio.git
cd ai_content_studio

# 2. Create .env file from template
copy .env.example .env    # Windows
# OR
cp .env.example .env      # Mac/Linux

# 3. Edit .env and add your API keys
notepad .env              # Windows
# OR
nano .env                 # Mac/Linux

# 4. Build and start services
docker-compose up -d

# 5. Access the application
# Backend API: http://localhost:8000
# Frontend UI: http://localhost:8501
```

**That's it!** 🎉

---

## 🔐 Environment Setup

### Step 1: Create .env File

```bash
# Create .env from template
copy .env.example .env    # Windows
cp .env.example .env      # Mac/Linux
```

### Step 2: Configure API Keys

Edit `.env` and fill in your keys:

```env
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx

# Tavily API Key (REQUIRED)
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxx

# Keep these defaults for local deployment
DATABASE_URL=sqlite+aiosqlite:///./data/articles.db
DEBUG_MODE=False
BACKEND_URL=http://localhost:8000
```

### Step 3: Verify Configuration

```bash
# Check .env file exists and has both keys
cat .env | grep API_KEY    # Mac/Linux
type .env | findstr API_KEY    # Windows
```

---

## 🐳 Local Docker Deployment

### Build Docker Images

```bash
# Build both backend and frontend images
docker-compose build

# This will:
# ✓ Install Python dependencies
# ✓ Copy application code
# ✓ Create necessary directories
# ✓ Configure services

# Expected time: 2-5 minutes (depending on internet speed)
```

### Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# Check status
docker-compose ps

# Expected output:
# NAME                        STATUS      PORTS
# content_studio_backend      Up          0.0.0.0:8000->8000/tcp
# content_studio_frontend     Up          0.0.0.0:8501->8501/tcp
```

### View Logs

```bash
# View all logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View frontend logs only
docker-compose logs -f frontend

# Press Ctrl+C to exit log view
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v
```

---

## ☁️ Cloud Deployment Options

### Option 1: Render (Recommended for Beginners)

**Pros:** Easy setup, free tier available, automatic SSL  
**Cons:** Cold starts on free tier

**Steps:**
1. Push code to GitHub
2. Go to https://render.com and sign in
3. Click "New +" → "Web Service"
4. Connect GitHub repository
5. Configure:
   - **Name:** `ai-content-studio-backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
6. Add environment variables (OPENAI_API_KEY, TAVILY_API_KEY)
7. Deploy frontend separately with Streamlit Cloud

**Cost:** Free tier available, $7/month for always-on

### Option 2: Railway

**Pros:** Simple deployment, GitHub integration, generous free tier  
**Cons:** May require credit card

**Steps:**
1. Go to https://railway.app
2. Click "Deploy from GitHub"
3. Select repository
4. Add environment variables
5. Deploy automatically

**Cost:** $5/month credit on free tier, pay-as-you-go after

### Option 3: Streamlit Cloud (Frontend Only)

**Pros:** Free, optimized for Streamlit apps  
**Cons:** Backend must be hosted separately

**Steps:**
1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Click "New app"
4. Select repository and `frontend/app.py`
5. Add secrets (API keys)
6. Set `BACKEND_URL` to your backend URL
7. Deploy

**Cost:** Free for public repos

### Option 4: AWS/GCP/Azure (Advanced)

**Services needed:**
- **Backend:** ECS/Cloud Run/App Service
- **Database:** RDS/Cloud SQL/Azure Database (for production)
- **Storage:** S3/Cloud Storage/Blob Storage
- **Frontend:** Amplify/Cloud Run/Static Web Apps

**Cost:** Variable, typically $20-50/month for small-scale

---

## 🐛 Troubleshooting

### Error: "Address already in use"

**Cause:** Port 8000 or 8501 is already in use

**Solution:**
```bash
# Stop conflicting services
docker-compose down

# Or change ports in docker-compose.yml
ports:
  - "8080:8000"    # Use 8080 instead of 8000
```

### Error: "Missing API key"

**Cause:** `.env` file not found or keys not set

**Solution:**
```bash
# 1. Verify .env exists
ls -la .env    # Mac/Linux
dir .env       # Windows

# 2. Check .env contents
cat .env       # Mac/Linux
type .env      # Windows

# 3. Restart services
docker-compose down
docker-compose up -d
```

### Error: "No such file or directory: frontend/app.py"

**Cause:** Docker can't find the Streamlit app

**Solution:**
```bash
# Verify file exists
ls frontend/app.py

# Rebuild images
docker-compose build --no-cache
```

### Error: "Connection refused" when accessing backend

**Cause:** Backend not fully started or crashed

**Solution:**
```bash
# Check backend logs
docker-compose logs backend

# Look for errors in startup
docker-compose restart backend

# Check health endpoint
curl http://localhost:8000/health
```

### Frontend can't connect to backend

**Cause:** Incorrect BACKEND_URL or CORS issues

**Solution:**
```bash
# For Docker, use service name
# In .env:
BACKEND_URL=http://backend:8000

# For local (outside Docker), use localhost
BACKEND_URL=http://localhost:8000
```

### Database errors

**Cause:** Database file corrupted or permissions issue

**Solution:**
```bash
# Reset database
docker-compose down
rm -rf data/articles.db    # Mac/Linux
del data\articles.db       # Windows
docker-compose up -d
```

---

## ✅ Post-Deployment Verification

### Automated Health Check

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","message":"AI Content Studio API is running"}

# Check frontend
curl -I http://localhost:8501

# Expected: HTTP/1.1 200 OK
```

### Manual Testing Checklist

#### Backend Tests:

- [ ] `/health` endpoint returns 200 OK
- [ ] API documentation accessible at http://localhost:8000/docs
- [ ] Can create new article via API
- [ ] WebSocket connection works

#### Frontend Tests:

- [ ] Page loads without errors
- [ ] Can input article topic
- [ ] "Generate Article" button works
- [ ] Progress updates display in real-time
- [ ] Generated content appears in tabs
- [ ] Export to Markdown/HTML/PDF works
- [ ] History panel shows created articles

#### Integration Tests:

- [ ] Complete article generation end-to-end
- [ ] All 6 agents execute successfully (Research → Outline → Writer → Editor → SEO → Image)
- [ ] Image generation works (DALL-E)
- [ ] SEO metadata generated
- [ ] Article saved to database
- [ ] Can view previously generated articles

### Performance Benchmarks

**Expected Performance:**
- Backend startup: < 5 seconds
- Frontend startup: < 10 seconds
- API response time: < 2 seconds
- Full article generation: 2-5 minutes (depending on length)
- WebSocket latency: < 500ms

---

## 📊 Monitoring & Logs

### View Application Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Logs since timestamp
docker-compose logs --since 2025-10-04T10:00:00
```

### Resource Usage

```bash
# Check container resource usage
docker stats

# Shows:
# - CPU usage
# - Memory usage
# - Network I/O
# - Disk I/O
```

---

## 🔒 Security Considerations

### Production Checklist:

- [ ] Change `DEBUG_MODE=False` in production
- [ ] Use strong, unique API keys
- [ ] Never commit `.env` to version control
- [ ] Configure CORS to allow only your frontend domain
- [ ] Use HTTPS for all public endpoints
- [ ] Regularly update dependencies
- [ ] Set up monitoring and alerting
- [ ] Implement rate limiting on API endpoints
- [ ] Use secrets management (e.g., AWS Secrets Manager)
- [ ] Regular security audits

---

## 🔄 Updating the Application

### Pull Latest Changes

```bash
# Stop services
docker-compose down

# Pull updates from Git
git pull origin main

# Rebuild images
docker-compose build

# Start with new images
docker-compose up -d
```

### Backup Before Update

```bash
# Backup database
cp data/articles.db data/articles_backup_$(date +%Y%m%d).db    # Mac/Linux
copy data\articles.db data\articles_backup.db                   # Windows

# Backup .env
cp .env .env.backup
```

---

## 📞 Support & Resources

### Documentation:
- [README.md](README.md) - Project overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Development setup
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing instructions
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - User guide

### API Documentation:
- Interactive API docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

### Getting Help:
- GitHub Issues: Create an issue for bugs or feature requests
- Discussions: Ask questions in GitHub Discussions
- Email: your-email@example.com

---

## 🎉 Success!

Your AI Content Studio should now be fully deployed and operational.

**Access your application:**
- 🔥 Backend API: http://localhost:8000
- 🎨 Frontend UI: http://localhost:8501
- 📚 API Docs: http://localhost:8000/docs

**Start creating amazing content!** ✨

---

*Last updated: October 4, 2025*

