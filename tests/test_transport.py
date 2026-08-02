import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiopulse.errors import NotConnectedException
from aiopulse.transport import (
    HubTransportBase,
    HubTransportTcp,
    HubTransportUdp,
    HubTransportUdpBroadcast,
)


class TestHubTransportBase:
    def test_init(self):
        transport = HubTransportBase()
        assert transport.transport is None

    def test_connection_made(self):
        transport = HubTransportBase()
        mock_t = MagicMock()
        transport.connection_made(mock_t)
        assert transport.transport == mock_t

    def test_error_received(self):
        transport = HubTransportBase()
        transport.error_received(OSError("test"))
        assert transport.transport is None

    def test_connection_lost(self):
        transport = HubTransportBase()
        transport.connection_lost(None)
        assert transport.transport is None


class TestHubTransportUdp:
    @pytest.fixture
    def udp(self):
        return HubTransportUdp(host="192.168.1.100")

    def test_init(self, udp):
        assert udp.host == "192.168.1.100"
        assert udp.port == 12414
        assert udp.is_udp is True
        assert udp.transport is None
        assert udp.protocol is None

    @pytest.mark.asyncio
    async def test_connect(self, udp):
        with patch.object(asyncio, "get_running_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop
            mock_loop.create_datagram_endpoint = AsyncMock(
                return_value=(MagicMock(), MagicMock())
            )

            await udp.connect("192.168.1.200")
            assert udp.host == "192.168.1.200"
            mock_loop.create_datagram_endpoint.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, udp):
        udp.transport = MagicMock()
        await udp.close()
        udp.transport.close.assert_called_once()

    def test_send(self, udp):
        udp.transport = MagicMock()
        udp.send(b"test")
        udp.transport.sendto.assert_called_once_with(b"test", ("192.168.1.100", 12414))

    def test_send_not_connected(self, udp):
        udp.transport = None
        with pytest.raises(NotConnectedException):
            udp.send(b"test")

    def test_send_uses_host_port(self, udp):
        udp.transport = MagicMock()
        udp.host = "10.0.0.5"
        udp.port = 9999
        udp.send(b"data")
        udp.transport.sendto.assert_called_once_with(b"data", ("10.0.0.5", 9999))

    @pytest.mark.asyncio
    async def test_receive(self, udp):
        udp.transport = MagicMock()
        expected = (b"response", ("192.168.1.100", 12414))
        udp.receive_queue.put_nowait(expected)
        result = await udp.receive()
        assert result == expected

    def test_datagram_received(self, udp):
        udp.datagram_received(b"data", ("1.2.3.4", 5678))
        result = udp.receive_queue.get_nowait()
        assert result == (b"data", ("1.2.3.4", 5678))

    @pytest.mark.asyncio
    async def test_receive_not_connected(self, udp):
        udp.transport = None
        with pytest.raises(NotConnectedException):
            await udp.receive()


class TestHubTransportUdpBroadcast:
    @pytest.mark.asyncio
    async def test_connect(self):
        transport = HubTransportUdpBroadcast()
        with patch.object(asyncio, "get_running_loop") as mock_get_loop, \
             patch("socket.socket") as mock_socket:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_loop.create_datagram_endpoint = AsyncMock(
                return_value=(MagicMock(), MagicMock())
            )

            await transport.connect()
            assert transport.host == "255.255.255.255"
            assert mock_sock_instance.setsockopt.call_count == 2
            mock_loop.create_datagram_endpoint.assert_called_once()


class TestHubTransportTcp:
    @pytest.fixture
    def tcp(self):
        return HubTransportTcp(host="192.168.1.100")

    def test_init(self, tcp):
        assert tcp.host == "192.168.1.100"
        assert tcp.port == 12416
        assert tcp.is_udp is False
        assert tcp.reader is None
        assert tcp.writer is None
        assert tcp.transport is None

    @pytest.mark.asyncio
    async def test_do_connection(self, tcp):
        with patch.object(asyncio, "get_running_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop
            mock_loop.create_connection = AsyncMock(
                return_value=(MagicMock(), MagicMock())
            )
            mock_reader = MagicMock()
            mock_reader.set_exception = MagicMock()

            with patch("asyncio.StreamReader", return_value=mock_reader), \
                 patch("asyncio.StreamReaderProtocol"), \
                 patch("asyncio.StreamWriter"):

                await tcp.do_connection()
                mock_loop.create_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_new(self, tcp):
        tcp.writer = None
        tcp.connect_task = None
        with patch.object(tcp, "do_connection", AsyncMock()) as mock_do:
            await tcp.connect()
            mock_do.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_already_connected(self, tcp):
        tcp.writer = MagicMock()
        with patch.object(tcp, "do_connection", AsyncMock()) as mock_do:
            await tcp.connect()
            mock_do.assert_not_called()

    @pytest.mark.asyncio
    async def test_connect_new_host(self, tcp):
        tcp.writer = None
        tcp.connect_task = None
        with patch.object(tcp, "do_connection", AsyncMock()) as mock_do:
            await tcp.connect("10.0.0.1")
            assert tcp.host == "10.0.0.1"
            mock_do.assert_called_once()

    @pytest.mark.asyncio
    async def test_send(self, tcp):
        mock_writer = MagicMock()
        mock_writer.is_closing.return_value = False
        tcp.writer = mock_writer

        tcp.send(b"testdata")
        mock_writer.write.assert_called_once_with(b"testdata")

    @pytest.mark.asyncio
    async def test_send_not_connected(self, tcp):
        tcp.writer = None
        with pytest.raises(NotConnectedException):
            tcp.send(b"test")

    @pytest.mark.asyncio
    async def test_send_writer_closing(self, tcp):
        mock_writer = MagicMock()
        mock_writer.is_closing.return_value = True
        tcp.writer = mock_writer

        with pytest.raises(NotConnectedException):
            tcp.send(b"test")

    @pytest.mark.asyncio
    async def test_receive(self, tcp):
        mock_writer = MagicMock()
        mock_writer.is_closing.return_value = False
        tcp.writer = mock_writer
        mock_reader = AsyncMock()
        mock_reader.read.return_value = b"response"
        tcp.reader = mock_reader

        result = await tcp.receive()
        assert result == b"response"
        mock_reader.read.assert_called_once_with(65535)

    @pytest.mark.asyncio
    async def test_receive_writer_closing(self, tcp):
        mock_writer = MagicMock()
        mock_writer.is_closing.return_value = True
        tcp.writer = mock_writer

        with pytest.raises(NotConnectedException):
            await tcp.receive()

    @pytest.mark.asyncio
    async def test_receive_not_connected(self, tcp):
        tcp.writer = None
        tcp.reader = None
        with pytest.raises(NotConnectedException):
            await tcp.receive()

    @pytest.mark.asyncio
    async def test_close_with_writer(self, tcp):
        mock_writer = MagicMock()
        mock_writer.is_closing.return_value = False
        mock_writer.wait_closed = AsyncMock()
        tcp.writer = mock_writer
        tcp.transport = MagicMock()

        await tcp.close()
        mock_writer.close.assert_called_once()
        tcp.transport.close.assert_called_once()
        assert tcp.writer is None

    @pytest.mark.asyncio
    async def test_close_without_writer(self, tcp):
        tcp.writer = None
        tcp.transport = None

        await tcp.close()
        # Should not raise

    def test_data_received(self, tcp):
        mock_protocol = MagicMock()
        tcp.protocol = mock_protocol
        tcp.data_received(b"data")
        mock_protocol.data_received.assert_called_once_with(b"data")

    def test_connection_made(self, tcp):
        mock_protocol = MagicMock()
        tcp.protocol = mock_protocol
        mock_transport = MagicMock()
        tcp.connection_made(mock_transport)
        mock_protocol.connection_made.assert_called_once_with(mock_transport)
        assert tcp.transport == mock_transport

    def test_connection_lost(self, tcp):
        mock_protocol = MagicMock()
        tcp.protocol = mock_protocol
        tcp.connection_lost(None)
        mock_protocol.connection_lost.assert_called_once_with(None)
