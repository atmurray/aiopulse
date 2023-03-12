"""Elements that hang off the hub."""
from typing import List, Callable

import aiopulse.utils as utils
import aiopulse.const as const
import asyncio


class Timer:
    """Representation of a Timer."""

    def __init__(self, hub, timer_id):
        """Init a new timer."""
        self.hub = hub
        self.id = timer_id
        self.icon = None
        self.name = None
        self.state = None
        self.hour = None
        self.minute = None
        self.days = None
        self.entity = None

    def __str__(self):
        """Returns string representation of timer."""
        return (
            f"Name: {self.name} "
            f"ID: {self.id[0:4]} "
            f"Icon: {self.icon} "
            f"State: {self.state} "
            f"Time: {self.hour}:{self.minute} "
            f"Days: {self.days:>07b} "
            f'Entity: {self.entity.name if self.entity else "None"}'
        )
