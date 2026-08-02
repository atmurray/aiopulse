import asyncio
from unittest.mock import MagicMock

import pytest

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

    @pytest.mark.asyncio
    async def test_notify_callback(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.notify_callback()
        await asyncio.sleep(0.1)
        callback.assert_called_once()
