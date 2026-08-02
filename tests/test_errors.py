
from aiopulse.errors import (
    CannotConnectException,
    HubBaseException,
    InvalidResponseException,
    NotConnectedException,
    NotRunningException,
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


class TestHubBaseException:
    def test_basic_creation(self):
        exc = HubBaseException("test message")
        assert str(exc) == "test message"

    def test_with_response_context(self):
        response = b"\x00\x01\x02\x03"
        exc = HubBaseException("test message", response=response)
        assert exc.response == response


class TestInvalidResponseException:
    def test_basic_creation(self):
        exc = InvalidResponseException("invalid response")
        assert str(exc) == "invalid response"
        assert exc.response is None

    def test_with_response(self):
        response = b"\xff\xff\xff\xff"
        exc = InvalidResponseException("invalid header", response=response)
        assert exc.response == response
        assert b"\xff\xff" in exc.response


class TestNotConnectedException:
    def test_basic_creation(self):
        exc = NotConnectedException("not connected")
        assert str(exc) == "not connected"


class TestCannotConnectException:
    def test_basic_creation(self):
        exc = CannotConnectException("connection refused")
        assert str(exc) == "connection refused"


class TestNotRunningException:
    def test_basic_creation(self):
        exc = NotRunningException("not running")
        assert str(exc) == "not running"
