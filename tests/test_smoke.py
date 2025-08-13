from nowcast_gdp.smoke import smoke


def test_smoke():
    assert smoke() == "ok"
