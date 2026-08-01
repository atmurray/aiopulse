from unittest.mock import AsyncMock, MagicMock

import pytest

from aiopulse.room import Room
from aiopulse.entities import HubEntity


class TestRoom:
    @pytest.fixture
    def hub_mock(self):
        hub = MagicMock()
        hub.host = "192.168.1.100"
        hub._schedule_callback = MagicMock()
        return hub

    @pytest.fixture
    def room(self, hub_mock):
        return Room(hub_mock, b"\x01\x00\x00\x00\x00\x00")

    def test_init(self, room):
        assert room.id == b"\x01\x00\x00\x00\x00\x00"
        assert room.icon is None
        assert room.name is None
        assert room.hub is not None
        assert room._update_callbacks == []

    def test_inherits_from_hub_entity(self, room):
        assert isinstance(room, HubEntity)

    def test_str(self, room):
        room.name = "Living Room"
        room.icon = 2
        result = str(room)
        assert "Living Room" in result
        assert "Icon: 2" in result

    def test_callback_subscribe(self, room):
        callback = MagicMock()
        room.callback_subscribe(callback)
        assert callback in room._update_callbacks

    def test_callback_unsubscribe(self, room):
        callback = MagicMock()
        room._update_callbacks.append(callback)
        room.callback_unsubscribe(callback)
        assert callback not in room._update_callbacks

    def test_callback_unsubscribe_not_found(self, room):
        callback = MagicMock()
        room.callback_unsubscribe(callback)
        assert room._update_callbacks == []

    @pytest.mark.asyncio
    async def test_move_to(self, room):
        room.id = 1
        room.hub.send_command = AsyncMock()
        await room.move_to(50)
        room.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_move_up(self, room):
        room.id = 1
        room.hub.send_command = AsyncMock()
        await room.move_up()
        room.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_move_stop(self, room):
        room.id = 1
        room.hub.send_command = AsyncMock()
        await room.move_stop()
        room.hub.send_command.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_move_down(self, room):
        room.id = 1
        room.hub.send_command = AsyncMock()
        await room.move_down()
        room.hub.send_command.assert_awaited_once()
