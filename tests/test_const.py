import pytest

from aiopulse.const import (
    UpdateType,
    HEADER,
    COMMAND_DISCOVER,
    RESPONSE_DISCOVER,
    COMMAND_CONNECT,
    RESPONSE_CONNECT,
    COMMAND_LOGIN,
    RESPONSE_LOGIN,
    COMMAND_PING,
    RESPONSE_PING,
    COMMAND_SETID,
    RESPONSE_SETID,
    COMMAND_UNKNOWN1,
    RESPONSE_UNKNOWN1,
    COMMAND_GET_HUB_INFO,
    RESPONSE_GET_HUB_INFO,
    COMMAND_MOVE_TO,
    RESPOSE_MOVE_TO,
    COMMAND_MOVE,
    GET_ROOMS,
    GET_ROLLERS,
    GET_HEALTH,
)


class TestUpdateType:
    def test_enum_values(self):
        assert UpdateType.info.value == 1
        assert UpdateType.rollers.value == 2
        assert UpdateType.rooms.value == 3
        assert UpdateType.scenes.value == 4
        assert UpdateType.timers.value == 5

    def test_enum_members(self):
        assert UpdateType(1) == UpdateType.info
        assert UpdateType(2) == UpdateType.rollers
        assert UpdateType(3) == UpdateType.rooms
        assert UpdateType(4) == UpdateType.scenes
        assert UpdateType(5) == UpdateType.timers


class TestConstants:
    def test_header(self):
        assert HEADER == bytes.fromhex("00000003")

    def test_discover(self):
        assert COMMAND_DISCOVER == bytes.fromhex("03000003")
        assert RESPONSE_DISCOVER == bytes.fromhex("57000004")

    def test_connect(self):
        assert COMMAND_CONNECT == bytes.fromhex("03000006")
        assert RESPONSE_CONNECT == bytes.fromhex("0f000007")

    def test_login(self):
        assert COMMAND_LOGIN == bytes.fromhex("0f000008")
        assert RESPONSE_LOGIN == bytes.fromhex("04000009")

    def test_ping(self):
        assert COMMAND_PING == bytes.fromhex("03000015")
        assert RESPONSE_PING == bytes.fromhex("03000016")

    def test_setid(self):
        assert COMMAND_SETID == bytes.fromhex("28000090")
        assert RESPONSE_SETID == bytes.fromhex("03000091")

    def test_unknown1(self):
        assert COMMAND_UNKNOWN1 == bytes.fromhex("23000090")
        assert RESPONSE_UNKNOWN1 == bytes.fromhex("28000091")

    def test_get_hub_info(self):
        assert COMMAND_GET_HUB_INFO == bytes.fromhex("1e000090")
        assert RESPONSE_GET_HUB_INFO == bytes.fromhex("4a000091")

    def test_move_to(self):
        assert COMMAND_MOVE_TO == bytes.fromhex("34000090")
        assert RESPOSE_MOVE_TO == bytes.fromhex("34000091")

    def test_move(self):
        assert COMMAND_MOVE == bytes.fromhex("2d000090")

    def test_get_rooms(self):
        assert GET_ROOMS == bytes.fromhex("01000091")

    def test_get_rollers(self):
        assert GET_ROLLERS == bytes.fromhex("03000091")

    def test_get_health(self):
        assert GET_HEALTH == bytes.fromhex("32000090")

    def test_all_constant_types(self):
        assert isinstance(HEADER, bytes)
        assert isinstance(COMMAND_DISCOVER, bytes)
        assert isinstance(RESPONSE_DISCOVER, bytes)
        assert isinstance(COMMAND_CONNECT, bytes)
        assert isinstance(RESPONSE_CONNECT, bytes)
        assert isinstance(COMMAND_LOGIN, bytes)
        assert isinstance(RESPONSE_LOGIN, bytes)
        assert isinstance(COMMAND_PING, bytes)
        assert isinstance(RESPONSE_PING, bytes)
        assert isinstance(COMMAND_SETID, bytes)
        assert isinstance(RESPONSE_SETID, bytes)
        assert isinstance(COMMAND_UNKNOWN1, bytes)
        assert isinstance(RESPONSE_UNKNOWN1, bytes)
        assert isinstance(COMMAND_GET_HUB_INFO, bytes)
        assert isinstance(RESPONSE_GET_HUB_INFO, bytes)
        assert isinstance(COMMAND_MOVE_TO, bytes)
        assert isinstance(RESPOSE_MOVE_TO, bytes)
        assert isinstance(COMMAND_MOVE, bytes)
        assert isinstance(GET_ROOMS, bytes)
        assert isinstance(GET_ROLLERS, bytes)
        assert isinstance(GET_HEALTH, bytes)
