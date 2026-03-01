# bodystate/core/resilience_engine.py

import numpy as np
from .rolling import rolling_std, rolling_mean, clamp
from .models import ResilienceOutput


class ResilienceEngine:
    VERSION = "1.0"

    @staticmethod
    def compute(
        volatility_index_14d: float,
        sleep_debt_daily: list,
        recovery_index_daily: list,
        stress_score_daily: list,
        baseline_window_days: int = 90,
        volatility_window_days: int = 14,
    ) -> ResilienceOutput:

        sleep = np.array(sleep_debt_daily, dtype=float)
        recovery = np.array(recovery_index_daily, dtype=float)
        stress = np.array(stress_score_daily, dtype=float)

        # --- Short-Term (14d) ---

        sleep_mean_14 = rolling_mean(sleep, volatility_window_days)
        recovery_mean_14 = rolling_mean(recovery, volatility_window_days)
        stress_mean_14 = rolling_mean(stress, volatility_window_days)

        recovery_deficit_14 = 100 - recovery_mean_14

        ri_st = (
            100
            - (0.4 * volatility_index_14d)
            - (0.3 * sleep_mean_14 / 2)  # scale sleep minutes to 0–100 approx
            - (0.2 * recovery_deficit_14)
            - (0.1 * stress_mean_14)
        )

        ri_st = clamp(ri_st, 0, 100)

        # --- Long-Term (90d baseline) ---

        sleep_std_90 = rolling_std(sleep, baseline_window_days)
        recovery_mean_90 = rolling_mean(recovery, baseline_window_days)

        baseline_sleep_instability = sleep_std_90 / 2  # scaling factor
        baseline_recovery_deficit = 100 - recovery_mean_90

        ri_lt = (
            100
            - (0.5 * volatility_index_14d)
            - (0.3 * baseline_sleep_instability)
            - (0.2 * baseline_recovery_deficit)
        )

        ri_lt = clamp(ri_lt, 0, 100)

        # --- Final Blend ---

        ri_final = (0.6 * ri_st) + (0.4 * ri_lt)
        ri_final = clamp(ri_final, 0, 100)

        # --- Tier Logic ---

        if ri_final >= 75:
            tier = "HIGH"
            multiplier = 1.05
        elif ri_final >= 50:
            tier = "MODERATE"
            multiplier = 1.00
        elif ri_final >= 35:
            tier = "LOW"
            multiplier = 0.95
        else:
            tier = "CRITICAL_LOW"
            multiplier = 0.90

        return ResilienceOutput(
            engine_version=ResilienceEngine.VERSION,
            short_term_score=round(ri_st, 2),
            long_term_score=round(ri_lt, 2),
            final_score=round(ri_final, 2),
            tier=tier,
            multiplier=multiplier,
            explainability={
                "volatility_index_used": volatility_index_14d,
                "sleep_mean_14d": round(sleep_mean_14, 2),
                "recovery_mean_14d": round(recovery_mean_14, 2),
                "stress_mean_14d": round(stress_mean_14, 2),
                "baseline_sleep_std_90d": round(sleep_std_90, 2),
                "baseline_recovery_mean_90d": round(recovery_mean_90, 2),
            }
        )