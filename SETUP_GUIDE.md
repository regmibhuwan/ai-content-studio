# 🚀 AI Content Studio - Setup & Testing Guide

## Phase 2 Progress: Multi-Agent System Implementation

### ✅ What's Been Built

1. **BaseAgent Class** (`backend/agents/base.py`)
   - Abstract foundation for all agents
   - Standardized `AgentResponse` format
   - Built-in logging, error handling, and timing
   - OpenAI LLM integration

2. **ResearchAgent** (`backend/agents/research_agent.py`)
   - Web search using Tavily API
   - Source extraction and ranking
   - LLM-powered research synthesis
   - Structured output format

3. **LangGraph Workflow** (`backend/agents/workflow.py`)
   - StateGraph orchestration
   - Multi-agent coordination
   - State management between nodes
   - Error handling and logging

---

## 📦 Installation Steps

### 1. Install Dependencies

```bash
# Ensure you're in the project directory
cd ai_content_studio

# Activate virtual environment (if not already active)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file from the template:

```bash
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...

# Get from: https://app.tavily.com/ (free tier: 1000 searches/month)
TAVILY_API_KEY=tvly-...
```

**Getting API Keys:**
- **OpenAI**: Sign up at https://platform.openai.com/, create an API key
- **Tavily**: Register at https://app.tavily.com/, get free API key

### 3. Initialize Database

```bash
python -c "from backend.database import init_db; import asyncio; asyncio.run(init_db())"
```

---

## 🧪 Testing the System

### Quick Test: Research Agent Only

```bash
python test_workflow.py
```

This will:
1. Test the ResearchAgent with a sample topic
2. Display research sources and synthesis
3. Run the full workflow (other agents are placeholders)

### Expected Output

```
🚀 AI CONTENT STUDIO - WORKFLOW TEST 🚀

==============================================================
TEST 1: Research Agent Only
==============================================================

2025-01-XX XX:XX:XX - agent.ResearchAgent - INFO - [ResearchAgent] Starting execution...
2025-01-XX XX:XX:XX - agent.ResearchAgent - INFO - [ResearchAgent] Researching topic: 'The impact of artificial intelligence on software development'
...

==============================================================
RESEARCH AGENT RESULTS
==============================================================
Status: success
Message: Research completed with 5 sources
Execution Time: 3.45s

Sources Found: 5

--- Research Synthesis ---
[AI-generated synthesis of findings...]

--- Top Sources ---
  • [Article Title]
    URL: https://...
    Score: 0.95
```

---

## 🏗️ Architecture Deep Dive

### State Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   ContentCreationState                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ topic, tone, target_audience, min_words              │   │
│  │ research_data, outline, content, seo_meta, image_url │   │
│  │ current_agent, agent_logs, errors, status            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌──────────────────────────────────────┐
        │      Research Node                    │
        │  • Searches web (Tavily)              │
        │  • Extracts sources                   │
        │  • Synthesizes findings               │
        │  • Updates state.research_data        │
        └──────────────────────────────────────┘
                            ↓
        ┌──────────────────────────────────────┐
        │      Outline Node (TODO)              │
        │  • Creates content structure          │
        │  • Updates state.outline              │
        └──────────────────────────────────────┘
                            ↓
        ┌──────────────────────────────────────┐
        │      Writer Node (TODO)               │
        │  • Generates article content          │
        │  • Updates state.content              │
        └──────────────────────────────────────┘
                            ↓
        ┌──────────────────────────────────────┐
        │      Editor Node (TODO)               │
        │  • Reviews and improves content       │
        │  • Updates state.edited_content       │
        └──────────────────────────────────────┘
                            ↓
        ┌──────────────────────────────────────┐
        │      SEO Node (TODO)                  │
        │  • Optimizes for search engines       │
        │  • Updates state.seo_meta             │
        └──────────────────────────────────────┘
                            ↓
        ┌──────────────────────────────────────┐
        │      Image Node (TODO)                │
        │  • Generates cover image (DALL-E)     │
        │  • Updates state.image_url            │
        └──────────────────────────────────────┘
                            ↓
                        END
```

### BaseAgent Pattern

All agents inherit from `BaseAgent` and follow this pattern:

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MyAgent")
        # Initialize tools/clients
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        # 1. Extract required data from input_data
        # 2. Perform agent-specific logic
        # 3. Call self._call_llm() if needed
        # 4. Return AgentResponse with results
        
        return AgentResponse(
            status="success",
            data={"key": "value"},
            message="Task completed"
        )
```

### Using the Workflow

**Option 1: High-level function**
```python
from backend.agents.workflow import create_article

result = await create_article(
    topic="Your topic here",
    tone="professional",
    target_audience="developers"
)

print(result["research_data"])
```

**Option 2: Direct workflow control**
```python
from backend.agents.workflow import ContentCreationWorkflow

workflow = ContentCreationWorkflow()
state = await workflow.run({
    "topic": "Your topic",
    "tone": "casual",
})

print(state["agent_logs"])
```

---

## 🐛 Troubleshooting

### Error: "Missing API key"
- Ensure `.env` file exists with `OPENAI_API_KEY` and `TAVILY_API_KEY`
- Check that keys are valid (no quotes, no extra spaces)

### Error: "ModuleNotFoundError"
- Run `pip install -r requirements.txt` again
- Ensure virtual environment is activated

### Tavily Rate Limit
- Free tier: 1000 searches/month
- If exceeded, wait for reset or upgrade plan

### Slow Research Agent
- First run downloads models and indexes
- Network latency affects Tavily API calls
- Typical execution: 3-5 seconds per research

---

## 📊 Next Steps

**Immediate:**
- ✅ Test the research agent with your own topics
- ✅ Verify API keys work correctly
- ✅ Review agent logs for debugging

**Phase 2 Continuation:**
- 🔨 Implement OutlineAgent
- 🔨 Implement WriterAgent
- 🔨 Implement EditorAgent
- 🔨 Implement SEOAgent
- 🔨 Implement ImageAgent

**Phase 3:**
- 🔨 Build FastAPI backend with WebSocket
- 🔨 Connect workflow to API endpoints

**Phase 4:**
- 🔨 Build Streamlit frontend
- 🔨 Real-time progress visualization

---

## 📝 Code Quality

All code follows:
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Async/await patterns
- ✅ Structured logging
- ✅ Error handling
- ✅ Consistent naming conventions

---

**Need help?** Check the logs in console output or review `backend/agents/` files for implementation details.

