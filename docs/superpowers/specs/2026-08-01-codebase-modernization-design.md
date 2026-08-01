# Aiopulse Codebase Modernization Design

**Date:** 2026-08-01  
**Version:** 0.5.0  
**Author:** Code Review Team  

## Overview

Comprehensive refactoring of the aiopulse library to modernize Python compatibility, improve resilience, reduce code duplication, and update CI/CD infrastructure.

## Goals

1. **Modernize Python Compatibility** - Target Python 3.10+ with modern asyncio patterns and type hints
2. **Improve Resilience** - Better error handling, bounds checking, lock management
3. **Reduce Code Duplication** - Extract shared patterns into base classes and mixins
4. **Update CI/CD** - Add testing, type checking, and release automation

## Constraints

- **Python Version:** 3.10+ minimum
- **Breaking Changes:** Deprecation warnings only - maintain backward compatibility
- **Scope:** Include CI/CD updates

## Module Structure

```
aiopulse/
├── __init__.py          # Public API, version, exports
├── hub.py               # Hub orchestrator (connect, run, commands)
├── transport.py         # Network transport abstraction (TCP/UDP)
├── roller.py            # Roller blind entity
├── room.py              # Room entity
├── scene.py             # Scene entity
├── timer.py             # Timer entity
├── callbacks.py         # NEW: CallbackMixin for shared callback logic
├── const.py             # Protocol constants (organized with enums)
├── errors.py            # Exception hierarchy
└── utils.py             # Serialization helpers
```

## Changes by Category

### 1. Modernization Changes

#### 1.1 asyncio Updates

**Remove `loop` parameter:**
- `Hub.__init__(host=None, loop=None)` → `Hub.__init__(host=None)`
- `Hub.discover(timeout=5, loop=None)` → `Hub.discover(timeout=5)`
- Add deprecation warning if `loop` parameter is passed:
  ```python
  def __init__(self, host=None, loop=None):
      if loop is not None:
          warnings.warn(
              "loop parameter is deprecated and will be removed in v0.6.0",
              DeprecationWarning,
              stacklevel=2
          )
  ```

**Replace event loop access:**
- `asyncio.get_event_loop()` → `asyncio.get_running_loop()`
- Store loop reference only when needed for callbacks

**Task creation:**
- Use `asyncio.create_task()` directly instead of `loop.create_task()`
- Remove `async_add_job` method from Hub (move to CallbackMixin)

#### 1.2 Type Hint Updates

Use Python 3.10+ type hint syntax:
- `Optional[X]` → `X | None`
- `List[X]` → `list[X]`
- `Dict[K, V]` → `dict[K, V]`
- `Callable[..., Any]` → `Callable[..., Any]` (unchanged)
- Add return type annotations to all public methods

Example:
```python
# Before
def __init__(self, host=None, loop: Optional[asyncio.events.AbstractEventLoop] = None):
    self.rollers: dict[int, aiopulse.Roller] = {}
    self.update_callbacks: List[Callable] = []

# After
def __init__(self, host: str | None = None, loop: asyncio.AbstractEventLoop | None = None):
    self.rollers: dict[int, Roller] = {}
    self._update_callbacks: list[Callable[..., None]] = []
```

#### 1.3 Lock Management

Convert manual lock patterns to context managers:

**Before (error-prone):**
```python
await self.command_lock.acquire()
try:
    self.protocol.send(buffer)
    await asyncio.wait_for(self.command_lock.acquire(), timeout=timeout)
except asyncio.TimeoutError:
    attempt += 1
finally:
    if self.command_lock.locked():
        self.command_lock.release()
```

**After (safe):**
```python
async with self.command_lock:
    self.protocol.send(buffer)
    try:
        await asyncio.wait_for(self.command_lock.acquire(), timeout=timeout)
    except asyncio.TimeoutError:
        attempt += 1
```

#### 1.4 Duplicate Exception Fix

Remove duplicate `InvalidResponseException` catch in `hub.py:704-708`:

**Before:**
```python
except errors.InvalidResponseException as inst:
    _LOGGER.warning(f"{self.host}: Handshake failed {inst}")
    await self.disconnect()
except errors.InvalidResponseException as inst:  # DUPLICATE!
    _LOGGER.warning(f"{self.host}: Protocol error {inst}")
```

**After:**
```python
except errors.InvalidResponseException as inst:
    _LOGGER.warning(f"{self.host}: Protocol error {inst}")
    await self.disconnect()
```

### 2. Resilience Improvements

#### 2.1 Bounds Checking in Response Parsers

All `response_*` methods must validate message length before parsing:

```python
def response_hubinfo(self, message: bytes) -> None:
    """Receive start of hub information."""
    if len(message) < 10:
        raise InvalidResponseException(
            f"Hub info message too short: {len(message)} bytes"
        )
    ptr = 10
    # ... rest of parsing
```

Apply to:
- `response_hubinfo()`
- `response_roller_updated()`
- `response_roomlist()`
- `response_rollerlist()`
- `response_scenelist()`
- `response_timerlist()`
- `response_position()`
- `response_rollerhealth()`
- `response_authinfo()`

#### 2.2 Transport State Validation

Add explicit connection state checks:

```python
def send(self, buffer: bytes) -> None:
    """Send buffer to hub."""
    if not self.writer or self.writer.is_closing():
        raise NotConnectedException("Transport not connected")
    self.writer.write(buffer)
```

#### 2.3 Health Lock Safety

Fix unsafe `health_lock.release()` in `response_rollerhealth()`:

**Before:**
```python
if self.health_lock.locked():
    self.health_lock.release()
```

**After:**
```python
# Use event-based signaling instead of lock release
self._health_event.set()
```

#### 2.4 Error Context

Add context to exceptions for better debugging:

```python
class InvalidResponseException(HubBaseException):
    """Exception thrown when an invalid response is received."""
    def __init__(self, message: str = "", response: bytes | None = None):
        super().__init__(message)
        self.response = response
```

### 3. Code Deduplication

#### 3.1 CallbackMixin (new `callbacks.py`)

Extract shared callback logic:

```python
"""Callback mixin for hub entities."""
from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable

_LOGGER = logging.getLogger(__name__)


class CallbackMixin:
    """Mixin for entities that support update callbacks."""

    def __init__(self) -> None:
        """Initialize callback list."""
        self._update_callbacks: list[Callable[..., None]] = []

    def callback_subscribe(self, callback: Callable[..., None]) -> None:
        """Add a callback for updates."""
        self._update_callbacks.append(callback)

    def callback_unsubscribe(self, callback: Callable[..., None]) -> None:
        """Remove a callback for updates."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)

    def notify_callback(self, *args: Any) -> None:
        """Notify all callbacks of an update."""
        for callback in self._update_callbacks:
            self._schedule_callback(callback, *args)

    def _schedule_callback(
        self, target: Callable[..., Any], *args: Any
    ) -> asyncio.Task | None:
        """Schedule a callback to run asynchronously.

        Must be called from within the event loop.
        """
        loop = asyncio.get_running_loop()

        # Check for partials to properly determine if coroutine function
        check_target = target
        while isinstance(check_target, functools.partial):
            check_target = check_target.func

        if asyncio.iscoroutine(check_target):
            return loop.create_task(target)  # type: ignore
        elif asyncio.iscoroutinefunction(check_target):
            return loop.create_task(target(*args))
        else:
            return loop.run_in_executor(None, target, *args)  # type: ignore
```

#### 3.2 HubEntity Base Class

Extract common entity patterns into a base class. Roller, Room, Scene, and Timer all share:
- `hub` reference
- `id` field
- `name` field
- `icon` field (Room, Scene, Timer)
- Callback mixin functionality

```python
"""Base class for hub entities."""
from __future__ import annotations

from aiopulse.callbacks import CallbackMixin


class HubEntity(CallbackMixin):
    """Base class for entities managed by a hub."""

    def __init__(self, hub: Hub, entity_id: bytes | int) -> None:
        """Initialize entity."""
        super().__init__()
        self.hub = hub
        self.id = entity_id
        self.name: str | None = None
        self.icon: int | None = None
```

**Implementation:** Roller, Room, Scene, and Timer will all inherit from HubEntity. The `icon` attribute will be optional (defaulting to None) since Roller doesn't use it.

#### 3.3 Protocol Constants Organization

Organize constants with enums and descriptive names:

```python
"""Acmeda Pulse Hub constants."""
from enum import IntEnum


class MessageType(IntEnum):
    """Protocol message types."""
    HUB_INFO = 0x1600
    HUB_INFO_UPDATED = 0x0D00
    ROOM_LIST = 0x0101
    SCENE_LIST = 0x3301
    ROLLER_LIST = 0x2101
    TIMER_LIST = 0x4101
    AUTH_INFO = 0x0800
    POSITION = 0x2301
    ROLLER_UPDATED = 0x2501
    TIMER_CREATED = 0x4301
    TIMER_DEVICE_UPDATED = 0x4501
    TIMER_INFO_UPDATED = 0x4901
    TIMER_DELETED = 0x4701
    ROLLER_HEALTH = 0x2B01
    DISCOVER_RESPONSE = 0x0F00


class CommandType(IntEnum):
    """Command message types."""
    DISCOVER = 0x03000003
    CONNECT = 0x03000006
    LOGIN = 0x0F000008
    PING = 0x03000015
    SETID = 0x28000090
    UNKNOWN1 = 0x23000090
    GET_HUB_INFO = 0x1E000090
    MOVE_TO = 0x34000090
    MOVE = 0x2D000090
    GET_HEALTH = 0x32000090


class ResponseType(IntEnum):
    """Response message types."""
    DISCOVER = 0x57000004
    CONNECT = 0x0F000007
    LOGIN = 0x04000009
    PING = 0x03000016
    SETID = 0x03000091
    UNKNOWN1 = 0x28000091
    GET_HUB_INFO = 0x4A000091
    MOVE_TO = 0x34000091
    GET_ROOMS = 0x01000091
    GET_ROLLERS = 0x03000091


HEADER = bytes.fromhex("00000003")
```

### 4. CI/CD Updates

#### 4.1 GitHub Actions (`python-app.yml`)

```yaml
name: Python application

on:
  push:
    branches: ["master"]
  pull_request:
    branches: ["master"]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Lint with ruff
      run: ruff check .
    - name: Type check with mypy
      run: mypy aiopulse
    - name: Test with pytest
      run: pytest --cov=aiopulse --cov-report=xml
    - name: Build package
      run: python -m build
```

#### 4.2 GitHub Actions (`python-release.yml`)

```yaml
name: Release to PyPI

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write
  id-token: write

jobs:
  release:
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/aiopulse

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python 3.10
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Run tests
      run: pytest
    - name: Build package
      run: python -m build
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        generate_release_notes: true
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
```

#### 4.3 Pre-commit Hooks (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        args:
          - --safe
          - --quiet
        files: ^((aiopulse)/.+)?[^/]+\.py$
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args:
          - --fix
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        files: ^aiopulse/.+\.py$
  - repo: https://github.com/codespell-project/codespell
    rev: v2.2.6
    hooks:
      - id: codespell
        args:
          - --ignore-words-list=aiopulse,acmeda
          - --skip="./.*,*.json"
          - --quiet-level=2
        exclude_types: [json]
```

#### 4.4 pyproject.toml Updates

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "aiopulse"
version = "0.5.0"
requires-python = ">=3.10"
# ... other metadata

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.4",
    "black>=24.0",
    "build>=1.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
target-version = "py310"
line-length = 88
select = ["E", "F", "I", "N", "W", "UP"]
```

#### 4.5 Type Checking Support

Add `py.typed` marker file:
```
aiopulse/py.typed
```

### 5. Testing Strategy

#### 5.1 Test Fixes

Fix async test patterns:

**Before (anti-pattern):**
```python
def test_callback_subscribe(self, hub):
    callback = MagicMock()
    hub.callback_subscribe(callback)
    assert callback in hub.update_callbacks
```

**After (proper async):**
```python
@pytest.mark.asyncio
async def test_callback_subscribe(self, hub):
    callback = MagicMock()
    hub.callback_subscribe(callback)
    assert callback in hub._update_callbacks
```

#### 5.2 New Tests

**CallbackMixin tests (`test_callbacks.py`):**
- Test subscribe/unsubscribe
- Test notify_callback with sync, async, and coroutine callbacks
- Test error handling in callbacks

**Bounds checking tests:**
- Test each response parser with truncated messages
- Test with exact minimum length messages
- Test with valid messages

**Deprecation warning tests:**
- Test that passing `loop` parameter emits DeprecationWarning
- Test that old method signatures still work

**Integration tests (`test_integration.py`):**
- Test full hub lifecycle (connect → update → disconnect)
- Test reconnection logic
- Test command retry logic

#### 5.3 Coverage Target

- Maintain current test coverage
- Add tests for all new code
- Add regression tests for fixed bugs
- Target: 80%+ line coverage

### 6. Version Management

#### 6.1 Version Bump

Update version from 0.4.7 to 0.5.0:
- `pyproject.toml`: `version = "0.5.0"`
- `setup.py`: `version="0.5.0"` (if kept)
- `aiopulse/__init__.py`: `__version__ = "0.5.0"`

#### 6.2 Changelog

Add CHANGELOG.md:
```markdown
# Changelog

## [0.5.0] - 2026-08-01

### Changed
- Minimum Python version is now 3.10
- Modernized asyncio patterns (removed loop parameter deprecation)
- Updated type hints to Python 3.10+ syntax
- Improved error handling with bounds checking
- Extracted CallbackMixin for shared callback logic
- Updated CI/CD with testing and type checking

### Deprecated
- `loop` parameter in Hub.__init__() and Hub.discover()
- Old callback method names (use new names with same signatures)

### Fixed
- Duplicate InvalidResponseException catch in hub.py
- Unsafe lock management in send_command()
- Missing bounds checking in response parsers
```

### 7. Migration Guide

For users upgrading from 0.4.x to 0.5.0:

```python
# Old (still works with deprecation warning)
hub = aiopulse.Hub(host="192.168.1.100", loop=loop)

# New (recommended)
hub = aiopulse.Hub(host="192.168.1.100")

# Callback subscription - API unchanged
hub.callback_subscribe(my_callback)
hub.callback_unsubscribe(my_callback)

# Roller callback subscription - API unchanged
roller.callback_subscribe(my_callback)
roller.callback_unsubscribe(my_callback)

# Room callback subscription - API unchanged
room.callback_subscribe(my_callback)
room.callback_unsubscribe(my_callback)
```

**Note:** All callback method names remain the same. The only change is that the internal implementation is now shared via CallbackMixin.

## Success Criteria

1. All existing tests pass
2. New tests added for all changes
3. mypy passes with no errors
4. ruff passes with no errors
5. CI/CD runs tests on Python 3.10, 3.11, 3.12
6. Release workflow successfully publishes to PyPI
7. No breaking changes for existing users
