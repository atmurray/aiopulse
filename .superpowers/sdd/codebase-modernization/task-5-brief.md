# Task 5: Update Room to Use HubEntity

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
