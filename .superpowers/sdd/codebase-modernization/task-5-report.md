# Task 5: Update Room to Use HubEntity — Report

## Status: DONE

## Summary

Updated `Room` class to inherit from `HubEntity` (which itself inherits from `CallbackMixin`), eliminating duplicated callback logic and aligning with the new entity hierarchy.

## Changes

### `aiopulse/room.py`
- `Room` now inherits from `HubEntity` instead of being a standalone class
- Removed duplicate `callback_subscribe`, `callback_unsubscribe`, `notify_callback` methods (inherited from `CallbackMixin` via `HubEntity`)
- Removed duplicate `hub`, `id`, `name`, `icon` attribute initialization (inherited from `HubEntity`)
- Removed duplicate `update_callbacks` list (now `_update_callbacks` from `CallbackMixin`)
- Added `from __future__ import annotations` and TYPE_CHECKING import for type hints
- Added type annotations to `__init__` and all async methods
- Updated `__str__` to handle both `bytes` and `int` id types safely

### `tests/test_room.py`
- Updated tests to reference `_update_callbacks` (from `CallbackMixin`) instead of `update_callbacks`
- Added `test_inherits_from_hub_entity` to verify `Room` is an instance of `HubEntity`
- Removed `test_notify_callback` (now tested in `test_callbacks.py` via `CallbackMixin`)
- Added hub mock fixture with `async_add_job` returning `MagicMock()` (needed for inherited notify behavior)

## TDD Process

1. **RED**: Wrote updated tests expecting HubEntity behavior → 5 failures as expected (no `_update_callbacks`, not instance of HubEntity)
2. **GREEN**: Updated `room.py` to inherit from HubEntity → all 10 tests pass
3. **Verify**: Full suite of 176 tests passes with no regressions

## Commits

- `66b2114` refactor: Room inherits from HubEntity
