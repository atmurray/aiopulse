import asyncio
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

import aiopulse.transport
from aiopulse.hub import Hub


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_transport():
    transport = MagicMock(spec=aiopulse.transport.HubTransportTcp)
    transport.is_udp = False
    transport.host = "192.168.1.100"
    transport.send = MagicMock()
    transport.close = AsyncMock()
    return transport


@pytest.fixture
def hub(event_loop, mock_transport):
    with patch.object(aiopulse.transport, "HubTransportTcp", return_value=mock_transport):
        h = Hub(host="192.168.1.100", loop=event_loop)
        h.running = False
        h.async_add_job = MagicMock(return_value=MagicMock())
        yield h


@pytest.fixture
def connected_hub(hub, mock_transport):
    hub.handshake.set()
    hub.id = "12345"
    hub.running = True
    mock_transport.receive = AsyncMock()
    return hub


@pytest.fixture
def mock_discover_client():
    client = MagicMock()
    client.connect = AsyncMock()
    client.send = MagicMock()
    client.receive = AsyncMock()
    client.close = AsyncMock()
    return client
