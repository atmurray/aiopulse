import pytest

from aiopulse.const import (
    UpdateType,
    MessageType,
    CommandType,
    ResponseType,
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


class TestUpdateType:
    def test_update_type_values(self):
        assert UpdateType.info.name == "info"
        assert UpdateType.rollers.name == "rollers"
        assert UpdateType.rooms.name == "rooms"
        assert UpdateType.scenes.name == "scenes"
        assert UpdateType.timers.name == "timers"


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
