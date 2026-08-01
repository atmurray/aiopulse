from aiopulse.const import (
    UpdateType,
    MessageType,
    CommandType,
    ResponseType,
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
