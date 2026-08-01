# Task 3: Create CallbackMixin — Report

## Status: DONE

## Summary

Created `CallbackMixin` class that extracts shared callback logic from Hub, Roller, and Room classes.

## Files Created

- `aiopulse/callbacks.py` — CallbackMixin class
- `tests/test_callbacks.py` — 10 unit tests

## Commit

- `b140867` — feat: add CallbackMixin for shared callback logic

## Test Results

```
10 passed in 0.52s
```

## Notes

- The task brief's sync callback tests required an async context since `_schedule_callback` needs a running event loop. Updated tests to use `@pytest.mark.asyncio` with `await asyncio.sleep(0.1)`.
- Fixed lint issues: moved `Callable` import to `collections.abc` (Python 3.10+ style) and sorted imports in test file.
