from datetime import date
from nowcast_gdp.dates import quarter, quarter_start, quarter_end

def test_quarter_number():
    assert quarter(date(2025, 1, 15)) == 1
    assert quarter(date(2025, 3, 31)) == 1
    assert quarter(date(2025, 4, 1)) == 2
    assert quarter(date(2025, 12, 31)) == 4

def test_quarter_bounds_mid_q3():
    d = date(2025, 8, 11)
    assert quarter_start(d) == date(2025, 7, 1)
    assert quarter_end(d) == date(2025, 9, 30)

def test_quarter_bounds_q4_edge():
    d = date(2025, 12, 31)
    assert quarter_start(d) == date(2025, 10, 1)
    assert quarter_end(d) == date(2025, 12, 31)
from datetime import date
from nowcast_gdp.dates import quarter, quarter_start, quarter_end

def test_quarter_number():
    assert quarter(date(2025, 1, 15)) == 1
    assert quarter(date(2025, 3, 31)) == 1
    assert quarter(date(2025, 4, 1)) == 2
    assert quarter(date(2025, 12, 31)) == 4

def test_quarter_bounds_mid_q3():
    d = date(2025, 8, 11)
    assert quarter_start(d) == date(2025, 7, 1)
    assert quarter_end(d) == date(2025, 9, 30)

def test_quarter_bounds_q4_edge():
    d = date(2025, 12, 31)
    assert quarter_start(d) == date(2025, 10, 1)
    assert quarter_end(d) == date(2025, 12, 31)
