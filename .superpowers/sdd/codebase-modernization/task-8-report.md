# Task 8: Update Roller to Use HubEntity - Report

## Status: DONE

## Summary

Successfully updated the `Roller` class to inherit from `HubEntity` instead of implementing its own callback methods.

## Changes Made

### `aiopulse/roller.py`
- Changed `Roller` to inherit from `HubEntity` (was standalone class)
- Removed duplicate callback methods (`callback_subscribe`, `callback_unsubscribe`, `notify_callback`)
- Removed `update_callbacks` attribute (now uses `_update_callbacks` from `CallbackMixin`)
- Added `from __future__ import annotations` for modern type hints
- Added type hints to `__init__` parameters and all methods
- Added `TYPE_CHECKING` import for `Hub` type
- Added null check in `__del__` for `health_task`
- Added docstrings to `__del__`, `health_updated`, `get_health`
- Fixed import ordering for ruff compliance
- Split long f-string to meet line length limits

### `tests/test_roller.py`
- Updated `test_init` to check `_update_callbacks` instead of `update_callbacks`
- Added `test_init_inherits_hub_entity` test
- Updated callback tests to use `_update_callbacks`
- Updated `test_notify_callback` to use `_schedule_callback` mock (from `CallbackMixin`)
- Added `test_callback_unsubscribe_not_found` test

## Test Results

- 16/16 roller tests pass
- 183/183 full test suite passes
- Lint clean (ruff)

## Commit

- SHA: `0803591`
- Message: `refactor: Roller inherits from HubEntity`
