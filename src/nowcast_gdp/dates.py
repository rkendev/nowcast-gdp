from datetime import date, timedelta

def week_ending(d: date) -> date:
    """Return the Saturday of the week containing d (ISO weeks: Mon–Sun)."""
    # ISO weekday: Mon=1 .. Sun=7 → Saturday is 6
    return d + timedelta(days=(6 - d.isoweekday()) % 7)
