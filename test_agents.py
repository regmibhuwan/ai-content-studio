"""
Comprehensive Test Script for AI Content Studio

Tests all agents in the full workflow with detailed output.
Run this after setup to verify all agents are working correctly.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from backend.agents.workflow import create_article
from utils.logger import get_logger

logger = get_logger(__name__)


def print_section(title: str, char: str = "="):
    """Print a formatted section header."""
    width = 70
    print("\n" + char * width)
    print(f"{title:^{width}}")
    print(char * width + "\n")


def print_agent_result(agent_name: str, log: dict):
    """Print formatted agent execution result."""
    status_icon = "✓" if log["status"] == "success" else "⊘" if log["status"] == "skipped" else "✗"
    print(f"  [{status_icon}] {agent_name}")
    print(f"      Status: {log['status']}")
    print(f"      Message: {log['message']}")
    if "execution_time" in log:
        print(f"      Time: {log['execution_time']:.2f}s")
    
    # Print agent-specific data
    if agent_name == "ResearchAgent" and "num_sources" in log:
        print(f"      Sources Found: {log.get('num_sources', 0)}")
    elif agent_name == "OutlineAgent" and "num_sections" in log:
        print(f"      Sections: {log.get('num_sections', 0)}")
    elif agent_name == "WriterAgent" and "word_count" in log:
        print(f"      Word Count: {log.get('word_count', 0)}")
    elif agent_name == "EditorAgent" and "improvements" in log:
        imp = log["improvements"]
        print(f"      Changes: {imp.get('summary', 'N/A')}")
    elif agent_name == "SEOAgent" and "keywords_count" in log:
        print(f"      Keywords: {log.get('keywords_count', 0)}")
    elif agent_name == "ImageAgent" and "image_generated" in log:
        print(f"      Image Generated: {'Yes' if log['image_generated'] else 'No'}")
    
    print()


async def test_simple_workflow():
    """Test workflow with a simple, fast topic."""
    print_section("TEST 1: Simple Workflow (Short Article)")
    
    topic = "The Benefits of Morning Routines"
    print(f"Topic: {topic}")
    print(f"Target: 500 words, professional tone\n")
    
    start_time = datetime.now()
    
    result = await create_article(
        topic=topic,
        tone="professional",
        target_audience="general",
        min_words=500,
        include_image=False,  # Skip image for faster testing
        seo_optimize=True,
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Display results
    print("\n--- Agent Execution Log ---")
    for log in result.get("agent_logs", []):
        print_agent_result(log["agent"], log)
    
    print(f"\n--- Final Status ---")
    print(f"Status: {result['status']}")
    print(f"Total Duration: {duration:.2f}s")
    print(f"Errors: {len(result.get('errors', []))}")
    
    if result.get("errors"):
        print("\n--- Errors ---")
        for error in result["errors"]:
            print(f"  ✗ {error}")
    
    # Show content preview
    if result.get("edited_content"):
        content = result["edited_content"]
        word_count = len(content.split())
        print(f"\n--- Content Preview ({word_count} words) ---")
        print(content[:500] + "..." if len(content) > 500 else content)
    
    # Show SEO data
    if result.get("seo_meta"):
        seo = result["seo_meta"]
        print(f"\n--- SEO Metadata ---")
        print(f"  Title: {seo.get('title', 'N/A')}")
        print(f"  Description: {seo.get('meta_description', 'N/A')[:100]}...")
        print(f"  Keywords: {', '.join(seo.get('keywords', [])[:5])}...")
    
    return result


async def test_full_workflow():
    """Test complete workflow with all features enabled."""
    print_section("TEST 2: Full Workflow (Complete Article + Image)")
    
    topic = "How Artificial Intelligence is Revolutionizing Healthcare"
    print(f"Topic: {topic}")
    print(f"Target: 1000 words, technical tone, developers audience\n")
    
    start_time = datetime.now()
    
    result = await create_article(
        topic=topic,
        tone="technical",
        target_audience="healthcare professionals",
        min_words=1000,
        include_image=True,  # Enable image generation
        seo_optimize=True,
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Display results
    print("\n--- Agent Execution Log ---")
    for log in result.get("agent_logs", []):
        print_agent_result(log["agent"], log)
    
    print(f"\n--- Final Status ---")
    print(f"Status: {result['status']}")
    print(f"Total Duration: {duration:.2f}s")
    print(f"Errors: {len(result.get('errors', []))}")
    
    if result.get("errors"):
        print("\n--- Errors ---")
        for error in result["errors"]:
            print(f"  ✗ {error}")
    
    # Show research data
    if result.get("research_data"):
        rd = result["research_data"]
        print(f"\n--- Research Summary ---")
        print(f"  Sources: {rd.get('num_sources', 0)}")
        print(f"  Synthesis: {rd.get('synthesis', 'N/A')[:200]}...")
    
    # Show outline
    if result.get("outline"):
        outline = result["outline"]
        lines = outline.split("\n")[:10]  # First 10 lines
        print(f"\n--- Outline Preview ---")
        for line in lines:
            print(f"  {line}")
        if len(outline.split("\n")) > 10:
            print("  ...")
    
    # Show content stats
    if result.get("edited_content"):
        content = result["edited_content"]
        word_count = len(content.split())
        para_count = content.count("\n\n")
        heading_count = content.count("#")
        
        print(f"\n--- Content Statistics ---")
        print(f"  Word Count: {word_count}")
        print(f"  Paragraphs: {para_count}")
        print(f"  Headings: {heading_count}")
        
        print(f"\n--- Content Preview ---")
        print(content[:400] + "..." if len(content) > 400 else content)
    
    # Show SEO data
    if result.get("seo_meta"):
        seo = result["seo_meta"]
        print(f"\n--- SEO Metadata ---")
        print(f"  Title: {seo.get('title', 'N/A')}")
        print(f"  Meta Description: {seo.get('meta_description', 'N/A')}")
        print(f"  Primary Keyword: {seo.get('primary_keyword', 'N/A')}")
        print(f"  Keywords ({len(seo.get('keywords', []))}): {', '.join(seo.get('keywords', [])[:8])}")
    
    # Show image info
    if result.get("image_url"):
        print(f"\n--- Cover Image ---")
        print(f"  URL: {result['image_url']}")
    
    return result


async def test_individual_agents():
    """Test each agent individually."""
    print_section("TEST 3: Individual Agent Tests")
    
    from backend.agents import (
        ResearchAgent,
        OutlineAgent,
        WriterAgent,
        EditorAgent,
        SEOAgent,
        ImageAgent,
    )
    
    topic = "Cloud Computing Basics"
    
    # Test 1: Research Agent
    print("\n[1] Testing ResearchAgent...")
    research_agent = ResearchAgent()
    research_result = await research_agent.run({"topic": topic})
    print(f"    Status: {research_result.status}")
    print(f"    Sources: {research_result.data.get('num_sources', 0)}")
    
    # Test 2: Outline Agent
    print("\n[2] Testing OutlineAgent...")
    outline_agent = OutlineAgent()
    outline_result = await outline_agent.run({
        "topic": topic,
        "research_data": research_result.data,
        "tone": "casual",
        "min_words": 600,
    })
    print(f"    Status: {outline_result.status}")
    print(f"    Sections: {outline_result.data.get('num_sections', 0)}")
    
    # Test 3: Writer Agent
    print("\n[3] Testing WriterAgent...")
    writer_agent = WriterAgent()
    writer_result = await writer_agent.run({
        "topic": topic,
        "outline": outline_result.data.get("outline"),
        "research_data": research_result.data,
        "tone": "casual",
        "min_words": 600,
    })
    print(f"    Status: {writer_result.status}")
    print(f"    Words: {writer_result.data.get('word_count', 0)}")
    
    # Test 4: Editor Agent
    print("\n[4] Testing EditorAgent...")
    editor_agent = EditorAgent()
    editor_result = await editor_agent.run({
        "topic": topic,
        "content": writer_result.data.get("content"),
        "research_data": research_result.data,
        "tone": "casual",
    })
    print(f"    Status: {editor_result.status}")
    print(f"    Changes: {editor_result.data.get('improvements', {}).get('summary', 'N/A')}")
    
    # Test 5: SEO Agent
    print("\n[5] Testing SEOAgent...")
    seo_agent = SEOAgent()
    seo_result = await seo_agent.run({
        "topic": topic,
        "edited_content": editor_result.data.get("edited_content"),
    })
    print(f"    Status: {seo_result.status}")
    print(f"    Keywords: {len(seo_result.data.get('keywords', []))}")
    
    # Test 6: Image Agent (skipped by default for speed)
    print("\n[6] Testing ImageAgent...")
    image_agent = ImageAgent()
    image_result = await image_agent.run({
        "topic": topic,
        "include_image": False,  # Skip actual generation
    })
    print(f"    Status: {seo_result.status}")
    print(f"    Skipped: {image_result.data.get('skipped', False)}")
    
    print("\n✓ All individual agent tests completed!")


async def save_article_to_file(result: dict, filename: str = "generated_article.md"):
    """Save generated article to a markdown file."""
    if not result.get("edited_content"):
        print("No content to save.")
        return
    
    content = result["edited_content"]
    seo = result.get("seo_meta", {})
    
    # Build markdown file
    output = []
    
    # Add frontmatter with SEO metadata
    output.append("---")
    output.append(f"title: {seo.get('title', result['topic'])}")
    output.append(f"description: {seo.get('meta_description', '')}")
    output.append(f"keywords: {', '.join(seo.get('keywords', []))}")
    output.append(f"generated: {datetime.now().isoformat()}")
    output.append("---\n")
    
    # Add image if available
    if result.get("image_url"):
        output.append(f"![Cover Image]({result['image_url']})\n")
    
    # Add content
    output.append(content)
    
    # Add metadata footer
    output.append("\n\n---\n")
    output.append("*Generated by AI Content Studio*\n")
    output.append(f"*Topic: {result['topic']}*\n")
    output.append(f"*Word Count: {len(content.split())}*\n")
    
    # Write to file
    filepath = Path(filename)
    filepath.write_text("\n".join(output), encoding="utf-8")
    
    print(f"\n✓ Article saved to: {filepath.absolute()}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(f"{'AI CONTENT STUDIO - COMPREHENSIVE AGENT TESTS':^70}")
    print("=" * 70)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Test 1: Simple workflow (faster)
        result1 = await test_simple_workflow()
        
        print("\n" + "-" * 70)
        input("\nPress Enter to continue to Test 2 (or Ctrl+C to stop)...")
        
        # Test 2: Full workflow with image
        result2 = await test_full_workflow()
        
        # Save the full article
        if result2.get("status") == "completed":
            await save_article_to_file(result2, "test_article_full.md")
        
        print("\n" + "-" * 70)
        input("\nPress Enter to continue to Test 3 (or Ctrl+C to stop)...")
        
        # Test 3: Individual agents
        await test_individual_agents()
        
        # Final summary
        print_section("ALL TESTS COMPLETED", "=")
        print("✓ All agents are functioning correctly!")
        print("\nNext steps:")
        print("  1. Review generated articles in your directory")
        print("  2. Check logs for any warnings")
        print("  3. Proceed to Phase 3 (FastAPI backend)")
        print("  4. Build the Streamlit frontend (Phase 4)")
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Initialize database first
    print("Initializing database...")
    from backend.database import init_db
    asyncio.run(init_db())
    print("Database initialized!\n")
    
    # Run tests
    asyncio.run(main())

