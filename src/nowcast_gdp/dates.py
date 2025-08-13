from datetime import date, timedelta

def week_ending(d: date) -> date:
    """Return the Saturday of the week containing d (ISO weeks: Mon–Sun)."""
    # ISO weekday: Mon=1 .. Sun=7 → Saturday is 6
    return d + timedelta(days=(6 - d.isoweekday()) % 7)

def week_ending(d: date) -> date:
    """Return the Saturday of the week containing d (ISO weeks: Mon–Sun)."""
    return d + timedelta(days=(6 - d.isoweekday()) % 7)

# Quarter helpers (calendar quarters: Q1=Jan–Mar, Q2=Apr–Jun, Q3=Jul–Sep, Q4=Oct–Dec)

def quarter(d: date) -> int:
    """Quarter number for date d (1..4)."""
    return (d.month - 1) // 3 + 1

def quarter_start(d: date) -> date:
    """First day of the calendar quarter containing d."""
    m0 = 3 * (quarter(d) - 1) + 1
    return date(d.year, m0, 1)

def quarter_end(d: date) -> date:
    """Last day of the calendar quarter containing d."""
    m0 = 3 * (quarter(d) - 1) + 1
    m_next = m0 + 3
    y_next = d.year + 1 if m_next > 12 else d.year
    m_next = 1 if m_next > 12 else m_next
    return date(y_next, m_next, 1) - timedelta(days=1)
