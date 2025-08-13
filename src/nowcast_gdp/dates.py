from __future__ import annotations

from datetime import date, timedelta

__all__ = ["week_ending", "quarter_start", "quarter_end"]


def week_ending(d: date) -> date:
    """Return the Saturday of the week containing ``d`` (ISO weeks: Mon–Sun)."""
    return d + timedelta(days=(6 - d.isoweekday()) % 7)


def quarter_start(d: date) -> date:
    start_month = 1 + 3 * ((d.month - 1) // 3)
    return date(d.year, start_month, 1)


def quarter_end(d: date) -> date:
    start_month = 1 + 3 * ((d.month - 1) // 3)
    if start_month == 10:
        next_q_start = date(d.year + 1, 1, 1)
    else:
        next_q_start = date(d.year, start_month + 3, 1)
    return next_q_start - timedelta(days=1)
