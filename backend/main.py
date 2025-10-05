"""
FastAPI Main Application for AI Content Studio

Entry point for the REST API and WebSocket server.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import router as articles_router
from backend.api.websocket import websocket_article_progress
from backend.database import init_db
from backend.config import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Handles:
    - Database initialization on startup
    - Cleanup on shutdown
    """
    # Startup
    logger.info("Starting AI Content Studio API...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Content Studio API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Multi-agent AI system for automated content creation with SEO optimization",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit default
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000",
        "*",  # Allow all in development (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(articles_router)


# WebSocket endpoint
@app.websocket("/ws/articles/{article_id}")
async def websocket_endpoint(websocket: WebSocket, article_id: int):
    """
    WebSocket endpoint for real-time article generation progress.

    Connect to: ws://localhost:8000/ws/articles/{article_id}

    Receives updates:
    - Agent execution progress
    - Status changes
    - Completion notifications
    """
    await websocket_article_progress(websocket, article_id)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API metadata and available endpoints
    """
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "articles": "/articles",
            "websocket": "/ws/articles/{id}",
        },
        "description": "Multi-agent AI content creation system",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "debug_mode": settings.debug_mode,
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Args:
        request: HTTP request
        exc: Exception

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.debug_mode else "An error occurred",
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower(),
    )

