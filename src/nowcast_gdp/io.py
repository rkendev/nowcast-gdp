# src/nowcast_gdp/io.py
from pathlib import Path

import pandas as pd


def to_parquet(df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def from_parquet(path: str | Path) -> pd.DataFrame:
    return pd.read_parquet(path)
