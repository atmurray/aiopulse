# Task 4: Create HubEntity Base Class

**Files:**
- Create: `aiopulse/entities.py`
- Create: `tests/test_entities.py`

**Interfaces:**
- Produces: `HubEntity` class inheriting from `CallbackMixin`

- [ ] **Step 1: Write tests for HubEntity**

```python
# tests/test_entities.py
import pytest
from unittest.mock import MagicMock

from aiopulse.entities import HubEntity


class ConcreteEntity(HubEntity):
    """Concrete implementation for testing."""

    pass


class TestHubEntity:
    @pytest.fixture
    def hub_mock(self):
        hub = MagicMock()
        hub.host = "192.168.1.100"
        return hub

    @pytest.fixture
    def entity(self, hub_mock):
        return ConcreteEntity(hub=hub_mock, entity_id=123)

    def test_init_with_int_id(self, hub_mock):
        entity = ConcreteEntity(hub=hub_mock, entity_id=123)
        assert entity.hub == hub_mock
        assert entity.id == 123
        assert entity.name is None
        assert entity.icon is None
        assert entity._update_callbacks == []

    def test_init_with_bytes_id(self, hub_mock):
        entity = ConcreteEntity(hub=hub_mock, entity_id=b"\x01\x02\x03\x04")
        assert entity.id == b"\x01\x02\x03\x04"

    def test_callback_subscribe(self, entity):
        callback = MagicMock()
        entity.callback_subscribe(callback)
        assert callback in entity._update_callbacks

    def test_callback_unsubscribe(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.callback_unsubscribe(callback)
        assert callback not in entity._update_callbacks

    def test_notify_callback(self, entity):
        callback = MagicMock()
        entity._update_callbacks.append(callback)
        entity.notify_callback()
        callback.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_entities.py -v`
Expected: FAIL (ImportError: cannot import 'HubEntity')

- [ ] **Step 3: Create HubEntity base class**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_entities.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/entities.py tests/test_entities.py
git commit -m "feat: add HubEntity base class for hub entities"
```
