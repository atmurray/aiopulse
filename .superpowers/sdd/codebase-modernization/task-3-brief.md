# Task 3: Create CallbackMixin

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
