import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiopulse.roller import Roller


class TestRoller:
    @pytest.fixture
    def hub_mock(self):
        hub = MagicMock()
        hub.host = "192.168.1.100"
        hub._schedule_callback = MagicMock(return_value=MagicMock())
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
        with patch.object(roller, "_schedule_callback") as mock_schedule:
            roller.notify_callback()
            mock_schedule.assert_called_once_with(callback)

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

    @pytest.mark.asyncio
    async def test_health_updater_recovers_after_transient_error(self, roller):
        """health_updater must not die permanently on hub disconnect errors."""
        call_count = 0

        async def get_health_flaky():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise OSError("[Errno 113] Host is unreachable")
            # Second call succeeds but we stop the loop via CancelledError
            raise asyncio.CancelledError

        roller.get_health = get_health_flaky

        # Patch sleep so the 30s retry delay doesn't slow the test
        with patch("asyncio.sleep", new_callable=AsyncMock):
            # Should return cleanly — CancelledError is handled internally
            await roller.health_updater()

        # get_health must have been called at least twice — once failing,
        # once after the retry, proving the updater recovered
        assert call_count >= 2

    @pytest.mark.asyncio
    async def test_health_updater_stops_cleanly_on_cancel(self, roller):
        """CancelledError on get_health should stop the updater without raising."""
        async def get_health_cancel():
            raise asyncio.CancelledError

        roller.get_health = get_health_cancel

        # Should return cleanly, not propagate CancelledError
        await roller.health_updater()

    @pytest.mark.asyncio
    async def test_health_updater_recovers_after_not_running_exception(self, roller):
        """NotRunningException (hub stopped) should be treated as transient."""
        from aiopulse.errors import NotRunningException

        call_count = 0

        async def get_health_not_running():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise NotRunningException("Hub not running")
            raise asyncio.CancelledError

        roller.get_health = get_health_not_running

        with patch("asyncio.sleep", new_callable=AsyncMock):
            await roller.health_updater()

        assert call_count >= 2

    @pytest.mark.asyncio
    async def test_health_updater_hourly_poll(self, roller):
        """After initial health check, updater re-polls on 1h timeout."""
        call_count = 0

        async def get_health_counter():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                raise asyncio.CancelledError

        roller.get_health = get_health_counter

        # Simulate the 1h wait_for timing out immediately
        async def fake_wait_for(coro, timeout):
            coro.close()
            raise TimeoutError

        with patch("asyncio.wait_for", side_effect=fake_wait_for):
            await roller.health_updater()

        # Initial call + at least one hourly re-poll
        assert call_count >= 2
