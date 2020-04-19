"""Elements that hang off the hub."""
from typing import List, Callable

import aiopulse.utils as utils
import aiopulse.const as const


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


class Scene:
    """Representation of a Scene."""

    def __init__(self, hub, scene_id):
        """Init a new scene."""
        self.hub = hub
        self.id = scene_id
        self.icon = None
        self.name = None

    def __str__(self):
        """Returns string representation of scene."""
        return "Name: {} ID: {} Icon: {}".format(self.name, self.id[0:4], self.icon)


class Timer:
    """Representation of a Timer."""

    def __init__(self, hub, timer_id):
        """Init a new timer."""
        self.hub = hub
        self.id = timer_id
        self.icon = None
        self.name = None
        self.state = None
        self.hour = None
        self.minute = None
        self.days = None
        self.entity = None

    def __str__(self):
        """Returns string representation of timer."""
        return (
            f"Name: {self.name} "
            f"ID: {self.id[0:4]} "
            f"Icon: {self.icon} "
            f"State: {self.state} "
            f"Time: {self.hour}:{self.minute} "
            f"Days: {self.days:>07b} "
            f'Entity: {self.entity.name if self.entity else "None"}'
        )
