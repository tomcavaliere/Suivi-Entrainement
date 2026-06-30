"""
Fonctions pures de physiologie / charge d'entraînement — sans I/O, sans Streamlit.
"""

import math

import numpy as np
import pandas as pd
from datetime import date


def bmr_mifflin(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "Homme" else base - 161


MET_TABLE = {
    ("Trail",    "Zone 2"):          8.0,
    ("Trail",    "Fractionné/PMA"): 11.0,
    ("Vélo",     "Zone 2"):          6.5,
    ("Vélo",     "Fractionné/PMA"):  9.5,
    ("Athlé",    "Zone 2"):          7.0,
    ("Athlé",    "Fractionné/PMA"): 10.5,
    ("Natation", "Zone 2"):          6.0,
    ("Natation", "Fractionné/PMA"):  8.5,
}


def training_kcal_estimate(weight_kg, sport, intensity, duration_min, elevation_m):
    met = MET_TABLE.get((sport, intensity), 7.0)
    base = met * weight_kg * (duration_min / 60)
    if elevation_m > 0:
        base += 0.5 * weight_kg * (elevation_m / 100)
    return round(base)


def workout_kcal(row, weight_kg: float) -> float:
    if pd.notna(row.kcal_actual) and row.kcal_actual:
        return float(row.kcal_actual)
    return training_kcal_estimate(weight_kg, row.type, row.intensity,
                                  row.duration_min, row.elevation_m)


def _assign_zone(hr: float, bounds: list) -> int:
    if   hr <= bounds[0]: return 0
    elif hr <= bounds[1]: return 1
    elif hr <= bounds[2]: return 2
    elif hr <= bounds[3]: return 3
    else:                 return 4


_ZONE_CARB_RATE = [0.2, 0.4, 0.65, 0.9, 1.1]  # g glycogen/min burned per zone


def compute_carb_adjustment(wks_df: pd.DataFrame) -> int:
    """Extra carbs (g) to replenish glycogen from today's training zones."""
    if wks_df.empty:
        return 0
    extra = 0.0
    for _, w in wks_df.iterrows():
        for rate, col in zip(_ZONE_CARB_RATE,
                             ["hr_z1_min", "hr_z2_min", "hr_z3_min", "hr_z4_min", "hr_z5_min"]):
            val = getattr(w, col, 0) or 0
            extra += rate * float(val)
    return round(extra)


def compute_srpe(rpe, duration_min):
    if rpe is None:
        return None
    return float(rpe) * float(duration_min)


def compute_trimp(duration_min, avg_hr, hr_repos, hr_max):
    if avg_hr is None:
        return None
    hr_range = float(hr_max) - float(hr_repos)
    if hr_range <= 0:
        return None
    delta = (float(avg_hr) - float(hr_repos)) / hr_range
    if delta <= 0:
        return None
    return float(duration_min) * delta * 0.64 * math.exp(1.92 * delta)


def compute_weekly_monotony_strain(daily_df: pd.DataFrame, weeks: int = 12) -> pd.DataFrame:
    """Monotony and strain per calendar week for the last `weeks` weeks."""
    if daily_df.empty:
        return pd.DataFrame(columns=["week_start", "load_sum", "monotony", "strain"])

    today   = pd.Timestamp(date.today())
    monday  = today - pd.Timedelta(days=today.weekday())
    records = []
    for w in range(weeks - 1, -1, -1):
        w_start  = monday - pd.Timedelta(weeks=w)
        w_end    = w_start + pd.Timedelta(days=6)
        mask     = (daily_df["date"] >= w_start) & (daily_df["date"] <= w_end)
        charges  = daily_df.loc[mask, "srpe"].fillna(0.0).values
        if len(charges) == 0:
            charges = np.zeros(7)
        mean_c   = float(np.mean(charges))
        std_c    = float(np.std(charges))
        monotony = mean_c / std_c if std_c > 1e-6 else 1.0
        load_sum = float(np.sum(charges))
        records.append({
            "week_start": w_start.strftime("%d/%m"),
            "load_sum":   round(load_sum, 1),
            "monotony":   round(monotony, 2),
            "strain":     round(load_sum * monotony, 1),
        })
    return pd.DataFrame(records)


def _hrv_eval_readiness(v: float):
    if v >= 80:  return ("Élevé",    "#3498db")
    if v >= 50:  return ("Normal",   "#2ecc71")
    if v >= 30:  return ("Bas",      "#f39c12")
    return           ("Très bas",  "#e74c3c")

def _hrv_eval_rmssd(v: float):
    if v > 75:   return ("Excellent", "#3498db")
    if v >= 50:  return ("Bon",       "#2ecc71")
    if v >= 19:  return ("Normal",    "#f39c12")
    return           ("Faible",    "#e74c3c")

def _hrv_eval_pns(v: float):
    if v > 1:    return ("Élevé",  "#3498db")
    if v >= -1:  return ("Normal", "#2ecc71")
    return           ("Faible", "#e74c3c")

def _hrv_eval_sns(v: float):
    if v > 1:    return ("Élevé", "#e74c3c")
    if v >= -1:  return ("Normal", "#2ecc71")
    return           ("Bas",    "#3498db")

def _hrv_eval_hr(v: int):
    if v < 40:   return ("Très bas",  "#9b59b6")
    if v <= 60:  return ("Athlète",   "#2ecc71")
    if v <= 77:  return ("Normal",    "#f39c12")
    return           ("Élevé",    "#e74c3c")

def _hrv_eval_sleep_h(v: float):
    if 7.0 <= v <= 9.0:  return ("Optimal",     "#2ecc71")
    if v >= 6.0:         return ("Insuffisant",  "#f39c12")
    if v > 9.0:          return ("Prolongé",     "#3498db")
    return                    ("Trop court",  "#e74c3c")
