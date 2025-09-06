# src/nowcast_gdp/baselines/__main__.py
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import List

from nowcast_gdp.dataio import read_latest_series

from .bl0 import forecast_last as carry_forward_forecast
from .bl1 import drift_forecast


def main(argv: List[str] | None = None) -> int:
    ap = ArgumentParser(description="Run simple baselines on latest ALFRED series")
    ap.add_argument("--series", required=True, help="Series ID, e.g., GDP")
    ap.add_argument("--h", type=int, default=3, help="Forecast horizon")
    ap.add_argument(
        "--model",
        choices=["bl0", "bl1"],
        default="bl0",
        help="Which baseline to run: bl0=carry-forward, bl1=drift",
    )
    ap.add_argument(
        "--window",
        type=int,
        default=4,
        help="Window of diffs for BL-1 drift (ignored for BL-0)",
    )
    ap.add_argument(
        "--base",
        type=str,
        default="data/raw/alfred",
        help="Base path to ALFRED raw data",
    )
    args = ap.parse_args(argv)

    base = Path(args.base)
    dates, values = read_latest_series(args.series, base)

    if args.model == "bl0":
        fcst = carry_forward_forecast(values, args.h)
    else:  # bl1
        fcst = drift_forecast(values, args.h, window=args.window)

    print(f"[{args.model}] {args.series} h={args.h} → {fcst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
