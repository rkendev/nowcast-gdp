# src/nowcast_gdp/alfred.py
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional

import requests

BASE_URL = "https://api.stlouisfed.org/fred"
API_KEY_ENV = "FRED_API_KEY"


@dataclass(frozen=True)
class Observation:
    date: date
    value: Optional[float]  # None when FRED provides blanks/NaN


# ---------- low-level request helper ----------


def _get(path: str, **params: Any) -> Dict[str, Any]:
    """GET JSON with simple retries and 429 (Retry-After) handling."""
    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise RuntimeError(f"{API_KEY_ENV} is not set; export your FRED API key")

    url = f"{BASE_URL}/{path}"
    q = {"api_key": api_key, "file_type": "json", **params}

    max_attempts = 6
    backoff = 1.0
    last_exc: Optional[Exception] = None

    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(url, params=q, timeout=30)
            # polite 429 handling
            if resp.status_code == 429:
                ra = resp.headers.get("Retry-After")
                sleep_for = float(ra) if (ra and ra.isdigit()) else backoff
                if attempt == max_attempts:
                    resp.raise_for_status()
                time.sleep(sleep_for)
                backoff = min(backoff * 2, 30.0)
                continue

            # transient 5xx
            if 500 <= resp.status_code < 600:
                if attempt == max_attempts:
                    resp.raise_for_status()
                time.sleep(backoff)
                backoff = min(backoff * 2, 30.0)
                continue

            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            last_exc = exc
            if attempt == max_attempts:
                break
            time.sleep(backoff)
            backoff = min(backoff * 2, 30.0)

    raise RuntimeError(f"FRED request failed for {path} with params {q}") from last_exc


# ---------- high-level helpers used by ingest ----------


def list_vintage_dates(series_id: str) -> List[date]:
    """
    Return all ALFRED vintage dates (as date objects) for a FRED series.
    """
    # ALFRED endpoint: fred/series/vintagedates
    # docs: https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html
    j = _get("series/vintagedates", series_id=series_id)
    # response has "vintage_dates": ["1991-12-04", ...]
    raw = j.get("vintage_dates", []) or []
    return [date.fromisoformat(s) for s in raw]


def fetch_observations_for_vintage(series_id: str, vintage: date) -> List[Observation]:
    """
    Fetch observations for a specific vintage.
    Returns a list[Observation(date, value|None)] where missing values map to None.
    """
    # ALFRED endpoint: fred/series/observations with "vintage_dates"
    # docs: https://fred.stlouisfed.org/docs/api/fred/series_observations.html
    j = _get(
        "series/observations",
        series_id=series_id,
        vintage_dates=vintage.isoformat(),
        # leave units/defaults; you can tweak later
    )
    obs = []
    for row in j.get("observations", []) or []:
        d = date.fromisoformat(row["date"])
        vs = row.get("value", "")
        if vs in ("", ".", "NaN", "nan"):  # FRED sometimes returns "." for missing
            v: Optional[float] = None
        else:
            try:
                v = float(vs)
            except ValueError:
                v = None
        obs.append(Observation(date=d, value=v))
    return obs
