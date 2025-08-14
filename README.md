# nowcast-gdp

Real‑time GDP nowcasting toolkit — **MVP scaffold**.
The repo is intentionally lightweight so you can move fast: a tiny package layout, pytest, Ruff linting/formatting, a Makefile for the common dev tasks, and GitHub Actions CI (tests + lint + a placeholder “metrics-gate”).

## Status

> CI runs on pull requests, and on pushes to `main`. You can also trigger it manually from the **Actions** tab.

<!-- You can create a badge in your repo UI: Actions → your workflow → “Create status badge”. -->
<!-- Example badge (replace OWNER/REPO and branch if desired): -->
[![CI](https://github.com/rkendev/nowcast-gdp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/rkendev/nowcast-gdp/actions/workflows/ci.yml)

## Quick start

```bash
# clone
git clone https://github.com/rkendev/nowcast-gdp.git
cd nowcast-gdp

# create venv + install package + dev extras (pytest, ruff, pre-commit)
make venv install

# install git hooks (ruff + ruff format, EoF/trailing-space)
make hooks

# fast feedback
make fmt          # format with Ruff
make lint         # lint with Ruff
make test         # run pytest
```

> Python **3.12+** is expected (see `pyproject.toml`).

## Project layout

```
nowcast-gdp/
├─ src/nowcast_gdp/        # package code
│  └─ dates.py             # date helpers (week_end, quarter helpers, …)
├─ tests/                  # pytest tests (unit + smoke)
├─ .github/workflows/ci.yml# Actions: lint + tests + metrics-gate
├─ .pre-commit-config.yaml # hooks: ruff, ruff-format, whitespace/eof
├─ Makefile                # tiny helper targets (see below)
└─ pyproject.toml          # build + tool config
```

## Makefile targets

```bash
make venv      # create .venv (python -m venv .venv)
make install   # editable install + dev extras
make hooks     # install pre-commit hooks
make fmt       # ruff format
make lint      # ruff lint
make test      # pytest -q
make clean     # remove build/pytest caches
```

## Development flow (solo-friendly)

* Work on **feature branches** (e.g., `feat/*`, `chore/*`), open a PR against `main`.
* CI runs on the PR (lint + tests + metrics-gate).
* Merge with **Squash** to keep a clean history. Commit messages follow **Conventional Commits**.

## Notes

* To show the live CI badge in this README, open **Actions → your workflow → Create status badge**, then copy the Markdown it provides and replace the badge above.
* When you add real model/backtest code, wire it into the *metrics-gate* job and assert thresholds there (fail the job on regressions).

## License

MIT — see [LICENSE](LICENSE).
