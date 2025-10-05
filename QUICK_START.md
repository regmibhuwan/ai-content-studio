# ⚡ Quick Start Guide - AI Content Studio

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies (2 min)

```bash
# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure API Keys (1 min)

```bash
# Copy template
copy .env.example .env    # Windows
cp .env.example .env      # Mac/Linux
```

Edit `.env` and add your keys:
- **OpenAI API Key**: Get from https://platform.openai.com/api-keys
- **Tavily API Key**: Get from https://app.tavily.com/ (free: 1000 searches/month)

### Step 3: Verify Setup (30 sec)

```bash
python check_setup.py
```

Should show `[SUCCESS] ALL CHECKS PASSED`

### Step 4: Initialize Database (30 sec)

```bash
python -c "from backend.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Step 5: Run Test (1 min)

```bash
python test_workflow.py
```

---

## 📋 Key Commands Reference

| Command | Purpose |
|---------|---------|
| `python check_setup.py` | Verify installation and configuration |
| `python test_workflow.py` | Run full test suite with example topics |
| `python -m pytest tests/` | Run unit tests (when implemented) |
| `uvicorn backend.main:app --reload` | Start FastAPI backend (Phase 3) |
| `streamlit run frontend/streamlit_app.py` | Start frontend UI (Phase 4) |

---

## 🧪 Try It Yourself

### Test Research Agent with Custom Topic

Create a file `my_test.py`:

```python
import asyncio
from backend.agents.research_agent import ResearchAgent

async def main():
    agent = ResearchAgent()
    
    result = await agent.run({
        "topic": "Your custom topic here",
        "tone": "professional",
        "target_audience": "general"
    })
    
    if result.is_success():
        print(f"\n✓ Found {result.data['num_sources']} sources")
        print(f"\nSynthesis:\n{result.data['synthesis']}")
        
        print("\nTop 3 Sources:")
        for source in result.data['sources'][:3]:
            print(f"  • {source['title']}")
            print(f"    {source['url']}\n")
    else:
        print(f"Error: {result.error}")

asyncio.run(main())
```

Run: `python my_test.py`

---

## 📁 Project Structure Quick Reference

```
ai_content_studio/
├── backend/
│   ├── agents/
│   │   ├── base.py           # Abstract agent class
│   │   ├── research_agent.py # ✅ Implemented
│   │   └── workflow.py       # ✅ LangGraph orchestration
│   ├── config.py             # Settings management
│   ├── database.py           # SQLAlchemy models
│   └── schemas.py            # API models
│
├── utils/
│   ├── logger.py             # Structured logging
│   └── helpers.py            # Text utilities
│
├── .env                      # Your API keys (git-ignored)
├── requirements.txt          # Dependencies
├── check_setup.py            # Setup verification
└── test_workflow.py          # Test suite
```

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError"
**Fix:** `pip install -r requirements.txt`

### Issue: "Missing API key"
**Fix:** Add keys to `.env` file (copy from `.env.example`)

### Issue: "UnicodeEncodeError" on Windows
**Fix:** Already patched in check_setup.py

### Issue: Slow first run
**Reason:** Downloading models and making API calls (normal)

---

## 📊 What Works Now (Phase 2)

✅ **BaseAgent**: Abstract foundation for all agents  
✅ **ResearchAgent**: Web search + synthesis using Tavily + GPT-4  
✅ **Workflow**: LangGraph orchestration with state management  
✅ **Logging**: Structured logs with timing  
✅ **Error Handling**: Graceful failures with detailed messages  

🔨 **Coming Next:**
- OutlineAgent (Phase 2 continuation)
- WriterAgent (Phase 2 continuation)
- EditorAgent (Phase 2 continuation)
- SEOAgent (Phase 2 continuation)
- ImageAgent (Phase 2 continuation)

---

## 💡 Quick Tips

1. **Check logs** - All agents log execution details
2. **Start simple** - Test with short topics first
3. **API costs** - Using `gpt-4o-mini` (cheap) by default
4. **Rate limits** - Tavily: 1000/month free, OpenAI: pay-per-use
5. **State inspection** - Access `state["agent_logs"]` to see what happened

---

## 🎯 Next Steps

1. ✅ Run `check_setup.py` and `test_workflow.py`
2. ✅ Test with your own topics
3. ⏭️ Implement remaining agents (Outline, Writer, Editor, SEO, Image)
4. ⏭️ Build FastAPI backend (Phase 3)
5. ⏭️ Create Streamlit frontend (Phase 4)
6. ⏭️ Deploy online (Phase 5)

---

**Questions?** Check `SETUP_GUIDE.md` for detailed explanations or `PHASE2_SUMMARY.md` for architecture details.

