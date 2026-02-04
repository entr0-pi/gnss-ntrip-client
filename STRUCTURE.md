# Package Structure

```
gnss-ntrip-client/
│
├── lib/
│   └── ntrip-client/             # Core library (PlatformIO/Arduino)
│       ├── include/
│       │   ├── NtripClient.h      # Main client header with API
│       │   └── RtcmParser.h       # RTCM frame parser header
│       └── src/
│           ├── NtripClient.cpp    # Client implementation
│           └── RtcmParser.cpp     # Parser implementation
│
├── examples/                     # Example sketches (C++)
│   ├── minimal/
│   │   └── minimal.cpp            # Bare minimum code (~40 lines)
│   ├── basic/
│   │   └── main.cpp               # JSON config with monitoring
│   ├── advanced/
│   │   └── advanced.cpp           # Full diagnostics & error handling
│   └── production/
│       └── main.cpp               # Production-ready template
│
├── docs/                          # Documentation
│   └── CONFIGURATION.md           # Detailed config guide
│
├── tests/
│   ├── ESP32_NTRIP_Fake_Caster.py # Python fake caster
│   └── ESP32_NTRIP_Test_Plan.md   # Manual/automated test plan
│
├── README.md                      # Main documentation
├── QUICKSTART.md                  # 5-minute getting started guide
├── LICENSE                        # MIT license
├── library.properties             # Arduino Library Manager metadata
├── keywords.txt                   # Arduino IDE syntax highlighting
└── platformio.ini                 # PlatformIO configuration
```

## File Descriptions

### Core Library (`lib/ntrip-client/`)

**NtripClient.h/cpp** - Main NTRIP client
- Connection management & state machine
- Two-phase stream validation
- Auto-reconnection with backoff
- Thread-safe statistics
- Error handling & reporting

**RtcmParser.h/cpp** - RTCM3 frame parser
- CRC24Q validation
- Message type extraction
- Byte-by-byte state machine
- Returns validation results

### Examples

**minimal.cpp** (40 lines)
- Simplest possible implementation
- WiFi + NTRIP in under 50 lines
- Perfect for testing or embedding

**main.cpp** (200 lines)
- JSON configuration from LittleFS
- Hot-reload on config changes
- Multi-task architecture
- Production-ready template

**advanced.cpp** (150 lines)
- Real-time statistics display
- Error handling examples
- RTCM message name lookup
- Dynamic configuration updates

**production/main.cpp**
- Production-ready template with monitoring
- JSON configuration with hot-reload
- Lockout state persistence
- Multi-core task architecture

### Documentation

**README.md**
- Features overview
- API reference
- Usage examples
- Troubleshooting

**QUICKSTART.md**
- Step-by-step first-time setup
- Common configurations
- Wiring diagrams
- Quick troubleshooting

**CONFIGURATION.md**
- Popular NTRIP casters
- Parameter tuning guide
- GNSS receiver setup
- Advanced configurations

## Installation Methods

### Method 1: Arduino Library Manager
1. Sketch → Include Library → Add .ZIP Library
2. Select the downloaded ZIP for this repository
3. Library appears in Sketch → Include Library

### Method 2: Manual Installation
1. Extract ZIP to `~/Arduino/libraries/`
2. Restart Arduino IDE
3. Examples appear in File → Examples

### Method 3: PlatformIO
```ini
lib_deps = 
    ntrip-client
    bblanchon/ArduinoJson@^6.21.0
```

## Usage

```cpp
#include <NtripClient.h>

NtripClient client;
NtripConfig cfg = {
  .host = "rtk2go.com",
  .port = 2101,
  .mount = "MOUNT",
  .user = "email@example.com",
  .pass = "none"
};

client.begin(cfg, Serial2);
client.startTask(0);
```

## Size Information

- **Source code**: ~15 KB
- **Compiled library**: ~25 KB Flash, 2 KB RAM
- **With examples**: ~60 KB total
- **Documentation**: ~35 KB

## Dependencies

Required:
- ESP32 Arduino Core
- ArduinoJson (v6 or v7)
- base64 library (included in ESP32 core)

Optional:
- LittleFS (for JSON config examples)

## License

MIT License - Free for personal and commercial use
