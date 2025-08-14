# nowcast-gdp

Real-time GDP **nowcasting** toolkit — _MVP scaffold_ focused on fast, clean iteration.

[![CI](https://github.com/rkendev/nowcast-gdp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/rkendev/nowcast-gdp/actions/workflows/ci.yml)

---

## What’s here

- **Modern packaging** with `pyproject.toml` (Python **3.12+**; Setuptools backend). The package lives under `src/nowcast_gdp`.
- **Date utilities (MVP)** in `nowcast_gdp.dates`:
  - `week_ending(d: date) -> date` — Saturday for the ISO week that contains `d`.
  - Quarter helpers: `quarter_of(d)`, `quarter_start(d)`, and `quarter_end(d)`.
- **Tests** with `pytest` (see `tests/`).
- **Lint & format** with **ruff** (formatter + linter) and **pre-commit** hooks for local hygiene.
- **CI (GitHub Actions)** with three jobs:
  - `lint` — ruff format & checks
  - `test` — pytest
  - `metrics-gate` — placeholder for backtests / acceptance thresholds
  - Triggers: PRs and/or pushes to `main`, plus a manual **Run workflow** button.

> Scope is intentionally small right now so you can iterate quickly and add data, models, and metrics next.

---

## Quickstart

```bash
# 1) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install the project (editable) + dev tools
pip install -U pip
pip install -e ".[dev]"

# 3) (Optional) enable local hooks
pre-commit install
```

### Makefile helpers

The repo includes a tiny `Makefile` for common tasks:

```makefile
.PHONY: install hooks fmt lint test check

install:
	pip install -U pip
	pip install -e ".[dev]"

hooks:
	pre-commit install

fmt:
	ruff format .

lint:
	ruff check .

test:
	pytest -q

check: fmt lint test
```

Common flows:

```bash
make install   # one-time setup in a fresh venv
make hooks     # enable pre-commit locally
make fmt       # format with ruff
make lint      # static checks with ruff
make test      # run tests
make check     # all of the above
```

---

## Project layout

```
nowcast-gdp/
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── pyproject.toml
├── src/
│   └── nowcast_gdp/
│       └── dates.py
└── tests/
    ├── test_dates.py
    └── test_quarters.py
```

---

## Usage (snippet)

```python
from datetime import date
from nowcast_gdp.dates import week_ending, quarter_of, quarter_start, quarter_end

assert week_ending(date(2025, 8, 11)).isoformat() == "2025-08-16"
assert quarter_of(date(2025, 2, 1)) == (2025, 1)         # (year, quarter)
assert quarter_start(date(2025, 2, 1)).isoformat() == "2025-01-01"
assert quarter_end(date(2025, 2, 1)).isoformat()   == "2025-03-31"
```

---

## Roadmap (MVP → v0)

- Flesh out **metrics-gate** in CI (backtest + acceptance thresholds).
- Ingestion pipelines for public macro data.
- Baseline nowcast model(s) + evaluation.
- Docs & examples notebook(s).

---

## License

MIT
