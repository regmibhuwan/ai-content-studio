# 🎨 AI Content Studio - Frontend

Interactive Streamlit UI for the AI Content Studio multi-agent system.

---

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
cd frontend
pip install -r requirements.txt
```

### **2. Configure Backend URL**

```bash
# Set backend URL (default: http://localhost:8000)
export BACKEND_URL=http://localhost:8000

# On Windows PowerShell:
$env:BACKEND_URL="http://localhost:8000"

# On Windows CMD:
set BACKEND_URL=http://localhost:8000
```

### **3. Run Streamlit App**

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📋 Prerequisites

**Backend must be running:**
```bash
# In project root
uvicorn backend.main:app --reload --port 8000
```

**API keys configured:**
- OpenAI API key in `.env`
- Tavily API key in `.env`

---

## 🎯 Features

### **Article Generation**
- Enter topic and preferences
- Click "Generate Article"
- Watch real-time progress
- View results in organized tabs

### **Progress Tracking**
- WebSocket connection for live updates (falls back to polling)
- Agent timeline showing each step
- Progress percentage
- Execution time per agent

### **Content Tabs**
- **Outline:** Structured article outline
- **Draft:** Initial content
- **Edited:** Polished version
- **SEO:** Metadata and keywords
- **Image:** AI-generated cover image

### **Export Options**
- **Markdown (.md)** - Plain text format
- **HTML (.html)** - Web-ready with styling
- **PDF (.pdf)** - Printable document
- **Copy** - Copy to clipboard

### **History**
- View recent articles
- Re-open past generations
- Delete old articles

---

## 🔧 Configuration

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:8000` | FastAPI backend URL |

### **Streamlit Configuration**

Create `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
port = 8501
address = "localhost"
```

---

## 🧪 Testing

### **Local Test**

```bash
# Start backend
uvicorn backend.main:app --port 8000 &

# Run Streamlit
streamlit run app.py

# Test in browser at http://localhost:8501
```

### **Health Check**

The app checks backend connectivity on load:
- ✅ Green banner: Backend accessible
- ❌ Red banner: Backend not found

---

## 🐛 Troubleshooting

### **"Backend not accessible" Error**

**Causes:**
1. Backend not running
2. Wrong `BACKEND_URL`
3. Port conflict

**Fix:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Start backend if needed
uvicorn backend.main:app --reload --port 8000
```

---

### **WebSocket Connection Fails**

The app automatically falls back to polling (every 2 seconds) if WebSocket fails. No action needed.

---

### **Slow Progress Updates**

**Cause:** Polling fallback (2-second intervals)

**Fix:** Ensure WebSocket works:
```bash
# Test WebSocket
pip install websocket-client
python -c "from websocket import create_connection; ws = create_connection('ws://localhost:8000/ws/articles/1'); print('Connected!'); ws.close()"
```

---

### **Image Not Displaying**

**Cause:** DALL-E generation failed or disabled

**Check:**
1. `include_image` checkbox enabled
2. OpenAI API key valid
3. DALL-E quota available

---

### **Export Fails**

**PDF Export:**
- Requires `fpdf2` package
- Check: `pip install fpdf2`

**HTML Export:**
- Requires `markdown` package
- Check: `pip install markdown`

---

## 📱 Mobile/Tablet Support

Streamlit is responsive by default. The app works on mobile browsers but is optimized for desktop.

---

## 🚀 Deployment

### **Streamlit Cloud (Free)**

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set `BACKEND_URL` in Secrets
5. Deploy!

**Secrets Configuration:**
```toml
# .streamlit/secrets.toml
BACKEND_URL = "https://your-backend.onrender.com"
```

### **Docker Deployment**

```bash
# Build image
docker build -t content-studio-frontend -f frontend/Dockerfile .

# Run container
docker run -p 8501:8501 -e BACKEND_URL=http://backend:8000 content-studio-frontend
```

---

## 🎨 UI Customization

### **Change Theme**

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#YOUR_COLOR"
```

### **Modify Layout**

Edit `app.py`:
```python
st.set_page_config(
    page_title="Your Title",
    page_icon="🎨",
    layout="wide"  # or "centered"
)
```

---

## 📊 Performance Tips

### **Faster Loading**
- Use WebSocket instead of polling
- Reduce `list_articles()` limit
- Cache results with `@st.cache_data`

### **Better UX**
- Add loading spinners
- Show estimated time remaining
- Cache API responses

---

## 🔐 Security Notes

**For production:**
- Add authentication (Streamlit supports OAuth)
- Validate all user inputs
- Use HTTPS for backend URL
- Implement rate limiting
- Add CSRF protection

---

## 📝 Code Structure

```python
# app.py structure

# Configuration
BACKEND_URL = ...

# Session State
st.session_state.current_article_id = None

# API Functions
def create_article(): ...
def get_article_status(): ...

# WebSocket Handler
def start_websocket(): ...

# Export Functions
def export_as_markdown(): ...
def export_as_html(): ...
def export_as_pdf(): ...

# UI Components
def render_agent_timeline(): ...
def render_content_tabs(): ...
def render_export_section(): ...

# Main App
def main(): ...
```

---

## 🆘 Support

**Issues:**
- Check backend logs: `uvicorn` console output
- Check Streamlit logs: Terminal running `streamlit run`
- Enable debug mode: Add `?debug=true` to URL

**Logs Location:**
- Backend: Console output
- Frontend: `~/.streamlit/logs/`

---

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [Markdown Guide](https://www.markdownguide.org)

---

## 🚀 Next Steps

**Enhancements:**
- Add article comparison
- Implement A/B testing UI
- Add analytics dashboard
- Support multiple languages
- Add user authentication
- Implement article templates

---

**Enjoy creating amazing content with AI! ✨**

