"""
AI Content Studio - Streamlit Frontend

Interactive UI for multi-agent AI content creation system.
Connects to FastAPI backend for article generation with real-time progress.
"""

import os
import json
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

import streamlit as st
import requests
from websocket import WebSocketApp
import markdown
from fpdf import FPDF, XPos, YPos

# ============================================================================
# Configuration
# ============================================================================

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
WS_BACKEND_URL = BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://")

# Page config
st.set_page_config(
    page_title="AI Content Studio",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Session State Initialization
# ============================================================================

if "current_article_id" not in st.session_state:
    st.session_state.current_article_id = None

if "article_status" not in st.session_state:
    st.session_state.article_status = None

if "article_result" not in st.session_state:
    st.session_state.article_result = None

if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []

if "progress" not in st.session_state:
    st.session_state.progress = 0

if "ws_messages" not in st.session_state:
    st.session_state.ws_messages = []

if "generation_complete" not in st.session_state:
    st.session_state.generation_complete = False


# ============================================================================
# API Functions
# ============================================================================

def check_backend_health() -> bool:
    """Check if backend is accessible."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def create_article(
    topic: str,
    tone: str = "professional",
    target_audience: str = "general",
    min_words: int = 800,
    include_image: bool = True,
    seo_optimize: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Create new article via API.
    
    Returns:
        Dict with article data or None if error
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/articles/create",
            json={
                "topic": topic,
                "tone": tone,
                "target_audience": target_audience,
                "min_words": min_words,
                "include_image": include_image,
                "seo_optimize": seo_optimize
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to create article: {str(e)}")
        return None


def get_article_status(article_id: int) -> Optional[Dict[str, Any]]:
    """Get article generation status."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/articles/{article_id}/status",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except:
        return None


def get_article_result(article_id: int) -> Optional[Dict[str, Any]]:
    """Get completed article content."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/articles/{article_id}/result",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to get article: {str(e)}")
        return None


def list_articles(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent articles."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/articles/?limit={limit}",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except:
        return []


def delete_article(article_id: int) -> bool:
    """Delete article."""
    try:
        response = requests.delete(
            f"{BACKEND_URL}/articles/{article_id}",
            timeout=5
        )
        return response.status_code == 204
    except:
        return False


# ============================================================================
# WebSocket Handler
# ============================================================================

def start_websocket(article_id: int):
    """
    Start WebSocket connection for real-time updates.
    Runs in separate thread.
    """
    ws_url = f"{WS_BACKEND_URL}/ws/articles/{article_id}"
    
    def on_message(ws, message):
        try:
            data = json.loads(message)
            st.session_state.ws_messages.append(data)
            
            # Update progress based on message type
            if data.get("type") == "agent_update":
                agent_name = data.get("agent")
                if agent_name and agent_name not in [log.get("agent") for log in st.session_state.agent_logs]:
                    st.session_state.agent_logs.append(data)
            
            elif data.get("type") == "final":
                st.session_state.generation_complete = True
                
        except Exception as e:
            pass
    
    def on_error(ws, error):
        pass
    
    def on_close(ws, close_status_code, close_msg):
        pass
    
    def on_open(ws):
        pass
    
    try:
        ws = WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        ws.run_forever()
    except Exception as e:
        # WebSocket failed, will fall back to polling
        pass


# ============================================================================
# Export Functions
# ============================================================================

def export_as_markdown(content: str, title: str) -> str:
    """Export content as markdown."""
    return f"# {title}\n\n{content}"


def export_as_html(content: str, title: str, seo_meta: Optional[Dict] = None) -> str:
    """Export content as HTML."""
    html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {f'<meta name="description" content="{seo_meta.get("meta_description", "")}">' if seo_meta else ""}
    {f'<meta name="keywords" content="{", ".join(seo_meta.get("keywords", []))}">' if seo_meta else ""}
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
    return html


def export_as_pdf(content: str, title: str) -> bytes:
    """Export content as PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "", 12)
    # Simple text export (markdown not rendered in PDF)
    for line in content.split('\n'):
        if line.strip():
            pdf.multi_cell(0, 6, line)
    
    return pdf.output(dest='S').encode('latin-1')


# ============================================================================
# UI Components
# ============================================================================

def render_agent_timeline(agent_logs: List[Dict], current_status: str):
    """Render agent execution timeline."""
    agents = ["ResearchAgent", "OutlineAgent", "WriterAgent", "EditorAgent", "SEOAgent", "ImageAgent"]
    
    # Create progress bar
    completed_agents = sum(1 for log in agent_logs if log.get("status") == "success")
    progress_percent = int((completed_agents / len(agents)) * 100)
    
    st.progress(progress_percent / 100, text=f"Progress: {progress_percent}%")
    
    # Agent timeline
    cols = st.columns(6)
    
    for idx, agent in enumerate(agents):
        with cols[idx]:
            # Find agent log
            agent_log = next((log for log in agent_logs if log.get("agent") == agent), None)
            
            if agent_log:
                status = agent_log.get("status")
                if status == "success":
                    st.success(f"✓ {agent.replace('Agent', '')}")
                elif status == "error":
                    st.error(f"✗ {agent.replace('Agent', '')}")
                else:
                    st.info(f"⟳ {agent.replace('Agent', '')}")
            else:
                st.write(f"○ {agent.replace('Agent', '')}")


def render_content_tabs(result: Dict[str, Any]):
    """Render content in tabs."""
    tabs = st.tabs(["📝 Outline", "✍️ Draft", "✨ Edited", "🔍 SEO", "🖼️ Image"])
    
    # Outline tab
    with tabs[0]:
        if result.get("outline"):
            st.markdown(result["outline"])
        else:
            st.info("Outline not available yet")
    
    # Draft tab
    with tabs[1]:
        if result.get("content"):
            # Show raw content before editing
            st.markdown(result["content"])
            
            # Word count
            word_count = len(result["content"].split())
            st.caption(f"📊 Word count: {word_count}")
        else:
            st.info("Draft not available yet")
    
    # Edited tab
    with tabs[2]:
        if result.get("content"):
            st.markdown(result["content"])
            
            # Word count
            word_count = len(result["content"].split())
            st.caption(f"📊 Word count: {word_count}")
        else:
            st.info("Edited content not available yet")
    
    # SEO tab
    with tabs[3]:
        if result.get("seo_meta"):
            seo = result["seo_meta"]
            
            st.subheader("SEO Metadata")
            st.write(f"**Title:** {seo.get('title', 'N/A')}")
            st.write(f"**Meta Description:** {seo.get('meta_description', 'N/A')}")
            
            st.write("**Keywords:**")
            keywords = seo.get("keywords", [])
            if keywords:
                st.write(", ".join(keywords[:10]))
            else:
                st.write("No keywords")
            
            if seo.get("headings"):
                st.write("**Headings:**")
                for heading in seo["headings"][:5]:
                    st.write(f"- {heading}")
        else:
            st.info("SEO data not available yet")
    
    # Image tab
    with tabs[4]:
        if result.get("image_url"):
            st.image(result["image_url"], caption="Generated Cover Image")
        else:
            st.info("Image not available yet")


def render_export_section(result: Dict[str, Any]):
    """Render export options."""
    st.subheader("💾 Export Article")
    
    cols = st.columns(4)
    
    topic = result.get("topic", "article")
    content = result.get("content", "")
    seo_meta = result.get("seo_meta", {})
    title = seo_meta.get("title", topic)
    
    # Markdown export
    with cols[0]:
        if st.button("📄 Download MD", use_container_width=True):
            md_content = export_as_markdown(content, title)
            st.download_button(
                label="Save Markdown",
                data=md_content,
                file_name=f"{topic.replace(' ', '_')}.md",
                mime="text/markdown"
            )
    
    # HTML export
    with cols[1]:
        if st.button("🌐 Download HTML", use_container_width=True):
            html_content = export_as_html(content, title, seo_meta)
            st.download_button(
                label="Save HTML",
                data=html_content,
                file_name=f"{topic.replace(' ', '_')}.html",
                mime="text/html"
            )
    
    # PDF export
    with cols[2]:
        if st.button("📕 Download PDF", use_container_width=True):
            try:
                pdf_content = export_as_pdf(content, title)
                st.download_button(
                    label="Save PDF",
                    data=pdf_content,
                    file_name=f"{topic.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF export failed: {str(e)}")
    
    # Copy to clipboard
    with cols[3]:
        if st.button("📋 Copy Text", use_container_width=True):
            st.code(content, language="markdown")


# ============================================================================
# Main App
# ============================================================================

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("✍️ AI Content Studio")
    st.markdown("*Multi-agent AI system for automated content creation*")
    
    # Check backend
    if not check_backend_health():
        st.error(f"⚠️ Backend not accessible at {BACKEND_URL}")
        st.info("Make sure the FastAPI backend is running: `uvicorn backend.main:app --reload`")
        return
    
    # Sidebar - Input Form
    with st.sidebar:
        st.header("📝 Create New Article")
        
        topic = st.text_input(
            "Topic *",
            placeholder="Enter article topic...",
            help="Main topic for your article"
        )
        
        tone = st.selectbox(
            "Tone",
            options=["professional", "casual", "technical", "friendly"],
            help="Writing style and voice"
        )
        
        audience = st.selectbox(
            "Target Audience",
            options=["general", "developers", "business", "students", "healthcare professionals"],
            help="Who will read this article?"
        )
        
        min_words = st.number_input(
            "Minimum Words",
            min_value=300,
            max_value=3000,
            value=800,
            step=100,
            help="Target article length"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            include_image = st.checkbox("Generate Image", value=True)
        with col2:
            seo_optimize = st.checkbox("SEO Optimize", value=True)
        
        st.markdown("---")
        
        # Generate button
        if st.button("🚀 Generate Article", type="primary", use_container_width=True):
            if not topic:
                st.error("Please enter a topic")
            else:
                with st.spinner("Creating article..."):
                    article = create_article(
                        topic=topic,
                        tone=tone,
                        target_audience=audience,
                        min_words=min_words,
                        include_image=include_image,
                        seo_optimize=seo_optimize
                    )
                    
                    if article:
                        st.session_state.current_article_id = article["id"]
                        st.session_state.article_status = "pending"
                        st.session_state.article_result = None
                        st.session_state.agent_logs = []
                        st.session_state.progress = 0
                        st.session_state.generation_complete = False
                        st.session_state.ws_messages = []
                        
                        st.success(f"✓ Article created (ID: {article['id']})")
                        
                        # Try to start WebSocket in background
                        try:
                            thread = threading.Thread(
                                target=start_websocket,
                                args=(article["id"],),
                                daemon=True
                            )
                            thread.start()
                        except:
                            pass  # Will fall back to polling
                        
                        st.rerun()
        
        st.markdown("---")
        
        # History section
        st.header("📚 Recent Articles")
        articles = list_articles(limit=5)
        
        if articles:
            for article in articles:
                with st.expander(f"📄 {article['topic'][:30]}..."):
                    st.write(f"**ID:** {article['id']}")
                    st.write(f"**Status:** {article['status']}")
                    st.write(f"**Created:** {article['created_at'][:16]}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View", key=f"view_{article['id']}"):
                            st.session_state.current_article_id = article['id']
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"del_{article['id']}"):
                            if delete_article(article['id']):
                                st.success("Deleted!")
                                st.rerun()
        else:
            st.info("No articles yet")
    
    # Main content area
    if st.session_state.current_article_id:
        article_id = st.session_state.current_article_id
        
        # Get current status
        status_data = get_article_status(article_id)
        
        if status_data:
            current_status = status_data["status"]
            
            # Status banner
            if current_status == "pending":
                st.info("⏳ Article queued for generation...")
            elif current_status == "processing":
                st.warning(f"⚙️ Generating article... {status_data.get('message', '')}")
            elif current_status == "completed":
                st.success("✅ Article generation completed!")
            elif current_status == "failed":
                st.error("❌ Article generation failed")
            
            # Show agent timeline if processing or completed
            if current_status in ["processing", "completed"]:
                st.subheader("🔄 Generation Progress")
                
                # Get article to check for agent_logs
                try:
                    article_data = requests.get(f"{BACKEND_URL}/articles/{article_id}").json()
                    if article_data.get("agent_logs"):
                        render_agent_timeline(article_data["agent_logs"], current_status)
                except:
                    pass
            
            # If completed, show content
            if current_status == "completed":
                result = get_article_result(article_id)
                
                if result:
                    st.session_state.article_result = result
                    
                    # Content tabs
                    st.subheader("📊 Generated Content")
                    render_content_tabs(result)
                    
                    st.markdown("---")
                    
                    # Export section
                    render_export_section(result)
            
            # If processing, auto-refresh
            elif current_status == "processing":
                time.sleep(2)
                st.rerun()
    
    else:
        # Welcome screen
        st.markdown("""
        ## Welcome to AI Content Studio! 👋
        
        **Get started:**
        1. Enter a topic in the sidebar
        2. Choose your preferences (tone, audience, length)
        3. Click "Generate Article"
        4. Watch as AI agents collaborate to create your content
        
        **Features:**
        - 🤖 Multi-agent workflow (Research → Outline → Write → Edit → SEO → Image)
        - ⚡ Real-time progress tracking
        - 📊 SEO optimization
        - 🎨 AI-generated cover images
        - 💾 Export to MD, HTML, PDF
        
        **Tech Stack:**
        - LangGraph workflow orchestration
        - GPT-4 content generation
        - Tavily web research
        - DALL-E 3 image generation
        """)
        
        # Sample topics
        st.subheader("💡 Sample Topics")
        cols = st.columns(3)
        
        samples = [
            "The Future of Artificial Intelligence",
            "Sustainable Energy Solutions",
            "Mental Health in the Digital Age",
            "Blockchain Technology Explained",
            "The Science of Productivity",
            "Climate Change and Innovation"
        ]
        
        for idx, sample in enumerate(samples):
            with cols[idx % 3]:
                if st.button(sample, use_container_width=True):
                    st.session_state.sample_topic = sample
                    st.rerun()


if __name__ == "__main__":
    main()

