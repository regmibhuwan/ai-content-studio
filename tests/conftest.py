"""
Pytest configuration and fixtures for AI Content Studio tests.
"""

import pytest
import asyncio
import os
from pathlib import Path

# Set test environment variables before any imports
os.environ["OPENAI_API_KEY"] = "test-key-123"
os.environ["TAVILY_API_KEY"] = "test-tavily-key-123"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DEBUG_MODE"] = "False"


# Remove custom event_loop fixture to avoid pytest-asyncio deprecation warning
# Tests will use pytest-asyncio's default event loop


@pytest.fixture
def mock_research_data():
    """Mock research data for testing."""
    return {
        "sources": [
            {
                "id": 1,
                "title": "Test Article 1",
                "url": "https://example.com/article1",
                "content": "This is test content about the topic.",
                "score": 0.95
            },
            {
                "id": 2,
                "title": "Test Article 2",
                "url": "https://example.com/article2",
                "content": "More test content with relevant information.",
                "score": 0.88
            }
        ],
        "key_findings": [
            {"source_id": 0, "finding": "AI-generated summary", "type": "ai_summary"},
            {"source_id": 1, "finding": "Key point from source 1"},
            {"source_id": 2, "finding": "Key point from source 2"}
        ],
        "synthesis": "This is a comprehensive synthesis of research findings about the topic.",
        "num_sources": 2
    }


@pytest.fixture
def mock_outline():
    """Mock outline for testing."""
    return """## Introduction
- Hook and context
- Thesis statement

## Main Point 1
- Supporting detail A
- Supporting detail B

## Main Point 2
- Supporting detail C
- Supporting detail D

## Conclusion
- Summary of key points
- Call to action"""


@pytest.fixture
def mock_content():
    """Mock article content for testing."""
    return """# Test Article Title

## Introduction

This is the introduction paragraph that sets the context for the article.
It provides background information and states the main thesis.

## Main Point 1

This section elaborates on the first main point with detailed explanations
and supporting evidence from research.

## Main Point 2

The second main point is discussed here with additional context and examples
that help illustrate the concepts being presented.

## Conclusion

In conclusion, this article has covered the main points and provided
comprehensive insights into the topic."""


@pytest.fixture
def mock_seo_meta():
    """Mock SEO metadata for testing."""
    return {
        "title": "Test Article: Complete Guide to the Topic",
        "meta_description": "Discover everything you need to know about the topic in this comprehensive guide with expert insights and practical tips.",
        "keywords": [
            "test topic",
            "main keyword",
            "related term",
            "specific phrase",
            "technical term"
        ],
        "primary_keyword": "test topic",
        "headings": ["H1: Test Article Title", "H2: Introduction", "H2: Main Point 1"],
        "heading_count": 3,
        "word_count": 150
    }


@pytest.fixture
def sample_article_state():
    """Complete article state for testing."""
    return {
        "topic": "Artificial Intelligence in Healthcare",
        "tone": "professional",
        "target_audience": "healthcare professionals",
        "min_words": 1000,
        "include_image": True,
        "seo_optimize": True,
        "status": "completed",
        "current_agent": None,
        "agent_logs": [],
        "errors": []
    }

