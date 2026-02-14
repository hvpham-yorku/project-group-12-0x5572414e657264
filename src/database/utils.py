"""
Type-safe conversion helpers used when moving data between
Peewee table rows and the application dataclass models.
"""

from typing import Optional
from datetime import datetime


def safe_int(value, default: int = -1) -> int:
    """Convert a value to int, returning *default* on None or failure."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    """Convert a value to float, returning *default* on None or failure."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_str(value, default: str = "") -> str:
    """Convert a value to str, returning *default* on None."""
    if value is None:
        return default
    return str(value)


def safe_datetime(value) -> Optional[datetime]:
    """Convert a value to datetime.

    Handles:
    - None          -> None
    - datetime      -> pass-through
    - str (ISO fmt) -> parsed datetime
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None
