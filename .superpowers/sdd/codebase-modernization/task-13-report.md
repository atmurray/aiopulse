# Task 13 Report: Update Hub Callbacks to Use CallbackMixin

## Status: DONE

**Commit:** 44b2766 refactor: Hub inherits from CallbackMixin

## Summary

Updated `Hub` class to inherit from `CallbackMixin` and removed the duplicate callback methods (`callback_subscribe`, `callback_unsubscribe`, `async_add_job`, `notify_callback`).

## Changes Made

### `aiopulse/hub.py`
- Added `from aiopulse.callbacks import CallbackMixin` import
- Changed `class Hub:` to `class Hub(CallbackMixin):`
- Added `super().__init__()` call in `__init__`
- Removed `self.update_callbacks: list[Callable] = []` (now inherited as `self._update_callbacks`)
- Removed duplicate methods: `callback_subscribe()`, `callback_unsubscribe()`, `async_add_job()`, `notify_callback()`
- Changed `self.async_add_job(self.update)` to `self._schedule_callback(self.update)` in `run()`
- Removed unused imports: `functools`, `Callable`, `Any`

### `aiopulse/roller.py`
- Changed `hub.async_add_job(self.health_updater)` to `hub._schedule_callback(self.health_updater)`

### `tests/conftest.py`
- Changed `h.async_add_job = MagicMock(...)` to `h._schedule_callback = MagicMock(...)`

### `tests/test_hub.py`
- Updated `hub.update_callbacks` references to `hub._update_callbacks`
- Changed `hub.async_add_job.assert_called_with(...)` to `hub._schedule_callback.assert_called_with(...)`
- Removed `TestHubAsyncAddJob` class (4 tests removed - `async_add_job` is no longer a Hub method)

### `tests/test_roller.py`
- Changed `hub.async_add_job = MagicMock(...)` to `hub._schedule_callback = MagicMock(...)`

### `tests/test_room.py`
- Changed `hub.async_add_job = MagicMock()` to `hub._schedule_callback = MagicMock()`

## Test Results

- 199 tests pass (down from 204 due to removing 4 `TestHubAsyncAddJob` tests +1 flaky test)
- 1 pre-existing flaky test (`test_discover_with_hub`) - passes individually, fails intermittently in full suite due to 0.01s timeout
- All callback-related tests pass

## Concerns

None.
