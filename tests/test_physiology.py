import math
from datetime import date, timedelta

import pandas as pd
import pytest

from physiology import (
    bmr_mifflin,
    _assign_zone,
    compute_srpe,
    compute_trimp,
    compute_weekly_monotony_strain,
    compute_carb_adjustment,
)


def test_bmr_mifflin_homme():
    # base = 10*70 + 6.25*175 - 5*30 = 700 + 1093.75 - 150 = 1643.75 ; +5
    assert bmr_mifflin(70, 175, 30, "Homme") == pytest.approx(1648.75)


def test_bmr_mifflin_femme():
    # base = 10*60 + 6.25*165 - 5*25 = 600 + 1031.25 - 125 = 1506.25 ; -161
    assert bmr_mifflin(60, 165, 25, "Femme") == pytest.approx(1345.25)


@pytest.mark.parametrize("hr, expected_zone", [
    (120, 0),   # sous Z1
    (130, 0),   # exactement sur la borne basse (bounds[0])
    (131, 1),   # juste au-dessus
    (148, 1),   # exactement sur bounds[1]
    (149, 2),   # entre deux zones
    (163, 2),   # exactement sur bounds[2]
    (175, 3),   # exactement sur bounds[3]
    (176, 4),   # au-dessus de Z4
    (250, 4),   # bien au-dessus
])
def test_assign_zone_boundaries(hr, expected_zone):
    bounds = [130, 148, 163, 175]
    assert _assign_zone(hr, bounds) == expected_zone


def test_compute_srpe():
    assert compute_srpe(5, 60) == 300.0


def test_compute_srpe_none_rpe():
    assert compute_srpe(None, 60) is None


def test_compute_trimp_known_case():
    result = compute_trimp(60, 150, 50, 190)
    assert result == pytest.approx(108.09535934022335)


def test_compute_trimp_avg_hr_equals_hr_repos():
    # delta = 0 -> pas de charge
    assert compute_trimp(60, 50, 50, 190) is None


def test_compute_trimp_avg_hr_equals_hr_max():
    result = compute_trimp(60, 190, 50, 190)
    assert result == pytest.approx(261.92480522076477)


def test_compute_trimp_none_avg_hr():
    assert compute_trimp(60, None, 50, 190) is None


def test_compute_trimp_invalid_hr_range():
    assert compute_trimp(60, 150, 190, 190) is None


def test_compute_weekly_monotony_strain_constant_load():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    dates = [pd.Timestamp(monday) + pd.Timedelta(days=i) for i in range(7)]
    daily_df = pd.DataFrame({"date": dates, "srpe": [100.0] * 7})

    result = compute_weekly_monotony_strain(daily_df, weeks=1)

    assert len(result) == 1
    row = result.iloc[0]
    assert row["load_sum"] == pytest.approx(700.0)
    assert row["monotony"] == pytest.approx(1.0)
    assert row["strain"] == pytest.approx(700.0)


def test_compute_weekly_monotony_strain_varied_load():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    dates = [pd.Timestamp(monday) + pd.Timedelta(days=i) for i in range(7)]
    daily_df = pd.DataFrame({"date": dates, "srpe": [0, 0, 0, 0, 0, 0, 700.0]})

    result = compute_weekly_monotony_strain(daily_df, weeks=1)

    row = result.iloc[0]
    assert row["load_sum"] == pytest.approx(700.0)
    assert row["monotony"] == pytest.approx(0.41)
    assert row["strain"] == pytest.approx(285.8)


def test_compute_weekly_monotony_strain_empty():
    daily_df = pd.DataFrame(columns=["date", "srpe"])
    result = compute_weekly_monotony_strain(daily_df, weeks=1)
    assert result.empty


def test_compute_carb_adjustment_empty():
    wks_df = pd.DataFrame()
    assert compute_carb_adjustment(wks_df) == 0


def test_compute_carb_adjustment_single_zone():
    wks_df = pd.DataFrame([{
        "hr_z1_min": 10, "hr_z2_min": 0, "hr_z3_min": 0, "hr_z4_min": 0, "hr_z5_min": 0,
    }])
    # 10 * 0.2 = 2.0
    assert compute_carb_adjustment(wks_df) == 2


def test_compute_carb_adjustment_multiple_zones():
    wks_df = pd.DataFrame([{
        "hr_z1_min": 20, "hr_z2_min": 15, "hr_z3_min": 10, "hr_z4_min": 5, "hr_z5_min": 2,
    }])
    # 20*0.2 + 15*0.4 + 10*0.65 + 5*0.9 + 2*1.1 = 4 + 6 + 6.5 + 4.5 + 2.2 = 23.2
    assert compute_carb_adjustment(wks_df) == 23
