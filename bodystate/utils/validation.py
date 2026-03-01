"""Validation utilities for common checks."""

from __future__ import annotations


def is_positive_number(val: float) -> bool:
    """Return True if val is a positive finite number."""
    try:
        return val > 0 and val != float("inf") and val == val
    except Exception:
        return False
