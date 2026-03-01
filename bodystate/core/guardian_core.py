# bodystate/core/guardian_core.py

import numpy as np
from .rolling import clamp
from .models import GuardianInput, GuardianOutput


class GuardianCore:
    VERSION = "2.3"

    BASE_YELLOW = 40
    BASE_ORANGE = 55
    BASE_RED = 70

    @staticmethod
    def compute(input_data: GuardianInput) -> GuardianOutput:

        # --- 1️⃣ Base Risk Score ---
        brs = (
            0.30 * input_data.metabolic_30d_risk +
            0.20 * input_data.sleep_debt_score +
            0.20 * (100 - input_data.recovery_index) +
            0.15 * input_data.stress_metabolism_score +
            0.15 * input_data.overtraining_risk
        )

        # --- 2️⃣ Adaptive Adjustment ---
        adaptive_multiplier = 1 + (input_data.adaptive_baseline_shift_percent / 100.0)
        adjusted_score = brs * adaptive_multiplier
        adjusted_score = clamp(adjusted_score, 0, 100)

        # --- 3️⃣ Threshold Adjustments (Hormonal + Resilience) ---
        combined_multiplier = (
            input_data.hormonal_threshold_multiplier *
            input_data.resilience_multiplier
        )

        combined_multiplier = clamp(combined_multiplier, 0.75, 1.10)

        yellow_thr = GuardianCore.BASE_YELLOW * combined_multiplier
        orange_thr = GuardianCore.BASE_ORANGE * combined_multiplier
        red_thr = GuardianCore.BASE_RED * combined_multiplier

        # --- 4️⃣ Drift Modifier ---
        resilience_pressure = (50 - input_data.resilience_final_score) / 200.0
        drift_modifier = (
            input_data.hormonal_drift_modifier *
            (1 + resilience_pressure)
        )

        drift_modifier = clamp(drift_modifier, 0.8, 1.2)

        # --- 5️⃣ Forecast Engine (Deterministic) ---
        predictive_delta = (
            0.4 * input_data.risk_score_7d_slope +
            0.2 * input_data.sleep_7d_slope -
            0.2 * input_data.recovery_7d_slope -
            0.2 * input_data.hrv_7d_slope
        )

        forecast_7d = adjusted_score + (predictive_delta * drift_modifier)
        forecast_7d = clamp(forecast_7d, 0, 100)

        # --- 6️⃣ Stability State ---
        if adjusted_score >= red_thr:
            state = "CRITICAL DRIFT"
            mode = "RED"
        elif adjusted_score >= orange_thr:
            state = "UNSTABLE"
            mode = "ORANGE"
        elif adjusted_score >= yellow_thr:
            state = "WATCH"
            mode = "YELLOW"
        else:
            state = "STABLE"
            mode = "GREEN"

        # --- 7️⃣ Safety Override ---
        safety_triggered = (
            input_data.safety_metabolic_slowdown or
            input_data.safety_extreme_sleep_debt or
            input_data.safety_recovery_collapse
        )

        if safety_triggered:
            state = "CRITICAL DRIFT"
            mode = "RED"

        return GuardianOutput(
            engine_version=GuardianCore.VERSION,
            risk_score=round(adjusted_score, 2),
            stability_state=state,
            guardian_mode=mode,
            forecast_7d_risk=round(forecast_7d, 2),
            resilience_score=input_data.resilience_final_score,
            thresholds_applied={
                "base_yellow": GuardianCore.BASE_YELLOW,
                "base_orange": GuardianCore.BASE_ORANGE,
                "base_red": GuardianCore.BASE_RED,
                "combined_multiplier": round(combined_multiplier, 3),
                "yellow_threshold": round(yellow_thr, 2),
                "orange_threshold": round(orange_thr, 2),
                "red_threshold": round(red_thr, 2),
            },
            drift_modifier_final=round(drift_modifier, 3),
            safety_override_triggered=safety_triggered,
            explainability={
                "base_risk_score": round(brs, 2),
                "adaptive_multiplier": round(adaptive_multiplier, 3),
                "predictive_delta": round(predictive_delta, 2),
                "volatility_index": input_data.volatility_index,
                "resilience_score": input_data.resilience_final_score,
            }
        )
