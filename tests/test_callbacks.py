import asyncio
from unittest.mock import AsyncMock, MagicMock

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

    @pytest.mark.asyncio
    async def test_notify_callback_sync(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.notify_callback()
        await asyncio.sleep(0.1)
        callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_callback_with_args(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.notify_callback("arg1", "arg2")
        await asyncio.sleep(0.1)
        callback.assert_called_once_with("arg1", "arg2")

    @pytest.mark.asyncio
    async def test_notify_callback_multiple(self, entity):
        callback1 = MagicMock()
        callback2 = MagicMock()
        entity._update_callbacks.append(callback1)
        entity._update_callbacks.append(callback2)
        entity.notify_callback()
        await asyncio.sleep(0.1)
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
