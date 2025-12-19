"""Input validation utilities for ytmusicapi.

Provides defensive validation for common input patterns to prevent errors early.
"""

from typing import Any, Optional


def require_non_empty(value: Optional[str], name: str) -> str:
    """Validate that a string value is not None or empty.

    Args:
        value: String value to validate
        name: Parameter name for error message

    Returns:
        The validated string value

    Raises:
        ValueError: If value is None or empty
    """
    if not value:
        raise ValueError(f"{name} cannot be None or empty")
    return value


def require_positive(value: int, name: str) -> int:
    """Validate that an integer value is positive.

    Args:
        value: Integer value to validate
        name: Parameter name for error message

    Returns:
        The validated integer value

    Raises:
        ValueError: If value is not positive
    """
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def require_non_negative(value: int, name: str) -> int:
    """Validate that an integer value is non-negative.

    Args:
        value: Integer value to validate
        name: Parameter name for error message

    Returns:
        The validated integer value

    Raises:
        ValueError: If value is negative
    """
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")
    return value


def require_type(value: Any, expected_type: type, name: str) -> Any:
    """Validate that a value is of the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type
        name: Parameter name for error message

    Returns:
        The validated value

    Raises:
        TypeError: If value is not of expected type
    """
    if not isinstance(value, expected_type):
        raise TypeError(
            f"{name} must be of type {expected_type.__name__}, got {type(value).__name__}"
        )
    return value


def require_in_range(value: int, min_val: int, max_val: int, name: str) -> int:
    """Validate that a value is within a specified range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        name: Parameter name for error message

    Returns:
        The validated value

    Raises:
        ValueError: If value is outside the range
    """
    if not min_val <= value <= max_val:
        raise ValueError(
            f"{name} must be between {min_val} and {max_val}, got {value}"
        )
    return value
