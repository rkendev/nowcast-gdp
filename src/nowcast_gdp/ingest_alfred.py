# src/nowcast_gdp/ingest_alfred.py
from __future__ import annotations

from argparse import ArgumentParser
from datetime import date
from pathlib import Path

from .alfred import (
    fetch_observations_for_vintage,  # returns list[Observation(date,value)]
    list_vintage_dates,
)
from .io import ensure_dir, write_csv, write_index_unique_sorted


def data_root(base: Path | None = None) -> Path:
    """
    Root directory for ALFRED raw data.
    - default: data/raw/alfred
    - used by tests to inject a tmp root
    """
    return (base or Path("data") / "raw" / "alfred").resolve()


def series_dir(series_id: str, base: Path | None = None) -> Path:
    return ensure_dir(data_root(base) / series_id)


def vintage_path(series_id: str, vintage: date, base: Path | None = None) -> Path:
    return series_dir(series_id, base) / f"{vintage.isoformat()}.csv"


def index_path(series_id: str, base: Path | None = None) -> Path:
    return series_dir(series_id, base) / "index.csv"


def _obs_to_rows(obs) -> list[dict[str, str]]:
    """
    Convert a list of Observation objects to rows suitable for CSV writing.
    Each row is a dict with keys: "date" and "value".
    Missing values (None) are written as empty strings.
    """
    rows: list[dict[str, str]] = []
    for o in obs:
        if o.value is None:
            val_str = ""  # or "NaN" if you prefer
        else:
            val_str = f"{o.value:.6f}"
        rows.append({"date": o.date.isoformat(), "value": val_str})
    return rows


def persist_series_vintage(series_id: str, vintage: date, base: Path | None = None) -> Path:
    """
    Fetch observations for a specific vintage and write to CSV.
    Also updates index.csv to include the vintage.
    Returns the path written.
    """
    path = vintage_path(series_id, vintage, base)
    if path.exists():
        # idempotent: do nothing if already present
        return path

    obs = fetch_observations_for_vintage(series_id, vintage)
    write_csv(path, _obs_to_rows(obs), header=["date", "value"])
    write_index_unique_sorted(index_path(series_id, base), [vintage.isoformat()])
    return path


def persist_all_vintages(
    series_id: str, latest_only: bool = False, base: Path | None = None
) -> list[Path]:
    """
    Persist either the latest vintage or all vintages for a series.
    Skips vintages that are already present.
    Returns list of paths written.
    """
    vdates = list_vintage_dates(series_id)
    if latest_only:
        vdates = [vdates[-1]]

    written: list[Path] = []
    for v in vdates:
        p = vintage_path(series_id, v, base)
        if p.exists():
            continue
        persist_series_vintage(series_id, v, base)
        written.append(p)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = ArgumentParser(description="Persist ALFRED vintages to data/raw/alfred")
    ap.add_argument("--series", required=True, help="Series ID, e.g., GDP")
    ap.add_argument("--latest-only", action="store_true", help="Only persist the latest vintage")
    args = ap.parse_args(argv)

    persist_all_vintages(args.series, latest_only=args.latest_only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
