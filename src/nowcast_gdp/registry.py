from __future__ import annotations

import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, Optional


@dataclass(frozen=True)
class SeriesCfg:
    id: str  # logical id (key in [series.*])
    fred_id: str  # ALFRED/FRED id to fetch
    name: Optional[str] = None
    frequency: Optional[str] = None
    vintage_start: Optional[date] = None
    latest_only: bool = False
    active: bool = True


def load_registry(path: str | Path = Path("config/series.toml")) -> Dict[str, SeriesCfg]:
    """Load series registry from TOML into a dict of SeriesCfg by logical id."""
    p = Path(path)
    data = tomllib.loads(p.read_text("utf-8")) if p.exists() else {"series": {}}
    res: Dict[str, SeriesCfg] = {}
    for sid, entry in data.get("series", {}).items():
        vintage_start = entry.get("vintage_start")
        res[sid] = SeriesCfg(
            id=sid,
            fred_id=entry.get("fred_id", sid),
            name=entry.get("name"),
            frequency=entry.get("frequency"),
            vintage_start=date.fromisoformat(vintage_start) if vintage_start else None,
            latest_only=bool(entry.get("latest_only", False)),
            active=bool(entry.get("active", True)),
        )
    return res


def select_series(
    registry: Dict[str, SeriesCfg],
    include: Optional[Iterable[str]] = None,
    active_only: bool = True,
) -> Dict[str, SeriesCfg]:
    """Filter series by include list and active flag."""
    items = registry
    if include:
        include_set = {s.strip() for s in include}
        items = {k: v for k, v in registry.items() if k in include_set or v.fred_id in include_set}
    if active_only:
        items = {k: v for k, v in items.items() if v.active}
    return items
