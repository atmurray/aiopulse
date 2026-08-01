# Task 11 Report: Add Transport State Validation

## Status: DONE

## Commit
- `a03cd00` refactor: add transport state validation and modern asyncio

## Test Summary
30/30 transport tests pass (204/204 full suite). Added 3 new tests: `test_send_not_connected` (UDP), `test_receive_not_connected` (UDP), `test_receive_not_connected` (TCP).

## Changes Made

### `aiopulse/transport.py`
- **UDP `send()`**: Added check for `self.transport is None` → raises `NotConnectedException("UDP transport not connected")`
- **UDP `receive()`**: Added check for `self.transport is None` → raises `NotConnectedException("UDP transport not connected")`
- **TCP `send()`**: Added message string to existing `NotConnectedException` raise
- **TCP `receive()`**: Enhanced validation to also check `self.reader is None` (previously only checked `writer.is_closing()`)
- **Modernized asyncio**: Replaced all `asyncio.get_event_loop()` with `asyncio.get_running_loop()` in:
  - `HubTransportUdp.connect()`
  - `HubTransportUdpBroadcast.connect()`
  - `HubTransportTcp.do_connection()`
- **Removed deprecated `loop` parameter** from `asyncio.StreamReader()` and `asyncio.StreamReaderProtocol()` constructors

### `tests/test_transport.py`
- Added `test_send_not_connected` for UDP (transport is None)
- Added `test_receive_not_connected` for UDP (transport is None)
- Added `test_receive_not_connected` for TCP (writer and reader are None)
- Updated `test_receive` for UDP to set `udp.transport` (required by new validation)
- Updated all `asyncio.get_event_loop` mocks to `asyncio.get_running_loop`
