"""
Structured logging configuration.

Provides consistent logging across the application.
"""

import logging
import sys
from typing import Optional

from backend.config import get_settings

settings = get_settings()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name or __name__)

    # Only configure if no handlers exist
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.log_level.upper()))

        # Console handler with formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, settings.log_level.upper()))

        # Format: timestamp - name - level - message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger

