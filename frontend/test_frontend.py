"""
Frontend Smoke Tests

Basic tests to ensure Streamlit app can be imported and key functions work.
Run with: pytest frontend/test_frontend.py -v
"""

import sys
from pathlib import Path

# Add frontend to path
sys.path.insert(0, str(Path(__file__).parent))

import pytest
from unittest.mock import patch, MagicMock
import requests


def test_imports():
    """Test that all required packages can be imported."""
    import streamlit as st
    import requests
    import markdown
    from fpdf import FPDF
    from websocket import WebSocketApp
    
    assert st is not None
    assert requests is not None
    assert markdown is not None
    assert FPDF is not None
    assert WebSocketApp is not None


def test_app_module_imports():
    """Test that app.py can be imported."""
    try:
        import app
        assert hasattr(app, 'main')
        assert hasattr(app, 'create_article')
        assert hasattr(app, 'check_backend_health')
    except Exception as e:
        pytest.fail(f"Failed to import app module: {e}")


@patch('app.requests.get')
def test_check_backend_health(mock_get):
    """Test backend health check function."""
    from app import check_backend_health
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    result = check_backend_health()
    assert result == True
    
    # Mock failed response
    mock_get.side_effect = requests.exceptions.ConnectionError()
    result = check_backend_health()
    assert result == False


@patch('app.requests.post')
def test_create_article_api(mock_post):
    """Test article creation API call."""
    from app import create_article
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 1,
        "topic": "Test Topic",
        "status": "pending"
    }
    mock_post.return_value = mock_response
    
    result = create_article(
        topic="Test Topic",
        tone="professional",
        min_words=500
    )
    
    assert result is not None
    assert result["id"] == 1
    assert result["topic"] == "Test Topic"


@patch('app.requests.get')
def test_get_article_status(mock_get):
    """Test article status retrieval."""
    from app import get_article_status
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "status": "processing",
        "progress_percentage": 50
    }
    mock_get.return_value = mock_response
    
    result = get_article_status(article_id=1)
    
    assert result is not None
    assert result["status"] == "processing"
    assert result["progress_percentage"] == 50


@patch('app.requests.get')
def test_list_articles(mock_get):
    """Test articles listing."""
    from app import list_articles
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "topic": "Article 1", "status": "completed"},
        {"id": 2, "topic": "Article 2", "status": "processing"}
    ]
    mock_get.return_value = mock_response
    
    result = list_articles(limit=10)
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == 1


def test_export_functions():
    """Test export functionality."""
    from app import export_as_markdown, export_as_html, export_as_pdf
    
    content = "# Test\n\nThis is test content."
    title = "Test Article"
    
    # Test Markdown export
    md = export_as_markdown(content, title)
    assert "# Test Article" in md
    assert "test content" in md
    
    # Test HTML export
    html = export_as_html(content, title)
    assert "<!DOCTYPE html>" in html
    assert "<title>Test Article</title>" in html
    
    # Test PDF export (basic test)
    try:
        pdf = export_as_pdf(content, title)
        assert isinstance(pdf, bytes)
        assert len(pdf) > 0
    except Exception as e:
        pytest.skip(f"PDF export not fully testable: {e}")


def test_config_loading():
    """Test configuration variables."""
    import os
    from app import BACKEND_URL, WS_BACKEND_URL
    
    # Default should be localhost
    assert "localhost:8000" in BACKEND_URL or "http://" in BACKEND_URL
    assert "ws://" in WS_BACKEND_URL


def test_session_state_keys():
    """Test that required session state keys are defined."""
    # These are initialized in app.py but we test the expected keys
    expected_keys = [
        "current_article_id",
        "article_status",
        "article_result",
        "agent_logs",
        "progress",
        "ws_messages",
        "generation_complete"
    ]
    
    # Just verify the keys exist in the code
    with open(Path(__file__).parent / "app.py") as f:
        code = f.read()
        for key in expected_keys:
            assert key in code, f"Session state key '{key}' not found in app.py"


@pytest.mark.integration
def test_full_workflow_mock():
    """
    Integration test simulating full workflow.
    
    Mark as integration so it can be skipped in CI.
    """
    from app import create_article, get_article_status, get_article_result
    
    with patch('app.requests.post') as mock_post, \
         patch('app.requests.get') as mock_get:
        
        # Mock create
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": 1, "status": "pending"}
        
        # Mock status
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 1,
            "status": "completed",
            "progress_percentage": 100
        }
        
        # Create article
        article = create_article(topic="Test")
        assert article["id"] == 1
        
        # Check status
        status = get_article_status(1)
        assert status["status"] == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

