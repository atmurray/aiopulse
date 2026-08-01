# Task 8: Update Roller to Use HubEntity

**Files:**
- Modify: `aiopulse/roller.py`
- Modify: `tests/test_roller.py`

**Interfaces:**
- Consumes: `HubEntity` from `aiopulse.entities`
- Produces: `Roller` class inheriting from `HubEntity`

- [ ] **Step 1: Run existing roller tests to establish baseline**

Run: `pytest tests/test_roller.py -v`
Expected: All tests pass

- [ ] **Step 2: Update roller.py to use HubEntity**

```python
"""Roller blind entity that hangs off the hub."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import aiopulse.utils as utils
import aiopulse.const as const
from aiopulse.entities import HubEntity

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
        self.type: int | None = None
        self.serial: str | None = None
        self.room_id: bytes | None = None
        self.room: Room | None = None
        self.battery: int | None = None
        self.closed_percent: int | None = None
        self.flags: int = 0

        self.health_lock = asyncio.Lock()
        self.health_task = hub.async_add_job(self.health_updater)

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
                f"{self.hub.host}:{self.name}: health updater unhandled exception: {inst}"
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
        """Send command to move the roller to fully open."""
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
        """Send command to stop the roller."""
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
        """Send command to move the roller to fully closed."""
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

    async def get_health(self) -> None:
        """Request health information from the roller."""
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
```

- [ ] **Step 3: Update test_roller.py for HubEntity**

```python
# tests/test_roller.py
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
        assert roller._update_callbacks == []

    def test_init_inherits_hub_entity(self, roller):
        assert roller.hub is not None
        assert roller.id == 123

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
        assert callback in roller._update_callbacks

    def test_callback_unsubscribe(self, roller):
        callback = MagicMock()
        roller._update_callbacks.append(callback)
        roller.callback_unsubscribe(callback)
        assert callback not in roller._update_callbacks

    def test_callback_unsubscribe_not_found(self, roller):
        callback = MagicMock()
        roller.callback_unsubscribe(callback)
        assert roller._update_callbacks == []

    def test_notify_callback(self, roller):
        callback = MagicMock()
        roller._update_callbacks.append(callback)
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_roller.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/roller.py tests/test_roller.py
git commit -m "refactor: Roller inherits from HubEntity"
```
