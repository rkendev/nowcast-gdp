# src/nowcast_gdp/io.py
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


def ensure_dir(p: Path) -> Path:
    """Create directory (and parents) if needed and return it."""
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_csv(path: Path, rows: Iterable[Mapping[str, Any]], header: Sequence[str]) -> None:
    """Write rows to CSV with a fixed header, overwriting if exists."""
    ensure_dir(path.parent)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(header))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    """Read a small CSV into memory as list of dicts (empty list if not found)."""
    if not path.exists():
        return []
    with path.open(newline="") as f:
        r = csv.DictReader(f)
        return [dict(row) for row in r]


def write_index_unique_sorted(path: Path, values: Iterable[str]) -> None:
    """Append-or-create index file with single column 'vintage_date', uniq+sorted."""
    existing = {row["vintage_date"] for row in read_csv_dicts(path)}
    existing.update(values)
    rows = [{"vintage_date": v} for v in sorted(existing)]
    write_csv(path, rows, header=["vintage_date"])
