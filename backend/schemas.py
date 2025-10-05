"""
Pydantic models for API request/response validation.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


class ArticleCreateRequest(BaseModel):
    """Request model for creating a new article."""

    topic: str = Field(..., min_length=5, max_length=500, description="Article topic")
    tone: str = Field(
        default="professional",
        description="Writing tone (professional, casual, technical, friendly)",
    )
    target_audience: str = Field(
        default="general",
        description="Target audience (general, developers, business, students)",
    )
    min_words: int = Field(default=800, ge=300, le=5000, description="Minimum word count")
    include_image: bool = Field(default=True, description="Generate cover image")
    seo_optimize: bool = Field(default=True, description="Apply SEO optimization")


class ArticleResponse(BaseModel):
    """Response model for article data."""

    id: int
    topic: str
    outline: Optional[str] = None
    content: Optional[str] = None
    seo_meta: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    status: str
    research_data: Optional[Dict[str, Any]] = None
    agent_logs: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ArticleStatusResponse(BaseModel):
    """Response model for article status check."""

    id: int
    status: str
    current_agent: Optional[str] = None
    progress_percentage: int
    message: str


class AgentUpdate(BaseModel):
    """Real-time agent execution update."""

    agent_name: str
    status: str  # started, completed, failed
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[Dict[str, Any]] = None

