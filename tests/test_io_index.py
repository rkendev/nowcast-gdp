# tests/test_io_index.py
import csv
from pathlib import Path

from nowcast_gdp.io import read_csv_dicts, write_index_unique_sorted


def test_write_index_sorted_and_deduped(tmp_path: Path):
    path = tmp_path / "index.csv"

    # 1. First write: unsorted values with duplicates
    write_index_unique_sorted(path, ["2025-08-01", "2025-07-01", "2025-07-01"])

    rows = read_csv_dicts(path)
    values = [r["vintage_date"] for r in rows]

    # Ensure deduped and sorted
    assert values == ["2025-07-01", "2025-08-01"]

    # 2. Second write: append more values, including duplicates
    write_index_unique_sorted(path, ["2025-06-01", "2025-08-01"])

    rows2 = read_csv_dicts(path)
    values2 = [r["vintage_date"] for r in rows2]

    # Ensure still deduped and sorted
    assert values2 == ["2025-06-01", "2025-07-01", "2025-08-01"]

    # Also verify file is still valid CSV with header
    with path.open() as f:
        header = next(csv.reader(f))
        assert header == ["vintage_date"]
