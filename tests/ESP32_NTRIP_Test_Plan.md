# ESP32 NTRIP Client – Test Plan (Patched)

This document defines the **manual and semi-automated validation tests** for the ESP32 NTRIP v1 client using a Python-based fake caster.

This **patched version** corrects minor inconsistencies and adds missing coverage identified during review:
- Clarifies that HTTP 404 testing validates *server response handling*, not mount mismatch routing
- Adds an explicit **mount mismatch routing** test
- Adds an explicit **HTTP 500 server error** test

---

## Test Environment Assumptions

- Fake caster runs on a development PC
- ESP32 points to the PC IP address as the NTRIP caster
- NTRIP version: v1
- No TLS
- No GGA uplink
- Receiver: Any RTCM-capable GNSS (UM980, u-blox, etc.)
- RTCM data source: a previously captured binary stream (`rtcm.bin`)

Default values used below:
- **Mount**: `MOUNT`
- **Username**: `user`
- **Password**: `pass`

---

## Test 1 — Happy Path / Stream Validation

```bash
python fake_caster.py   --mode ok   --mount MOUNT   --user user   --password pass   --rtcm rtcm.bin
```

**Objective**
- Validate successful connection, RTCM validation, and transition to healthy streaming state.

**Pass Criteria**
- Client logs "Connected – validating stream…"
- Required number of valid RTCM frames detected
- Client transitions to `STREAMING`
- `isHealthy() == true`
- GNSS receiver receives RTCM corrections

---

## Test 2 — HTTP Header Draining (ASCII Leakage Test)

```bash
python fake_caster.py   --mode ok_headers   --mount MOUNT   --user user   --password pass   --rtcm rtcm.bin
```

**Objective**
- Ensure HTTP headers are fully drained and **no ASCII data reaches the GNSS UART**.

**Pass Criteria**
- Serial2 TX begins with RTCM preamble (`0xD3`)
- No ASCII strings ("HTTP", "Server", "Date") forwarded to GNSS
- Stream validates and runs normally

---

## Test 3 — Authentication Failure (401)

```bash
python fake_caster.py   --mode unauth   --mount MOUNT
```

**Objective**
- Validate authentication failure handling and retry/lockout behavior.

**Pass Criteria**
- Client reports authentication error
- Retries follow `retryDelayMs`
- Client enters `LOCKED_OUT` after `maxTries`
- Lockout state persisted

---

## Test 4 — HTTP 404 Handling (Mount Not Found Response)

```bash
python fake_caster.py   --mode nomount   --mount MOUNT   --user user   --password pass
```

**Objective**
- Validate client behavior when the server explicitly returns HTTP 404.

**Pass Criteria**
- Client reports mount not found
- Retries occur
- Lockout engages after maximum retries

> **Note:** This test validates handling of a *404 response*, not incorrect mount routing.

---

## Test 5 — Mount Mismatch Routing

```bash
python fake_caster.py   --mode ok   --mount EXPECTED_MOUNT   --user user   --password pass   --rtcm rtcm.bin
```

**Procedure**
- Configure ESP32 to request a *different* mount name (e.g. `MOUNT`).

**Objective**
- Validate server-side mount mismatch detection and client handling of the resulting 404.

**Pass Criteria**
- Fake caster logs mount mismatch
- Client receives HTTP 404
- Client retries and eventually locks out

---

## Test 6 — TCP Segmentation Torture (Parser Robustness)

```bash
python fake_caster.py   --mode ok   --mount MOUNT   --user user   --password pass   --rtcm rtcm.bin
```

**Objective**
- Ensure RTCM parser handles arbitrary TCP segmentation correctly.

**Pass Criteria**
- Valid frames detected despite fragmented delivery
- No CRC storms or false disconnects
- Stream validates successfully

---

## Test 7 — CRC Corruption Handling

```bash
python fake_caster.py   --mode corrupt   --mount MOUNT   --user user   --password pass   --rtcm rtcm.bin
```

**Objective**
- Confirm corrupted frames increment CRC error counters without stopping forwarding.

**Pass Criteria**
- `crcErrors` increments
- Valid frames still accepted
- Client remains healthy

---

## Test 8 — Zombie Stream Detection (Silent Stall)

```bash
python fake_caster.py   --mode stall   --mount MOUNT   --user user   --password pass   --rtcm rtcm.bin
```

**Objective**
- Validate detection of a stalled stream with TCP still connected.

**Pass Criteria**
- After `healthTimeoutMs`, client reports zombie stream
- Client disconnects and retries

---

## Test 9 — Abrupt Connection Drop

```bash
python fake_caster.py   --mode drop   --mount MOUNT   --user user   --password pass   --rtcm rtcm.bin
```

**Objective**
- Validate clean recovery from abrupt server-side connection termination.

**Pass Criteria**
- Client logs connection loss
- No crash or watchdog reset
- Reconnection attempts follow retry rules

---

## Test 10 — Junk Data Before RTCM

```bash
python fake_caster.py   --mode junk   --mount MOUNT   --user user   --password pass   --rtcm rtcm.bin
```

**Objective**
- Verify robustness when non-RTCM data precedes corrections.

**Pass Criteria**
- Client does not falsely validate early
- RTCM parsing resumes once valid data appears
- No persistent desynchronization

---

## Test 11 — HTTP 500 Server Error Handling

```bash
python fake_caster.py   --mode servererr   --mount MOUNT   --user user   --password pass
```

**Objective**
- Validate handling of generic server-side errors.

**Pass Criteria**
- Client reports unknown HTTP error
- Retries occur
- Lockout engages after `maxTries`

---

## Test 12 — Hot Configuration Reload During Streaming

```bash
python fake_caster.py   --mode ok   --mount MOUNT   --user user   --password pass   --rtcm rtcm.bin
```

**Procedure**
- While streaming, edit `/ntrip_config.json`:
  - Change mount / host / credentials

**Objective**
- Validate thread safety and correct restart behavior on config reload.

**Pass Criteria**
- No crash or reset
- Client disconnects and reconnects cleanly
- New configuration takes effect

---

## Minimum Acceptance Test Set

If time-constrained, the following provide ~90% coverage:

- Test 1 — Happy Path
- Test 2 — HTTP Header Draining
- Test 5 — Mount Mismatch Routing
- Test 6 — TCP Segmentation
- Test 8 — Zombie Detection
- Test 12 — Hot Reload

---

**Status:** This patched test plan fully aligns with the Python fake caster implementation and provides complete coverage of protocol handling, parser robustness, health monitoring, error recovery, and configuration safety for a receiver-agnostic ESP32 NTRIP v1 client.
