# src/nowcast_gdp/baselines/bl0.py
from __future__ import annotations

from typing import List, Sequence


def forecast_last(y: Sequence[float], h: int = 1) -> List[float]:
    """
    BL-0 carry-forward baseline:
    Return an h-step forecast where every horizon equals the last observed value.
    Raises ValueError if y is empty or h < 1.
    """
    if h < 1:
        raise ValueError("h must be >= 1")
    if not y:
        raise ValueError("y must be non-empty")
    last = y[-1]
    return [float(last)] * h
