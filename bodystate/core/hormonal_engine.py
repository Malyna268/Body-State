# bodystate/core/hormonal_engine.py

import numpy as np
from .models import HormonalEngineInput, HormonalVolatilityOutput
from .rolling import rolling_std, rolling_mean, rolling_range, clamp


class HormonalEngine:
    VERSION = "1.3"

    @staticmethod
    def compute(input_data: HormonalEngineInput) -> HormonalVolatilityOutput:
        window = input_data.volatility_window_days

        hrv = np.array(input_data.hrv_percent_daily, dtype=float)
        sleep = np.array(input_data.sleep_duration_minutes_daily, dtype=float)
        weight = np.array(input_data.weight_kg_daily, dtype=float)
        recovery = np.array(input_data.recovery_index_daily, dtype=float)

        # --- HRV Volatility Score ---
        hrv_std = rolling_std(hrv, window)

        if hrv_std <= 3:
            hvs = 0
        elif hrv_std <= 8:
            hvs = (hrv_std - 3) / 5 * 70
        elif hrv_std <= 15:
            hvs = 70 + (hrv_std - 8) / 7 * 30
        else:
            hvs = 100

        hvs = clamp(hvs, 0, 100)

        # --- Sleep Debt Calculation ---
        sleep_7d_mean = rolling_mean(sleep, 7)
        sleep_debt = max(0.0, 480 - sleep_7d_mean)

        sleep_std = rolling_std(sleep, window)
        sleep_mean = rolling_mean(sleep, window)

        sleep_cv = sleep_std / (sleep_mean + 20.0)

        if sleep_cv <= 0.10:
            sis = 0
        elif sleep_cv <= 0.25:
            sis = (sleep_cv - 0.10) / 0.15 * 70
        elif sleep_cv <= 0.40:
            sis = 70 + (sleep_cv - 0.25) / 0.15 * 30
        else:
            sis = 100

        # Chronic debt penalty
        if sleep_debt < 30:
            penalty = 0
        elif sleep_debt < 60:
            penalty = 10
        elif sleep_debt < 120:
            penalty = 20
        else:
            penalty = 30

        sis = clamp(sis + penalty, 0, 100)

        # --- Weight Oscillation ---
        weight_range = rolling_range(weight, 7)

        if weight_range <= 0.4:
            wros = 0
        elif weight_range <= 1.2:
            wros = (weight_range - 0.4) / 0.8 * 70
        elif weight_range <= 2.0:
            wros = 70 + (weight_range - 1.2) / 0.8 * 30
        else:
            wros = 100

        wros = clamp(wros, 0, 100)

        # --- Recovery Volatility ---
        rec_std = rolling_std(recovery, window)

        if rec_std <= 5:
            rsv = 0
        elif rec_std <= 12:
            rsv = (rec_std - 5) / 7 * 80
        else:
            rsv = 100

        rsv = clamp(rsv, 0, 100)

        # --- Final HVI ---
        hvi = (
            0.35 * hvs +
            0.25 * sis +
            0.20 * wros +
            0.20 * rsv
        )

        hvi = clamp(hvi, 0, 100)

        # Tier logic
        if hvi <= 25:
            tier = "STABLE"
            multiplier = 1.00
            drift_modifier = 1.00
            trend_window = 7
        elif hvi <= 50:
            tier = "MILD"
            multiplier = 0.95
            drift_modifier = 0.95
            trend_window = 10
        elif hvi <= 75:
            tier = "HIGH"
            multiplier = 0.88
            drift_modifier = 0.88
            trend_window = 14
        else:
            tier = "SEVERE"
            multiplier = 0.80
            drift_modifier = 0.80
            trend_window = 21

        return HormonalVolatilityOutput(
            engine_version=HormonalEngine.VERSION,
            hvi_score=round(hvi, 2),
            tier=tier,
            trend_window_days=trend_window,
            threshold_multiplier=multiplier,
            drift_speed_modifier=drift_modifier,
            component_scores={
                "hvs": round(hvs, 2),
                "sis": round(sis, 2),
                "wros": round(wros, 2),
                "rsv": round(rsv, 2)
            }
        )
