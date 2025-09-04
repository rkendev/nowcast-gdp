from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List


def ensure_dir(path: Path) -> Path:
    """Ensure the directory for `path` exists; return the directory path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_csv(path: Path, rows: Iterable[Dict[str, str]], header: List[str]) -> None:
    """
    Write rows (list of dicts) to CSV with a given header.
    All values are written as strings as-is.
    """
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    """
    Read a CSV file into a list of dicts (string values).
    Note: for headerless single-column files, DictReader treats the first row
    as the header and returns an empty list. Use line readers for those.
    """
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---- index.csv helpers (newline-delimited, NO header) -----------------------------


def _read_nonempty_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _write_lines(path: Path, lines: List[str]) -> None:
    ensure_dir(path.parent)
    # Write trailing newline when non-empty to keep diffs tidy
    path.write_text(("\n".join(lines) + "\n") if lines else "", encoding="utf-8")


def write_index_unique_sorted(path: Path, new_entries: Iterable[str]) -> None:
    """
    Maintain a newline-delimited index file (no header) of vintage dates.
      - creates file if missing
      - merges with existing lines
      - de-duplicates
      - sorts ascending (ISO dates sort lexicographically)
    """
    existing = set(_read_nonempty_lines(path))
    incoming = {v for v in new_entries if v}
    merged = sorted(existing | incoming)
    _write_lines(path, merged)


__all__ = [
    "ensure_dir",
    "write_csv",
    "read_csv_dicts",
    "write_index_unique_sorted",
]
