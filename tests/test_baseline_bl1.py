# tests/test_baseline_bl1.py
from nowcast_gdp.baselines.bl1 import drift_forecast


def test_bl1_drift_simple_window2():
    values = [100.0, 102.0, 103.0, 108.0]  # diffs: [2, 1, 5]
    # window=2 → diffs [1, 5] → avg=3 → forecasts 111,114,117
    out = drift_forecast(values, h=3, window=2)
    assert out == [111.0, 114.0, 117.0]


def test_bl1_drift_handles_nans_and_short_series():
    # Missing values inside and at end
    values = [100.0, None, 101.0, None, 101.5]
    out = drift_forecast(values, h=2, window=3)
    # diffs from valid neighbors: [1.0, 0.5] → avg=0.75 → start=101.5 → [102.25, 103.0]
    assert [round(v, 2) for v in out] == [102.25, 103.0]


def test_bl1_falls_back_to_carry_forward_if_not_enough_points():
    assert drift_forecast([None, 10.0], h=2) == [10.0, 10.0]
    # no valid points → NaNs
    out = drift_forecast([None, None], h=2)
    assert len(out) == 2 and all(v != v for v in out)  # NaN check (v != v)
