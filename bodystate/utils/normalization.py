"""Normalization helpers."""

from __future__ import annotations


def min_max_scale(value: float, min_val: float, max_val: float) -> float:
    """Scale a value to [0,1] based on provided bounds."""
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)
