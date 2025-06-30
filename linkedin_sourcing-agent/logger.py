"""
Logger Module
============

Provides centralized logging functionality for the AI Sourcing Agent.
"""

import logging
import sys
from pathlib import Path
from loguru import logger
from typing import Optional

def setup_logger(
    level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: int = 10
) -> logger:
    """
    Setup and configure the application logger

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        rotation: Log file rotation size
        retention: Number of log files to retain

    Returns:
        Configured logger instance
    """

    # Remove default handler
    logger.remove()

    # Add console handler with custom format
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=rotation,
            retention=retention,
            compression="zip"
        )

    return logger

def get_logger(name: str) -> logger:
    """Get a logger instance for a specific module"""
    return logger.bind(name=name)
