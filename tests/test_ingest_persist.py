# tests/test_ingest_persist.py
from datetime import date
from pathlib import Path

import pytest

from nowcast_gdp.ingest_alfred import (
    index_path,
    persist_all_vintages,
    persist_series_vintage,
    vintage_path,
)


@pytest.fixture
def tmp_root(tmp_path: Path) -> Path:
    return tmp_path / "dataroot"


class FakeObs:
    def __init__(self, d, v):
        self.date = d
        self.value = v


def test_persist_single_vintage_idempotent(monkeypatch, tmp_root: Path):
    series = "GDP"
    v = date(2025, 7, 30)

    # fake network
    monkeypatch.setattr(
        "nowcast_gdp.ingest_alfred.fetch_observations_for_vintage",
        lambda sid, vv: [FakeObs(date(2025, 4, 1), 30331.117)],
    )
    monkeypatch.setattr(
        "nowcast_gdp.ingest_alfred.list_vintage_dates", lambda sid: [date(2025, 1, 31), v]
    )

    # first write
    p = persist_series_vintage(series, v, base=tmp_root)
    assert p.exists()
    idx = index_path(series, base=tmp_root)
    assert idx.exists()
    first_size = p.stat().st_size

    # run again -> idempotent (no duplication / overwrite okay)
    p2 = persist_series_vintage(series, v, base=tmp_root)
    assert p2 == p
    assert p2.stat().st_size == first_size


def test_persist_all_skips_existing(monkeypatch, tmp_root: Path):
    series = "GDP"
    v1, v2 = date(2025, 1, 31), date(2025, 7, 30)

    monkeypatch.setattr("nowcast_gdp.ingest_alfred.list_vintage_dates", lambda sid: [v1, v2])
    monkeypatch.setattr(
        "nowcast_gdp.ingest_alfred.fetch_observations_for_vintage",
        lambda sid, vv: [FakeObs(date(2025, 4, 1), 30331.117)],
    )

    # pre-create first vintage
    persist_series_vintage(series, v1, base=tmp_root)

    # call for all -> should only write the missing one
    written = persist_all_vintages(series, latest_only=False, base=tmp_root)
    assert vintage_path(series, v2, base=tmp_root) in written
    assert vintage_path(series, v1, base=tmp_root) not in written


def test_missing_values_are_written_as_empty_strings(monkeypatch, tmp_root: Path):
    series = "GDP"
    v = date(2025, 7, 30)

    class FakeObs:
        def __init__(self, d, v):
            self.date = d
            self.value = v

    # One missing value and one present value
    monkeypatch.setattr(
        "nowcast_gdp.ingest_alfred.fetch_observations_for_vintage",
        lambda sid, vv: [FakeObs(date(2025, 4, 1), None), FakeObs(date(2025, 7, 1), 123.456789)],
    )
    monkeypatch.setattr("nowcast_gdp.ingest_alfred.list_vintage_dates", lambda sid: [v])

    p = persist_series_vintage(series, v, base=tmp_root)
    content = p.read_text().splitlines()
    # header + 2 rows
    assert len(content) == 3
    # row with missing value should end with a comma
    assert content[1].endswith(",")
    # row with present value should be rounded to 6 decimals
    assert content[2].endswith(",123.456789")
