# Makefile — tiny, batteries-included
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
PRECOMMIT := $(VENV)/bin/pre-commit

.PHONY: help venv install hooks lint fmt test check clean

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z_-]+:.*##/ {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: $(PYTHON) ## Create virtualenv at .venv
$(PYTHON):
	python3 -m venv $(VENV)

install: venv ## Install project (+ dev tools)
	$(PIP) install -U pip
	$(PIP) install -e ".[dev]" ruff pre-commit

hooks: venv ## Install pre-commit Git hook
	$(PRECOMMIT) install  # sets up .git/hooks/pre-commit

lint: venv ## Lint (no changes)
	$(RUFF) check .

fmt: venv ## Format code in-place
	$(RUFF) format

## Run only super-fast unit tests (no network, no filesystem heavy ops)
test-unit:
	$(PYTEST) -q -k "not smoke and not slow"

## Run just IO/index-related tests (guard against regressions in index.csv logic)
test-io:
	$(PYTEST) -q -k "io or index"

# DataIO tests (latest vintage reader)
test-dataio:
	$(PYTEST) -q -k "dataio"

## Run smoke tests only (e.g., minimal end-to-end; can be skipped on CI without keys)
test-smoke:
	$(PYTEST) -q -k "smoke"

## Full suite with summary (useful locally before pushing)
test-all:
	$(PYTEST) -q

## Everything: format, lint, and full tests (pre-flight before PR)
check:
	$(RUFF) format
	$(RUFF) check .
	$(PYTEST) -q

clean: ## Remove caches, builds, and the venv
	rm -rf .pytest_cache __pycache__ build dist *.egg-info $(VENV)

.PHONY: ingest-gdp ingest-gdp-latest
ingest-gdp:
	python -m nowcast_gdp.ingest_alfred --series GDP

ingest-gdp-latest:
	python -m nowcast_gdp.ingest_alfred --series GDP --latest-only

.PHONY: ingest-registry
ingest-registry:
	python -m nowcast_gdp.ingest_alfred --from-registry --active-only --registry config/series.toml

# --- Baselines: BL-0 quick print
bl0-print:
	python -m nowcast_gdp.baselines --series $(SERIES) --model bl0 --h $(H) --print
