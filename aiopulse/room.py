"""Room entity that hangs off the hub."""
from __future__ import annotations

from typing import TYPE_CHECKING

import aiopulse.utils as utils
from aiopulse.entities import HubEntity
from aiopulse.const import CommandType

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
            CommandType.MOVE_TO.to_bytes(4, 'big'), bytes.fromhex("2201"), message
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
            CommandType.MOVE.to_bytes(4, 'big'), bytes.fromhex("2201"), message
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
            CommandType.MOVE.to_bytes(4, 'big'), bytes.fromhex("2201"), message
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
            CommandType.MOVE.to_bytes(4, 'big'), bytes.fromhex("2201"), message
        )
