"""
Logging configuration for Schedule DND.

Author: DmitrTRC
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from schedule_dnd.infrastructure.config.settings import get_settings


def setup_logging(log_file: Optional[Path] = None) -> None:
    """
    Configure logging for the application.

    Args:
        log_file: Optional path to log file. If None, uses default from settings.
    """
    settings = get_settings()

    # Determine log level
    if settings.debug:
        log_level = logging.DEBUG
        log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    else:
        log_level = logging.INFO
        log_format = "%(asctime)s | %(levelname)-8s | %(message)s"

    # Create formatter
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler (only if debug or errors)
    if settings.debug:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file is None:
        log_file = settings.log_file

    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # Always log everything to file
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Log startup info
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Schedule DND Application Started")
    logger.info(f"Log Level: {logging.getLevelName(log_level)}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Log File: {log_file}")
    logger.info(f"Data Directory: {settings.data_dir}")
    logger.info(f"Output Directory: {settings.output_dir}")
    logger.info("=" * 70)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
