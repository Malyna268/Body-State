# bodystate/core/rolling.py

import numpy as np


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def rolling_std(values: np.ndarray, window: int) -> float:
    if len(values) < window:
        raise ValueError("Not enough data for rolling window")
    return float(np.std(values[-window:]))


def rolling_mean(values: np.ndarray, window: int) -> float:
    if len(values) < window:
        raise ValueError("Not enough data for rolling window")
    return float(np.mean(values[-window:]))


def rolling_range(values: np.ndarray, window: int) -> float:
    if len(values) < window:
        raise ValueError("Not enough data for rolling window")
    subset = values[-window:]
    return float(np.max(subset) - np.min(subset))
