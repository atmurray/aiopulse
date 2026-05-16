import pytest

from aiopulse.scene import Scene


class TestScene:
    @pytest.fixture
    def hub_mock(self):
        return type("HubMock", (), {"host": "192.168.1.100"})()

    @pytest.fixture
    def scene(self, hub_mock):
        return Scene(hub_mock, b"\x01\x00\x00\x00\x00\x00")

    def test_init(self, scene):
        assert scene.id == b"\x01\x00\x00\x00\x00\x00"
        assert scene.icon is None
        assert scene.name is None

    def test_str_with_values(self, scene):
        scene.name = "Test Scene"
        scene.icon = 3
        result = str(scene)
        assert "Test Scene" in result
        assert "Icon: 3" in result

    def test_str_no_name(self, scene):
        result = str(scene)
        assert "None" in result or "Name: None" in result
