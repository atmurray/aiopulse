# Task 11: Add Transport State Validation

**Files:**
- Modify: `aiopulse/transport.py`
- Modify: `tests/test_transport.py`

**Interfaces:**
- Produces: Enhanced transport with state validation

- [ ] **Step 1: Run existing transport tests to establish baseline**

Run: `pytest tests/test_transport.py -v`
Expected: All tests pass

- [ ] **Step 2: Update transport.py with state validation**

Key changes:
- Add explicit connection state checks before operations
- Update `send()` to raise `NotConnectedException` if not connected
- Update `receive()` to raise `NotConnectedException` if not connected
- Use `asyncio.get_running_loop()` instead of `asyncio.get_event_loop()`

Example:
```python
def send(self, buffer: bytes) -> None:
    """Send buffer to hub."""
    if not self.writer or self.writer.is_closing():
        raise NotConnectedException("TCP transport not connected")
    self.writer.write(buffer)
```

- [ ] **Step 3: Update test_transport.py with state validation tests**

Add tests for:
- `send()` when not connected raises `NotConnectedException`
- `receive()` when not connected raises `NotConnectedException`

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_transport.py -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add aiopulse/transport.py tests/test_transport.py
git commit -m "refactor: add transport state validation and modern asyncio"
```
