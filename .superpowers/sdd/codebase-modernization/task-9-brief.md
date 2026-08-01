# Task 9: Organize Protocol Constants with Enums

**Files:**
- Modify: `aiopulse/const.py`
- Modify: `tests/test_const.py`

**Interfaces:**
- Produces: `MessageType`, `CommandType`, `ResponseType` enums

- [ ] **Step 1: Write tests for new enums**

```python
# tests/test_const.py
import pytest
from aiopulse.const import UpdateType, MessageType, CommandType, ResponseType, HEADER


class TestUpdateType:
    def test_update_type_values(self):
        assert UpdateType.info.name == "info"
        assert UpdateType.rollers.name == "rollers"
        assert UpdateType.rooms.name == "rooms"
        assert UpdateType.scenes.name == "scenes"
        assert UpdateType.timers.name == "timers"


class TestMessageType:
    def test_message_type_values(self):
        assert MessageType.HUB_INFO == 0x1600
        assert MessageType.ROOM_LIST == 0x0101
        assert MessageType.ROLLER_LIST == 0x2101
        assert MessageType.SCENE_LIST == 0x3301
        assert MessageType.TIMER_LIST == 0x4101
        assert MessageType.POSITION == 0x2301
        assert MessageType.ROLLER_UPDATED == 0x2501
        assert MessageType.ROLLER_HEALTH == 0x2B01

    def test_message_type_is_int(self):
        assert isinstance(MessageType.HUB_INFO, int)


class TestCommandType:
    def test_command_type_values(self):
        assert CommandType.DISCOVER == 0x03000003
        assert CommandType.CONNECT == 0x03000006
        assert CommandType.LOGIN == 0x0F000008
        assert CommandType.PING == 0x03000015
        assert CommandType.SETID == 0x28000090
        assert CommandType.GET_HUB_INFO == 0x1E000090
        assert CommandType.MOVE_TO == 0x34000090
        assert CommandType.MOVE == 0x2D000090
        assert CommandType.GET_HEALTH == 0x32000090


class TestResponseType:
    def test_response_type_values(self):
        assert ResponseType.DISCOVER == 0x57000004
        assert ResponseType.CONNECT == 0x0F000007
        assert ResponseType.LOGIN == 0x04000009
        assert ResponseType.PING == 0x03000016
        assert ResponseType.SETID == 0x03000091
        assert ResponseType.GET_HUB_INFO == 0x4A000091
        assert ResponseType.MOVE_TO == 0x34000091


class TestConstants:
    def test_header(self):
        assert HEADER == bytes.fromhex("00000003")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_const.py -v`
Expected: FAIL (ImportError for new enums)

- [ ] **Step 3: Update const.py with organized enums**

```python
"""Acmeda Pulse Hub constants."""
from enum import Enum, IntEnum


class UpdateType(Enum):
    """Types of hub updates."""
    info = "info"
    rollers = "rollers"
    rooms = "rooms"
    scenes = "scenes"
    timers = "timers"


class MessageType(IntEnum):
    """Protocol message types for incoming messages."""
    HUB_INFO = 0x1600
    HUB_INFO_UPDATED = 0x0D00
    ROOM_LIST = 0x0101
    SCENE_LIST = 0x3301
    ROLLER_LIST = 0x2101
    TIMER_LIST = 0x4101
    AUTH_INFO = 0x0800
    POSITION = 0x2301
    ROLLER_UPDATED = 0x2501
    TIMER_CREATED = 0x4301
    TIMER_DEVICE_UPDATED = 0x4501
    TIMER_INFO_UPDATED = 0x4901
    TIMER_DELETED = 0x4701
    ROLLER_HEALTH = 0x2B01
    DISCOVER_RESPONSE = 0x0F00


class CommandType(IntEnum):
    """Command message types."""
    DISCOVER = 0x03000003
    CONNECT = 0x03000006
    LOGIN = 0x0F000008
    PING = 0x03000015
    SETID = 0x28000090
    UNKNOWN1 = 0x23000090
    GET_HUB_INFO = 0x1E000090
    MOVE_TO = 0x34000090
    MOVE = 0x2D000090
    GET_HEALTH = 0x32000090


class ResponseType(IntEnum):
    """Response message types."""
    DISCOVER = 0x57000004
    CONNECT = 0x0F000007
    LOGIN = 0x04000009
    PING = 0x03000016
    SETID = 0x03000091
    UNKNOWN1 = 0x28000091
    GET_HUB_INFO = 0x4A000091
    MOVE_TO = 0x34000091
    GET_ROOMS = 0x01000091
    GET_ROLLERS = 0x03000091


HEADER = bytes.fromhex("00000003")

# Keep old constants for backward compatibility
COMMAND_DISCOVER = bytes.fromhex("03000003")
RESPONSE_DISCOVER = bytes.fromhex("57000004")

COMMAND_CONNECT = bytes.fromhex("03000006")
RESPONSE_CONNECT = bytes.fromhex("0f000007")

COMMAND_LOGIN = bytes.fromhex("0f000008")
RESPONSE_LOGIN = bytes.fromhex("04000009")

COMMAND_PING = bytes.fromhex("03000015")
RESPONSE_PING = bytes.fromhex("03000016")

COMMAND_SETID = bytes.fromhex("28000090")
RESPONSE_SETID = bytes.fromhex("03000091")

COMMAND_UNKNOWN1 = bytes.fromhex("23000090")
RESPONSE_UNKNOWN1 = bytes.fromhex("28000091")

COMMAND_GET_HUB_INFO = bytes.fromhex("1e000090")
RESPONSE_GET_HUB_INFO = bytes.fromhex("4a000091")

COMMAND_MOVE_TO = bytes.fromhex("34000090")
RESPOSE_MOVE_TO = bytes.fromhex("34000091")

COMMAND_MOVE = bytes.fromhex("2d000090")

GET_ROOMS = bytes.fromhex("01000091")
GET_ROLLERS = bytes.fromhex("03000091")

GET_HEALTH = bytes.fromhex("32000090")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_const.py -v`
Expected: All tests pass

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add aiopulse/const.py tests/test_const.py
git commit -m "refactor: organize protocol constants with enums"
```
