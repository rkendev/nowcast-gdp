from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

import requests

FRED_BASE = "https://api.stlouisfed.org/fred"
DEFAULT_FILE_TYPE = "json"


class AlfredError(RuntimeError):
    pass


def _api_key() -> str:
    key = os.getenv("FRED_API_KEY")
    if not key:
        raise AlfredError(
            "Missing FRED_API_KEY. Get a key at https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    return key


def _get(path: str, **params) -> dict:
    """Low-level GET with api_key + json."""
    url = f"{FRED_BASE}/{path}"
    resp = requests.get(
        url,
        params={"api_key": _api_key(), "file_type": DEFAULT_FILE_TYPE, **params},
        timeout=30,
    )
    try:
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise AlfredError(
            f"Bad response from FRED: {e}\nURL={resp.url}\nText={resp.text[:500]}"
        ) from e


def list_vintage_dates(series_id: str) -> list[date]:
    data = _get("series/vintagedates", series_id=series_id)
    # FRED returns "vintage_dates" (underscore), not "vintagedates"
    return [date.fromisoformat(d) for d in data.get("vintage_dates", [])]


@dataclass(frozen=True)
class Observation:
    date: date
    value: Optional[float]  # None if value is "."


def fetch_observations_for_vintage(
    series_id: str,
    vintage: date,
    observation_start: Optional[date] = None,
    observation_end: Optional[date] = None,
) -> List[Observation]:
    """
    Fetch observations for a specific vintage using realtime params.
    Uses: /fred/series/observations?realtime_start=YYYY-MM-DD&realtime_end=YYYY-MM-DD
    """
    params = {
        "series_id": series_id,
        "realtime_start": vintage.isoformat(),
        "realtime_end": vintage.isoformat(),
    }
    if observation_start:
        params["observation_start"] = observation_start.isoformat()
    if observation_end:
        params["observation_end"] = observation_end.isoformat()

    data = _get("series/observations", **params)
    out: List[Observation] = []
    for obs in data.get("observations", []):
        raw = obs.get("value")
        out.append(
            Observation(
                date=date.fromisoformat(obs["date"]),
                value=None if raw in (None, ".", "") else float(raw),
            )
        )
    return out
