# bodystate/core/models.py

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class HormonalEngineInput:
    engine_version: str
    hrv_percent_daily: List[float]
    sleep_duration_minutes_daily: List[float]
    weight_kg_daily: List[float]
    recovery_index_daily: List[float]
    volatility_window_days: int = 14
    baseline_window_days: int = 56


@dataclass(frozen=True)
class HormonalVolatilityOutput:
    engine_version: str
    hvi_score: float
    tier: str
    trend_window_days: int
    threshold_multiplier: float
    drift_speed_modifier: float
    component_scores: dict


@dataclass(frozen=True)
class ResilienceOutput:
    engine_version: str
    short_term_score: float
    long_term_score: float
    final_score: float
    tier: str
    multiplier: float
    explainability: dict

@dataclass(frozen=True)
class GuardianInput:
    engine_version: str

    metabolic_30d_risk: float
    sleep_debt_score: float
    recovery_index: float
    stress_metabolism_score: float
    overtraining_risk: float

    risk_score_7d_slope: float
    sleep_7d_slope: float
    recovery_7d_slope: float
    hrv_7d_slope: float

    hormonal_threshold_multiplier: float
    hormonal_drift_modifier: float
    volatility_index: float

    adaptive_baseline_shift_percent: float

    resilience_multiplier: float
    resilience_final_score: float

    safety_metabolic_slowdown: bool
    safety_extreme_sleep_debt: bool
    safety_recovery_collapse: bool


@dataclass(frozen=True)
class GuardianOutput:
    engine_version: str
    risk_score: float
    stability_state: str
    guardian_mode: str
    forecast_7d_risk: float
    resilience_score: float
    thresholds_applied: Dict
    drift_modifier_final: float
    safety_override_triggered: bool
    explainability: Dict