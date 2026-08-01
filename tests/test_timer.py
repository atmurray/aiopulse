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
        import asyncio

        callback = MagicMock()
        timer._update_callbacks.append(callback)

        async def run():
            timer.notify_callback()
            await asyncio.sleep(0)

        asyncio.run(run())
        callback.assert_called_once()
