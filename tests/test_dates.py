from datetime import date

from nowcast_gdp.dates import week_ending


def test_week_ending():
    assert week_ending(date(2025, 8, 11)).isoformat() == "2025-08-16"
