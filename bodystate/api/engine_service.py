# bodystate/api/engine_service.py

from dataclasses import asdict
from typing import Dict, Any

from bodystate.core.hormonal_engine import HormonalEngine
from bodystate.core.resilience_engine import ResilienceEngine
from bodystate.core.guardian_core import GuardianCore
from bodystate.core.models import (
    HormonalEngineInput,
    GuardianInput,
)


class EngineService:
    VERSION = "1.0"

    @staticmethod
    def run(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration entrypoint.
        Deterministic. Stateless. Pure compute.
        """

        # -------------------------------
        # 1️⃣ Hormonal Engine (HVI)
        # -------------------------------

        hormonal_input = HormonalEngineInput(
            engine_version="1.3",
            hrv_percent_daily=payload["hrv_percent_daily"],
            sleep_duration_minutes_daily=payload["sleep_duration_minutes_daily"],
            weight_kg_daily=payload["weight_kg_daily"],
            recovery_index_daily=payload["recovery_index_daily"],
            volatility_window_days=payload.get("volatility_window_days", 14),
            baseline_window_days=payload.get("baseline_window_days", 56),
        )

        hormonal_output = HormonalEngine.compute(hormonal_input)

        # -------------------------------
        # 2️⃣ Resilience Engine
        # -------------------------------

        resilience_output = ResilienceEngine.compute(
            volatility_index_14d=hormonal_output.hvi_score,
            sleep_debt_daily=payload["sleep_debt_minutes_daily"],
            recovery_index_daily=payload["recovery_index_daily"],
            stress_score_daily=payload["stress_score_daily"],
            baseline_window_days=payload.get("baseline_window_days", 90),
            volatility_window_days=payload.get("volatility_window_days", 14),
        )

        # -------------------------------
        # 3️⃣ Guardian Core
        # -------------------------------

        guardian_input = GuardianInput(
            engine_version="2.3",

            metabolic_30d_risk=payload["metabolic_30d_risk"],
            sleep_debt_score=payload["sleep_debt_score"],
            recovery_index=payload["recovery_index"],
            stress_metabolism_score=payload["stress_metabolism_score"],
            overtraining_risk=payload["overtraining_risk"],

            risk_score_7d_slope=payload["risk_score_7d_slope"],
            sleep_7d_slope=payload["sleep_7d_slope"],
            recovery_7d_slope=payload["recovery_7d_slope"],
            hrv_7d_slope=payload["hrv_7d_slope"],

            hormonal_threshold_multiplier=hormonal_output.threshold_multiplier,
            hormonal_drift_modifier=hormonal_output.drift_speed_modifier,
            volatility_index=hormonal_output.hvi_score,

            adaptive_baseline_shift_percent=payload.get(
                "adaptive_baseline_shift_percent", 0
            ),

            resilience_multiplier=resilience_output.multiplier,
            resilience_final_score=resilience_output.final_score,

            safety_metabolic_slowdown=payload.get(
                "safety_metabolic_slowdown", False
            ),
            safety_extreme_sleep_debt=payload.get(
                "safety_extreme_sleep_debt", False
            ),
            safety_recovery_collapse=payload.get(
                "safety_recovery_collapse", False
            ),
        )

        guardian_output = GuardianCore.compute(guardian_input)

        # -------------------------------
        # 4️⃣ Unified Response
        # -------------------------------

        return {
            "engine_service_version": EngineService.VERSION,
            "hormonal": asdict(hormonal_output),
            "resilience": asdict(resilience_output),
            "guardian": asdict(guardian_output),
        }
