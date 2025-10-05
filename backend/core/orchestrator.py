"""
Async Background Task Orchestrator

Manages asynchronous article generation workflows with real-time progress tracking.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.database import Article, async_session_maker
from backend.agents.workflow import create_article
from utils.logger import get_logger

logger = get_logger(__name__)


class ArticleOrchestrator:
    """
    Orchestrates article creation workflows with background task management.
    
    Handles:
    - Async workflow execution
    - Progress tracking
    - Database persistence
    - Real-time update callbacks
    """

    def __init__(self):
        """Initialize orchestrator with task tracking."""
        self.active_tasks: Dict[int, asyncio.Task] = {}
        self.progress_callbacks: Dict[int, list] = {}

    async def create_article_async(
        self,
        article_id: int,
        topic: str,
        tone: str = "professional",
        target_audience: str = "general",
        min_words: int = 800,
        include_image: bool = True,
        seo_optimize: bool = True,
    ) -> None:
        """
        Execute article creation workflow asynchronously.

        Args:
            article_id: Database article ID
            topic: Article topic
            tone: Writing tone
            target_audience: Target audience
            min_words: Minimum word count
            include_image: Whether to generate image
            seo_optimize: Whether to apply SEO
        """
        logger.info(f"Starting article creation for ID {article_id}: {topic}")

        try:
            # Update status to processing
            await self._update_article_status(article_id, "processing")

            # Execute workflow with progress tracking
            result = await create_article(
                topic=topic,
                tone=tone,
                target_audience=target_audience,
                min_words=min_words,
                include_image=include_image,
                seo_optimize=seo_optimize,
            )

            # Save results to database
            await self._save_article_results(article_id, result)

            # Mark as completed
            await self._update_article_status(article_id, "completed")

            logger.info(f"Article {article_id} completed successfully")

        except Exception as e:
            logger.error(f"Article {article_id} failed: {str(e)}")
            await self._update_article_status(article_id, "failed")
            
            # Save error details
            async with async_session_maker() as session:
                stmt = (
                    update(Article)
                    .where(Article.id == article_id)
                    .values(
                        agent_logs=[{
                            "agent": "Orchestrator",
                            "status": "error",
                            "message": str(e),
                            "timestamp": datetime.utcnow().isoformat()
                        }]
                    )
                )
                await session.execute(stmt)
                await session.commit()

        finally:
            # Remove from active tasks
            if article_id in self.active_tasks:
                del self.active_tasks[article_id]

    def start_article_creation(
        self,
        article_id: int,
        topic: str,
        **kwargs
    ) -> asyncio.Task:
        """
        Start article creation as a background task.

        Args:
            article_id: Database article ID
            topic: Article topic
            **kwargs: Additional arguments for create_article

        Returns:
            asyncio.Task: Background task handle
        """
        task = asyncio.create_task(
            self.create_article_async(article_id, topic, **kwargs)
        )
        
        self.active_tasks[article_id] = task
        logger.info(f"Background task started for article {article_id}")
        
        return task

    async def _update_article_status(
        self,
        article_id: int,
        status: str
    ) -> None:
        """
        Update article status in database.

        Args:
            article_id: Article ID
            status: New status
        """
        async with async_session_maker() as session:
            stmt = (
                update(Article)
                .where(Article.id == article_id)
                .values(
                    status=status,
                    updated_at=datetime.utcnow(),
                    completed_at=datetime.utcnow() if status == "completed" else None
                )
            )
            await session.execute(stmt)
            await session.commit()

    async def _save_article_results(
        self,
        article_id: int,
        result: Dict[str, Any]
    ) -> None:
        """
        Save workflow results to database.

        Args:
            article_id: Article ID
            result: Workflow result state
        """
        async with async_session_maker() as session:
            stmt = (
                update(Article)
                .where(Article.id == article_id)
                .values(
                    research_data=result.get("research_data"),
                    outline=result.get("outline"),
                    content=result.get("edited_content") or result.get("content"),
                    seo_meta=result.get("seo_meta"),
                    image_url=result.get("image_url"),
                    agent_logs=result.get("agent_logs", []),
                    updated_at=datetime.utcnow(),
                )
            )
            await session.execute(stmt)
            await session.commit()

    def get_active_tasks(self) -> Dict[int, str]:
        """
        Get all active article generation tasks.

        Returns:
            Dict mapping article IDs to task status
        """
        return {
            article_id: "running" if not task.done() else "done"
            for article_id, task in self.active_tasks.items()
        }

    async def cancel_task(self, article_id: int) -> bool:
        """
        Cancel an active article generation task.

        Args:
            article_id: Article ID

        Returns:
            bool: True if cancelled, False if not found
        """
        if article_id in self.active_tasks:
            task = self.active_tasks[article_id]
            task.cancel()
            await self._update_article_status(article_id, "cancelled")
            logger.info(f"Article {article_id} task cancelled")
            return True
        return False


# Global orchestrator instance
orchestrator = ArticleOrchestrator()

