# 🧪 Testing Guide - AI Content Studio

Complete guide for testing your multi-agent content creation system.

---

## 🚀 Quick Start Testing

### **1. Pre-Test Checklist**

```bash
# Ensure virtual environment is active
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Verify setup
python check_setup.py
```

Expected output: `[SUCCESS] ALL CHECKS PASSED`

### **2. Initialize Database**

```bash
python -c "from backend.database import init_db; import asyncio; asyncio.run(init_db())"
```

### **3. Run Comprehensive Tests**

```bash
python test_agents.py
```

This runs 3 test suites:
- Test 1: Simple workflow (500 words, no image)
- Test 2: Full workflow (1000 words with image)
- Test 3: Individual agent tests

---

## 📋 Test Scenarios

### **Scenario 1: Quick Article (3-5 minutes)**

**Purpose:** Verify basic workflow  
**Expected Time:** ~30-45 seconds

```python
import asyncio
from backend.agents.workflow import create_article

async def quick_test():
    result = await create_article(
        topic="Benefits of Regular Exercise",
        tone="professional",
        target_audience="general",
        min_words=500,
        include_image=False,  # Skip for speed
        seo_optimize=True
    )
    
    print(f"Status: {result['status']}")
    print(f"Word Count: {len(result['edited_content'].split())}")
    return result

asyncio.run(quick_test())
```

**Expected Output:**
- Status: `completed`
- Word Count: 500-650 words
- Agent Logs: 5 success entries (all except Image)
- Research: 5 sources
- SEO: 10-15 keywords

---

### **Scenario 2: Full Article with Image (5-10 minutes)**

**Purpose:** Test complete pipeline with all features  
**Expected Time:** ~50-70 seconds

```python
import asyncio
from backend.agents.workflow import create_article

async def full_test():
    result = await create_article(
        topic="Artificial Intelligence in Modern Healthcare",
        tone="technical",
        target_audience="healthcare professionals",
        min_words=1200,
        include_image=True,  # Enable DALL-E
        seo_optimize=True
    )
    
    # Display results
    print(f"\n{'='*60}")
    print(f"Status: {result['status']}")
    print(f"{'='*60}\n")
    
    # Agent execution summary
    print("Agent Execution Log:")
    for log in result['agent_logs']:
        icon = "✓" if log['status'] == 'success' else "✗"
        print(f"  [{icon}] {log['agent']}: {log['message']}")
    
    # Content stats
    content = result['edited_content']
    print(f"\nContent Statistics:")
    print(f"  Word Count: {len(content.split())}")
    print(f"  Paragraphs: {content.count(chr(10) + chr(10))}")
    print(f"  Headings: {content.count('#')}")
    
    # SEO data
    seo = result['seo_meta']
    print(f"\nSEO Metadata:")
    print(f"  Title: {seo['title']}")
    print(f"  Description: {seo['meta_description'][:80]}...")
    print(f"  Keywords: {', '.join(seo['keywords'][:5])}")
    
    # Image
    if result.get('image_url'):
        print(f"\nImage Generated:")
        print(f"  URL: {result['image_url']}")
    
    # Save to file
    with open('test_article.md', 'w', encoding='utf-8') as f:
        f.write(f"# {seo['title']}\n\n")
        if result.get('image_url'):
            f.write(f"![Cover]({result['image_url']})\n\n")
        f.write(content)
    
    print(f"\n✓ Article saved to test_article.md")
    
    return result

asyncio.run(full_test())
```

**Expected Output:**
- Status: `completed`
- Word Count: 1200-1500 words
- Agent Logs: 6 success entries (all agents)
- Image URL: DALL-E generated image
- File: `test_article.md` created

---

### **Scenario 3: Individual Agent Testing**

**Purpose:** Debug specific agents  
**Expected Time:** ~2 minutes per agent

```python
import asyncio

async def test_individual_agent():
    # Example: Testing OutlineAgent
    from backend.agents import OutlineAgent, ResearchAgent
    
    # Step 1: Get research (prerequisite)
    research_agent = ResearchAgent()
    research_result = await research_agent.run({
        "topic": "Python Programming Best Practices"
    })
    
    # Step 2: Test outline agent
    outline_agent = OutlineAgent()
    outline_result = await outline_agent.run({
        "topic": "Python Programming Best Practices",
        "research_data": research_result.data,
        "tone": "technical",
        "target_audience": "developers",
        "min_words": 800
    })
    
    # Display results
    print(f"Status: {outline_result.status}")
    print(f"Message: {outline_result.message}")
    print(f"\nOutline:\n{outline_result.data['outline']}")
    
    return outline_result

asyncio.run(test_individual_agent())
```

---

## 🔍 Verification Checklist

After running tests, verify:

### **✅ ResearchAgent**
- [ ] Finds 5 sources from web search
- [ ] Returns URLs and content snippets
- [ ] Generates synthesis (200+ words)
- [ ] Execution time: 3-5 seconds

### **✅ OutlineAgent**
- [ ] Creates hierarchical structure (## and -)
- [ ] Has 3+ main sections
- [ ] Includes intro and conclusion
- [ ] Execution time: 3-5 seconds

### **✅ WriterAgent**
- [ ] Generates full article
- [ ] Meets minimum word count (±20%)
- [ ] Follows outline structure
- [ ] Includes proper markdown headings
- [ ] Execution time: 10-20 seconds

### **✅ EditorAgent**
- [ ] Improves grammar and flow
- [ ] Returns edited_content
- [ ] Shows improvement metrics
- [ ] Execution time: 8-15 seconds

### **✅ SEOAgent**
- [ ] Generates SEO title (50-60 chars)
- [ ] Creates meta description (150-160 chars)
- [ ] Extracts 10-15 keywords
- [ ] Execution time: 5-8 seconds

### **✅ ImageAgent**
- [ ] Generates DALL-E image (if enabled)
- [ ] Returns valid image URL
- [ ] Gracefully fails if disabled
- [ ] Execution time: 10-15 seconds (if enabled)

---

## 🐛 Troubleshooting

### **Issue: "Missing API key" Error**

```bash
# Check .env file exists
ls .env  # Mac/Linux
dir .env  # Windows

# Verify keys are set
cat .env  # Mac/Linux
type .env  # Windows
```

**Fix:** Ensure `.env` has valid keys:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

---

### **Issue: "Rate limit exceeded"**

**Cause:** Too many API calls in short time

**Fix:**
1. Wait 60 seconds between tests
2. Check API quota at:
   - OpenAI: https://platform.openai.com/usage
   - Tavily: https://app.tavily.com/dashboard

---

### **Issue: Agent execution timeout**

**Symptoms:** Test hangs, no output

**Fix:**
1. Check internet connection
2. Verify API endpoints are accessible
3. Add timeout to test:

```python
import asyncio

try:
    result = await asyncio.wait_for(
        create_article(topic="Test"),
        timeout=120  # 2 minutes
    )
except asyncio.TimeoutError:
    print("Test timed out after 2 minutes")
```

---

### **Issue: Content is too short**

**Expected:** 800 words, **Got:** 400 words

**Cause:** WriterAgent expansion logic may need adjustment

**Debug:**
```python
# Check individual agent
writer_result = await writer_agent.run({
    "topic": "Test",
    "outline": "## Section 1\n- Point A\n## Section 2\n- Point B",
    "research_data": {...},
    "min_words": 800
})

print(f"Word count: {writer_result.data['word_count']}")
print(f"Meets minimum: {writer_result.data['meets_minimum']}")
```

**Fix:** Increase `min_words` parameter or adjust temperature

---

### **Issue: Image generation fails**

**Error:** "Image generation failed"

**Common Causes:**
1. DALL-E 3 rate limit reached
2. Invalid image prompt
3. Content filtering triggered

**Workaround:** Disable image generation temporarily:
```python
result = await create_article(
    topic="...",
    include_image=False  # Skip image
)
```

---

## 📊 Performance Benchmarks

### **Expected Execution Times**

| Test Type | Word Count | Image | Total Time |
|-----------|------------|-------|------------|
| Quick | 500 | No | 30-45s |
| Standard | 1000 | No | 40-55s |
| Full | 1000 | Yes | 50-70s |
| Long | 2000 | Yes | 70-100s |

### **Memory Usage**

- Base: ~100-150 MB
- Peak (during LLM calls): ~200-300 MB
- Per article in memory: ~5-10 MB

---

## 📝 Sample Test Output

```
======================================================================
                 TEST 1: Simple Workflow (Short Article)
======================================================================

Topic: The Benefits of Morning Routines
Target: 500 words, professional tone


--- Agent Execution Log ---
  [✓] ResearchAgent
      Status: success
      Message: Research completed with 5 sources
      Time: 3.42s
      Sources Found: 5

  [✓] OutlineAgent
      Status: success
      Message: Outline created with 4 sections
      Time: 3.18s
      Sections: 4

  [✓] WriterAgent
      Status: success
      Message: Article written with 587 words
      Time: 12.34s
      Word Count: 587

  [✓] EditorAgent
      Status: success
      Message: Content edited successfully. Refined content
      Time: 9.21s
      Changes: Refined content (12 words added)

  [✓] SEOAgent
      Status: success
      Message: SEO metadata generated with 12 keywords
      Time: 5.67s
      Keywords: 12

  [⊘] ImageAgent
      Status: skipped
      Message: Image generation skipped per configuration


--- Final Status ---
Status: completed
Total Duration: 34.82s
Errors: 0

--- Content Preview (587 words) ---
# The Benefits of Morning Routines

A well-structured morning routine can transform your daily life...
[content continues...]

--- SEO Metadata ---
  Title: Morning Routines: Transform Your Day with These Simple Habits
  Description: Discover how establishing a morning routine can boost productivity...
  Keywords: morning routine, productivity, habits, wellness, success...

✓ All tests passed!
```

---

## 🎯 Testing Best Practices

### **1. Start Small**
- Test with 500-word articles first
- Disable image generation initially
- Use simple topics

### **2. Incremental Testing**
- Test one agent at a time
- Verify each agent's output before continuing
- Check state transformation at each step

### **3. Monitor API Usage**
- Track OpenAI token usage
- Monitor Tavily search quota
- Set spending limits on OpenAI dashboard

### **4. Save Test Results**
- Save generated articles for review
- Compare outputs across different topics
- Keep logs for debugging

### **5. Use Version Control**
- Commit working configurations
- Track changes to prompts
- Document what works well

---

## 🚀 Advanced Testing

### **Load Testing**

```python
import asyncio

async def load_test(num_articles=5):
    """Generate multiple articles concurrently."""
    topics = [
        "Machine Learning Basics",
        "Cloud Computing Fundamentals",
        "Web Development Best Practices",
        "Data Science Career Guide",
        "Cybersecurity Essentials"
    ]
    
    tasks = [
        create_article(topic=topic, min_words=600, include_image=False)
        for topic in topics[:num_articles]
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successes = sum(1 for r in results if isinstance(r, dict) and r['status'] == 'completed')
    print(f"\n{successes}/{num_articles} articles generated successfully")
    
    return results

asyncio.run(load_test(5))
```

---

## ✅ Ready for Production?

Before moving to Phase 3 (API) or Phase 4 (UI), ensure:

- [ ] All 6 agents pass individual tests
- [ ] Full workflow completes successfully
- [ ] Generated articles meet quality standards
- [ ] Execution time is acceptable (< 90s)
- [ ] Error handling works correctly
- [ ] API costs are within budget
- [ ] Documentation is clear and complete

---

**Happy Testing!** 🎉

Once all tests pass, you're ready to build the FastAPI backend (Phase 3) or Streamlit frontend (Phase 4)!

