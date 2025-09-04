import pytest

from nowcast_gdp.smoke import smoke


@pytest.mark.smoke
def test_smoke():
    assert smoke() == "ok"
