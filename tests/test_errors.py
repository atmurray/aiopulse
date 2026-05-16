import pytest

from aiopulse.errors import (
    HubBaseException,
    NotConnectedException,
    NotRunningException,
    CannotConnectException,
    InvalidResponseException,
)


class TestErrors:
    def test_hub_base_exception(self):
        exc = HubBaseException("test")
        assert isinstance(exc, Exception)
        assert str(exc) == "test"

    def test_not_connected_exception(self):
        exc = NotConnectedException("not connected")
        assert isinstance(exc, HubBaseException)
        assert str(exc) == "not connected"

    def test_not_running_exception(self):
        exc = NotRunningException("not running")
        assert isinstance(exc, HubBaseException)
        assert str(exc) == "not running"

    def test_cannot_connect_exception(self):
        exc = CannotConnectException("cannot connect")
        assert isinstance(exc, HubBaseException)
        assert str(exc) == "cannot connect"

    def test_invalid_response_exception(self):
        exc = InvalidResponseException("invalid response")
        assert isinstance(exc, HubBaseException)
        assert str(exc) == "invalid response"

    def test_exception_chain(self):
        assert issubclass(NotConnectedException, HubBaseException)
        assert issubclass(NotRunningException, HubBaseException)
        assert issubclass(CannotConnectException, HubBaseException)
        assert issubclass(InvalidResponseException, HubBaseException)
        assert issubclass(HubBaseException, Exception)
