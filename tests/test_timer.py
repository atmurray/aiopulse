import pytest

from aiopulse.timer import Timer


class TestTimer:
    @pytest.fixture
    def hub_mock(self):
        hub = type("HubMock", (), {"host": "192.168.1.100"})()
        hub.rollers = {}
        hub.scenes = {}
        return hub

    @pytest.fixture
    def timer(self, hub_mock):
        return Timer(hub_mock, b"\x01\x00\x00\x00\x00\x00")

    def test_init(self, timer):
        assert timer.id == b"\x01\x00\x00\x00\x00\x00"
        assert timer.icon is None
        assert timer.name is None
        assert timer.state is None
        assert timer.hour is None
        assert timer.minute is None
        assert timer.days is None
        assert timer.entity is None

    def test_str_all_fields(self, timer):
        timer.name = "Morning"
        timer.icon = 5
        timer.state = 1
        timer.hour = 7
        timer.minute = 30
        timer.days = 0b01111111
        result = str(timer)
        assert "Morning" in result
        assert "State: 1" in result
        assert "Time: 7:30" in result
        assert "Entity: None" in result

    def test_str_with_entity(self, timer, hub_mock):
        roller_mock = type("RollerMock", (), {"name": "Living Room"})()
        timer.entity = roller_mock
        timer.name = "Test"
        timer.icon = 1
        timer.state = 1
        timer.hour = 8
        timer.minute = 0
        timer.days = 0
        result = str(timer)
        assert "Living Room" in result
