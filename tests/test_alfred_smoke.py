import os

import pytest

from nowcast_gdp.alfred import fetch_observations_for_vintage, list_vintage_dates

REQUIRES_KEY = pytest.mark.skipif(not os.getenv("FRED_API_KEY"), reason="No FRED_API_KEY set")


@pytest.mark.integration
@REQUIRES_KEY
def test_vintages_and_observations():
    vdates = list_vintage_dates("GDP")
    assert len(vdates) > 10
    v = vdates[-1]
    obs = fetch_observations_for_vintage("GDP", v)
    assert len(obs) >= 4
    assert obs[0].date <= obs[-1].date
