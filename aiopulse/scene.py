"""Elements that hang off the hub."""
from typing import List, Callable

import aiopulse.utils as utils
import aiopulse.const as const
import asyncio


class Scene:
    """Representation of a Scene."""

    def __init__(self, hub, scene_id):
        """Init a new scene."""
        self.hub = hub
        self.id = scene_id
        self.icon = None
        self.name = None

    def __str__(self):
        """Returns string representation of scene."""
        return "Name: {} ID: {} Icon: {}".format(self.name, self.id[0:4], self.icon)
