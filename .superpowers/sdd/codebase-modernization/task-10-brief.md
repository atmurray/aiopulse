# Task 10: Modernize Hub asyncio Patterns

**Files:**
- Modify: `aiopulse/hub.py`

**Interfaces:**
- Produces: Modernized Hub class with deprecation warnings for loop parameter

- [ ] **Step 1: Run existing hub tests to establish baseline**

Run: `pytest tests/test_hub.py -v`
Expected: All tests pass (note any current failures)

- [ ] **Step 2: Update hub.py asyncio patterns**

Key changes:
- Add deprecation warning if `loop` parameter is passed
- Replace `asyncio.get_event_loop()` with `asyncio.get_running_loop()`
- Use `asyncio.create_task()` instead of `loop.create_task()`
- Fix duplicate `InvalidResponseException` catch in `run()` method
- Add bounds checking to all `response_*` methods
- Use context managers for locks where safe

Example deprecation warning:
```python
def __init__(self, host=None, loop=None):
    if loop is not None:
        warnings.warn(
            "loop parameter is deprecated and will be removed in v0.6.0",
            DeprecationWarning,
            stacklevel=2,
        )
```

Example bounds checking:
```python
def response_hubinfo(self, message):
    if len(message) < 10:
        raise errors.InvalidResponseException(
            f"Hub info message too short: {len(message)} bytes",
            response=message,
        )
    ptr = 10
    # ... rest of parsing
```

Fix duplicate exception (remove lines 707-708):
```python
# Before (duplicate):
except errors.InvalidResponseException as inst:
    _LOGGER.warning(f"{self.host}: Handshake failed {inst}")
    await self.disconnect()
except errors.InvalidResponseException as inst:  # DUPLICATE!
    _LOGGER.warning(f"{self.host}: Protocol error {inst}")

# After (single):
except errors.InvalidResponseException as inst:
    _LOGGER.warning(f"{self.host}: Protocol error {inst}")
    await self.disconnect()
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pytest tests/test_hub.py -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add aiopulse/hub.py
git commit -m "refactor: modernize hub asyncio patterns and add bounds checking"
```
