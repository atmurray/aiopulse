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
        assert roller.update_callbacks == []

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
        assert callback in roller.update_callbacks

    def test_callback_unsubscribe(self, roller):
        callback = MagicMock()
        roller.update_callbacks.append(callback)
        roller.callback_unsubscribe(callback)
        assert callback not in roller.update_callbacks

    def test_callback_unsubscribe_not_found(self, roller):
        callback = MagicMock()
        roller.callback_unsubscribe(callback)
        assert roller.update_callbacks == []

    def test_notify_callback(self, roller):
        callback = MagicMock()
        roller.update_callbacks.append(callback)
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
