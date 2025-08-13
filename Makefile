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

test: venv ## Run tests
	$(PYTEST) -q

check: fmt lint test ## Format, then lint, then tests

clean: ## Remove caches, builds, and the venv
	rm -rf .pytest_cache __pycache__ build dist *.egg-info $(VENV)
