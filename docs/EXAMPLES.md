# Example Comparison Guide

## Which Example Should I Use?

### 🚀 **minimal.ino** (40 lines)
**Best for:** Quick testing, learning, embedding in existing code

**Features:**
- ✅ Hardcoded configuration (no JSON/LittleFS needed)
- ✅ WiFi connection
- ✅ Basic status display
- ✅ Minimal dependencies

**Use when:**
- You want to test NTRIP quickly
- Configuration won't change often
- You're integrating into existing firmware
- You don't need advanced diagnostics

**Code snippet:**
```cpp
NtripConfig cfg;
cfg.host = "rtk2go.com";
cfg.mount = "MOUNT";
ntripClient.begin(cfg, Serial2);
```

---

### 📊 **advanced.ino** (150 lines)
**Best for:** Development, debugging, detailed monitoring

**Features:**
- ✅ Hardcoded configuration
- ✅ WiFi connection
- ✅ Detailed statistics every 10 seconds
- ✅ RTCM message type decoding
- ✅ Auto-lockout reset (2 minutes)
- ✅ Comprehensive error handling

**Use when:**
- You're debugging connection issues
- You need to monitor RTCM message types
- You want to understand what's happening
- You're developing/testing

**Sample output:**
```
╔════════════════════════════════════════╗
║        NTRIP CLIENT STATUS             ║
╚════════════════════════════════════════╝
State:         STREAMING (HEALTHY)
Uptime:        245 seconds
Valid Frames:  1274
CRC Errors:    3
Data RX:       156.23 KB
Last RTCM:     1077 (GPS MSM7)
Frame Age:     0.234 seconds
```

---

### 🏭 **production/main.ino** (NEW - 300 lines)
**Best for:** Production deployments, field installations

**Features:**
- ✅ JSON configuration from LittleFS
- ✅ Hot-reload on config changes
- ✅ Lockout state persistence across reboots
- ✅ Auto-recovery after failures
- ✅ Detailed stats every 30 seconds
- ✅ Compact status every 5 seconds
- ✅ Multi-core task architecture
- ✅ Flash wear protection

**Use when:**
- Deploying to production
- Configuration needs to change without reflashing
- Multiple devices need different configs
- You need robust error recovery
- Remote/field installations

**Sample output:**
```
[CONFIG] Current settings:
  Host:    rtk2go.com:2101
  Mount:   MY_STATION
  Enabled: YES

[STATUS] ✅ STREAMING | ⬇ 234 KB | 📡 RTCM1077 | ✓ Fresh (0.4s ago)

╔════════════════════════════════════════╗
║        NTRIP STATISTICS                ║
╚════════════════════════════════════════╝
Uptime:        1245 seconds
Valid Frames:  6234
CRC Errors:    12 (0.2%)
Frame Rate:    5.01 frames/sec
```

**Config file example** (`/ntrip_config.json`):
```json
{
  "ntrip": {
    "enabled": true,
    "host": "rtk2go.com",
    "port": 2101,
    "mount": "STATION_XYZ",
    "user": "email@example.com",
    "pass": "none",
    "max_tries": 5,
    "retry_delay_ms": 30000,
    "health_timeout_ms": 60000
  },
  "lockout": {
    "failed_attempts": 0,
    "abandoned": false,
    "last_config_hash": ""
  }
}
```

---

### 📝 **basic/main.ino** (200 lines)
**Best for:** JSON config without all the bells and whistles

**Features:**
- ✅ JSON configuration from LittleFS
- ✅ Config monitoring
- ✅ Basic status display
- ✅ Simpler than production version

**Use when:**
- You want JSON config but not full production features
- Learning how JSON integration works
- Don't need detailed statistics

---

## Feature Comparison Matrix

| Feature | minimal | basic | advanced | production |
|---------|---------|-------|----------|------------|
| Lines of code | 40 | 200 | 150 | 300 |
| Configuration | Hardcoded | JSON | Hardcoded | JSON |
| Hot-reload | ❌ | ✅ | ❌ | ✅ |
| LittleFS required | ❌ | ✅ | ❌ | ✅ |
| Detailed stats | ❌ | ❌ | ✅ | ✅ |
| RTCM decoding | ❌ | ❌ | ✅ | ✅ |
| Auto-reset lockout | ❌ | ❌ | ✅ | ✅ |
| Multi-task | ❌ | ✅ | ❌ | ✅ |
| Flash persistence | ❌ | ✅ | ❌ | ✅ |
| Error diagnostics | Basic | Medium | Advanced | Advanced |
| Production-ready | ⚠️ | ✅ | ⚠️ | ✅✅ |

## Decision Tree

```
Do you need to change config without reflashing?
├─ NO → Do you need detailed diagnostics?
│       ├─ NO → Use minimal.ino
│       └─ YES → Use advanced.ino
│
└─ YES → Is this going to production/field?
         ├─ NO (just testing) → Use basic/main.ino
         └─ YES → Use production/main.ino ⭐
```

## Upgrade Path

1. **Start with `minimal.ino`** to test hardware and caster
2. **Move to `advanced.ino`** to debug any issues
3. **Switch to `production/main.ino`** for deployment

## Configuration Management

### Hardcoded (minimal/advanced)
```cpp
// Change requires reflashing
NtripConfig cfg;
cfg.host = "rtk2go.com";
cfg.mount = "STATION";
```

**Pros:** Simple, no filesystem needed
**Cons:** Must reflash to change

### JSON (basic/production)
```json
// Change by editing file on device
{
  "ntrip": {
    "host": "rtk2go.com",
    "mount": "STATION"
  }
}
```

**Pros:** Remote config, hot-reload, version control
**Cons:** Requires LittleFS, more complex

## Memory Usage

| Example | Flash | RAM (heap) |
|---------|-------|------------|
| minimal | ~25 KB | ~2 KB |
| basic | ~32 KB | ~8 KB |
| advanced | ~28 KB | ~3 KB |
| production | ~35 KB | ~10 KB |

All examples fit comfortably on ESP32 (4MB Flash, 520KB RAM).

## Recommendation

**For most users:** Start with `production/main.ino`

It provides:
- Best error recovery
- Easiest configuration management
- Production-grade reliability
- Excellent diagnostics

The extra complexity is worth it for real-world deployments!
