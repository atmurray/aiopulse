# Task 2: Update Errors Module with Context

**Files:**
- Modify: `aiopulse/errors.py`

**Interfaces:**
- Consumes: None
- Produces: Enhanced exception classes with optional context

- [ ] **Step 1: Write tests for enhanced errors**

```python
# tests/test_errors.py
import pytest
from aiopulse.errors import (
    HubBaseException,
    NotConnectedException,
    NotRunningException,
    CannotConnectException,
    InvalidResponseException,
)


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_errors.py -v`
Expected: FAIL (ImportError or tests fail)

- [ ] **Step 3: Update errors.py with context support**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_errors.py -v`
Expected: All tests pass

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add aiopulse/errors.py tests/test_errors.py
git commit -m "feat: add response context to exception classes"
```
