# src/nowcast_gdp/ingest_alfred.py
from __future__ import annotations

import time
from argparse import ArgumentParser
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

from .alfred import (
    fetch_observations_for_vintage,  # returns list[Observation(date,value)]
    list_vintage_dates,
)
from .io import ensure_dir, write_csv, write_index_unique_sorted
from .registry import load_registry, select_series


def data_root(base: Path | None = None) -> Path:
    """Root directory for ALFRED raw data (default: data/raw/alfred)."""
    return (base or Path("data") / "raw" / "alfred").resolve()


def series_dir(series_id: str, base: Path | None = None) -> Path:
    return ensure_dir(data_root(base) / series_id)


def vintage_path(series_id: str, vintage: date, base: Path | None = None) -> Path:
    return series_dir(series_id, base) / f"{vintage.isoformat()}.csv"


def index_path(series_id: str, base: Path | None = None) -> Path:
    return series_dir(series_id, base) / "index.csv"


def _obs_to_rows(obs) -> list[dict[str, str]]:
    """Map Observation(date,value|None) -> CSV rows with empty-string for missing."""
    rows: list[dict[str, str]] = []
    for o in obs:
        rows.append(
            {
                "date": o.date.isoformat(),
                "value": "" if o.value is None else f"{o.value:.6f}",
            }
        )
    return rows


def persist_series_vintage(series_id: str, vintage: date, base: Path | None = None) -> Path:
    """
    Fetch observations for a vintage and write to:
      data/raw/alfred/{series}/{YYYY-MM-DD}.csv
    Also update index.csv (idempotent; skip if file exists).
    """
    path = vintage_path(series_id, vintage, base)
    if path.exists():
        return path
    obs = fetch_observations_for_vintage(series_id, vintage)
    write_csv(path, _obs_to_rows(obs), header=["date", "value"])
    write_index_unique_sorted(index_path(series_id, base), [vintage.isoformat()])
    return path


def persist_all_vintages(
    series_id: str,
    latest_only: bool = False,
    start: Optional[date] = None,
    base: Path | None = None,
    throttle_sec: float = 0.0,
) -> list[Path]:
    """
    Persist either the latest vintage or all vintages (optionally >= start).
    Skips vintages already present. Optional throttle between requests.
    """
    vdates = list_vintage_dates(series_id)
    if start:
        vdates = [v for v in vdates if v >= start]
    if latest_only and vdates:
        vdates = [vdates[-1]]

    written: list[Path] = []
    for v in vdates:
        p = vintage_path(series_id, v, base)
        if p.exists():
            continue
        persist_series_vintage(series_id, v, base)
        written.append(p)
        if throttle_sec > 0:
            time.sleep(throttle_sec)
    return written


def ingest_from_registry(
    registry_path: str | Path = "config/series.toml",
    series: Optional[Iterable[str]] = None,  # logical ids or fred_ids; None = all
    latest_only: Optional[bool] = None,  # override per-series default if not None
    active_only: bool = True,
    throttle_sec: float = 0.0,
) -> None:
    """Ingest one or many series as declared in the TOML registry."""
    reg = load_registry(registry_path)
    chosen = select_series(reg, include=series, active_only=active_only)
    if not chosen:
        print("No series selected; check registry or filters.")
        return

    for sid, cfg in chosen.items():
        series_id = cfg.fred_id
        print(f"[ingest] {sid} (fred_id={series_id})")
        # Resolve latest-only behavior (global override wins if provided)
        use_latest = (
            latest_only if latest_only is not None else bool(getattr(cfg, "latest_only", False))
        )
        if use_latest:
            vdates = list_vintage_dates(series_id)
            if not vdates:
                print("  -> no vintages found")
                continue
            latest = vdates[-1]
            print(f"  -> latest vintage: {latest}")
            persist_series_vintage(series_id, latest)
        else:
            vstart = getattr(cfg, "vintage_start", None)
            print(f"  -> full ingest (start={vstart})")
            persist_all_vintages(
                series_id,
                latest_only=False,
                start=vstart,
                throttle_sec=throttle_sec,
            )


def _parse_bool_override(s: Optional[str]) -> Optional[bool]:
    if s is None:
        return None
    s = s.strip().lower()
    if s in {"true", "1", "yes", "y"}:
        return True
    if s in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean override: {s!r}")


def main(argv: list[str] | None = None) -> int:
    ap = ArgumentParser(description="Persist ALFRED vintages to data/raw/alfred")

    # Registry mode
    ap.add_argument(
        "--from-registry",
        action="store_true",
        help="Use the TOML registry (config/series.toml) instead of --series.",
    )
    ap.add_argument(
        "--registry",
        default="config/series.toml",
        help="Path to series registry (TOML). Used with --from-registry.",
    )
    ap.add_argument(
        "--include",
        default=None,
        help="Comma-separated logical ids or fred_ids to include (registry mode).",
    )
    ap.add_argument(
        "--active-only",
        action="store_true",
        default=False,
        help="Registry mode: ingest only active series.",
    )
    ap.add_argument(
        "--latest-only-override",
        default=None,
        help="Registry mode: override per-series latest_only with true/false.",
    )
    ap.add_argument(
        "--throttle",
        type=float,
        default=0.0,
        help="Seconds to sleep between requests (helps avoid 429s).",
    )

    # Single-series mode (back-compat)
    ap.add_argument("--series", help="FRED series ID, e.g., GDP (single-series mode).")
    ap.add_argument(
        "--latest-only", action="store_true", help="Single-series: only persist the latest vintage."
    )
    ap.add_argument("--start", type=str, help="Single-series: start date (YYYY-MM-DD).")

    args = ap.parse_args(argv)

    if args.from_registry:
        include_list = None
        if args.include:
            include_list = [s.strip() for s in args.include.split(",") if s.strip()]
        lo = _parse_bool_override(args.latest_only_override)
        ingest_from_registry(
            registry_path=args.registry,
            series=include_list,
            latest_only=lo,
            active_only=bool(args.active_only),
            throttle_sec=float(args.throttle or 0.0),
        )
        return 0

    # Single-series mode requires --series
    if not args.series:
        ap.error("the following arguments are required: --series (or use --from-registry)")

    start_date = date.fromisoformat(args.start) if args.start else None
    persist_all_vintages(
        args.series,
        latest_only=bool(args.latest_only),
        start=start_date,
        throttle_sec=float(args.throttle or 0.0),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
