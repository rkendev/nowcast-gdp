from pathlib import Path

from nowcast_gdp.io import write_index_unique_sorted


def _read_nonempty_lines(p: Path):
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def test_write_index_sorted_and_deduped(tmp_path: Path):
    path = tmp_path / "index.csv"

    # 1) First write: unsorted values with duplicates
    write_index_unique_sorted(path, ["2025-08-01", "2025-07-01", "2025-07-01"])
    assert _read_nonempty_lines(path) == ["2025-07-01", "2025-08-01"]

    # 2) Append more, includes a duplicate and earlier date
    write_index_unique_sorted(path, ["2025-06-01", "2025-08-01"])
    assert _read_nonempty_lines(path) == ["2025-06-01", "2025-07-01", "2025-08-01"]
