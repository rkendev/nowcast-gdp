# tests/test_dataio.py
from __future__ import annotations

from datetime import date
from pathlib import Path

from nowcast_gdp.dataio import latest_vintage, read_latest_series


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_latest_vintage_and_reader(tmp_path: Path):
    base = tmp_path / "data" / "raw" / "alfred" / "GDP"
    # create two vintages
    v1 = "2025-07-30"
    v2 = "2025-08-28"

    # index.csv sorted, with duplicates (shouldn’t matter here)
    _write(base / "index.csv", f"{v1}\n{v1}\n{v2}\n")

    # first CSV (has one blank row to test skipping)
    _write(
        base / f"{v1}.csv",
        "date,value\n2025-01-01,100\n2025-04-01,\n2025-07-01,110\n",
    )
    # second CSV (latest)
    _write(
        base / f"{v2}.csv",
        "date,value\n2025-01-01,200\n2025-04-01,210\n2025-07-01,220\n",
    )

    # latest vintage detection
    assert latest_vintage("GDP", base=tmp_path / "data" / "raw" / "alfred") == date.fromisoformat(
        v2
    )

    # read latest series values
    dts, vals = read_latest_series("GDP", base=tmp_path / "data" / "raw" / "alfred")
    assert len(dts) == len(vals) == 3
    assert vals == [200.0, 210.0, 220.0]
    assert dts[0].isoformat() == "2025-01-01"
