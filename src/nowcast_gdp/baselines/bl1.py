# src/nowcast_gdp/baselines/bl1.py
from __future__ import annotations

from typing import Iterable, List, Optional


def _last_non_none(values: Iterable[Optional[float]]) -> Optional[float]:
    last = None
    for v in values:
        if v is not None:
            last = v
    return last


def drift_forecast(
    values: List[Optional[float]],
    h: int,
    window: int = 4,
) -> List[float]:
    """
    BL-1 'drift' baseline: extrapolate by the average of the last `window` differences.
    - If <2 valid points → carry-forward.
    - Ignores trailing/inner None values when computing diffs (skips missing).
    - Returns h-step-ahead point forecasts (same units as input).

    Example:
      values = [100, 102, 103, 108], window=2
      diffs (last 2) = [1, 5] → avg = 3
      forecasts for h=3: [111, 114, 117]
    """
    # Collect the valid (index, value) pairs
    xv = [(i, v) for i, v in enumerate(values) if v is not None]
    if len(xv) < 2:
        # not enough info → carry-forward
        last = _last_non_none(values)
        return [last] * h if last is not None else [float("nan")] * h

    # Compute consecutive diffs using only valid neighbors
    diffs: List[float] = []
    for (i1, v1), (i2, v2) in zip(xv[:-1], xv[1:]):
        # If there are gaps, we still use (v2 - v1) over the gap (per-step "macro" drift)
        diffs.append(v2 - v1)

    if not diffs:
        last = _last_non_none(values)
        return [last] * h if last is not None else [float("nan")] * h

    use = diffs[-window:] if window > 0 else diffs
    avg = sum(use) / len(use)

    start = xv[-1][1]  # last observed value
    return [start + avg * i for i in range(1, h + 1)]
