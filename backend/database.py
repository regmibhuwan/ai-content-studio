"""
Database models and setup using SQLAlchemy.

Manages article storage, drafts, and agent execution logs.
"""

import datetime
from typing import AsyncGenerator

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from backend.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug_mode,
    future=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


class Article(Base):
    """Article model for storing generated content."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False, index=True)
    
    # Content fields
    outline = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    seo_meta = Column(JSON, nullable=True)  # Keywords, description, title
    image_url = Column(String(500), nullable=True)
    
    # Metadata
    status = Column(
        String(50),
        default="pending",
        index=True,
    )  # pending, processing, completed, failed
    research_data = Column(JSON, nullable=True)  # Sources and research findings
    agent_logs = Column(JSON, nullable=True)  # Track agent execution
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, topic='{self.topic[:30]}...', status='{self.status}')>"


async def init_db() -> None:
    """Initialize database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

