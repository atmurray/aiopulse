# Task 1 Report: Update pyproject.toml and Setup Configuration

## Status: DONE

## What I Implemented

All 6 steps from the task brief:

1. **pyproject.toml** - Updated version to 0.5.0, requires-python to >=3.10, added Python 3.10/3.11/3.12 classifiers, added `[project.optional-dependencies]` dev section, added `[tool.pytest.ini_options]` with testpaths, `[tool.mypy]`, `[tool.ruff]` configs, updated bumpver current_version.

2. **setup.py** - Updated version to 0.5.0, changed import from `distutils.core` to `setuptools`, updated download_url, python_requires to >=3.10, classifier to "Development Status :: 4 - Beta".

3. **aiopulse/__init__.py** - Updated `__version__` from "0.4.6" to "0.5.0".

4. **aiopulse/py.typed** - Created empty PEP 561 marker file.

5. **Tests** - Ran `pytest tests/ -v`. All 154 tests pass.

6. **Committed** - `73fd40b` "chore: update version to 0.5.0 and add dev dependencies"

## Files Changed

- `pyproject.toml` - Major config updates
- `setup.py` - Version bump and setuptools migration
- `aiopulse/__init__.py` - Version bump
- `aiopulse/py.typed` - New empty marker file

## Test Results

```
154 passed in 5.90s
```

## Self-Review

No issues found. All changes match the task brief exactly.

## Fix Round 1

### Finding
`pyproject.toml:52` — `disallow_untyped_defs = true` is too strict for incremental adoption. This mypy setting flags every existing function without annotations across the entire codebase, producing noise on any mypy run against existing code.

### Fix Applied
Changed `disallow_untyped_defs = true` to `disallow_untyped_defs = false` in `[tool.mypy]` section.

### Test Results
```
python -m pytest tests/ -v
154 passed in 5.81s
```

### Commit
`3e55d60` "fix: relax mypy disallow_untyped_defs for incremental adoption"
