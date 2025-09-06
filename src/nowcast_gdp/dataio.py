# src/nowcast_gdp/dataio.py
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List, Tuple

from .io import read_csv_dicts


# ---------- paths ----------
def _root(base: Path | None = None) -> Path:
    # raw ALFRED layout already used by ingest
    return (base or Path("data") / "raw" / "alfred").resolve()


def _series_dir(series_id: str, base: Path | None = None) -> Path:
    return _root(base) / series_id


def _index_path(series_id: str, base: Path | None = None) -> Path:
    return _series_dir(series_id, base) / "index.csv"


def _vintage_csv(series_id: str, vintage: date, base: Path | None = None) -> Path:
    return _series_dir(series_id, base) / f"{vintage.isoformat()}.csv"


# ---------- helpers ----------
def _read_nonempty_lines(p: Path) -> list[str]:
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _scan_vintages_from_files(series_dir: Path) -> list[date]:
    """Fallback if index.csv is missing: scan *.csv filenames (except index.csv)."""
    vintages: list[date] = []
    if not series_dir.exists():
        return vintages
    for fp in series_dir.glob("*.csv"):
        if fp.name == "index.csv":
            continue
        try:
            vintages.append(date.fromisoformat(fp.stem))
        except Exception:
            # Ignore non-vintage files
            pass
    return sorted(vintages)


# ---------- public API ----------
def latest_vintage(series_id: str, base: Path | None = None) -> date:
    """
    Return the latest vintage date for a series by reading index.csv.
    Falls back to scanning files if index is absent.
    """
    idx = _index_path(series_id, base)
    lines = _read_nonempty_lines(idx)
    if lines:
        # index is sorted ascending by our ingest helpers
        return date.fromisoformat(lines[-1])
    # fallback scan
    vintages = _scan_vintages_from_files(_series_dir(series_id, base))
    if not vintages:
        raise FileNotFoundError(
            f"No vintages found for series '{series_id}' under {_series_dir(series_id, base)}"
        )
    return vintages[-1]


def read_latest_series(series_id: str, base: Path | None = None) -> Tuple[List[date], List[float]]:
    """
    Load the *latest* vintage CSV -> (dates, values), skipping empty/missing values.
    CSV schema (from ingest): header 'date,value'
    """
    v = latest_vintage(series_id, base)
    path = _vintage_csv(series_id, v, base)
    rows = read_csv_dicts(path)

    dts: list[date] = []
    vals: list[float] = []
    for r in rows:
        s_val = r.get("value", "")
        if not s_val:
            continue  # skip blanks
        try:
            dts.append(date.fromisoformat(r["date"]))
            vals.append(float(s_val))
        except Exception:
            # Robust to occasional bad rows
            continue
    return dts, vals


# ---------- aliases & niceties ----------
# alias for discoverability (so your earlier import works)
read_latest_vintage = latest_vintage


def read_latest_series_df(series_id: str, base: Path | None = None):
    """Return latest series as a pandas DataFrame with Date index."""
    import pandas as pd

    dts, vals = read_latest_series(series_id, base)
    return pd.DataFrame({"date": dts, "value": vals}).set_index("date")


__all__ = [
    "latest_vintage",
    "read_latest_vintage",
    "read_latest_series",
    "read_latest_series_df",
]
