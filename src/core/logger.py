"""Logging setup and management."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


_logger: Optional[logging.Logger] = None


def setup_logging(log_file: str = "logs/signspeak.log", level: str = "INFO") -> None:
    """
    Configure logging with console and file handlers.

    Args:
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global _logger

    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    _logger = logging.getLogger("signspeak")
    _logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    _logger.handlers.clear()

    # Console handler - INFO level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)

    # File handler - DEBUG level
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)

    # Add handlers
    _logger.addHandler(console_handler)
    _logger.addHandler(file_handler)


def get_logger(name: str = "signspeak") -> logging.Logger:
    """
    Get or create logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    global _logger

    if _logger is None:
        setup_logging()

    return logging.getLogger(name)
