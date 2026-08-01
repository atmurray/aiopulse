# Task 13: Update Hub Callbacks to Use CallbackMixin

**Files:**
- Modify: `aiopulse/hub.py`

**Interfaces:**
- Consumes: `CallbackMixin` from `aiopulse.callbacks`
- Produces: Hub using CallbackMixin for callbacks

- [ ] **Step 1: Update hub.py to inherit from CallbackMixin**

```python
"""Acmeda Pulse Hub Interface."""
from __future__ import annotations

import asyncio
import binascii
import logging
import warnings
from typing import Any, Callable

import async_timeout

import aiopulse.const as const
import aiopulse.utils as utils
import aiopulse.errors as errors
import aiopulse.transport
from aiopulse.callbacks import CallbackMixin

_LOGGER = logging.getLogger(__name__)


class Hub(CallbackMixin):
    """Representation of an Acmeda Pulse Hub."""

    def __init__(
        self, host: str | None = None, loop: asyncio.AbstractEventLoop | None = None
    ) -> None:
        """Init the hub.

        Args:
            host: The hub's IP address or hostname.
            loop: Deprecated. The event loop to use.
        """
        super().__init__()
        
        if loop is not None:
            warnings.warn(
                "loop parameter is deprecated and will be removed in v0.6.0",
                DeprecationWarning,
                stacklevel=2,
            )

        self.topic: bytes = str.encode("Smart_Id1_y:")
        self.sequence: int = 4
        self.handshake: asyncio.Event = asyncio.Event()
        self.command_lock: asyncio.Lock = asyncio.Lock()
        self.health_lock: asyncio.Lock = asyncio.Lock()
        self.response_task: asyncio.Task | None = None
        self.running: bool = False

        self.id: str | None = None
        self.host: str | None = host
        self.mac_address: str | None = None
        self.ip_address: str | None = None
        self.firmware_name: str | None = None
        self.wifi_module: str | None = None

        self.protocol = aiopulse.transport.HubTransportTcp(host)

        self.rollers: dict[int, aiopulse.Roller] = {}
        self.rooms: dict[int, aiopulse.Room] = {}
        self.scenes: dict[int, aiopulse.Scene] = {}
        self.timers: dict[int, aiopulse.Timer] = {}

        self.handshake.clear()

    # ... rest of hub methods
```

- [ ] **Step 2: Remove duplicate callback methods from Hub**

Remove these methods from Hub (they're now in CallbackMixin):
- `callback_subscribe()`
- `callback_unsubscribe()`
- `notify_callback()`
- `async_add_job()`

- [ ] **Step 3: Update Hub.notify_callback calls**

Update all calls to use the inherited `notify_callback()` method.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_hub.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/hub.py
git commit -m "refactor: Hub inherits from CallbackMixin"
```
