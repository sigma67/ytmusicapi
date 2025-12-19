"""Logging configuration for ytmusicapi.

Provides structured logging with configurable levels and optional debug output.
"""

import logging
import os

DEFAULT_LOG_LEVEL = logging.WARNING
_logger: logging.Logger | None = None


def get_logger(name: str = "ytmusicapi") -> logging.Logger:
    """Get or create a logger instance.

    Args:
        name: Logger name (default: "ytmusicapi")

    Returns:
        Configured logger instance
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        _configure_logger(_logger)
    return _logger


def _configure_logger(logger: logging.Logger) -> None:
    """Configure logger with appropriate handler and level."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    level_str = os.getenv("YTMUSIC_LOG_LEVEL", "").upper()
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    level = level_map.get(level_str, DEFAULT_LOG_LEVEL)

    if os.getenv("YTMUSIC_DEBUG", "").lower() in ("1", "true", "yes"):
        level = logging.DEBUG

    logger.setLevel(level)


def debug(message: str) -> None:
    """Log a debug message."""
    get_logger().debug(message)


def info(message: str) -> None:
    """Log an info message."""
    get_logger().info(message)


def warning(message: str) -> None:
    """Log a warning message."""
    get_logger().warning(message)


def error(message: str) -> None:
    """Log an error message."""
    get_logger().error(message)
