# 🆓 AI Content Studio - 100% Free Deployment Guide

**Deploy your AI Content Studio for FREE** using Render (backend) + Streamlit Cloud (frontend)

**Total Cost:** $0/month  
**Setup Time:** 15-20 minutes  
**No credit card required** (with limitations)

---

## 🎯 Overview

This guide shows you how to deploy AI Content Studio using **completely free** platforms:

| Component | Platform | Free Tier | Limitations |
|-----------|----------|-----------|-------------|
| **Backend API** | Render | 750 hours/month | Spins down after 15 min inactivity |
| **Frontend UI** | Streamlit Cloud | Unlimited | Public repos only |
| **Database** | SQLite (bundled) | Unlimited | Stored in container |
| **Total Cost** | - | **$0/month** | - |

---

## 📋 Prerequisites

- **GitHub Account** (free) - https://github.com/signup
- **Render Account** (free) - https://render.com/register
- **Streamlit Cloud Account** (free) - https://streamlit.io/cloud
- **Your API Keys**:
  - OpenAI API Key (from https://platform.openai.com/api-keys)
  - Tavily API Key (from https://app.tavily.com/)

---

## 🚀 Step-by-Step Deployment

### Phase 1: Prepare GitHub Repository (5 minutes)

#### 1.1 Create GitHub Repository

```bash
# Navigate to your project
cd c:\Users\regmi\OneDrive\Desktop\ai_agents

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - AI Content Studio"

# Create repo on GitHub (via web interface)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/ai-content-studio.git
git branch -M main
git push -u origin main
```

#### 1.2 Verify Repository Structure

Make sure these files are in your repo:
- ✅ `backend/` (all backend code)
- ✅ `frontend/` (all frontend code)
- ✅ `requirements.txt` (root dependencies)
- ✅ `frontend/requirements.txt` (frontend dependencies)
- ✅ `.env.example` (template, no secrets)
- ❌ `.env` (should be in .gitignore, NOT pushed)

---

### Phase 2: Deploy Backend to Render (7 minutes)

#### 2.1 Create Render Account

1. Go to https://render.com/register
2. Sign up with GitHub (recommended)
3. Authorize Render to access your repositories

#### 2.2 Create Web Service

1. **Dashboard** → Click **"New +"** → Select **"Web Service"**

2. **Connect Repository:**
   - Select your `ai-content-studio` repository
   - Click **"Connect"**

3. **Configure Service:**
   ```
   Name: ai-content-studio-backend
   Region: Choose closest to you (e.g., Oregon, Frankfurt)
   Branch: main
   Root Directory: (leave blank)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Select Free Plan:**
   - Instance Type: **Free**
   - Click **"Advanced"** to expand

5. **Add Environment Variables:**
   Click **"Add Environment Variable"** for each:

   ```
   OPENAI_API_KEY = sk-your-actual-key-here
   TAVILY_API_KEY = tvly-your-actual-key-here
   DATABASE_URL = sqlite+aiosqlite:///./data/articles.db
   DEBUG_MODE = False
   ```

6. **Create Web Service:**
   - Click **"Create Web Service"**
   - Wait 5-10 minutes for deployment

#### 2.3 Verify Backend Deployment

Once deployed, you'll get a URL like: `https://ai-content-studio-backend.onrender.com`

**Test it:**
```bash
# Check health endpoint
curl https://YOUR-APP-NAME.onrender.com/health

# Expected response:
# {"status":"ok","message":"AI Content Studio API is running"}
```

**Important:** Copy this URL! You'll need it for frontend configuration.

---

### Phase 3: Deploy Frontend to Streamlit Cloud (5 minutes)

#### 3.1 Create Streamlit Cloud Account

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Authorize Streamlit Cloud

#### 3.2 Deploy App

1. Click **"New app"** (big blue button)

2. **Configure App:**
   ```
   Repository: YOUR_USERNAME/ai-content-studio
   Branch: main
   Main file path: frontend/app.py
   ```

3. **Advanced Settings** → Click **"Advanced settings"**

4. **Add Secrets:**
   Click on the "Secrets" section and add:

   ```toml
   # Streamlit secrets format (TOML)
   OPENAI_API_KEY = "sk-your-actual-key-here"
   TAVILY_API_KEY = "tvly-your-actual-key-here"
   BACKEND_URL = "https://YOUR-RENDER-APP.onrender.com"
   ```

   **⚠️ IMPORTANT:** Replace `YOUR-RENDER-APP` with your actual Render backend URL!

5. **Deploy:**
   - Click **"Deploy!"**
   - Wait 2-3 minutes

#### 3.3 Access Your App

Your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

**Test it:**
1. Open the URL in your browser
2. You should see the AI Content Studio interface
3. Try generating a test article!

---

## ✅ Post-Deployment Checklist

### Backend Verification:

- [ ] Backend URL accessible: `https://YOUR-APP.onrender.com/health`
- [ ] Returns `{"status":"ok",...}`
- [ ] API docs accessible: `https://YOUR-APP.onrender.com/docs`
- [ ] No errors in Render logs

### Frontend Verification:

- [ ] Frontend loads without errors
- [ ] Can input article topic
- [ ] "Generate Article" button visible
- [ ] No connection errors to backend

### Integration Test:

- [ ] Generate a test article (use a simple topic like "Benefits of Exercise")
- [ ] Progress updates appear in real-time
- [ ] All 6 agents execute successfully
- [ ] Final article displays with sections
- [ ] Export buttons work

---

## 🔧 Troubleshooting

### Backend Issues

#### ❌ "Web service failed to bind to $PORT"

**Solution:** Make sure Start Command uses `$PORT`:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### ❌ "Application failed to start"

1. Check Render logs (Logs tab)
2. Look for missing dependencies
3. Verify environment variables are set
4. Check Build Command completed successfully

#### ❌ Backend spins down (Free tier limitation)

**Expected behavior:** Free tier spins down after 15 minutes of inactivity.

**Solutions:**
- First request will wake it up (takes 30-60 seconds)
- Upgrade to paid plan ($7/month) for always-on
- Use a ping service (e.g., UptimeRobot) to keep it alive

---

### Frontend Issues

#### ❌ "Connection Error" to backend

**Solution:** Check `BACKEND_URL` in Streamlit secrets:
1. Go to Streamlit Cloud dashboard
2. Click your app → **"Settings"** → **"Secrets"**
3. Verify `BACKEND_URL` matches your Render URL exactly
4. Must include `https://` and no trailing slash

#### ❌ "Invalid API Key" errors

**Solution:** 
1. Verify API keys in Streamlit secrets (no quotes in TOML format)
2. Make sure keys are also set in Render backend environment variables
3. Test keys locally first

#### ❌ Article generation times out

**Possible causes:**
- Backend spinning up from sleep (wait 60 seconds, try again)
- OpenAI API rate limits
- Network issues

**Solution:** 
- Wait for backend to fully start
- Check OpenAI account has credits
- Try a shorter article (reduce min_words to 500)

---

## 💰 Cost Comparison

| Deployment Option | Free Tier | Paid Tier | Best For |
|-------------------|-----------|-----------|----------|
| **Render Free** | 750 hrs/mo<br>Spins down | $7/mo<br>Always-on | Testing, portfolios |
| **Railway** | $5 credit<br>~100 hrs | $5/mo + usage | Simple deployments |
| **Streamlit Cloud** | Unlimited<br>Public repos | $20/mo<br>Private repos | Sharing demos |
| **Heroku** | No free tier | $7/mo + addons | Traditional apps |
| **AWS/GCP/Azure** | Free trial only | $20-50/mo+ | Production apps |

**Recommended:** Start with Render Free + Streamlit Cloud Free = **$0/month**

---

## 🔒 Important Notes

### Free Tier Limitations:

1. **Backend Sleep:** Render free tier spins down after 15 minutes of inactivity
   - First request wakes it up (30-60 seconds)
   - Not suitable for high-traffic production use

2. **Public Repository:** Streamlit Cloud free tier requires public GitHub repo
   - Your code will be visible to everyone
   - Don't commit `.env` or secrets

3. **Database Persistence:** SQLite in container may reset on deployment updates
   - For production, use PostgreSQL (Render has free tier too)

4. **Monthly Hours:** Render free tier = 750 hours/month
   - Enough for always-on if you're the only user
   - Exceeding limit causes service to stop

### Security Best Practices:

- ✅ Never commit `.env` file (use `.gitignore`)
- ✅ Use environment variables for all secrets
- ✅ Rotate API keys periodically
- ✅ Set `DEBUG_MODE=False` in production
- ✅ Monitor usage to avoid unexpected charges

---

## 🚀 Upgrade Paths

### When to Upgrade:

**Upgrade Backend ($7/mo)** when:
- You need always-on availability
- Users complain about slow first load
- You exceed 750 hours/month

**Upgrade Frontend ($20/mo)** when:
- You want a private repository
- You need custom domains
- You need more resources

**Upgrade Database (Free PostgreSQL)** when:
- You need data persistence across deployments
- You have multiple instances
- You need better performance

---

## 📊 Free PostgreSQL Option (Advanced)

Render also offers **free PostgreSQL** (90 days, then deletes):

1. In Render Dashboard → **"New +"** → **"PostgreSQL"**
2. Name: `ai-content-studio-db`
3. Region: Same as web service
4. Plan: **Free**
5. Copy the "Internal Database URL"
6. Update backend environment variable:
   ```
   DATABASE_URL = postgresql+asyncpg://[the-url-from-render]
   ```
7. Redeploy backend

**Note:** Free PostgreSQL expires after 90 days. Good for testing!

---

## 🎓 Learning Resources

### Render Documentation:
- Getting Started: https://render.com/docs
- Environment Variables: https://render.com/docs/environment-variables
- Free Plan Details: https://render.com/docs/free

### Streamlit Cloud Documentation:
- Deploy Apps: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- Secrets Management: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

---

## 🆘 Getting Help

### If deployment fails:

1. **Check logs first:**
   - Render: Logs tab in service dashboard
   - Streamlit: Click "Manage app" → View logs

2. **Verify all files pushed to GitHub:**
   ```bash
   git status
   git push origin main
   ```

3. **Test locally first:**
   ```bash
   # Backend
   uvicorn backend.main:app --reload
   
   # Frontend (separate terminal)
   streamlit run frontend/app.py
   ```

4. **Common issues:**
   - Missing files in GitHub repo
   - Wrong file paths in configuration
   - API keys not set or invalid
   - Port binding issues

### Support Resources:

- **This Project:** GitHub Issues (your repo)
- **Render:** https://render.com/docs/support
- **Streamlit:** https://discuss.streamlit.io/

---

## ✅ Success Checklist

You know deployment succeeded when:

- ✅ Backend health check returns 200 OK
- ✅ Frontend loads without errors
- ✅ Can create and generate articles
- ✅ Real-time progress updates work
- ✅ All 6 agents execute successfully
- ✅ Generated articles display correctly
- ✅ Images generate (DALL-E)
- ✅ Export functions work

---

## 🎉 You're Live!

**Congratulations!** Your AI Content Studio is now deployed and accessible worldwide for **$0/month**.

**Share your app:**
- Frontend URL: `https://your-app.streamlit.app`
- Add it to your portfolio
- Share with friends and colleagues
- Use it for your content creation needs!

**Next steps:**
- Generate your first article
- Experiment with different topics
- Share feedback and improvements
- Consider upgrading if usage grows

---

## 💡 Pro Tips

1. **Pin specific Python version** in Render:
   - Add `python_version = "3.11.9"` to `runtime.txt`

2. **Speed up wake-up time:**
   - Use a smaller Docker image
   - Minimize dependencies

3. **Monitor usage:**
   - Check Render dashboard weekly
   - Watch for 750-hour limit

4. **Test before sharing:**
   - Generate multiple articles
   - Test all features
   - Check error handling

5. **Keep it updated:**
   - Pull updates from main branch
   - Render auto-deploys on push

---

**Happy Deploying!** 🚀

*Last updated: October 4, 2025*

