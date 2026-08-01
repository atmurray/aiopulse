# Task 14: Update utils.py with Type Hints

**Files:**
- Modify: `aiopulse/utils.py`

**Interfaces:**
- Produces: Type-annotated utility functions

- [ ] **Step 1: Update utils.py with type hints**

```python
"""Serialisation / Deserialisation helpers."""
from __future__ import annotations


def unpack_int(buffer: bytes, ptr: int, length: int) -> tuple[int, int]:
    """Unpack an int of specified length from the buffer and advance the pointer.

    Args:
        buffer: The bytes buffer to read from.
        ptr: Current position in the buffer.
        length: Number of bytes to read.

    Returns:
        Tuple of (value, new_pointer).
    """
    return (
        int.from_bytes(buffer[ptr : (ptr + length)], "little", signed=False),
        ptr + length,
    )


def pack_int(value: int, length: int) -> bytes:
    """Pack an int for serialisation.

    Args:
        value: The integer value to pack.
        length: Number of bytes to use.

    Returns:
        Bytes representation.
    """
    return value.to_bytes(length, "little", signed=False)


def unpack_bytes(
    buffer: bytes, ptr: int, length: int | None = None
) -> tuple[bytes, int]:
    """Unpack a specified number of bytes from the buffer and advance the pointer.

    Args:
        buffer: The bytes buffer to read from.
        ptr: Current position in the buffer.
        length: Number of bytes to read, or None to read length prefix.

    Returns:
        Tuple of (bytes, new_pointer).
    """
    ptr_new = ptr
    if not length:
        length, ptr_new = unpack_int(buffer, ptr, 2)
    return (buffer[(ptr_new) : (ptr_new + length)], ptr_new + length)


def unpack_string(
    buffer: bytes, ptr: int, length: int | None = None
) -> tuple[str, int]:
    """Unpack a specified number of characters from the buffer and advance the pointer.

    Args:
        buffer: The bytes buffer to read from.
        ptr: Current position in the buffer.
        length: Number of bytes to read, or None to read length prefix.

    Returns:
        Tuple of (string, new_pointer).
    """
    str_new, ptr_new = unpack_bytes(buffer, ptr, length=None)
    return (str_new.decode("utf-8", "ignore"), ptr_new)


def unpack_roller_percent(buffer: bytes, ptr: int) -> tuple[int, int]:
    """Unpack roller close percentage.

    Args:
        buffer: The bytes buffer to read from.
        ptr: Current position in the buffer.

    Returns:
        Tuple of (percent, new_pointer).
    """
    ptr += 4
    roller_state, ptr = unpack_bytes(buffer, ptr, 1)
    ptr += 5  # unknown field
    if roller_state == b"\x10":  # roller is open
        ptr += 1  # unused percent field
        return 0, ptr
    elif roller_state == b"\x12":  # roller is closed
        ptr += 1  # unused percent field
        return 100, ptr
    else:  # read roller percent
        return unpack_int(buffer, ptr, 1)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_utils.py -v`
Expected: All tests pass

- [ ] **Step 3: Commit**

```bash
git add aiopulse/utils.py
git commit -m "refactor: add type hints to utils module"
```
