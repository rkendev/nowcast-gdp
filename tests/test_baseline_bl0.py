# tests/test_baseline_bl0.py
from __future__ import annotations

import pytest

from nowcast_gdp.baselines.bl0 import forecast_last


def test_bl0_basic():
    y = [1.0, 2.0, 3.5]
    assert forecast_last(y, h=1) == [3.5]
    assert forecast_last(y, h=3) == [3.5, 3.5, 3.5]


def test_bl0_validations():
    with pytest.raises(ValueError):
        forecast_last([], h=1)
    with pytest.raises(ValueError):
        forecast_last([1.0], h=0)
