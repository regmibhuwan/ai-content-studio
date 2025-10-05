"""
REST API Routes for AI Content Studio

Provides endpoints for article creation, retrieval, and management.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.database import Article, get_db
from backend.schemas import ArticleCreateRequest, ArticleResponse, ArticleStatusResponse
from backend.core.orchestrator import orchestrator
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/create", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article_endpoint(
    request: ArticleCreateRequest,
    db: AsyncSession = Depends(get_db)
) -> ArticleResponse:
    """
    Create a new article and start async generation workflow.

    This endpoint:
    1. Creates a database record with 'pending' status
    2. Starts background task for article generation
    3. Returns immediately with article ID for status checking

    Args:
        request: Article creation parameters
        db: Database session

    Returns:
        ArticleResponse: Created article with pending status

    Example:
        POST /articles/create
        {
            "topic": "AI in Healthcare",
            "tone": "professional",
            "target_audience": "healthcare professionals",
            "min_words": 1000,
            "include_image": true,
            "seo_optimize": true
        }
    """
    logger.info(f"Creating article: {request.topic}")

    # Create database record
    article = Article(
        topic=request.topic,
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(article)
    await db.commit()
    await db.refresh(article)

    logger.info(f"Article {article.id} created in database")

    # Start background task
    orchestrator.start_article_creation(
        article_id=article.id,
        topic=request.topic,
        tone=request.tone,
        target_audience=request.target_audience,
        min_words=request.min_words,
        include_image=request.include_image,
        seo_optimize=request.seo_optimize,
    )

    logger.info(f"Background task started for article {article.id}")

    return ArticleResponse.model_validate(article)


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
) -> ArticleResponse:
    """
    Get article by ID with current status and results.

    Args:
        article_id: Article ID
        db: Database session

    Returns:
        ArticleResponse: Article data with current status

    Raises:
        HTTPException: If article not found
    """
    stmt = select(Article).where(Article.id == article_id)
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()

    if not article:
        logger.warning(f"Article {article_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )

    return ArticleResponse.model_validate(article)


@router.get("/{article_id}/status", response_model=ArticleStatusResponse)
async def get_article_status(
    article_id: int,
    db: AsyncSession = Depends(get_db)
) -> ArticleStatusResponse:
    """
    Get article generation status and progress.

    Args:
        article_id: Article ID
        db: Database session

    Returns:
        ArticleStatusResponse: Current status with progress info

    Raises:
        HTTPException: If article not found
    """
    stmt = select(Article).where(Article.id == article_id)
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )

    # Calculate progress percentage
    status_map = {
        "pending": 0,
        "processing": 50,
        "completed": 100,
        "failed": 100,
        "cancelled": 100,
    }

    progress = status_map.get(article.status, 0)

    # Get current agent from logs
    current_agent = None
    if article.agent_logs:
        # Find the last agent that's not completed
        for log in reversed(article.agent_logs):
            if log.get("status") not in ["success", "skipped", "error"]:
                current_agent = log.get("agent")
                break
        # If all completed, get the last one
        if not current_agent and article.agent_logs:
            current_agent = article.agent_logs[-1].get("agent")

    # Create status message
    if article.status == "pending":
        message = "Article queued for generation"
    elif article.status == "processing":
        message = f"Generating article... Current agent: {current_agent or 'Starting'}"
    elif article.status == "completed":
        message = "Article generation completed successfully"
    elif article.status == "failed":
        message = "Article generation failed"
    elif article.status == "cancelled":
        message = "Article generation was cancelled"
    else:
        message = f"Status: {article.status}"

    return ArticleStatusResponse(
        id=article.id,
        status=article.status,
        current_agent=current_agent,
        progress_percentage=progress,
        message=message,
    )


@router.get("/{article_id}/result")
async def get_article_result(
    article_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get final article result (content, SEO, image).

    Args:
        article_id: Article ID
        db: Database session

    Returns:
        dict: Article content and metadata

    Raises:
        HTTPException: If article not found or not completed
    """
    stmt = select(Article).where(Article.id == article_id)
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )

    if article.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Article is not completed yet. Current status: {article.status}"
        )

    return {
        "id": article.id,
        "topic": article.topic,
        "content": article.content,
        "outline": article.outline,
        "seo_meta": article.seo_meta,
        "image_url": article.image_url,
        "research_data": article.research_data,
        "created_at": article.created_at,
        "completed_at": article.completed_at,
    }


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete an article by ID.

    Args:
        article_id: Article ID
        db: Database session

    Raises:
        HTTPException: If article not found
    """
    # Check if article exists
    stmt = select(Article).where(Article.id == article_id)
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )

    # Cancel task if running
    await orchestrator.cancel_task(article_id)

    # Delete from database
    delete_stmt = delete(Article).where(Article.id == article_id)
    await db.execute(delete_stmt)
    await db.commit()

    logger.info(f"Article {article_id} deleted")


@router.get("/", response_model=List[ArticleResponse])
async def list_articles(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
) -> List[ArticleResponse]:
    """
    List all articles with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[ArticleResponse]: List of articles
    """
    stmt = (
        select(Article)
        .order_by(Article.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()

    return [ArticleResponse.model_validate(article) for article in articles]


@router.get("/active/tasks")
async def get_active_tasks() -> dict:
    """
    Get all currently running article generation tasks.

    Returns:
        dict: Active tasks with their status
    """
    active_tasks = orchestrator.get_active_tasks()
    return {
        "active_count": len(active_tasks),
        "tasks": active_tasks
    }

