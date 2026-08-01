"""Timer entity that hangs off the hub."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiopulse.entities import HubEntity

if TYPE_CHECKING:
    from aiopulse.hub import Hub


class Timer(HubEntity):
    """Representation of a Timer."""

    def __init__(self, hub: Hub, timer_id: bytes) -> None:
        """Init a new timer.

        Args:
            hub: The hub instance.
            timer_id: The unique timer identifier.
        """
        super().__init__(hub, timer_id)
        self.state: int | None = None
        self.hour: int | None = None
        self.minute: int | None = None
        self.days: int | None = None
        self.entity: HubEntity | None = None

    def __str__(self) -> str:
        """Returns string representation of timer."""
        id_str = self.id[0:4].hex() if isinstance(self.id, bytes) else str(self.id)
        days_str = f"{self.days:>07b}" if self.days is not None else "None"
        entity_str = self.entity.name if self.entity else "None"
        return (
            f"Name: {self.name} "
            f"ID: {id_str} "
            f"Icon: {self.icon} "
            f"State: {self.state} "
            f"Time: {self.hour}:{self.minute} "
            f"Days: {days_str} "
            f"Entity: {entity_str}"
        )
