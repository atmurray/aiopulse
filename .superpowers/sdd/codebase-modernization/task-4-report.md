# Task 4 Report: HubEntity Base Class

## Status: DONE

## Summary

Created `HubEntity` base class in `aiopulse/entities.py` that inherits from `CallbackMixin` and provides common attributes for hub-managed entities (Roller, Room, Scene, Timer).

## Implementation

### `aiopulse/entities.py`
- `HubEntity(CallbackMixin)` with `__init__` accepting `hub` and `entity_id`
- Sets `hub`, `id`, `name`, `icon` attributes
- Uses `TYPE_CHECKING` guard for `Hub` import to avoid circular imports

### `tests/test_entities.py`
- 5 tests covering init with int/bytes IDs, callback subscribe/unsubscribe, and notify

## Test Results

All 176 tests pass (including 5 new entity tests).

## Commit

`fb97717` - feat: add HubEntity base class for hub entities
