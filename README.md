# 🎨 AI Content Studio

An advanced multi-agent AI system that automates the entire content creation pipeline using **LangGraph** and specialized AI agents.

## 🌟 Features

- **Multi-Agent Coordination**: Six specialized agents working together
  - 🔍 Research Agent: Web search and source gathering
  - 📝 Outline Agent: Structured content planning
  - ✍️ Writer Agent: High-quality content generation
  - 🔎 Editor Agent: Grammar, flow, and fact-checking
  - 📊 SEO Agent: Keyword optimization and meta descriptions
  - 🎨 Image Agent: AI-generated cover images

- **Real-Time Progress**: Watch agents collaborate in real-time
- **Interactive UI**: Streamlit-based interface for easy interaction
- **Export Options**: Markdown, HTML, and more
- **Persistent Storage**: SQLite database for drafts and history

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Tavily API key (for web search)

### Installation

1. **Clone and setup:**
```bash
cd ai_content_studio
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Initialize database:**
```bash
python -c "from backend.database import init_db; import asyncio; asyncio.run(init_db())"
```

4. **Run the application:**
```bash
# Terminal 1: Start backend API
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Start Streamlit frontend
streamlit run frontend/streamlit_app.py
```

5. **Open browser:**
Navigate to `http://localhost:8501`

## 🏗️ Architecture

```
User Input → Research Agent → Outline Agent → Writer Agent → Editor Agent → SEO Agent → Image Agent → Final Article
```

Each agent is powered by GPT-4 and has specialized tools and prompts.

## 📦 Project Structure

```
ai_content_studio/
├── backend/          # FastAPI backend and agent logic
├── frontend/         # Streamlit UI
├── tests/            # Unit and integration tests
├── utils/            # Shared utilities
└── data/             # SQLite database
```

## 🛠️ Technology Stack

- **AI Framework**: LangGraph, LangChain
- **LLM**: OpenAI GPT-4
- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: Streamlit
- **APIs**: Tavily (search), DALL-E (images)

## 📝 Usage

1. Enter your article topic and preferences
2. Watch agents collaborate in real-time
3. Review and edit the generated content
4. Export as Markdown or HTML
5. (Optional) Publish to Medium/Dev.to

## 🚢 Deployment

See `Dockerfile` and `docker-compose.yml` for containerized deployment.

**Recommended platforms:**
- Backend: Render, Railway, or AWS
- Frontend: Streamlit Cloud

## 📄 License

MIT License - feel free to use for learning and production!

## 🤝 Contributing

This is an educational project. Feel free to fork and extend!

---

Built with ❤️ using LangGraph and OpenAI

