# Changelog

All notable changes to the NTRIP Client Enhanced library will be documented in this file.

## [2.0.0] - 2024-02-02

### Added
- **Complete rewrite** for production use
- Two-phase stream validation (strict → passive)
- Comprehensive error handling with `NtripError` enum
- Thread-safe statistics via `NtripStats` structure
- RTCM message type detection (1005, 1077, MSM7, etc.)
- Auto-reconnection with exponential backoff
- Lockout protection after repeated failures
- Zombie stream detection (no data for X seconds)
- `reset()` method to clear lockout state
- `reconnect()` method to force immediate retry
- `getStats()` for real-time metrics
- `getLastError()` and `getErrorMessage()` for diagnostics
- Semaphore protection for multi-threaded stats access
- Configurable buffer sizes and timeouts
- HTTP error code parsing (401, 404, timeout)
- Serial logging of all state transitions
- Version macro `NTRIP_CLIENT_VERSION`

### Changed
- `RtcmParser::feed()` now returns `RtcmResult` struct instead of `bool`
- Enhanced passive sampling checks first 10 bytes instead of just buffer[0]
- Improved CRC error counting
- Better connection state machine with explicit phases
- Default buffer size increased to 1024 bytes
- Task stack size remains 8192 bytes (tested stable)

### Fixed
- Passive sampling false negatives (was only checking first byte)
- Missing mutex protection on statistics
- Potential buffer overflow in CRC validation
- Memory leak from unclosed WiFiClient on errors
- Zombie streams not being detected in edge cases
- Flash wear from excessive JSON writes

### Removed
- Hardcoded magic numbers (now configurable)
- Redundant state checks

## [1.0.0] - Initial Release

### Features
- Basic NTRIP client functionality
- RTCM3 frame parsing with CRC24Q
- Simple state machine (DISCONNECTED/CONNECTING/STREAMING/LOCKED_OUT)
- Auto-retry with backoff
- FreeRTOS task-based architecture

### Known Issues
- Passive sampling only checked first byte
- No detailed error reporting
- No statistics tracking
- Fixed timeouts and buffer sizes
- No message type detection
