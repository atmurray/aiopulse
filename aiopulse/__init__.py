"""Rollease Acmeda Automate Pulse asyncio protocol implementation."""

import logging

from aiopulse.const import UpdateType
from aiopulse.errors import (
    CannotConnectException,
    InvalidResponseException,
    NotConnectedException,
    NotRunningException,
)
from aiopulse.hub import Hub
from aiopulse.roller import Roller
from aiopulse.room import Room
from aiopulse.scene import Scene
from aiopulse.timer import Timer

__all__ = [
    "Hub",
    "Roller",
    "Room",
    "Scene",
    "Timer",
    "CannotConnectException",
    "NotConnectedException",
    "NotRunningException",
    "InvalidResponseException",
    "UpdateType",
]
__version__ = "0.5.2"
__author__ = "Alan Murray"

_LOGGER = logging.getLogger(__name__)
