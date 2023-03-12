"""Elements that hang off the hub."""
from typing import List, Callable

import aiopulse.utils as utils
import aiopulse.const as const
import asyncio


class Roller:
    """Representation of a Roller blind."""

    def __init__(self, hub, roller_id):
        """Init a new roller blind."""
        self.hub = hub
        self.id = roller_id
        self.name = None
        self.type = None
        self.serial = None
        self.room_id = None
        self.room = None
        self.battery = None
        self.closed_percent = None
        self.flags = 0
        self.update_callbacks: List[Callable] = []

        self.health_lock = asyncio.Lock()
        self.health_task = hub.async_add_job(self.health_updater)

    def __del__(self):
        self.health_task.cancel()

    def health_updated(self):
        try:
            self.health_lock.release()
        except RuntimeError:
            pass

    async def health_updater(self):
        await self.get_health()
        running = True
        while running:
            try:
                await asyncio.wait_for(self.health_lock, timeout=3600)
            except asyncio.TimeoutError:
                await self.get_health()
            except asyncio.CancelledError:
                running = False

    def __str__(self):
        """Returns string representation of roller."""
        return (
            "Name: {} ID: {} Serial: {} Room: {} Type: {} Closed %: {} Battery %: {}"
            " Flags: {:08b}"
        ).format(
            self.name,
            self.id,
            self.serial,
            self.room.name if self.room else "None",
            self.type,
            self.closed_percent,
            self.battery,
            self.flags,
        )

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

    async def get_health(self):
        """."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(self.id, 6)
            + bytes.fromhex("410201000E4202010004")
            + bytes.fromhex("ff")
        )
        await self.hub.send_healthcheck(
            const.GET_HEALTH, bytes.fromhex("2A01"), message
        )
