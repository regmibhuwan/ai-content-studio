"""
Test script for the content creation workflow.

Demonstrates how to use the ResearchAgent and workflow system.
Run this after setting up your .env file with API keys.
"""

import asyncio
import json
from backend.agents.workflow import create_article
from utils.logger import get_logger

logger = get_logger(__name__)


async def test_research_only():
    """Test just the research agent."""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Research Agent Only")
    logger.info("="*60 + "\n")

    from backend.agents.research_agent import ResearchAgent

    agent = ResearchAgent()
    
    input_data = {
        "topic": "The impact of artificial intelligence on software development",
        "tone": "technical",
        "target_audience": "developers",
    }

    response = await agent.run(input_data)

    print("\n" + "="*60)
    print("RESEARCH AGENT RESULTS")
    print("="*60)
    print(f"Status: {response.status}")
    print(f"Message: {response.message}")
    print(f"Execution Time: {response.execution_time:.2f}s")
    
    if response.is_success():
        print(f"\nSources Found: {response.data.get('num_sources', 0)}")
        print("\n--- Research Synthesis ---")
        print(response.data.get('synthesis', 'N/A')[:500] + "...")
        
        print("\n--- Top Sources ---")
        for source in response.data.get('sources', [])[:3]:
            print(f"  • {source['title']}")
            print(f"    URL: {source['url']}")
            print(f"    Score: {source['score']:.2f}\n")
    else:
        print(f"Error: {response.error}")

    return response


async def test_full_workflow():
    """Test the complete workflow (currently only research works)."""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Full Workflow")
    logger.info("="*60 + "\n")

    result = await create_article(
        topic="How to build scalable microservices with Python",
        tone="technical",
        target_audience="developers",
        min_words=1000,
        include_image=True,
        seo_optimize=True,
    )

    print("\n" + "="*60)
    print("WORKFLOW RESULTS")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Current Agent: {result.get('current_agent', 'N/A')}")
    
    print("\n--- Agent Execution Log ---")
    for log in result.get('agent_logs', []):
        print(f"  • {log['agent']}: {log['status']} - {log['message']}")
    
    if result.get('errors'):
        print("\n--- Errors ---")
        for error in result['errors']:
            print(f"  ❌ {error}")
    
    print("\n--- Research Data Summary ---")
    if result.get('research_data'):
        rd = result['research_data']
        print(f"  Sources: {rd.get('num_sources', 0)}")
        print(f"  Search Query: {rd.get('search_query', 'N/A')}")
    else:
        print("  No research data available")

    return result


async def main():
    """Run all tests."""
    print("\n" + "🚀 "*20)
    print("AI CONTENT STUDIO - WORKFLOW TEST")
    print("🚀 "*20 + "\n")

    try:
        # Test 1: Research agent only
        await test_research_only()
        
        print("\n" + "-"*60 + "\n")
        
        # Test 2: Full workflow
        await test_full_workflow()
        
        print("\n" + "✅ "*20)
        print("ALL TESTS COMPLETED")
        print("✅ "*20 + "\n")

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

