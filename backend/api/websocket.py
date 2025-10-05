"""
WebSocket Handler for Real-Time Article Generation Updates

Provides live progress streaming for article creation workflow.
"""

import asyncio
import json
from typing import Dict
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import Article, async_session_maker
from utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts.

    Handles:
    - Connection lifecycle
    - Message broadcasting
    - Progress updates
    """

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, article_id: int):
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            article_id: Article ID to monitor
        """
        await websocket.accept()
        
        if article_id not in self.active_connections:
            self.active_connections[article_id] = []
        
        self.active_connections[article_id].append(websocket)
        logger.info(f"WebSocket connected for article {article_id}")

    def disconnect(self, websocket: WebSocket, article_id: int):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            article_id: Article ID
        """
        if article_id in self.active_connections:
            if websocket in self.active_connections[article_id]:
                self.active_connections[article_id].remove(websocket)
            
            # Clean up empty lists
            if not self.active_connections[article_id]:
                del self.active_connections[article_id]
        
        logger.info(f"WebSocket disconnected for article {article_id}")

    async def broadcast(self, article_id: int, message: dict):
        """
        Broadcast message to all connections for an article.

        Args:
            article_id: Article ID
            message: Message dict to send
        """
        if article_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[article_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to WebSocket: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn, article_id)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to specific WebSocket.

        Args:
            message: Message dict
            websocket: Target WebSocket connection
        """
        await websocket.send_json(message)


# Global connection manager
manager = ConnectionManager()


async def websocket_article_progress(websocket: WebSocket, article_id: int):
    """
    WebSocket endpoint for article generation progress updates.

    Streams real-time updates as agents execute:
    - Agent start/completion
    - Progress percentage
    - Status changes
    - Error messages

    Args:
        websocket: WebSocket connection
        article_id: Article ID to monitor

    Usage:
        Connect to: ws://localhost:8000/ws/articles/{article_id}
        
        Receive messages like:
        {
            "type": "agent_update",
            "article_id": 1,
            "agent": "ResearchAgent",
            "status": "started",
            "message": "Searching web sources...",
            "progress": 10,
            "timestamp": "2024-01-01T12:00:00"
        }
    """
    await manager.connect(websocket, article_id)

    try:
        # Send initial status
        async with async_session_maker() as session:
            stmt = select(Article).where(Article.id == article_id)
            result = await session.execute(stmt)
            article = result.scalar_one_or_none()

            if not article:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": f"Article {article_id} not found"
                    },
                    websocket
                )
                return

            # Send initial status
            await manager.send_personal_message(
                {
                    "type": "status",
                    "article_id": article_id,
                    "status": article.status,
                    "message": f"Article status: {article.status}",
                    "timestamp": datetime.utcnow().isoformat()
                },
                websocket
            )

        # Poll for updates
        last_log_count = 0
        last_status = article.status if article else "unknown"

        while True:
            async with async_session_maker() as session:
                stmt = select(Article).where(Article.id == article_id)
                result = await session.execute(stmt)
                article = result.scalar_one_or_none()

                if not article:
                    break

                # Check for new agent logs
                current_logs = article.agent_logs or []
                if len(current_logs) > last_log_count:
                    # Send new logs
                    for log in current_logs[last_log_count:]:
                        await manager.broadcast(
                            article_id,
                            {
                                "type": "agent_update",
                                "article_id": article_id,
                                "agent": log.get("agent"),
                                "status": log.get("status"),
                                "message": log.get("message"),
                                "execution_time": log.get("execution_time"),
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
                    last_log_count = len(current_logs)

                # Check for status change
                if article.status != last_status:
                    await manager.broadcast(
                        article_id,
                        {
                            "type": "status_change",
                            "article_id": article_id,
                            "old_status": last_status,
                            "new_status": article.status,
                            "message": f"Status changed to {article.status}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    last_status = article.status

                # If completed or failed, send final message and close
                if article.status in ["completed", "failed", "cancelled"]:
                    await manager.broadcast(
                        article_id,
                        {
                            "type": "final",
                            "article_id": article_id,
                            "status": article.status,
                            "message": f"Article generation {article.status}",
                            "has_content": bool(article.content),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    break

            # Wait before next poll
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for article {article_id}")
    except Exception as e:
        logger.error(f"WebSocket error for article {article_id}: {e}")
        try:
            await manager.send_personal_message(
                {
                    "type": "error",
                    "message": f"WebSocket error: {str(e)}"
                },
                websocket
            )
        except:
            pass
    finally:
        manager.disconnect(websocket, article_id)

