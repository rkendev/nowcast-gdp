from pathlib import Path

from nowcast_gdp.io import write_index_unique_sorted


def _read_nonempty_lines(p: Path):
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def test_index_sorted_and_deduped(tmp_path: Path):
    idx = tmp_path / "index.csv"
    idx.parent.mkdir(parents=True, exist_ok=True)

    # pre-existing index with duplicates and out-of-order lines
    idx.write_text("2025-08-28\n2025-08-28\n2024-01-01\n", encoding="utf-8")

    # new lines include a duplicate and a new date
    write_index_unique_sorted(idx, ["2023-12-31", "2025-08-28", "2024-07-01"])

    lines = _read_nonempty_lines(idx)
    # ISO YYYY-MM-DD sorts lexicographically == chronologically
    expected = sorted(set(["2025-08-28", "2024-01-01", "2023-12-31", "2024-07-01"]))
    assert lines == expected


def test_index_created_when_missing(tmp_path: Path):
    idx = tmp_path / "index.csv"
    idx.parent.mkdir(parents=True, exist_ok=True)

    write_index_unique_sorted(idx, ["2025-01-01"])
    assert idx.exists()
    assert _read_nonempty_lines(idx) == ["2025-01-01"]
