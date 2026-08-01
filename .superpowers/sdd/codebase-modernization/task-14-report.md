# Task 14: Update utils.py with Type Hints

**Status:** DONE

## Summary

Added full type hints and Google-style docstrings to all functions in `aiopulse/utils.py`.

## Changes Made

- Added `from __future__ import annotations` for modern annotation syntax
- Added type hints to all 5 functions:
  - `unpack_int(buffer: bytes, ptr: int, length: int) -> tuple[int, int]`
  - `pack_int(value: int, length: int) -> bytes`
  - `unpack_bytes(buffer: bytes, ptr: int, length: int | None = None) -> tuple[bytes, int]`
  - `unpack_string(buffer: bytes, ptr: int, length: int | None = None) -> tuple[str, int]`
  - `unpack_roller_percent(buffer: bytes, ptr: int) -> tuple[int, int]`
- Replaced terse docstrings with Google-style docstrings including Args and Returns sections

## Verification

- All 21 tests in `tests/test_utils.py` pass

## Commit

- `828126d` - refactor: add type hints to utils module
