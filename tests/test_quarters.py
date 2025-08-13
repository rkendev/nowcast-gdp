from datetime import date

from nowcast_gdp.dates import quarter_end, quarter_start


def test_q1_edges():
    assert quarter_start(date(2025, 1, 15)) == date(2025, 1, 1)
    assert quarter_end(date(2025, 3, 31)) == date(2025, 3, 31)


def test_q3_middle():
    assert quarter_start(date(2025, 8, 11)) == date(2025, 7, 1)
    assert quarter_end(date(2025, 8, 11)) == date(2025, 9, 30)


def test_q4_year_boundary():
    assert quarter_start(date(2025, 12, 5)) == date(2025, 10, 1)
    assert quarter_end(date(2025, 12, 5)) == date(2025, 12, 31)
