import asyncio
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch, call

import pytest

import aiopulse.transport
import aiopulse.const as const
from aiopulse.hub import Hub
from aiopulse.errors import (
    CannotConnectException,
    NotConnectedException,
    NotRunningException,
    InvalidResponseException,
)


# Helper to create a valid parseable ping response payload
def _ping_response():
    """HEADER + msg_len=3 + unknown(2) + mtype=22(ping)"""
    return const.HEADER + b"\x03\x00\x00\x16"


class TestHubInit:
    def test_init_with_host(self, hub):
        assert hub.host == "192.168.1.100"
        assert hub.topic == b"Smart_Id1_y:"
        assert hub.sequence == 4
        assert hub.running is False
        assert hub.rollers == {}
        assert hub.rooms == {}
        assert hub.scenes == {}
        assert hub.timers == {}
        assert hub.update_callbacks == []

    def test_init_without_host(self, event_loop):
        mock_transport = MagicMock(spec=aiopulse.transport.HubTransportTcp)
        with patch.object(aiopulse.transport, "HubTransportTcp", return_value=mock_transport):
            h = Hub(loop=event_loop)
            assert h.host is None
            assert h.running is False

    def test_str(self, hub):
        hub.id = "12345"
        hub.mac_address = "AA:BB:CC:DD:EE:FF"
        hub.firmware_name = "v1.0"
        hub.wifi_module = "ESP8266"
        result = str(hub)
        assert "12345" in result
        assert "AA:BB:CC:DD:EE:FF" in result
        assert "v1.0" in result


class TestHubCallbacks:
    def test_callback_subscribe(self, hub):
        callback = MagicMock()
        hub.callback_subscribe(callback)
        assert callback in hub.update_callbacks

    def test_callback_unsubscribe(self, hub):
        callback = MagicMock()
        hub.update_callbacks.append(callback)
        hub.callback_unsubscribe(callback)
        assert callback not in hub.update_callbacks

    def test_notify_callback(self, hub):
        callback = MagicMock()
        hub.update_callbacks.append(callback)
        hub.notify_callback(const.UpdateType.info)
        hub.async_add_job.assert_called_with(callback, const.UpdateType.info)


class TestHubAsyncAddJob:
    def test_async_add_job_coroutine(self, hub):
        async def fake_coro():
            pass

        task = hub.async_add_job(fake_coro())
        assert task is not None

    def test_async_add_job_coroutine_function(self, hub):
        async def fake_func():
            pass

        task = hub.async_add_job(fake_func)
        assert task is not None

    def test_async_add_job_regular_function(self, hub):
        def fake_func():
            pass

        task = hub.async_add_job(fake_func)
        assert task is not None


class TestHubConnect:
    @pytest.mark.asyncio
    async def test_connect_success(self, hub, mock_transport):
        mock_transport.is_udp = False
        mock_transport.send = MagicMock()
        mock_transport.receive = AsyncMock()
        # Responses: CONNECT, LOGIN, SETID(->response_parse), UNKNOWN1(->response_parse), SETID(->response_parse)
        mock_transport.receive.side_effect = [
            const.HEADER + const.RESPONSE_CONNECT + b"Hub123",
            const.HEADER + const.RESPONSE_LOGIN + b"\x00",
            const.HEADER + const.RESPONSE_SETID + _ping_response(),
            const.HEADER + const.RESPONSE_UNKNOWN1 + bytes.fromhex("06") + hub.topic + bytes.fromhex("16000f0002000000000000000c000600120311073816ff9d") + _ping_response(),
            const.HEADER + const.RESPONSE_SETID + _ping_response(),
        ]

        result = await hub.connect()
        assert result is True
        assert hub.id == "b123"
        assert hub.handshake.is_set()

    @pytest.mark.asyncio
    async def test_connect_oserror(self, hub, mock_transport):
        mock_transport.connect = AsyncMock(side_effect=OSError("Connection refused"))

        with pytest.raises(CannotConnectException):
            await hub.connect()
        assert hub.handshake.is_set() is False

    @pytest.mark.asyncio
    async def test_connect_already_handshaken(self, hub, mock_transport):
        hub.handshake.set()
        mock_transport.connect = AsyncMock()

        result = await hub.connect()
        assert result is False

    @pytest.mark.asyncio
    async def test_connect_invalid_response(self, hub, mock_transport):
        mock_transport.send = MagicMock()
        mock_transport.receive = AsyncMock(return_value=b"\x00\x00\x00\x00")

        with pytest.raises(InvalidResponseException):
            await hub.connect()


class TestHubDisconnect:
    @pytest.mark.asyncio
    async def test_disconnect(self, hub, mock_transport):
        hub.handshake.set()
        mock_transport.close = AsyncMock()

        await hub.disconnect()
        mock_transport.close.assert_awaited_once()
        assert hub.handshake.is_set() is False


class TestHubGetResponse:
    @pytest.mark.asyncio
    async def test_get_response_without_target(self, hub, mock_transport):
        mock_transport.receive = AsyncMock(return_value=b"\x00\x01\x02\x03")
        result = await hub.get_response()
        assert result == b"\x00\x01\x02\x03"

    @pytest.mark.asyncio
    async def test_get_response_matches(self, hub, mock_transport):
        target = const.RESPONSE_CONNECT
        raw = const.HEADER + target + b"extra"
        mock_transport.receive = AsyncMock(return_value=raw)

        result = await hub.get_response(target)
        assert result == b"extra"

    @pytest.mark.asyncio
    async def test_get_response_too_short(self, hub, mock_transport):
        mock_transport.receive = AsyncMock(return_value=b"\x00\x00")

        with pytest.raises(InvalidResponseException):
            await hub.get_response(const.RESPONSE_CONNECT)

    @pytest.mark.asyncio
    async def test_get_response_wrong_header(self, hub, mock_transport):
        mock_transport.receive = AsyncMock(return_value=b"\xff\xff\xff\xff\x00\x00")

        with pytest.raises(InvalidResponseException):
            await hub.get_response(const.RESPONSE_CONNECT)


class TestHubResponseHandlers:
    def test_response_hubinfo(self, hub):
        message = (
            b"\x00" * 10
            + b"\x07\x00" + b"Firm v1" + b"\x00" * 2
            + b"\x04\x00" + b"Skip" + b"\x00" * 2
            + b"\x07\x00" + b"ESP8266" + b"\x00" * 2
            + b"\x11\x00" + b"AA:BB:CC:DD:EE:FF" + b"\x00" * 2
            + b"\x0e\x00" + b"192.168.1.100"
        )
        hub.response_hubinfo(message)
        assert hub.firmware_name == "Firm v1"
        assert hub.wifi_module == "ESP8266"
        assert hub.mac_address == "AA:BB:CC:DD:EE:FF"
        assert hub.ip_address == "192.168.1.100"

    def test_response_roller_updated_new_roller(self, hub):
        hub.rooms[b"\x01\x00\x00\x00"] = MagicMock()
        hub.rooms[b"\x01\x00\x00\x00"].name = "Living Room"
        message = (
            b"\x00" * 10
            + b"\x04\x00" + b"\x01\x00\x00\x00"
            + b"\x00" * 4
            + b"\x01"
            + b"\x00" * 2
            + b"\x06\x00" + b"Blind1"
            + b"\x00" * 10
            + b"\x01\x00\x00\x00\x00\x00"
            + b"\x00\x00\x00\x00" + b"\x12" + b"\x00\x00\x00\x00\x00"
            + b"\x00"
            + b"\x00\x00"
        )
        hub.response_roller_updated(message)
        assert 1 in hub.rollers
        roller = hub.rollers[1]
        assert roller.name == "Blind1"
        assert roller.type == 1
        assert roller.room.name == "Living Room"

    def test_response_roller_updated_existing_roller(self, hub):
        existing = MagicMock()
        existing.name = "OldName"
        hub.rollers[1] = existing
        hub.rooms[b"\x02\x00\x00\x00"] = MagicMock()
        hub.rooms[b"\x02\x00\x00\x00"].name = "Kitchen"
        message = (
            b"\x00" * 10
            + b"\x04\x00" + b"\x02\x00\x00\x00"
            + b"\x00" * 4
            + b"\x02"
            + b"\x00" * 2
            + b"\x06\x00" + b"Blind2"
            + b"\x00" * 10
            + b"\x01\x00\x00\x00\x00\x00"
            + b"\x00\x00\x00\x00" + b"\x10" + b"\x00\x00\x00\x00\x00"
            + b"\x00"
            + b"\x00\x00"
        )
        hub.response_roller_updated(message)

    def test_response_roomlist(self, hub):
        room_data = (
            b"\x00" * 12
            + b"\x02"
            + b"\x00\x00"
            + b"\x04\x00" + b"\x01\x01\x01\x01"
            + b"\x00" * 4
            + b"\x03"
            + b"\x00\x00"
            + b"\x06\x00" + b"Living"
            + b"\x00\x00"
            + b"\x04\x00" + b"\x02\x02\x02\x02"
            + b"\x00" * 4
            + b"\x01"
            + b"\x00\x00"
            + b"\x07\x00" + b"Kitchen"
        )
        hub.response_roomlist(room_data)
        assert len(hub.rooms) == 2

    def test_response_rollerlist(self, hub):
        message = (
            b"\x00" * 2
            + b"\x00" * 10
            + b"\x01"
            + b"\x00" * 4
            + b"\x01\x00\x00\x00\x00\x00"
            + b"\x00\x00"
            + b"\x04\x00" + b"\x01\x00\x00\x00"
            + b"\x00" * 4
            + b"\x01"
            + b"\x00" * 2
            + b"\x06\x00" + b"Blind1"
            + b"\x00" * 8
            + b"\x02\x00" + b"S1"
            + b"\x00\x00\x00\x00" + b"\x12" + b"\x00\x00\x00\x00\x00"
            + b"\x00"
        )
        hub.response_rollerlist(message)
        assert 1 in hub.rollers
        roller = hub.rollers[1]
        assert roller.name == "Blind1"
        assert roller.serial == "S1"
        assert roller.closed_percent == 100

    def test_response_scenelist(self, hub):
        message = (
            b"\x00" * 12
            + b"\x01"
            + b"\x00\x00"
            + b"\x04\x00" + b"\x01\x01\x01\x01"
            + b"\x00" * 4
            + b"\x02"
            + b"\x00\x00"
            + b"\x06\x00" + b"Scene1"
            + b"\x00" * 5
            + b"\x00\x00"
        )
        hub.response_scenelist(message)
        assert len(hub.scenes) == 1
        scene = list(hub.scenes.values())[0]
        assert scene.name == "Scene1"
        assert scene.icon == 2

    def test_response_timerlist_device_timer(self, hub):
        roller_mock = MagicMock()
        hub.rollers[1] = roller_mock
        message = (
            b"\x00" * 12
            + b"\x01"
            + b"\x00\x00"
            + b"\x04\x00" + b"\x01\x01\x01\x01"
            + b"\x00" * 4
            + b"\x03"
            + b"\x00\x00"
            + b"\x06\x00" + b"Timer1"
            + b"\x00" * 4
            + b"\x01"
            + b"\x00" * 4
            + b"\x07"
            + b"\x00" * 4
            + b"\x1e"
            + b"\x00" * 4
            + b"\x7f"
            + b"\x00" * 4
            + b"\x00\x00"
            + b"\x00\x01\x03\x01"
            + b"\x00" * 8
            + b"\x32"
            + b"\x00" * 5
            + b"\x01\x00\x00\x00\x00\x00"
            + b"\x00\x00"
        )
        hub.response_timerlist(message)
        assert len(hub.timers) == 1

    def test_response_timerlist_scene_timer(self, hub):
        scene_mock = MagicMock()
        hub.scenes[b"\x01\x01\x01\x01"] = scene_mock
        message = (
            b"\x00" * 12
            + b"\x01"
            + b"\x00\x00"
            + b"\x04\x00" + b"\x05\x05\x05\x05"
            + b"\x00" * 4
            + b"\x01"
            + b"\x00\x00"
            + b"\x08\x00" + b"SceneTim"
            + b"\x00" * 4
            + b"\x01"
            + b"\x00" * 4
            + b"\x06"
            + b"\x00" * 4
            + b"\x15"
            + b"\x00" * 4
            + b"\x3f"
            + b"\x00" * 4
            + b"\x00\x00"
            + b"\x00\x00\x10\x02"
            + b"\x04\x00" + b"\x01\x01\x01\x01"
            + b"\x00\x00"
        )
        hub.response_timerlist(message)
        assert len(hub.timers) == 1

    def test_response_authinfo(self, hub):
        message = b"\x00" * 15 + b"\x03\x00" + b"ABC"
        hub.response_authinfo(message)

    def test_response_position(self, hub):
        roller_mock = MagicMock()
        roller_mock.notify_callback = MagicMock()
        hub.rollers[1] = roller_mock
        message = (
            b"\x00" * 12
            + b"\x01\x00\x00\x00\x00\x00"
            + b"\x00\x00\x00\x00" + b"\x12" + b"\x00\x00\x00\x00\x00"
            + b"\x00"
        )
        hub.response_position(message)
        assert roller_mock.closed_percent == 100

    def test_response_rollerhealth(self, hub):
        roller_mock = MagicMock()
        roller_mock.notify_callback = MagicMock()
        roller_mock.health_updated = MagicMock()
        hub.rollers[1] = roller_mock
        message = (
            b"\x00" * 12
            + b"\x01\x00\x00\x00\x00\x00"
            + b"A" + b"\x00" * 4
            + b"B" + b"\x00" * 4
            + b"C" + b"\x00" * 4
            + b"\x00" * 3
            + b"\x0a"
            + b"\x00"
            + b"\x00" * 8
            + b"\x00\x00"
        )
        hub.response_rollerhealth(message)
        assert roller_mock.battery == 19


class TestHubRecMessage:
    def test_rec_message_invalid_first_byte(self, hub):
        with pytest.raises(InvalidResponseException):
            hub.rec_message(b"\x07" + hub.topic + b"\x00" * 10)

    def test_rec_message_invalid_topic(self, hub):
        with pytest.raises(InvalidResponseException):
            hub.rec_message(b"\x06" + b"WrongTopic" + b"\x00" * 10)

    def test_rec_message_acknowledgement(self, hub):
        hub.command_lock = asyncio.Lock()
        async def do_test():
            await hub.command_lock.acquire()
            hub.rec_message(b"")
            assert not hub.command_lock.locked()
        asyncio.run(do_test())

    def test_rec_message_known_type(self, hub):
        message = (
            b"\x06" + hub.topic
            + b"\x00\x00"
            + bytes.fromhex("0d00")
            + b"\x00" * 4
        )
        hub.rec_message(message)

    def test_rec_message_unknown_type(self, hub):
        message = (
            b"\x06" + hub.topic
            + b"\x00\x00"
            + bytes.fromhex("ffff")
            + b"\x00" * 4
        )
        hub.rec_message(message)


class TestHubResponseParse:
    def test_response_parse_ping(self, hub):
        # msg_len=3 (unknown2 + mtype1), mtype=22(ping, harmless)
        response = const.HEADER + b"\x03\x00\x00\x16"
        hub.response_parse(response)

    def test_response_parse_message(self, hub):
        inner = b"\x06" + hub.topic + b"\x00\x00" + bytes.fromhex("0d00") + b"\x00" * 4
        msg_len = 3 + len(inner)
        response = const.HEADER + bytes([msg_len]) + b"\x00\x00" + b"\x16" + inner
        hub.response_parse(response)

    def test_response_parse_invalid_header(self, hub):
        response = b"\xff\xff\xff\xff\x00\x00"
        with pytest.raises(InvalidResponseException):
            hub.response_parse(response)

    def test_response_parse_truncated(self, hub):
        # msg_len=22 but not enough data follows
        response = const.HEADER + b"\x16\x00\x00\x00"
        with pytest.raises(InvalidResponseException):
            hub.response_parse(response)

    def test_response_parse_multi_block(self, hub):
        # msg_len=128 (>127) triggers multi-block parsing with msg_blocks=1
        # Content: unknown(2) + mtype(22/ping) + 125 zero bytes
        content = b"\x00\x00\x16" + b"\x00" * 125
        response = const.HEADER + b"\x80\x01" + content
        hub.response_parse(response)


class TestHubResponseParser:
    @pytest.mark.asyncio
    async def test_response_parser_timeout(self, hub, mock_transport):
        hub.handshake.set()

        async def slow_timeout():
            await asyncio.sleep(0.001)
            raise asyncio.TimeoutError

        mock_transport.receive = AsyncMock(side_effect=slow_timeout)
        mock_transport.send = MagicMock()

        task = asyncio.create_task(hub.response_parser())
        await asyncio.sleep(0.05)
        task.cancel()
        await asyncio.sleep(0.01)
        try:
            await task
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
        mock_transport.send.assert_called_with(const.HEADER + const.COMMAND_PING)

    @pytest.mark.asyncio
    async def test_response_parser_invalid_response(self, hub, mock_transport):
        hub.handshake.set()

        async def slow_receive():
            await asyncio.sleep(0.001)
            return b"\xff"

        mock_transport.receive = AsyncMock(side_effect=slow_receive)
        mock_transport.send = MagicMock()

        task = asyncio.create_task(hub.response_parser())
        await asyncio.sleep(0.05)
        task.cancel()
        await asyncio.sleep(0.01)
        try:
            await task
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
        mock_transport.send.assert_called_with(const.HEADER + const.COMMAND_PING)


class TestHubSendCommand:
    @pytest.mark.asyncio
    async def test_send_command_not_running(self, hub, mock_transport):
        hub.running = False
        with pytest.raises(NotRunningException):
            await hub.send_command(
                const.COMMAND_GET_HUB_INFO, bytes.fromhex("F000"), b"\x00" * 7
            )

    @pytest.mark.asyncio
    async def test_send_command_success(self, hub, mock_transport):
        hub.running = True
        hub.handshake.set()
        mock_transport.send = MagicMock()
        hub.command_lock = MagicMock(spec=asyncio.Lock)
        hub.command_lock.acquire = AsyncMock(side_effect=[None, None])
        hub.command_lock.locked = MagicMock(return_value=False)
        hub.command_lock.release = MagicMock()

        await hub.send_command(
            const.COMMAND_GET_HUB_INFO, bytes.fromhex("F000"), b"\x00" * 7
        )
        assert mock_transport.send.call_count == 1

    @pytest.mark.asyncio
    async def test_send_command_timeout(self, hub, mock_transport):
        hub.running = True
        hub.handshake.set()
        mock_transport.send = MagicMock()
        hub.command_lock = MagicMock(spec=asyncio.Lock)

        call_count = [0]

        async def mock_acquire():
            call_count[0] += 1
            if call_count[0] == 1:
                return
            raise asyncio.TimeoutError()

        hub.command_lock.acquire = AsyncMock(side_effect=mock_acquire)
        hub.command_lock.locked = MagicMock(return_value=True)
        hub.command_lock.release = MagicMock()

        await hub.send_command(
            const.COMMAND_GET_HUB_INFO, bytes.fromhex("F000"), b"\x00" * 7,
            timeout=0.01, retries=2
        )
        assert mock_transport.send.call_count == 2


class TestHubSendHealthcheck:
    @pytest.mark.asyncio
    async def test_send_healthcheck(self, hub, mock_transport):
        hub.running = True
        hub.handshake.set()
        hub.send_command = AsyncMock()
        hub.health_lock = asyncio.Lock()

        async def release_health():
            hub.health_lock.release()
            return True

        with patch.object(hub.health_lock, "acquire") as mock_acquire:
            mock_acquire.side_effect = [True, asyncio.TimeoutError]
            await hub.send_healthcheck(
                const.GET_HEALTH, bytes.fromhex("2A01"), b"\x00" * 10
            )
            hub.send_command.assert_awaited_once()


class TestHubRunStop:
    @pytest.mark.asyncio
    async def test_run_already_running(self, hub):
        hub.running = True
        await hub.run()

    @pytest.mark.asyncio
    async def test_run_and_stop(self, hub, mock_transport):
        hub.running = False
        hub.connect = AsyncMock()
        hub.update = AsyncMock()
        hub.disconnect = AsyncMock()
        mock_transport.close = AsyncMock()

        async def mock_response_parser():
            pass

        hub.response_parser = mock_response_parser

        run_task = asyncio.create_task(hub.run())
        await asyncio.sleep(0.05)
        assert hub.running is True

        await hub.stop()
        await run_task
        assert hub.running is False
        hub.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_already_stopped(self, hub):
        hub.running = False
        await hub.stop()

    @pytest.mark.asyncio
    async def test_stop_clears_data(self, hub, mock_transport):
        hub.running = True
        hub.rooms = {"r1": MagicMock()}
        hub.scenes = {"s1": MagicMock()}
        hub.timers = {"t1": MagicMock()}
        hub.rollers = {"r1": MagicMock()}
        hub.handshake.set()
        mock_transport.close = AsyncMock()

        await hub.stop()
        assert hub.rooms == {}
        assert hub.scenes == {}
        assert hub.timers == {}
        assert hub.rollers == {}
        assert hub.running is False


class TestHubDiscover:
    @pytest.mark.asyncio
    async def test_discover_sets_up_broadcast_client(self):
        with patch.object(aiopulse.transport, "HubTransportUdpBroadcast") as mock_cls:

            async def _receive():
                await asyncio.sleep(0.001)
                raise asyncio.TimeoutError

            mock_client = MagicMock()
            mock_client.connect = AsyncMock()
            mock_client.send = MagicMock()
            mock_client.receive = AsyncMock(side_effect=_receive)
            mock_client.close = AsyncMock()
            mock_cls.return_value = mock_client

            gen = Hub.discover(timeout=0.01)
            try:
                await asyncio.wait_for(gen.__anext__(), timeout=2.0)
            except (StopAsyncIteration, asyncio.TimeoutError):
                pass
            finally:
                await gen.aclose()

            mock_client.connect.assert_awaited_once()
            mock_client.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_discover_with_hub(self):
        with patch.object(aiopulse.transport, "HubTransportUdpBroadcast") as mock_cls, \
             patch.object(aiopulse.transport, "HubTransportTcp") as mock_tcp_cls:

            async def _receive():
                await asyncio.sleep(0.001)
                return (b"response", ("192.168.1.100", 12414))

            mock_client = MagicMock()
            mock_client.connect = AsyncMock()
            mock_client.send = MagicMock()
            mock_client.receive = AsyncMock(side_effect=_receive)
            mock_client.close = AsyncMock()
            mock_cls.return_value = mock_client

            ping = _ping_response()
            mock_tcp = MagicMock()
            mock_tcp.is_udp = False
            mock_tcp.connect = AsyncMock()
            mock_tcp.send = MagicMock()
            mock_tcp.receive = AsyncMock()
            mock_tcp.receive.side_effect = [
                const.HEADER + const.RESPONSE_CONNECT + b"12",
                const.HEADER + const.RESPONSE_LOGIN + b"\x00",
                const.HEADER + const.RESPONSE_SETID + ping,
                const.HEADER + const.RESPONSE_UNKNOWN1 + bytes.fromhex("06") + b"Smart_Id1_y:" + bytes.fromhex("16000f0002000000000000000c000600120311073816ff9d") + ping,
                const.HEADER + const.RESPONSE_SETID + ping,
            ]
            mock_tcp.close = AsyncMock()
            mock_tcp_cls.return_value = mock_tcp

            gen = Hub.discover(timeout=0.01)
            hubs = []
            try:
                hub = await asyncio.wait_for(gen.__anext__(), timeout=2.0)
                hubs.append(hub)
            except (StopAsyncIteration, asyncio.TimeoutError):
                pass
            finally:
                await gen.aclose()

            assert len(hubs) == 1
            assert hubs[0].host == "192.168.1.100"

    @pytest.mark.asyncio
    async def test_discover_connect_failure(self):
        with patch.object(aiopulse.transport, "HubTransportUdpBroadcast") as mock_cls, \
             patch.object(aiopulse.transport, "HubTransportTcp") as mock_tcp_cls:

            async def _receive():
                await asyncio.sleep(0.001)
                return (b"response", ("192.168.1.100", 12414))

            mock_client = MagicMock()
            mock_client.connect = AsyncMock()
            mock_client.send = MagicMock()
            mock_client.receive = AsyncMock(side_effect=_receive)
            mock_client.close = AsyncMock()
            mock_cls.return_value = mock_client

            mock_tcp = MagicMock()
            mock_tcp.connect = AsyncMock(side_effect=CannotConnectException("fail"))
            mock_tcp.close = AsyncMock()
            mock_tcp_cls.return_value = mock_tcp

            gen = Hub.discover(timeout=0.01)
            hubs = []
            try:
                hub = await asyncio.wait_for(gen.__anext__(), timeout=2.0)
                hubs.append(hub)
            except (StopAsyncIteration, asyncio.TimeoutError):
                pass
            finally:
                await gen.aclose()

            assert hubs == []


class TestHubUpdate:
    @pytest.mark.asyncio
    async def test_update(self, hub, mock_transport):
        hub.running = True
        hub.handshake.set()
        hub.send_command = AsyncMock()

        await hub.update()
        hub.send_command.assert_awaited_once_with(
            const.COMMAND_GET_HUB_INFO,
            bytes.fromhex("F000"),
            bytes.fromhex("000000000000FF"),
        )
