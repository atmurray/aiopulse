"""Roller blind entity that hangs off the hub."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import aiopulse.utils as utils
from aiopulse.entities import HubEntity
from aiopulse.const import CommandType

if TYPE_CHECKING:
    from aiopulse.hub import Hub

_LOGGER = logging.getLogger(__name__)


class Roller(HubEntity):
    """Representation of a Roller blind."""

    def __init__(self, hub: Hub, roller_id: int) -> None:
        """Init a new roller blind.

        Args:
            hub: The hub instance.
            roller_id: The unique roller identifier.
        """
        super().__init__(hub, roller_id)
        self.id: int  # Override type from HubEntity
        self.type: int | None = None
        self.serial: str | None = None
        self.room_id: bytes | None = None
        self.room = None
        self.battery: int | None = None
        self.closed_percent: int | None = None
        self.flags: int = 0

        self.health_lock = asyncio.Lock()
        self.health_task = hub._schedule_callback(self.health_updater)

    def __del__(self) -> None:
        """Cancel health updater task on deletion."""
        if self.health_task:
            self.health_task.cancel()

    def health_updated(self) -> None:
        """Signal that health data has been received."""
        try:
            self.health_lock.release()
        except RuntimeError:
            pass

    async def health_updater(self) -> None:
        """Periodically update roller health."""
        await self.get_health()
        running = True
        try:
            while running:
                try:
                    await asyncio.wait_for(
                        self.health_lock.acquire(), timeout=3600
                    )
                except asyncio.TimeoutError:
                    await self.get_health()
                except asyncio.CancelledError:
                    running = False
        except Exception as inst:
            _LOGGER.error(
                f"{self.hub.host}:{self.name}: health updater "
                f"unhandled exception: {inst}"
            )
        _LOGGER.info(f"{self.hub.host}:{self.name}: health updater stopped")
        running = False

    def __str__(self) -> str:
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

    async def move_to(self, percent: int) -> None:
        """Send command to move the roller to a percentage closed.

        Args:
            percent: Target position (0-100).
        """
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(int(self.id), 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("190401030001")
            + utils.pack_int(percent, 2)
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            CommandType.MOVE_TO.to_bytes(4, 'big'), bytes.fromhex("2201"), message
        )

    async def move_up(self) -> None:
        """Send command to move the roller to fully open."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(int(self.id), 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("10")
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            CommandType.MOVE.to_bytes(4, 'big'), bytes.fromhex("2201"), message
        )

    async def move_stop(self) -> None:
        """Send command to stop the roller."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(int(self.id), 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("11")
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            CommandType.MOVE.to_bytes(4, 'big'), bytes.fromhex("2201"), message
        )

    async def move_down(self) -> None:
        """Send command to move the roller to fully closed."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(int(self.id), 6)
            + bytes.fromhex("03010100")
            + bytes.fromhex("12")
            + bytes.fromhex("ff")
        )
        await self.hub.send_command(
            CommandType.MOVE.to_bytes(4, 'big'), bytes.fromhex("2201"), message
        )

    async def get_health(self) -> None:
        """Request health information from the roller."""
        message = (
            bytes.fromhex("0000000000000101")
            + bytes.fromhex("0600")
            + utils.pack_int(int(self.id), 6)
            + bytes.fromhex("410201000E4202010004")
            + bytes.fromhex("ff")
        )
        await self.hub.send_healthcheck(
            CommandType.GET_HEALTH.to_bytes(4, 'big'), bytes.fromhex("2A01"), message
        )
