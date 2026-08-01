# Task 6: Update Scene to Use HubEntity

**Files:**
- Modify: `aiopulse/scene.py`
- Modify: `tests/test_scene.py`

**Interfaces:**
- Consumes: `HubEntity` from `aiopulse.entities`
- Produces: `Scene` class inheriting from `HubEntity`

- [ ] **Step 1: Update scene.py to use HubEntity**

```python
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
```

- [ ] **Step 2: Update test_scene.py for HubEntity**

```python
# tests/test_scene.py
from unittest.mock import MagicMock

import pytest

from aiopulse.scene import Scene


class TestScene:
    @pytest.fixture
    def hub_mock(self):
        hub = MagicMock()
        hub.host = "192.168.1.100"
        return hub

    @pytest.fixture
    def scene(self, hub_mock):
        return Scene(hub_mock, b"\x01\x02\x03\x04")

    def test_init(self, scene):
        assert scene.id == b"\x01\x02\x03\x04"
        assert scene.name is None
        assert scene.icon is None
        assert scene.hub is not None
        assert scene._update_callbacks == []

    def test_str(self, scene):
        scene.name = "Movie Night"
        scene.icon = 5
        result = str(scene)
        assert "Movie Night" in result

    def test_callback_subscribe(self, scene):
        callback = MagicMock()
        scene.callback_subscribe(callback)
        assert callback in scene._update_callbacks

    def test_callback_unsubscribe(self, scene):
        callback = MagicMock()
        scene._update_callbacks.append(callback)
        scene.callback_unsubscribe(callback)
        assert callback not in scene._update_callbacks

    def test_notify_callback(self, scene):
        callback = MagicMock()
        scene._update_callbacks.append(callback)
        scene.notify_callback()
        callback.assert_called_once()
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pytest tests/test_scene.py -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add aiopulse/scene.py tests/test_scene.py
git commit -m "refactor: Scene inherits from HubEntity"
```
