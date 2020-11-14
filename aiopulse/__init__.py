"""Rollease Acmeda Automate Pulse asyncio protocol implementation."""
import logging

from aiopulse.hub import Hub
from aiopulse.elements import Roller, Room, Scene
from aiopulse.errors import (
    CannotConnectException,
    NotConnectedException,
    NotRunningException,
    InvalidResponseException,
)
from aiopulse.const import UpdateType

__all__ = [
    "Hub",
    "Roller",
    "Room",
    "Scene",
    "CannotConnectException",
    "NotConnectedException",
    "NotRunningException",
    "InvalidResponseException",
    "UpdateType",
]
__version__ = "0.4.2"
__author__ = "Alan Murray"

_LOGGER = logging.getLogger(__name__)
