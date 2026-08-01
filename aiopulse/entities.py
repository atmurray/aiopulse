"""Base class for hub entities."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiopulse.callbacks import CallbackMixin

if TYPE_CHECKING:
    from aiopulse.hub import Hub


class HubEntity(CallbackMixin):
    """Base class for entities managed by a hub."""

    def __init__(self, hub: Hub, entity_id: bytes | int) -> None:
        """Initialize entity.

        Args:
            hub: The hub instance that manages this entity.
            entity_id: The unique identifier for this entity.
        """
        super().__init__()
        self.hub = hub
        self.id = entity_id
        self.name: str | None = None
        self.icon: int | None = None
