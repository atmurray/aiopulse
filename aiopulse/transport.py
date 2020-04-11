"""Network transport abstraction for hub."""
import logging
import asyncio
import socket

from aiopulse.errors import NotConnectedException

_LOGGER = logging.getLogger(__name__)


class HubTransportBase(asyncio.Protocol):
    """Base class for Hub transport implementations."""

    def __init__(self):
        """Constructor for the base transport class."""
        self.transport = None

    def connection_made(self, transport):
        """Called when a connection is made."""
        _LOGGER.debug("Connection established")
        self.transport = transport

    def error_received(self, exc):
        """Called when an error is received."""
        _LOGGER.error("Error received: %s", exc)

    def connection_lost(self, exc):
        """Called when a connection is lost."""
        _LOGGER.info("Socket closed")


class HubTransportUdp(HubTransportBase):
    """UDP Based Hub transport."""

    def __init__(self, host=None, port=12414):
        """Constructor for UDP transport class."""
        self.host = host
        self.port = port
        self.transport = None
        self.protocol = None
        self.is_udp = True
        self.receive_queue = asyncio.Queue()
        super().__init__()

    async def connect(self, host=None):
        """Initialise connection."""
        if host:
            self.host = host

        loop = asyncio.get_event_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: self, remote_addr=(self.host, self.port),
        )

    async def close(self):
        """Close the connection."""
        self.transport.close()
        _LOGGER.info("UDP connection closed")

    def send(self, buffer):
        """Abstraction of the underlying transport to send a buffer."""
        self.transport.sendto(buffer, (self.host, self.port))

    async def receive(self):
        """Abstraction of the underlying transport to receive."""
        return await self.receive_queue.get()

    def datagram_received(self, data, addr):
        """Callback for a received datagram, enqueue it."""
        # Don't close the socket as we might get multiple responses.
        _LOGGER.debug("UDP datagram received")
        self.receive_queue.put_nowait((data, addr))


class HubTransportUdpBroadcast(HubTransportUdp):
    """UDP Based Hub transport."""

    async def connect(self, host="255.255.255.255"):
        """Init connection."""
        if host:
            self.host = host
        addrinfo = socket.getaddrinfo(self.host, None)[0]
        sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        loop = asyncio.get_event_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: self, sock=sock,
        )


class HubTransportTcp(HubTransportBase):
    """TCP based Hub transport."""

    def __init__(self, host=None):
        """TCP Transport constructor."""
        self.host = host
        self.port = 12416

        self.reader = None
        self.writer = None
        self.transport = None
        self.protocol = None
        self.is_udp = False
        super().__init__()

    async def connect(self, host=None):
        """Init connection."""
        if host:
            self.host = host

        if self.writer:
            _LOGGER.warn("Already connected.")
            return

        loop = asyncio.get_event_loop()
        self.reader = asyncio.StreamReader(loop=loop)
        # super().__init__(self.reader)
        self.protocol = asyncio.StreamReaderProtocol(self.reader, loop=loop)
        self.transport, _ = await loop.create_connection(
            lambda: self, self.host, self.port
        )
        self.writer = asyncio.StreamWriter(
            self.transport, self.protocol, self.reader, loop
        )

    async def close(self):
        """Close the connection."""
        if not self.writer:
            _LOGGER.error("Not connected")
            return

        self.writer.close()
        await self.writer.wait_closed()
        self.writer = None
        _LOGGER.info("TCP connection closed.")

    def send(self, buffer):
        """Abstraction of the underlying transport to send a buffer."""
        self.writer.write(buffer)

    async def receive(self):
        """Receive from stream."""
        if self.writer.is_closing():
            raise NotConnectedException
        return await self.reader.read(65535)

    def data_received(self, data):
        """Callback when data has been received."""
        _LOGGER.debug("TCP data received.")
        self.protocol.data_received(data)

    def connection_made(self, transport):
        """Callback when a connection has been made."""
        self.protocol.connection_made(transport)
        super().connection_made(transport)

    def connection_lost(self, exc):
        """Callback when a connection is lost."""
        self.protocol.connection_lost(exc)
        super().connection_lost(exc)
