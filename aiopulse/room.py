"""Elements that hang off the hub."""
from typing import List, Callable

import aiopulse.utils as utils
import aiopulse.const as const
import asyncio


class Room:
    """Representation of a Room."""

    def __init__(self, hub, room_id):
        """Init a new room."""
        self.hub = hub
        self.id = room_id
        self.icon = None
        self.name = None
        self.update_callbacks: List[Callable] = []

    def __str__(self):
        """Returns string representation of room."""
        return "Name: {} ID: {} Icon: {}".format(self.name, self.id[0:4], self.icon)

    def callback_subscribe(self, callback):
        """Add a callback for hub updates."""
        self.update_callbacks.append(callback)

    def callback_unsubscribe(self, callback):
        """Remove a callback for hub updates."""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)

    def notify_callback(self):
        """Tell callback that device has been updated."""
        for callback in self.update_callbacks:
            self.hub.async_add_job(callback)

    async def move_to(self, percent):
        """Send command to move the roller to a percentage closed."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("190401030001")
            + utils.pack_int(percent, 2)
            + bytes.fromhex("ff")
        )
        await self.hub.send_payload(
            const.COMMAND_MOVE_TO, bytes.fromhex("2201"), message
        )

    async def move_up(self):
        """Send command to move the roller to fully open."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("10")
            + bytes.fromhex("ff")
        )
        await self.hub.send_payload(const.COMMAND_MOVE, bytes.fromhex("2201"), message)

    async def move_stop(self):
        """Send command to stop the roller."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("11")
            + bytes.fromhex("ff")
        )
        await self.hub.send_payload(const.COMMAND_MOVE, bytes.fromhex("2201"), message)

    async def move_down(self):
        """Send command to move the roller to fully closed."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("12")
            + bytes.fromhex("ff")
        )
        await self.hub.send_payload(const.COMMAND_MOVE, bytes.fromhex("2201"), message)
