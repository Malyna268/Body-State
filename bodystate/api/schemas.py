# bodystate/api/schemas.py

from pydantic import BaseModel, Field
from typing import List


class EngineRequest(BaseModel):
    hrv_percent_daily: List[float]
    sleep_duration_minutes_daily: List[float]
    sleep_debt_minutes_daily: List[float]
    weight_kg_daily: List[float]
    recovery_index_daily: List[float]
    stress_score_daily: List[float]

    metabolic_30d_risk: float = Field(ge=0, le=100)
    sleep_debt_score: float = Field(ge=0, le=100)
    recovery_index: float = Field(ge=0, le=100)
    stress_metabolism_score: float = Field(ge=0, le=100)
    overtraining_risk: float = Field(ge=0, le=100)

    risk_score_7d_slope: float
    sleep_7d_slope: float
    recovery_7d_slope: float
    hrv_7d_slope: float

    adaptive_baseline_shift_percent: float = 0

    safety_metabolic_slowdown: bool = False
    safety_extreme_sleep_debt: bool = False
    safety_recovery_collapse: bool = False
    