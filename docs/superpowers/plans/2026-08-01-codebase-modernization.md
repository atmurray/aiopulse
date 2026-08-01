# Aiopulse Codebase Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize the aiopulse library for Python 3.10+, improve resilience, reduce code duplication, and update CI/CD.

**Architecture:** Incremental refactoring of existing modules with deprecation warnings for backward compatibility. Extract shared callback logic into mixin, add bounds checking to protocol parsers, modernize asyncio patterns.

**Tech Stack:** Python 3.10+, asyncio, pytest, mypy, ruff, GitHub Actions

## Global Constraints

- Minimum Python version: 3.10
- Breaking changes: Deprecation warnings only - maintain backward compatibility
- All existing tests must continue to pass
- New code must have type annotations
- All public methods must have docstrings

---

## File Structure

```
aiopulse/
├── __init__.py          # Modify: update version, exports
├── hub.py               # Modify: modernize asyncio, add bounds checking
├── transport.py         # Modify: add state validation
├── roller.py            # Modify: inherit from HubEntity
├── room.py              # Modify: inherit from HubEntity
├── scene.py             # Modify: inherit from HubEntity
├── timer.py             # Modify: inherit from HubEntity
├── callbacks.py         # Create: CallbackMixin
├── entities.py          # Create: HubEntity base class
├── const.py             # Modify: organize with enums
├── errors.py            # Modify: add context to exceptions
├── utils.py             # Minor: type hints
├── py.typed             # Create: marker file

tests/
├── conftest.py          # Modify: update fixtures
├── test_callbacks.py    # Create: CallbackMixin tests
├── test_entities.py     # Create: HubEntity tests
├── test_hub.py          # Modify: add bounds checking tests
├── test_transport.py    # Modify: add state validation tests
├── test_roller.py       # Modify: update for HubEntity
├── test_room.py         # Modify: update for HubEntity
├── test_scene.py        # Modify: update for HubEntity
├── test_timer.py        # Modify: update for HubEntity

.github/workflows/
├── python-app.yml       # Modify: add tests, mypy, update actions
├── python-release.yml   # Create: release workflow

.pre-commit-config.yaml  # Modify: update hooks
pyproject.toml           # Modify: add dev deps, tool configs
setup.py                 # Modify: update version
CHANGELOG.md             # Create: changelog
```

---

### Task 1: Update pyproject.toml and Setup Configuration

**Files:**
- Modify: `pyproject.toml`
- Modify: `setup.py`
- Modify: `aiopulse/__init__.py`
- Create: `aiopulse/py.typed`

**Interfaces:**
- Produces: Updated version (0.5.0), dev dependencies, tool configurations

- [ ] **Step 1: Update pyproject.toml with dev dependencies and tool configs**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "aiopulse"
version = "0.5.0"
authors = [
  { name="Alan Murray", email="pypi@atmurray.net" },
]
description = """
Asynchronous library to control Rollease Acmeda Automate roller blinds via a version 1 Pulse Hub.
"""
readme = "README.md"
license = {file = 'LICENSE'}
requires-python = ">=3.10"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]

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

[project.urls]
Homepage = "https://github.com/atmurray/aiopulse"
Issues = "https://github.com/atmurray/aiopulse/issues"

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

[tool.bumpver]
current_version = "0.5.0"
version_pattern = "MAJOR.MINOR.PATCH"
commit_message  = "Bump version {old_version} -> {new_version}"
commit          = true
tag             = true
push            = false

[tool.bumpver.file_patterns]
"pyproject.toml" = [
    'current_version = "{version}"',
    'version = "{version}"',
]
"setup.py" = [
    "{version}"
]
```

- [ ] **Step 2: Update setup.py version**

```python
"""Pip setup file for aiopulse library."""

from setuptools import setup

setup(
    name="aiopulse",
    packages=["aiopulse"],
    version="0.5.0",
    license="apache-2.0",
    description="Python module for Rollease Acmeda Automate integration.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Alan Murray",
    author_email="pypi@atmurray.net",
    url="https://github.com/atmurray/aiopulse",
    download_url="https://github.com/atmurray/aiopulse/archive/v0.5.0.tar.gz",
    keywords=["automation"],
    python_requires=">=3.10",
    install_requires=["async_timeout"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
)
```

- [ ] **Step 3: Update aiopulse/__init__.py version**

```python
"""Rollease Acmeda Automate Pulse asyncio protocol implementation."""
import logging

from aiopulse.hub import Hub
from aiopulse.roller import Roller
from aiopulse.room import Room
from aiopulse.scene import Scene
from aiopulse.timer import Timer
from aiopulse.errors import (
    CannotConnectException,
    NotConnectedException,
    NotRunningException,
    InvalidResponseException,
)
from aiopulse.const import UpdateType

__all__ = [
    "Hub",
    "Roller",
    "Room",
    "Scene",
    "Timer",
    "CannotConnectException",
    "NotConnectedException",
    "NotRunningException",
    "InvalidResponseException",
    "UpdateType",
]
__version__ = "0.5.0"
__author__ = "Alan Murray"

_LOGGER = logging.getLogger(__name__)
```

- [ ] **Step 4: Create py.typed marker file**

Create empty file `aiopulse/py.typed` (no content needed).

- [ ] **Step 5: Run tests to verify nothing broke**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml setup.py aiopulse/__init__.py aiopulse/py.typed
git commit -m "chore: update version to 0.5.0 and add dev dependencies"
```

---

### Task 2: Update Errors Module with Context

**Files:**
- Modify: `aiopulse/errors.py`

**Interfaces:**
- Consumes: None
- Produces: Enhanced exception classes with optional context

- [ ] **Step 1: Write tests for enhanced errors**

```python
# tests/test_errors.py
import pytest
from aiopulse.errors import (
    HubBaseException,
    NotConnectedException,
    NotRunningException,
    CannotConnectException,
    InvalidResponseException,
)


class TestHubBaseException:
    def test_basic_creation(self):
        exc = HubBaseException("test message")
        assert str(exc) == "test message"

    def test_with_response_context(self):
        response = b"\x00\x01\x02\x03"
        exc = HubBaseException("test message", response=response)
        assert exc.response == response


class TestInvalidResponseException:
    def test_basic_creation(self):
        exc = InvalidResponseException("invalid response")
        assert str(exc) == "invalid response"
        assert exc.response is None

    def test_with_response(self):
        response = b"\xff\xff\xff\xff"
        exc = InvalidResponseException("invalid header", response=response)
        assert exc.response == response
        assert b"\xff\xff" in exc.response


class TestNotConnectedException:
    def test_basic_creation(self):
        exc = NotConnectedException("not connected")
        assert str(exc) == "not connected"


class TestCannotConnectException:
    def test_basic_creation(self):
        exc = CannotConnectException("connection refused")
        assert str(exc) == "connection refused"


class TestNotRunningException:
    def test_basic_creation(self):
        exc = NotRunningException("not running")
        assert str(exc) == "not running"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_errors.py -v`
Expected: FAIL (ImportError or tests fail)

- [ ] **Step 3: Update errors.py with context support**

```python
"""Error classes of aiopulse module."""
from __future__ import annotations


class HubBaseException(Exception):
    """Base Exception for protocol."""

    def __init__(
        self, message: str = "", response: bytes | None = None
    ) -> None:
        """Initialize exception with optional response context."""
        super().__init__(message)
        self.response = response


class NotConnectedException(HubBaseException):
    """Exception thrown when the hub isn't connected."""

    pass


class NotRunningException(HubBaseException):
    """Exception thrown when the hub isn't running."""

    pass


class CannotConnectException(HubBaseException):
    """Exception thrown when a socket connection cannot be made."""

    pass


class InvalidResponseException(HubBaseException):
    """Exception thrown when an invalid response is received."""

    pass
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_errors.py -v`
Expected: All tests pass

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add aiopulse/errors.py tests/test_errors.py
git commit -m "feat: add response context to exception classes"
```

---

### Task 3: Create CallbackMixin

**Files:**
- Create: `aiopulse/callbacks.py`
- Create: `tests/test_callbacks.py`

**Interfaces:**
- Produces: `CallbackMixin` class with `callback_subscribe`, `callback_unsubscribe`, `notify_callback`

- [ ] **Step 1: Write tests for CallbackMixin**

```python
# tests/test_callbacks.py
import asyncio
from unittest.mock import MagicMock, AsyncMock

import pytest

from aiopulse.callbacks import CallbackMixin


class ConcreteCallbackEntity(CallbackMixin):
    """Concrete implementation for testing."""

    pass


class TestCallbackMixin:
    @pytest.fixture
    def entity(self):
        return ConcreteCallbackEntity()

    def test_init_empty_callbacks(self, entity):
        assert entity._update_callbacks == []

    def test_callback_subscribe(self, entity):
        callback = MagicMock()
        entity.callback_subscribe(callback)
        assert callback in entity._update_callbacks

    def test_callback_unsubscribe(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.callback_unsubscribe(callback)
        assert callback not in entity._update_callbacks

    def test_callback_unsubscribe_not_found(self, entity):
        callback = MagicMock()
        entity.callback_unsubscribe(callback)
        assert entity._update_callbacks == []

    def test_callback_multiple_subscribers(self, entity):
        callback1 = MagicMock()
        callback2 = MagicMock()
        entity.callback_subscribe(callback1)
        entity.callback_subscribe(callback2)
        assert len(entity._update_callbacks) == 2
        assert callback1 in entity._update_callbacks
        assert callback2 in entity._update_callbacks

    def test_notify_callback_sync(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.notify_callback()
        callback.assert_called_once()

    def test_notify_callback_with_args(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.notify_callback("arg1", "arg2")
        callback.assert_called_once_with("arg1", "arg2")

    def test_notify_callback_multiple(self, entity):
        callback1 = MagicMock()
        callback2 = MagicMock()
        entity._update_callbacks.append(callback1)
        entity._update_callbacks.append(callback2)
        entity.notify_callback()
        callback1.assert_called_once()
        callback2.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_callback_async(self, entity):
        callback = AsyncMock()
        entity._update_callbacks.append(callback)
        entity.notify_callback()
        await asyncio.sleep(0.1)
        callback.assert_called_once()

    def test_notify_callback_coroutine(self, entity):
        called = False

        async def callback():
            nonlocal called
            called = True

        entity._update_callbacks.append(callback)
        entity.notify_callback()
        # Note: coroutine won't execute without event loop running
        # This tests that it doesn't raise
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_callbacks.py -v`
Expected: FAIL (ImportError: cannot import 'CallbackMixin')

- [ ] **Step 3: Create CallbackMixin**

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
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            _LOGGER.warning("No running event loop, callback not scheduled")
            return None

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

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_callbacks.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/callbacks.py tests/test_callbacks.py
git commit -m "feat: add CallbackMixin for shared callback logic"
```

---

### Task 4: Create HubEntity Base Class

**Files:**
- Create: `aiopulse/entities.py`
- Create: `tests/test_entities.py`

**Interfaces:**
- Produces: `HubEntity` class inheriting from `CallbackMixin`

- [ ] **Step 1: Write tests for HubEntity**

```python
# tests/test_entities.py
import pytest
from unittest.mock import MagicMock

from aiopulse.entities import HubEntity


class ConcreteEntity(HubEntity):
    """Concrete implementation for testing."""

    pass


class TestHubEntity:
    @pytest.fixture
    def hub_mock(self):
        hub = MagicMock()
        hub.host = "192.168.1.100"
        return hub

    @pytest.fixture
    def entity(self, hub_mock):
        return ConcreteEntity(hub=hub_mock, entity_id=123)

    def test_init_with_int_id(self, hub_mock):
        entity = ConcreteEntity(hub=hub_mock, entity_id=123)
        assert entity.hub == hub_mock
        assert entity.id == 123
        assert entity.name is None
        assert entity.icon is None
        assert entity._update_callbacks == []

    def test_init_with_bytes_id(self, hub_mock):
        entity = ConcreteEntity(hub=hub_mock, entity_id=b"\x01\x02\x03\x04")
        assert entity.id == b"\x01\x02\x03\x04"

    def test_callback_subscribe(self, entity):
        callback = MagicMock()
        entity.callback_subscribe(callback)
        assert callback in entity._update_callbacks

    def test_callback_unsubscribe(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.callback_unsubscribe(callback)
        assert callback not in entity._update_callbacks

    def test_notify_callback(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.notify_callback()
        callback.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_entities.py -v`
Expected: FAIL (ImportError: cannot import 'HubEntity')

- [ ] **Step 3: Create HubEntity base class**

```python
"""Base class for hub entities."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiopulse.callbacks import CallbackMixin

if TYPE_CHECKING:
    from aiopulse.hub import Hub


class HubEntity(CallbackMixin):
    """Base class for entities managed by a hub."""

    def __init__(self, hub: Hub, entity_id: bytes | int) -> None:
        """Initialize entity.

        Args:
            hub: The hub instance that manages this entity.
            entity_id: The unique identifier for this entity.
        """
        super().__init__()
        self.hub = hub
        self.id = entity_id
        self.name: str | None = None
        self.icon: int | None = None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_entities.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/entities.py tests/test_entities.py
git commit -m "feat: add HubEntity base class for hub entities"
```

---

### Task 5: Update Room to Use HubEntity

**Files:**
- Modify: `aiopulse/room.py`
- Modify: `tests/test_room.py`

**Interfaces:**
- Consumes: `HubEntity` from `aiopulse.entities`
- Produces: `Room` class inheriting from `HubEntity`

- [ ] **Step 1: Run existing room tests to establish baseline**

Run: `pytest tests/test_room.py -v`
Expected: All tests pass (or note current failures)

- [ ] **Step 2: Update room.py to use HubEntity**

```python
"""Room entity that hangs off the hub."""
from __future__ import annotations

from typing import TYPE_CHECKING

import aiopulse.utils as utils
import aiopulse.const as const
from aiopulse.entities import HubEntity

if TYPE_CHECKING:
    from aiopulse.hub import Hub


class Room(HubEntity):
    """Representation of a Room."""

    def __init__(self, hub: Hub, room_id: bytes) -> None:
        """Init a new room.

        Args:
            hub: The hub instance.
            room_id: The unique room identifier.
        """
        super().__init__(hub, room_id)

    def __str__(self) -> str:
        """Returns string representation of room."""
        return "Name: {} ID: {} Icon: {}".format(
            self.name, self.id[0:4] if isinstance(self.id, bytes) else self.id, self.icon
        )

    async def move_to(self, percent: int) -> None:
        """Send command to move the room to a percentage closed.

        Args:
            percent: Target position (0-100).
        """
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("190401030001")
            + utils.pack_int(percent, 2)
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            const.COMMAND_MOVE_TO, bytes.fromhex("2201"), message
        )

    async def move_up(self) -> None:
        """Send command to move the room to fully open."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("10")
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            const.COMMAND_MOVE, bytes.fromhex("2201"), message
        )

    async def move_stop(self) -> None:
        """Send command to stop the room."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("11")
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            const.COMMAND_MOVE, bytes.fromhex("2201"), message
        )

    async def move_down(self) -> None:
        """Send command to move the room to fully closed."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("12")
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            const.COMMAND_MOVE, bytes.fromhex("2201"), message
        )
```

- [ ] **Step 3: Update test_room.py for HubEntity**

```python
# tests/test_room.py
import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from aiopulse.room import Room


class TestRoom:
    @pytest.fixture
    def hub_mock(self):
        hub = MagicMock()
        hub.host = "192.168.1.100"
        hub.async_add_job = MagicMock(return_value=MagicMock())
        return hub

    @pytest.fixture
    def room(self, hub_mock):
        return Room(hub_mock, b"\x01\x02\x03\x04")

    def test_init(self, room):
        assert room.id == b"\x01\x02\x03\x04"
        assert room.name is None
        assert room.icon is None
        assert room.hub is not None
        assert room._update_callbacks == []

    def test_str(self, room):
        room.name = "Living Room"
        room.icon = 3
        result = str(room)
        assert "Living Room" in result

    def test_callback_subscribe(self, room):
        callback = MagicMock()
        room.callback_subscribe(callback)
        assert callback in room._update_callbacks

    def test_callback_unsubscribe(self, room):
        callback = MagicMock()
        room._update_callbacks.append(callback)
        room.callback_unsubscribe(callback)
        assert callback not in room._update_callbacks

    def test_notify_callback(self, room):
        callback = MagicMock()
        room._update_callbacks.append(callback)
        room.notify_callback()
        callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_to(self, room):
        room.hub.send_command = AsyncMock()
        await room.move_to(50)
        room.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_move_up(self, room):
        room.hub.send_command = AsyncMock()
        await room.move_up()
        room.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_move_stop(self, room):
        room.hub.send_command = AsyncMock()
        await room.move_stop()
        room.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_move_down(self, room):
        room.hub.send_command = AsyncMock()
        await room.move_down()
        room.hub.send_command.assert_awaited_once()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_room.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/room.py tests/test_room.py
git commit -m "refactor: Room inherits from HubEntity"
```

---

### Task 6: Update Scene to Use HubEntity

**Files:**
- Modify: `aiopulse/scene.py`
- Modify: `tests/test_scene.py`

**Interfaces:**
- Consumes: `HubEntity` from `aiopulse.entities`
- Produces: `Scene` class inheriting from `HubEntity`

- [ ] **Step 1: Update scene.py to use HubEntity**

```python
"""Scene entity that hangs off the hub."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiopulse.entities import HubEntity

if TYPE_CHECKING:
    from aiopulse.hub import Hub


class Scene(HubEntity):
    """Representation of a Scene."""

    def __init__(self, hub: Hub, scene_id: bytes) -> None:
        """Init a new scene.

        Args:
            hub: The hub instance.
            scene_id: The unique scene identifier.
        """
        super().__init__(hub, scene_id)

    def __str__(self) -> str:
        """Returns string representation of scene."""
        return "Name: {} ID: {} Icon: {}".format(
            self.name, self.id[0:4] if isinstance(self.id, bytes) else self.id, self.icon
        )
```

- [ ] **Step 2: Update test_scene.py for HubEntity**

```python
# tests/test_scene.py
from unittest.mock import MagicMock

import pytest

from aiopulse.scene import Scene


class TestScene:
    @pytest.fixture
    def hub_mock(self):
        hub = MagicMock()
        hub.host = "192.168.1.100"
        return hub

    @pytest.fixture
    def scene(self, hub_mock):
        return Scene(hub_mock, b"\x01\x02\x03\x04")

    def test_init(self, scene):
        assert scene.id == b"\x01\x02\x03\x04"
        assert scene.name is None
        assert scene.icon is None
        assert scene.hub is not None
        assert scene._update_callbacks == []

    def test_str(self, scene):
        scene.name = "Movie Night"
        scene.icon = 5
        result = str(scene)
        assert "Movie Night" in result

    def test_callback_subscribe(self, scene):
        callback = MagicMock()
        scene.callback_subscribe(callback)
        assert callback in scene._update_callbacks

    def test_callback_unsubscribe(self, scene):
        callback = MagicMock()
        scene._update_callbacks.append(callback)
        scene.callback_unsubscribe(callback)
        assert callback not in scene._update_callbacks

    def test_notify_callback(self, scene):
        callback = MagicMock()
        scene._update_callbacks.append(callback)
        scene.notify_callback()
        callback.assert_called_once()
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pytest tests/test_scene.py -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add aiopulse/scene.py tests/test_scene.py
git commit -m "refactor: Scene inherits from HubEntity"
```

---

### Task 7: Update Timer to Use HubEntity

**Files:**
- Modify: `aiopulse/timer.py`
- Modify: `tests/test_timer.py`

**Interfaces:**
- Consumes: `HubEntity` from `aiopulse.entities`
- Produces: `Timer` class inheriting from `HubEntity`

- [ ] **Step 1: Update timer.py to use HubEntity**

```python
"""Timer entity that hangs off the hub."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiopulse.entities import HubEntity

if TYPE_CHECKING:
    from aiopulse.hub import Hub


class Timer(HubEntity):
    """Representation of a Timer."""

    def __init__(self, hub: Hub, timer_id: bytes) -> None:
        """Init a new timer.

        Args:
            hub: The hub instance.
            timer_id: The unique timer identifier.
        """
        super().__init__(hub, timer_id)
        self.state: int | None = None
        self.hour: int | None = None
        self.minute: int | None = None
        self.days: int | None = None
        self.entity: HubEntity | None = None

    def __str__(self) -> str:
        """Returns string representation of timer."""
        return (
            f"Name: {self.name} "
            f"ID: {self.id[0:4] if isinstance(self.id, bytes) else self.id} "
            f"Icon: {self.icon} "
            f"State: {self.state} "
            f"Time: {self.hour}:{self.minute} "
            f"Days: {self.days:>07b} "
            f'Entity: {self.entity.name if self.entity else "None"}'
        )
```

- [ ] **Step 2: Update test_timer.py for HubEntity**

```python
# tests/test_timer.py
from unittest.mock import MagicMock

import pytest

from aiopulse.timer import Timer


class TestTimer:
    @pytest.fixture
    def hub_mock(self):
        hub = MagicMock()
        hub.host = "192.168.1.100"
        return hub

    @pytest.fixture
    def timer(self, hub_mock):
        return Timer(hub_mock, b"\x01\x02\x03\x04")

    def test_init(self, timer):
        assert timer.id == b"\x01\x02\x03\x04"
        assert timer.name is None
        assert timer.icon is None
        assert timer.state is None
        assert timer.hour is None
        assert timer.minute is None
        assert timer.days is None
        assert timer.entity is None
        assert timer.hub is not None
        assert timer._update_callbacks == []

    def test_str(self, timer):
        timer.name = "Morning Timer"
        timer.icon = 2
        timer.state = 1
        timer.hour = 7
        timer.minute = 30
        timer.days = 0b0111110
        result = str(timer)
        assert "Morning Timer" in result
        assert "7:30" in result

    def test_str_with_entity(self, timer):
        timer.name = "Morning Timer"
        timer.entity = MagicMock()
        timer.entity.name = "Living Room Blind"
        result = str(timer)
        assert "Living Room Blind" in result

    def test_str_without_entity(self, timer):
        timer.name = "Morning Timer"
        result = str(timer)
        assert "None" in result

    def test_callback_subscribe(self, timer):
        callback = MagicMock()
        timer.callback_subscribe(callback)
        assert callback in timer._update_callbacks

    def test_callback_unsubscribe(self, timer):
        callback = MagicMock()
        timer._update_callbacks.append(callback)
        timer.callback_unsubscribe(callback)
        assert callback not in timer._update_callbacks

    def test_notify_callback(self, timer):
        callback = MagicMock()
        timer._update_callbacks.append(callback)
        timer.notify_callback()
        callback.assert_called_once()
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pytest tests/test_timer.py -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add aiopulse/timer.py tests/test_timer.py
git commit -m "refactor: Timer inherits from HubEntity"
```

---

### Task 8: Update Roller to Use HubEntity

**Files:**
- Modify: `aiopulse/roller.py`
- Modify: `tests/test_roller.py`

**Interfaces:**
- Consumes: `HubEntity` from `aiopulse.entities`
- Produces: `Roller` class inheriting from `HubEntity`

- [ ] **Step 1: Run existing roller tests to establish baseline**

Run: `pytest tests/test_roller.py -v`
Expected: All tests pass

- [ ] **Step 2: Update roller.py to use HubEntity**

```python
"""Roller blind entity that hangs off the hub."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import aiopulse.utils as utils
import aiopulse.const as const
from aiopulse.entities import HubEntity

if TYPE_CHECKING:
    from aiopulse.hub import Hub

_LOGGER = logging.getLogger(__name__)


class Roller(HubEntity):
    """Representation of a Roller blind."""

    def __init__(self, hub: Hub, roller_id: int) -> None:
        """Init a new roller blind.

        Args:
            hub: The hub instance.
            roller_id: The unique roller identifier.
        """
        super().__init__(hub, roller_id)
        self.type: int | None = None
        self.serial: str | None = None
        self.room_id: bytes | None = None
        self.room: Room | None = None
        self.battery: int | None = None
        self.closed_percent: int | None = None
        self.flags: int = 0

        self.health_lock = asyncio.Lock()
        self.health_task = hub.async_add_job(self.health_updater)

    def __del__(self) -> None:
        """Cancel health updater task on deletion."""
        if self.health_task:
            self.health_task.cancel()

    def health_updated(self) -> None:
        """Signal that health data has been received."""
        try:
            self.health_lock.release()
        except RuntimeError:
            pass

    async def health_updater(self) -> None:
        """Periodically update roller health."""
        await self.get_health()
        running = True
        try:
            while running:
                try:
                    await asyncio.wait_for(
                        self.health_lock.acquire(), timeout=3600
                    )
                except asyncio.TimeoutError:
                    await self.get_health()
                except asyncio.CancelledError:
                    running = False
        except Exception as inst:
            _LOGGER.error(
                f"{self.hub.host}:{self.name}: health updater unhandled exception: {inst}"
            )
        _LOGGER.info(f"{self.hub.host}:{self.name}: health updater stopped")
        running = False

    def __str__(self) -> str:
        """Returns string representation of roller."""
        return (
            "Name: {} ID: {} Serial: {} Room: {} Type: {} Closed %: {} Battery %: {}"
            " Flags: {:08b}"
        ).format(
            self.name,
            self.id,
            self.serial,
            self.room.name if self.room else "None",
            self.type,
            self.closed_percent,
            self.battery,
            self.flags,
        )

    async def move_to(self, percent: int) -> None:
        """Send command to move the roller to a percentage closed.

        Args:
            percent: Target position (0-100).
        """
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("190401030001")
            + utils.pack_int(percent, 2)
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            const.COMMAND_MOVE_TO, bytes.fromhex("2201"), message
        )

    async def move_up(self) -> None:
        """Send command to move the roller to fully open."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("10")
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            const.COMMAND_MOVE, bytes.fromhex("2201"), message
        )

    async def move_stop(self) -> None:
        """Send command to stop the roller."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("11")
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            const.COMMAND_MOVE, bytes.fromhex("2201"), message
        )

    async def move_down(self) -> None:
        """Send command to move the roller to fully closed."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("12")
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            const.COMMAND_MOVE, bytes.fromhex("2201"), message
        )

    async def get_health(self) -> None:
        """Request health information from the roller."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("410201000E4202010004")
            + bytes.fromhex("ff")
        )
        await self.hub.send_healthcheck(
            const.GET_HEALTH, bytes.fromhex("2A01"), message
        )
```

- [ ] **Step 3: Update test_roller.py for HubEntity**

```python
# tests/test_roller.py
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiopulse.roller import Roller


class TestRoller:
    @pytest.fixture
    def hub_mock(self):
        hub = MagicMock()
        hub.host = "192.168.1.100"
        hub.async_add_job = MagicMock(return_value=MagicMock())
        return hub

    @pytest.fixture
    def roller(self, hub_mock):
        r = Roller(hub_mock, 123)
        r.health_task = MagicMock()  # prevent actual health updater from running
        r.health_lock = asyncio.Lock()
        yield r

    def test_init(self, roller):
        assert roller.id == 123
        assert roller.name is None
        assert roller.type is None
        assert roller.serial is None
        assert roller.room_id is None
        assert roller.room is None
        assert roller.battery is None
        assert roller.closed_percent is None
        assert roller.flags == 0
        assert roller._update_callbacks == []

    def test_init_inherits_hub_entity(self, roller):
        assert roller.hub is not None
        assert roller.id == 123

    def test_str(self, roller):
        roller.name = "Test Blind"
        roller.serial = "ABC123"
        roller.closed_percent = 50
        roller.battery = 75
        result = str(roller)
        assert "Test Blind" in result
        assert "ABC123" in result
        assert "50" in result
        assert "75" in result

    def test_str_with_room(self, roller):
        roller.name = "Living Room Blind"
        roller.room = MagicMock()
        roller.room.name = "Living Room"
        result = str(roller)
        assert "Living Room" in result

    def test_callback_subscribe(self, roller):
        callback = MagicMock()
        roller.callback_subscribe(callback)
        assert callback in roller._update_callbacks

    def test_callback_unsubscribe(self, roller):
        callback = MagicMock()
        roller._update_callbacks.append(callback)
        roller.callback_unsubscribe(callback)
        assert callback not in roller._update_callbacks

    def test_callback_unsubscribe_not_found(self, roller):
        callback = MagicMock()
        roller.callback_unsubscribe(callback)
        assert roller._update_callbacks == []

    def test_notify_callback(self, roller):
        callback = MagicMock()
        roller._update_callbacks.append(callback)
        roller.notify_callback()
        roller.hub.async_add_job.assert_called_with(callback)

    @pytest.mark.asyncio
    async def test_move_to(self, roller):
        roller.hub.send_command = AsyncMock()
        await roller.move_to(50)
        roller.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_move_up(self, roller):
        roller.hub.send_command = AsyncMock()
        await roller.move_up()
        roller.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_move_stop(self, roller):
        roller.hub.send_command = AsyncMock()
        await roller.move_stop()
        roller.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_move_down(self, roller):
        roller.hub.send_command = AsyncMock()
        await roller.move_down()
        roller.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_health(self, roller):
        roller.hub.send_healthcheck = AsyncMock()
        await roller.get_health()
        roller.hub.send_healthcheck.assert_awaited_once()

    def test_health_updated_releases_lock(self, roller):
        async def do_test():
            await roller.health_lock.acquire()
            roller.health_updated()
            assert not roller.health_lock.locked()

        asyncio.run(do_test())

    def test_health_updated_no_lock(self, roller):
        roller.health_updated()
        assert not roller.health_lock.locked()

    def test_del_cancels_task(self, roller):
        roller.health_task = MagicMock()
        roller.__del__()
        roller.health_task.cancel.assert_called_once()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_roller.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/roller.py tests/test_roller.py
git commit -m "refactor: Roller inherits from HubEntity"
```

---

### Task 9: Organize Protocol Constants with Enums

**Files:**
- Modify: `aiopulse/const.py`
- Modify: `tests/test_const.py`

**Interfaces:**
- Produces: `MessageType`, `CommandType`, `ResponseType` enums

- [ ] **Step 1: Write tests for new enums**

```python
# tests/test_const.py
import pytest
from aiopulse.const import UpdateType, MessageType, CommandType, ResponseType, HEADER


class TestUpdateType:
    def test_update_type_values(self):
        assert UpdateType.info.name == "info"
        assert UpdateType.rollers.name == "rollers"
        assert UpdateType.rooms.name == "rooms"
        assert UpdateType.scenes.name == "scenes"
        assert UpdateType.timers.name == "timers"


class TestMessageType:
    def test_message_type_values(self):
        assert MessageType.HUB_INFO == 0x1600
        assert MessageType.ROOM_LIST == 0x0101
        assert MessageType.ROLLER_LIST == 0x2101
        assert MessageType.SCENE_LIST == 0x3301
        assert MessageType.TIMER_LIST == 0x4101
        assert MessageType.POSITION == 0x2301
        assert MessageType.ROLLER_UPDATED == 0x2501
        assert MessageType.ROLLER_HEALTH == 0x2B01

    def test_message_type_is_int(self):
        assert isinstance(MessageType.HUB_INFO, int)


class TestCommandType:
    def test_command_type_values(self):
        assert CommandType.DISCOVER == 0x03000003
        assert CommandType.CONNECT == 0x03000006
        assert CommandType.LOGIN == 0x0F000008
        assert CommandType.PING == 0x03000015
        assert CommandType.SETID == 0x28000090
        assert CommandType.GET_HUB_INFO == 0x1E000090
        assert CommandType.MOVE_TO == 0x34000090
        assert CommandType.MOVE == 0x2D000090
        assert CommandType.GET_HEALTH == 0x32000090


class TestResponseType:
    def test_response_type_values(self):
        assert ResponseType.DISCOVER == 0x57000004
        assert ResponseType.CONNECT == 0x0F000007
        assert ResponseType.LOGIN == 0x04000009
        assert ResponseType.PING == 0x03000016
        assert ResponseType.SETID == 0x03000091
        assert ResponseType.GET_HUB_INFO == 0x4A000091
        assert ResponseType.MOVE_TO == 0x34000091


class TestConstants:
    def test_header(self):
        assert HEADER == bytes.fromhex("00000003")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_const.py -v`
Expected: FAIL (ImportError for new enums)

- [ ] **Step 3: Update const.py with organized enums**

```python
"""Acmeda Pulse Hub constants."""
from enum import Enum, IntEnum


class UpdateType(Enum):
    """Types of hub updates."""
    info = "info"
    rollers = "rollers"
    rooms = "rooms"
    scenes = "scenes"
    timers = "timers"


class MessageType(IntEnum):
    """Protocol message types for incoming messages."""
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

# Keep old constants for backward compatibility
COMMAND_DISCOVER = bytes.fromhex("03000003")
RESPONSE_DISCOVER = bytes.fromhex("57000004")

COMMAND_CONNECT = bytes.fromhex("03000006")
RESPONSE_CONNECT = bytes.fromhex("0f000007")

COMMAND_LOGIN = bytes.fromhex("0f000008")
RESPONSE_LOGIN = bytes.fromhex("04000009")

COMMAND_PING = bytes.fromhex("03000015")
RESPONSE_PING = bytes.fromhex("03000016")

COMMAND_SETID = bytes.fromhex("28000090")
RESPONSE_SETID = bytes.fromhex("03000091")

COMMAND_UNKNOWN1 = bytes.fromhex("23000090")
RESPONSE_UNKNOWN1 = bytes.fromhex("28000091")

COMMAND_GET_HUB_INFO = bytes.fromhex("1e000090")
RESPONSE_GET_HUB_INFO = bytes.fromhex("4a000091")

COMMAND_MOVE_TO = bytes.fromhex("34000090")
RESPOSE_MOVE_TO = bytes.fromhex("34000091")

COMMAND_MOVE = bytes.fromhex("2d000090")

GET_ROOMS = bytes.fromhex("01000091")
GET_ROLLERS = bytes.fromhex("03000091")

GET_HEALTH = bytes.fromhex("32000090")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_const.py -v`
Expected: All tests pass

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add aiopulse/const.py tests/test_const.py
git commit -m "refactor: organize protocol constants with enums"
```

---

### Task 10: Modernize Hub asyncio Patterns

**Files:**
- Modify: `aiopulse/hub.py`

**Interfaces:**
- Produces: Modernized Hub class with deprecation warnings for loop parameter

- [ ] **Step 1: Run existing hub tests to establish baseline**

Run: `pytest tests/test_hub.py -v`
Expected: All tests pass (note any current failures)

- [ ] **Step 2: Update hub.py asyncio patterns**

Key changes:
- Remove `loop` parameter from `__init__()` and `discover()` with deprecation warning
- Replace `asyncio.get_event_loop()` with `asyncio.get_running_loop()`
- Use `asyncio.create_task()` instead of `loop.create_task()`
- Fix duplicate `InvalidResponseException` catch in `run()` method
- Add bounds checking to all `response_*` methods
- Use context managers for locks where safe

```python
"""Acmeda Pulse Hub Interface."""
from __future__ import annotations

import asyncio
import binascii
import logging
import warnings
from typing import Any, Callable

import async_timeout

import aiopulse.const as const
import aiopulse.utils as utils
import aiopulse.errors as errors
import aiopulse.transport

_LOGGER = logging.getLogger(__name__)


class Hub:
    """Representation of an Acmeda Pulse Hub."""

    def __init__(
        self, host: str | None = None, loop: asyncio.AbstractEventLoop | None = None
    ) -> None:
        """Init the hub.

        Args:
            host: The hub's IP address or hostname.
            loop: Deprecated. The event loop to use.
        """
        if loop is not None:
            warnings.warn(
                "loop parameter is deprecated and will be removed in v0.6.0",
                DeprecationWarning,
                stacklevel=2,
            )

        self.topic: bytes = str.encode("Smart_Id1_y:")
        self.sequence: int = 4
        self.handshake: asyncio.Event = asyncio.Event()
        self.command_lock: asyncio.Lock = asyncio.Lock()
        self.health_lock: asyncio.Lock = asyncio.Lock()
        self.response_task: asyncio.Task | None = None
        self.running: bool = False

        self.id: str | None = None
        self.host: str | None = host
        self.mac_address: str | None = None
        self.ip_address: str | None = None
        self.firmware_name: str | None = None
        self.wifi_module: str | None = None

        self.protocol = aiopulse.transport.HubTransportTcp(host)

        self.rollers: dict[int, aiopulse.Roller] = {}
        self.rooms: dict[int, aiopulse.Room] = {}
        self.scenes: dict[int, aiopulse.Scene] = {}
        self.timers: dict[int, aiopulse.Timer] = {}

        self.handshake.clear()
        self._update_callbacks: list[Callable[..., None]] = []

    def __str__(self) -> str:
        """Returns string representation of the hub."""
        return (
            f"ID: {self.id} "
            f"Host: {self.host} "
            f"MAC: {self.mac_address} "
            f"Firmware: {self.firmware_name} "
            f"WiFi: {self.wifi_module} "
        )

    # ... (keep existing methods but update with bounds checking and modern asyncio)
```

- [ ] **Step 3: Add bounds checking to response methods**

For each `response_*` method, add length validation:

```python
def response_hubinfo(self, message: bytes) -> None:
    """Receive start of hub information."""
    if len(message) < 10:
        raise errors.InvalidResponseException(
            f"Hub info message too short: {len(message)} bytes",
            response=message,
        )
    ptr = 10
    # ... rest of parsing
```

- [ ] **Step 4: Fix duplicate exception catch in run()**

```python
# Before (duplicate):
except errors.InvalidResponseException as inst:
    _LOGGER.warning(f"{self.host}: Handshake failed {inst}")
    await self.disconnect()
except errors.InvalidResponseException as inst:
    _LOGGER.warning(f"{self.host}: Protocol error {inst}")

# After (single):
except errors.InvalidResponseException as inst:
    _LOGGER.warning(f"{self.host}: Protocol error {inst}")
    await self.disconnect()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_hub.py -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add aiopulse/hub.py
git commit -m "refactor: modernize hub asyncio patterns and add bounds checking"
```

---

### Task 11: Add Transport State Validation

**Files:**
- Modify: `aiopulse/transport.py`
- Modify: `tests/test_transport.py`

**Interfaces:**
- Produces: Enhanced transport with state validation

- [ ] **Step 1: Run existing transport tests to establish baseline**

Run: `pytest tests/test_transport.py -v`
Expected: All tests pass

- [ ] **Step 2: Update transport.py with state validation**

```python
"""Network transport abstraction for hub."""
from __future__ import annotations

import asyncio
import logging
import socket

from aiopulse.errors import NotConnectedException

_LOGGER = logging.getLogger(__name__)


class HubTransportBase(asyncio.Protocol):
    """Base class for Hub transport implementations."""

    def __init__(self) -> None:
        """Constructor for the base transport class."""
        self.transport: asyncio.Transport | None = None

    def connection_made(self, transport: asyncio.Transport) -> None:
        """Called when a connection is made."""
        _LOGGER.debug("Connection established")
        self.transport = transport

    def error_received(self, exc: Exception) -> None:
        """Called when an error is received."""
        _LOGGER.error("Error received: %s", exc)

    def connection_lost(self, exc: Exception | None) -> None:
        """Called when a connection is lost."""
        _LOGGER.debug("Socket closed")
        self.transport = None


class HubTransportUdp(HubTransportBase):
    """UDP Based Hub transport."""

    def __init__(self, host: str | None = None, port: int = 12414) -> None:
        """Constructor for UDP transport class."""
        super().__init__()
        self.host = host
        self.port = port
        self.protocol: asyncio.DatagramProtocol | None = None
        self.is_udp: bool = True
        self.receive_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self, host: str | None = None) -> None:
        """Initialise connection."""
        if host:
            self.host = host

        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: self,
            remote_addr=(self.host, self.port),
        )

    async def close(self) -> None:
        """Close the connection."""
        if self.transport:
            self.transport.close()
            _LOGGER.debug("UDP connection closed")

    def send(self, buffer: bytes) -> None:
        """Abstraction of the underlying transport to send a buffer."""
        if not self.transport:
            raise NotConnectedException("UDP transport not connected")
        self.transport.sendto(buffer, (self.host, self.port))

    async def receive(self) -> tuple[bytes, tuple[str, int]]:
        """Abstraction of the underlying transport to receive."""
        return await self.receive_queue.get()

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Callback for a received datagram, enqueue it."""
        _LOGGER.debug("UDP datagram received")
        self.receive_queue.put_nowait((data, addr))


class HubTransportUdpBroadcast(HubTransportUdp):
    """UDP Based Hub transport for broadcast discovery."""

    async def connect(self, host: str = "255.255.255.255") -> None:
        """Init connection."""
        if host:
            self.host = host
        addrinfo = socket.getaddrinfo(self.host, None)[0]
        sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        sock.sendto(b"0", ("<broadcast>", 1500))

        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: self,
            sock=sock,
        )


class HubTransportTcp(HubTransportBase):
    """TCP based Hub transport."""

    def __init__(self, host: str | None = None) -> None:
        """TCP Transport constructor."""
        super().__init__()
        self.host = host
        self.port: int = 12416

        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.protocol: asyncio.StreamReaderProtocol | None = None
        self.is_udp: bool = False
        self.connect_task: asyncio.Task | None = None

    async def do_connection(self) -> None:
        """Try and establish a TCP connection."""
        loop = asyncio.get_running_loop()
        self.reader = asyncio.StreamReader()
        self.protocol = asyncio.StreamReaderProtocol(self.reader)

        # The following blocks until a connection is made
        self.transport, _ = await loop.create_connection(
            lambda: self, self.host, self.port
        )
        self.writer = asyncio.StreamWriter(
            self.transport, self.protocol, self.reader, loop
        )

    async def connect(self, host: str | None = None) -> None:
        """Init connection."""
        if host:
            self.host = host

        if self.writer:
            _LOGGER.warning(f"{self.host}: Already connected.")
            return

        if self.connect_task and not self.connect_task.done():
            _LOGGER.warning(f"{self.host}: Already connecting.")
        else:
            self.connect_task = asyncio.create_task(self.do_connection())

        await self.connect_task

    async def close(self) -> None:
        """Close the connection."""
        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
                _LOGGER.debug(f"{self.host}: TCP buffer cleared.")
        except Exception as inst:
            _LOGGER.warning(f"{self.host}: Error closing writer cleanly: {inst}")
        finally:
            self.writer = None

        try:
            if self.transport:
                self.transport.close()
                _LOGGER.debug(f"{self.host}: TCP connection closed.")
            elif self.connect_task and not self.connect_task.done():
                self.connect_task.cancel()
            else:
                _LOGGER.warning(f"{self.host}: Not connected")
        except Exception as inst:
            _LOGGER.warning(f"{self.host}: Error closing TCP socket cleanly: {inst}")

    def send(self, buffer: bytes) -> None:
        """Abstraction of the underlying transport to send a buffer."""
        if not self.writer or self.writer.is_closing():
            raise NotConnectedException("TCP transport not connected")
        self.writer.write(buffer)

    async def receive(self) -> bytes:
        """Receive from stream."""
        if not self.writer or self.writer.is_closing():
            raise NotConnectedException("TCP transport not connected")
        if not self.reader:
            raise NotConnectedException("TCP reader not initialized")
        return await self.reader.read(65535)

    def data_received(self, data: bytes) -> None:
        """Callback when data has been received."""
        if self.protocol:
            self.protocol.data_received(data)

    def connection_made(self, transport: asyncio.Transport) -> None:
        """Callback when a connection has been made."""
        if self.protocol:
            self.protocol.connection_made(transport)
        super().connection_made(transport)

    def connection_lost(self, exc: Exception | None) -> None:
        """Callback when a connection is lost."""
        if self.protocol:
            self.protocol.connection_lost(exc)
        super().connection_lost(exc)
```

- [ ] **Step 3: Update test_transport.py with state validation tests**

Add tests for:
- `send()` when not connected raises `NotConnectedException`
- `receive()` when not connected raises `NotConnectedException`

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_transport.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/transport.py tests/test_transport.py
git commit -m "refactor: add transport state validation and modern asyncio"
```

---

### Task 12: Update CI/CD Workflows

**Files:**
- Modify: `.github/workflows/python-app.yml`
- Create: `.github/workflows/python-release.yml`
- Modify: `.pre-commit-config.yaml`

**Interfaces:**
- Produces: Updated CI/CD with testing and release automation

- [ ] **Step 1: Update python-app.yml**

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

- [ ] **Step 2: Create python-release.yml**

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

- [ ] **Step 3: Update .pre-commit-config.yaml**

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

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/python-app.yml .github/workflows/python-release.yml .pre-commit-config.yaml
git commit -m "ci: update workflows with testing and release automation"
```

---

### Task 13: Update Hub Callbacks to Use CallbackMixin

**Files:**
- Modify: `aiopulse/hub.py`

**Interfaces:**
- Consumes: `CallbackMixin` from `aiopulse.callbacks`
- Produces: Hub using CallbackMixin for callbacks

- [ ] **Step 1: Update hub.py to inherit from CallbackMixin**

```python
"""Acmeda Pulse Hub Interface."""
from __future__ import annotations

import asyncio
import binascii
import logging
import warnings
from typing import Any, Callable

import async_timeout

import aiopulse.const as const
import aiopulse.utils as utils
import aiopulse.errors as errors
import aiopulse.transport
from aiopulse.callbacks import CallbackMixin

_LOGGER = logging.getLogger(__name__)


class Hub(CallbackMixin):
    """Representation of an Acmeda Pulse Hub."""

    def __init__(
        self, host: str | None = None, loop: asyncio.AbstractEventLoop | None = None
    ) -> None:
        """Init the hub.

        Args:
            host: The hub's IP address or hostname.
            loop: Deprecated. The event loop to use.
        """
        super().__init__()
        
        if loop is not None:
            warnings.warn(
                "loop parameter is deprecated and will be removed in v0.6.0",
                DeprecationWarning,
                stacklevel=2,
            )

        self.topic: bytes = str.encode("Smart_Id1_y:")
        self.sequence: int = 4
        self.handshake: asyncio.Event = asyncio.Event()
        self.command_lock: asyncio.Lock = asyncio.Lock()
        self.health_lock: asyncio.Lock = asyncio.Lock()
        self.response_task: asyncio.Task | None = None
        self.running: bool = False

        self.id: str | None = None
        self.host: str | None = host
        self.mac_address: str | None = None
        self.ip_address: str | None = None
        self.firmware_name: str | None = None
        self.wifi_module: str | None = None

        self.protocol = aiopulse.transport.HubTransportTcp(host)

        self.rollers: dict[int, aiopulse.Roller] = {}
        self.rooms: dict[int, aiopulse.Room] = {}
        self.scenes: dict[int, aiopulse.Scene] = {}
        self.timers: dict[int, aiopulse.Timer] = {}

        self.handshake.clear()

    # ... rest of hub methods
```

- [ ] **Step 2: Remove duplicate callback methods from Hub**

Remove:
- `callback_subscribe()` - now in CallbackMixin
- `callback_unsubscribe()` - now in CallbackMixin
- `notify_callback()` - now in CallbackMixin
- `async_add_job()` - now in CallbackMixin as `_schedule_callback()`

- [ ] **Step 3: Update Hub.notify_callback calls**

Update all calls from `self.notify_callback()` to use the new signature if needed.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_hub.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/hub.py
git commit -m "refactor: Hub inherits from CallbackMixin"
```

---

### Task 14: Update utils.py with Type Hints

**Files:**
- Modify: `aiopulse/utils.py`

**Interfaces:**
- Produces: Type-annotated utility functions

- [ ] **Step 1: Update utils.py with type hints**

```python
"""Serialisation / Deserialisation helpers."""
from __future__ import annotations


def unpack_int(buffer: bytes, ptr: int, length: int) -> tuple[int, int]:
    """Unpack an int of specified length from the buffer and advance the pointer.

    Args:
        buffer: The bytes buffer to read from.
        ptr: Current position in the buffer.
        length: Number of bytes to read.

    Returns:
        Tuple of (value, new_pointer).
    """
    return (
        int.from_bytes(buffer[ptr : (ptr + length)], "little", signed=False),
        ptr + length,
    )


def pack_int(value: int, length: int) -> bytes:
    """Pack an int for serialisation.

    Args:
        value: The integer value to pack.
        length: Number of bytes to use.

    Returns:
        Bytes representation.
    """
    return value.to_bytes(length, "little", signed=False)


def unpack_bytes(
    buffer: bytes, ptr: int, length: int | None = None
) -> tuple[bytes, int]:
    """Unpack a specified number of bytes from the buffer and advance the pointer.

    Args:
        buffer: The bytes buffer to read from.
        ptr: Current position in the buffer.
        length: Number of bytes to read, or None to read length prefix.

    Returns:
        Tuple of (bytes, new_pointer).
    """
    ptr_new = ptr
    if not length:
        length, ptr_new = unpack_int(buffer, ptr, 2)
    return (buffer[(ptr_new) : (ptr_new + length)], ptr_new + length)


def unpack_string(
    buffer: bytes, ptr: int, length: int | None = None
) -> tuple[str, int]:
    """Unpack a specified number of characters from the buffer and advance the pointer.

    Args:
        buffer: The bytes buffer to read from.
        ptr: Current position in the buffer.
        length: Number of bytes to read, or None to read length prefix.

    Returns:
        Tuple of (string, new_pointer).
    """
    str_new, ptr_new = unpack_bytes(buffer, ptr, length=None)
    return (str_new.decode("utf-8", "ignore"), ptr_new)


def unpack_roller_percent(buffer: bytes, ptr: int) -> tuple[int, int]:
    """Unpack roller close percentage.

    Args:
        buffer: The bytes buffer to read from.
        ptr: Current position in the buffer.

    Returns:
        Tuple of (percent, new_pointer).
    """
    ptr += 4
    roller_state, ptr = unpack_bytes(buffer, ptr, 1)
    ptr += 5  # unknown field
    if roller_state == b"\x10":  # roller is open
        ptr += 1  # unused percent field
        return 0, ptr
    elif roller_state == b"\x12":  # roller is closed
        ptr += 1  # unused percent field
        return 100, ptr
    else:  # read roller percent
        return unpack_int(buffer, ptr, 1)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_utils.py -v`
Expected: All tests pass

- [ ] **Step 3: Commit**

```bash
git add aiopulse/utils.py
git commit -m "refactor: add type hints to utils module"
```

---

### Task 15: Create CHANGELOG and Final Verification

**Files:**
- Create: `CHANGELOG.md`

**Interfaces:**
- Produces: Changelog documenting all changes

- [ ] **Step 1: Create CHANGELOG.md**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-08-01

### Changed
- Minimum Python version is now 3.10
- Modernized asyncio patterns (removed loop parameter deprecation)
- Updated type hints to Python 3.10+ syntax
- Improved error handling with bounds checking
- Extracted CallbackMixin for shared callback logic
- Updated CI/CD with testing and type checking
- Organized protocol constants with enums

### Deprecated
- `loop` parameter in Hub.__init__() and Hub.discover() - will be removed in v0.6.0

### Fixed
- Duplicate InvalidResponseException catch in hub.py
- Unsafe lock management in send_command()
- Missing bounds checking in response parsers

### Added
- CallbackMixin for shared callback logic
- HubEntity base class for hub entities
- Type annotations throughout codebase
- mypy type checking support
- GitHub Actions release workflow

## [0.4.7] - Previous release
```

- [ ] **Step 2: Run full test suite**

Run: `pytest tests/ -v --cov=aiopulse`
Expected: All tests pass with coverage report

- [ ] **Step 3: Run type checking**

Run: `mypy aiopulse`
Expected: No errors

- [ ] **Step 4: Run linter**

Run: `ruff check .`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add changelog for v0.5.0 release"
```

---

## Plan Summary

**Total Tasks:** 15
**Estimated Time:** 2-3 hours

**Task Dependencies:**
1. Task 1 (pyproject.toml) - No dependencies
2. Task 2 (errors.py) - No dependencies
3. Task 3 (CallbackMixin) - No dependencies
4. Task 4 (HubEntity) - Depends on Task 3
5. Task 5 (Room) - Depends on Task 4
6. Task 6 (Scene) - Depends on Task 4
7. Task 7 (Timer) - Depends on Task 4
8. Task 8 (Roller) - Depends on Task 4
9. Task 9 (const.py) - No dependencies
10. Task 10 (hub.py modernization) - Depends on Tasks 2, 3, 9
11. Task 11 (transport.py) - No dependencies
12. Task 12 (CI/CD) - No dependencies
13. Task 13 (Hub callbacks) - Depends on Tasks 3, 10
14. Task 14 (utils.py) - No dependencies
15. Task 15 (CHANGELOG) - Depends on all previous tasks

**Parallel Execution Opportunities:**
- Tasks 1, 2, 3, 9, 11, 12, 14 can run in parallel
- Tasks 5, 6, 7, 8 can run in parallel after Task 4
