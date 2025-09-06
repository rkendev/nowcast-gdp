# src/nowcast_gdp/baselines/__main__.py
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import List

from nowcast_gdp.dataio import read_latest_series

from .bl0 import forecast_last


def main(argv: List[str] | None = None) -> int:
    ap = ArgumentParser(description="Run simple baselines over latest series")
    ap.add_argument("--series", required=True, help="Series ID, e.g. GDP")
    ap.add_argument("--model", default="bl0", choices=["bl0"], help="Baseline model")
    ap.add_argument("--h", type=int, default=1, help="Forecast horizon (steps)")
    ap.add_argument(
        "--base",
        default=str(Path("data") / "raw" / "alfred"),
        help="Root for raw ALFRED data (default: data/raw/alfred)",
    )
    ap.add_argument("--print", action="store_true", help="Print forecasts to stdout")
    args = ap.parse_args(argv)

    # load latest vintage series
    _dates, values = read_latest_series(args.series, base=Path(args.base))
    if not values:
        raise SystemExit(f"No values found for series {args.series} under {args.base}")

    # select model
    if args.model == "bl0":
        yhat = forecast_last(values, h=args.h)
    else:
        raise SystemExit(f"Unknown model: {args.model}")

    if args.print:
        for i, val in enumerate(yhat, start=1):
            print(f"h={i}, forecast={val}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
