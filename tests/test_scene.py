import asyncio
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

    @pytest.mark.asyncio
    async def test_notify_callback(self, scene):
        callback = MagicMock()
        scene._update_callbacks.append(callback)
        scene.notify_callback()
        await asyncio.sleep(0.1)
        callback.assert_called_once()
