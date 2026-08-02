"""Network transport abstraction for hub."""

import asyncio
import logging
import socket

# psutil does not provide type stubs in this project; ignore typing for import
import psutil  # type: ignore

from aiopulse.errors import NotConnectedException

_LOGGER = logging.getLogger(__name__)


class HubTransportBase(asyncio.Protocol):
    """Base class for Hub transport implementations."""

    def __init__(self) -> None:
        """Constructor for the base transport class."""
        self.transport: asyncio.BaseTransport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called when a connection is made."""
        _LOGGER.debug("Connection established")
        self.transport = transport

    def error_received(self, exc: Exception) -> None:
        """Called when an error is received."""
        _LOGGER.error("Error received: %s", exc)

    def connection_lost(self, exc: Exception | None) -> None:
        """Called when a connection is lost."""
        _LOGGER.debug("Socket closed")


class HubTransportUdp(HubTransportBase):
    """UDP Based Hub transport."""

    def __init__(self, host: str | None = None, port: int = 12414) -> None:
        """Constructor for UDP transport class."""
        self.host = host
        self.port = port
        self.transport: asyncio.DatagramTransport | None = None
        self.protocol: asyncio.DatagramProtocol | None = None
        self.is_udp: bool = True
        self.receive_queue: asyncio.Queue[tuple[bytes, tuple[str, int]]] = (
            asyncio.Queue()
        )
        super().__init__()

    async def connect(self, host: str | None = None) -> None:
        """Initialise connection."""
        if host:
            self.host = host

        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(  # type: ignore[assignment]
            lambda: self,
            remote_addr=(self.host or "", self.port),
        )

    async def close(self) -> None:
        """Close the connection."""
        if self.transport:
            self.transport.close()
        _LOGGER.debug("UDP connection closed")

    def send(self, buffer: bytes) -> None:
        """Abstraction of the underlying transport to send a buffer."""
        if not self.transport:
            raise NotConnectedException("UDP transport not connected")
        self.transport.sendto(buffer, (self.host or "", self.port))

    async def receive(self) -> tuple[bytes, tuple[str, int]]:
        """Abstraction of the underlying transport to receive."""
        if not self.transport:
            raise NotConnectedException("UDP transport not connected")
        return await self.receive_queue.get()

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Callback for a received datagram, enqueue it."""
        # Don't close the socket as we might get multiple responses.
        _LOGGER.debug("UDP datagram received")
        self.receive_queue.put_nowait((data, addr))


class HubTransportUdpBroadcast(HubTransportUdp):
    """UDP Based Hub transport."""

    async def connect(  # type: ignore[override]
        self, host: str = "255.255.255.255", bind_address: str | None = None
    ) -> None:
        """Init connection.

        Args:
            host: Broadcast address (default 255.255.255.255).
            bind_address: Local interface to bind to (e.g., '10.0.0.24').
                         If None, sends broadcast on all interfaces.
        """
        if host:
            self.host = host
        addrinfo = socket.getaddrinfo(self.host, None)
        sock = socket.socket(addrinfo[0][0], socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to specific interface if provided
        if bind_address:
            sock.bind((bind_address, 0))
            _LOGGER.debug(f"Socket bound to interface: {bind_address}")

        # Send a test broadcast to port 1500 (Windows discovery fix)
        sock.sendto(b"0", ("<broadcast>", 1500))

        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(  # type: ignore[assignment]
            lambda: self,
            sock=sock,
        )

    def send(self, buffer: bytes) -> None:
        """Send buffer - on all interfaces for broadcast, or main socket otherwise."""
        if not self.transport:
            raise NotConnectedException("UDP transport not connected")

        # For broadcast, send on all interfaces
        if self.host == "255.255.255.255":
            self._send_to_all_interfaces(buffer)
        else:
            self.transport.sendto(buffer, (self.host or "", self.port))

    def _send_to_all_interfaces(self, buffer: bytes) -> None:
        """Send buffer on all available network interfaces."""
        try:
            interfaces: list[str] = []
            for name, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    _LOGGER.debug(
                        "Interface %s has address %s (family %s)",
                        name,
                        addr.address,
                        addr.family,
                    )
                    if addr.family == socket.AF_INET:
                        interfaces.append(addr.address)

            _LOGGER.info(f"Sending on {len(interfaces)} interfaces: {interfaces}")

            # Get the main socket's port
            if self.transport:
                sockname = self.transport.get_extra_info("sockname")
                main_port = sockname[1] if sockname else 0
            else:
                main_port = 0

            for ip in interfaces:
                if not ip.startswith("127.") and not ip.startswith("169.254."):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        sock.bind((ip, main_port))
                        sock.sendto(buffer, (self.host or "", self.port))
                        sock.close()
                        _LOGGER.debug(f"Sent {len(buffer)} bytes on interface {ip}")
                    except Exception as e:
                        _LOGGER.debug(f"Failed to send on interface {ip}: {e}")
        except Exception as e:
            _LOGGER.debug(f"Error sending to all interfaces: {e}")


class HubTransportTcp(HubTransportBase):
    """TCP based Hub transport."""

    def __init__(self, host: str | None = None) -> None:
        """TCP Transport constructor."""
        self.host = host
        self.port: int = 12416

        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.transport: asyncio.BaseTransport | None = None
        self.protocol: asyncio.StreamReaderProtocol | None = None
        self.is_udp: bool = False
        self.connect_task: asyncio.Task[None] | None = None
        super().__init__()

    async def do_connection(self) -> None:
        """Try and establish a TCP connection."""
        loop = asyncio.get_running_loop()
        self.reader = asyncio.StreamReader()
        self.protocol = asyncio.StreamReaderProtocol(self.reader)

        # The following blocks until a connection is made
        writetransport, _ = await loop.create_connection(
            lambda: self, self.host or "", self.port
        )
        self.transport = writetransport
        self.writer = asyncio.StreamWriter(
            writetransport, self.protocol, self.reader, loop
        )

    async def connect(self, host: str | None = None) -> None:
        """Init connection."""
        if host:
            self.host = host

        if self.writer:
            _LOGGER.warning(f"{self.host}: Already connected.")
            return

        if self.connect_task and not self.connect_task.done():
            _LOGGER.warning(f"{self.host}: Already connecting.")
        else:
            self.connect_task = asyncio.create_task(self.do_connection())

        await self.connect_task

    async def close(self) -> None:
        """Close the connection."""
        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
                _LOGGER.debug(f"{self.host}: TCP buffer cleared.")
        except Exception as inst:
            _LOGGER.warning(f"{self.host}: Error closing writer cleanly: {inst}")
        finally:
            self.writer = None

        try:
            if self.transport:
                self.transport.close()
                _LOGGER.debug(f"{self.host}: TCP connection closed.")
            elif self.connect_task and not self.connect_task.done():
                self.connect_task.cancel()
            else:
                _LOGGER.warning(f"{self.host}: Not connected")
        except Exception as inst:
            _LOGGER.warning(f"{self.host}: Error closing TCP socket cleanly: {inst}")

    def send(self, buffer: bytes) -> None:
        """Abstraction of the underlying transport to send a buffer."""
        if not self.writer or self.writer.is_closing():
            raise NotConnectedException("TCP transport not connected")
        self.writer.write(buffer)

    async def receive(self) -> bytes:
        """Receive from stream."""
        if not self.reader or not self.writer or self.writer.is_closing():
            raise NotConnectedException("TCP transport not connected")
        return await self.reader.read(65535)

    def data_received(self, data: bytes) -> None:
        """Callback when data has been received."""
        if self.protocol:
            self.protocol.data_received(data)

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Callback when a connection has been made."""
        if self.protocol:
            self.protocol.connection_made(transport)
        super().connection_made(transport)

    def connection_lost(self, exc: Exception | None) -> None:
        """Callback when a connection is lost."""
        if self.protocol:
            self.protocol.connection_lost(exc)
        super().connection_lost(exc)
