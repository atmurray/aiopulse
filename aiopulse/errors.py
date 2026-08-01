"""Error classes of aiopulse module."""
from __future__ import annotations


class HubBaseException(Exception):
    """Base Exception for protocol."""

    def __init__(
        self, message: str = "", response: bytes | None = None
    ) -> None:
        """Initialize exception with optional response context."""
        super().__init__(message)
        self.response = response


class NotConnectedException(HubBaseException):
    """Exception thrown when the hub isn't connected."""

    pass


class NotRunningException(HubBaseException):
    """Exception thrown when the hub isn't running."""

    pass


class CannotConnectException(HubBaseException):
    """Exception thrown when a socket connection cannot be made."""

    pass


class InvalidResponseException(HubBaseException):
    """Exception thrown when an invalid response is received."""

    pass
