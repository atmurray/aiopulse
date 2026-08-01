"""Scene entity that hangs off the hub."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiopulse.entities import HubEntity

if TYPE_CHECKING:
    from aiopulse.hub import Hub


class Scene(HubEntity):
    """Representation of a Scene."""

    def __init__(self, hub: Hub, scene_id: bytes) -> None:
        """Init a new scene.

        Args:
            hub: The hub instance.
            scene_id: The unique scene identifier.
        """
        super().__init__(hub, scene_id)

    def __str__(self) -> str:
        """Returns string representation of scene."""
        return "Name: {} ID: {} Icon: {}".format(
            self.name, self.id[0:4] if isinstance(self.id, bytes) else self.id, self.icon
        )
