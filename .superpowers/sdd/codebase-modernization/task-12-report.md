# Task 12 Report: Update CI/CD Workflows

**Status:** DONE
**Commit:** 322ef7f - ci: update workflows with testing and release automation

## Changes Made

### 1. Updated `.github/workflows/python-app.yml`
- Upgraded `actions/checkout` v3 → v4
- Upgraded `actions/setup-python` v3 → v5
- Added Python matrix strategy (3.10, 3.11, 3.12)
- Replaced `flake8` linting with `ruff check .`
- Added `mypy` type checking step
- Replaced manual dependency installation with `pip install -e ".[dev]"`
- Updated test step to use `pytest --cov=aiopulse --cov-report=xml`
- Removed artifact upload step (handled by release workflow)

### 2. Created `.github/workflows/python-release.yml`
- Triggers on version tags (`v*`)
- Uses trusted publishing via `pypa/gh-action-pypi-publish@release/v1`
- Creates GitHub Release with auto-generated release notes
- Runs tests before publishing
- Configures `pypi` environment with proper permissions (`contents: write`, `id-token: write`)

### 3. Updated `.pre-commit-config.yaml`
- Updated `black` 19.10b0 → 24.4.2
- Replaced `flake8` with `ruff` v0.4.4 (with `--fix` arg)
- Added `mypy` v1.10.0 hook with `types-all` dependency
- Updated `codespell` v1.16.0 → v2.2.6

## Verification
- All three YAML files validated with `yaml.safe_load()` — no syntax errors
- All changes committed as single atomic commit
