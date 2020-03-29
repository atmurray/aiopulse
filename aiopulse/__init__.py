"""Rollease Acmeda Automate Pulse asyncio protocol implementation."""
import logging

from aiopulse.hub import Hub
from aiopulse.elements import Roller, Room, Scene
from aiopulse.errors import (
    NotConnectedException,
    NotRunningException,
    InvalidResponseException,
)

__all__ = [
    "Hub",
    "Roller",
    "Room",
    "Scene",
    "NotConnectedException",
    "NotRunningException",
    "InvalidResponseException",
]
__version__ = "0.2.3"
__author__ = "Alan Murray"

_LOGGER = logging.getLogger(__name__)
