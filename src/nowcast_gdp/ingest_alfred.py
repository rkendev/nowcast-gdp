# src/nowcast_gdp/ingest_alfred.py
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

from .alfred import fetch_observations_for_vintage, list_vintage_dates
from .io import to_parquet

CACHE_DIR = Path("data/cache/alfred")
RAW_DIR = Path("data/raw/alfred")


def _vintage_cache_path(series_id: str) -> Path:
    return CACHE_DIR / series_id / "vintages.json"


def list_vintages_cached(series_id: str, refresh: bool = False) -> list[date]:
    p = _vintage_cache_path(series_id)
    if not refresh and p.exists():
        if datetime.now() - datetime.fromtimestamp(p.stat().st_mtime) < timedelta(hours=24):
            return [date.fromisoformat(d) for d in json.loads(p.read_text())]
    vintages = list_vintage_dates(series_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps([d.isoformat() for d in vintages]))
    return vintages


def resolve_vintage(series_id: str, spec: str) -> date:
    if spec == "latest":
        return list_vintages_cached(series_id)[-1]
    return date.fromisoformat(spec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("series_id")
    ap.add_argument("--vintage", default="latest")
    ap.add_argument("--refresh", action="store_true", help="refresh cached vintages")
    args = ap.parse_args()

    v = resolve_vintage(args.series_id, args.vintage)
    obs = fetch_observations_for_vintage(args.series_id, v)
    df = pd.DataFrame([{"date": o.date, "value": o.value, "vintage": v} for o in obs])

    out = RAW_DIR / args.series_id / f"observations_vintage={v}.parquet"
    path = to_parquet(df, out)
    print(path)


if __name__ == "__main__":
    main()
