"""Configuration management for ytmusicapi.

This module provides centralized configuration with validation and environment variable support.
"""

import os
from typing import Final

from ytmusicapi.constants import SUPPORTED_LANGUAGES, SUPPORTED_LOCATIONS

# API Configuration
DEFAULT_TIMEOUT: Final[int] = 30
DEFAULT_RETRY_COUNT: Final[int] = 2
DEFAULT_RETRY_DELAY: Final[int] = 5

# Environment Variables
ENV_TIMEOUT: Final[str] = "YTMUSIC_TIMEOUT"
ENV_DEBUG: Final[str] = "YTMUSIC_DEBUG"
ENV_LOG_LEVEL: Final[str] = "YTMUSIC_LOG_LEVEL"


def get_timeout() -> int:
    """Get request timeout from environment or default."""
    timeout_str = os.getenv(ENV_TIMEOUT)
    if timeout_str:
        try:
            return int(timeout_str)
        except ValueError:
            pass
    return DEFAULT_TIMEOUT


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled via environment."""
    return os.getenv(ENV_DEBUG, "").lower() in ("1", "true", "yes")


def validate_language(language: str) -> None:
    """Validate language code against supported languages.

    Args:
        language: Language code to validate

    Raises:
        ValueError: If language is not supported
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported languages: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )


def validate_location(location: str) -> None:
    """Validate location code against supported locations.

    Args:
        location: Location code to validate

    Raises:
        ValueError: If location is not supported
    """
    if location and location not in SUPPORTED_LOCATIONS:
        raise ValueError(
            f"Unsupported location '{location}'. "
            f"Supported locations: {', '.join(sorted(SUPPORTED_LOCATIONS))}"
        )
