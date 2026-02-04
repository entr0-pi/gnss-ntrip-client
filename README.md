# NTRIP Client v2.0 - Production Ready

A robust, production-ready NTRIP client for ESP32 that streams RTK correction data to GNSS receivers with advanced health monitoring, error handling, and diagnostics.

## 🌟 Features

- **Two-Phase Stream Validation**: Strict startup validation followed by efficient passive monitoring
- **Comprehensive Error Handling**: Detailed error codes and messages for all failure modes
- **Thread-Safe Statistics**: Real-time metrics on frames, bytes, uptime, and errors
- **Auto-Reconnection**: Smart retry logic with exponential backoff and lockout protection
- **RTCM Message Detection**: Identifies RTCM message types (1005, 1077, MSM7, etc.)
- **JSON Configuration**: Hot-reload configuration without restart
- **Zombie Stream Detection**: Automatically reconnects on dead connections
- **Multi-Core Architecture**: NTRIP processing on Core 0, monitoring on Core 1
- **Flash Wear Protection**: Only writes to LittleFS when values actually change

## 📋 Requirements

### Hardware
- ESP32 (any variant)
- GNSS receiver (ZED-F9P, M8P, etc.) connected via Serial2

### Software Dependencies
```cpp
#include <WiFi.h>          // ESP32 core
#include <LittleFS.h>      // ESP32 core
#include <ArduinoJson.h>   // v6.x or v7.x
#include <base64.h>        // ESP32 base64 library
```

### Pin Configuration
Default Serial2 pins (configurable in setup()):
- RX: GPIO 16
- TX: GPIO 17

## 🚀 Quick Start

### 1. Installation

Copy the library files to your project:
```
YourProject/
├── src/
│   ├── NtripClient.h
│   ├── NtripClient.cpp
│   ├── RtcmParser.h
│   └── RtcmParser.cpp
└── main.ino
```

### 2. Basic Setup

```cpp
#include "NtripClient.h"

NtripClient ntripClient;
bool isInternetReachable = true; // Update this based on WiFi status

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200);
  
  NtripConfig config;
  config.host = "rtk2go.com";
  config.port = 2101;
  config.mount = "YOUR_MOUNT";
  config.user = "your_email@example.com";
  config.pass = "none";
  
  ntripClient.begin(config, Serial2);
  ntripClient.startTask(0); // Start on Core 0
}

void loop() {
  if (ntripClient.isHealthy()) {
    Serial.println("RTK corrections flowing!");
  }
  delay(1000);
}
```

### 3. Configuration File

Create `/ntrip_config.json` on LittleFS:

```json
{
  "ntrip": {
    "enabled": true,
    "host": "rtk2go.com",
    "port": 2101,
    "mount": "YOUR_MOUNT",
    "user": "your_email@example.com",
    "pass": "none",
    "max_tries": 5,
    "retry_delay_ms": 30000,
    "health_timeout_ms": 60000,
    "passive_sample_ms": 5000,
    "required_valid_frames": 3,
    "buffer_size": 1024,
    "connect_timeout_ms": 5000
  },
  "lockout": {
    "failed_attempts": 0,
    "abandoned": false,
    "last_config_hash": ""
  }
}
```

## 📊 API Reference

### NtripClient Class

#### Initialization
```cpp
bool begin(const NtripConfig& cfg, HardwareSerial& gnss);
```
Initialize client with configuration and GNSS serial port.

#### Control Methods
```cpp
void startTask(uint8_t core = 0);    // Start processing task
void stop();                          // Stop and enter lockout
void reset();                         // Clear lockout state
void reconnect();                     // Force immediate reconnect
```

#### Status Methods
```cpp
bool isStreaming() const;            // True if connected
bool isHealthy() const;              // True if receiving valid RTCM
NtripState state() const;            // Current state enum
```

#### Diagnostics
```cpp
NtripStats getStats() const;         // Get statistics
NtripError getLastError() const;     // Get last error code
String getErrorMessage() const;      // Get human-readable error
```

### NtripConfig Structure

```cpp
struct NtripConfig {
  String host;                       // Caster hostname
  uint16_t port;                     // Caster port (default 2101)
  String mount;                      // Mount point name
  String user;                       // Username
  String pass;                       // Password
  uint8_t maxTries;                  // Max retry attempts (default 5)
  
  // Advanced (optional)
  uint32_t retryDelayMs;            // Retry interval (default 30000)
  uint32_t healthTimeoutMs;         // Zombie timeout (default 60000)
  uint32_t passiveSampleMs;         // Sample interval (default 5000)
  uint8_t requiredValidFrames;      // Validation frames (default 3)
  uint16_t bufferSize;              // Read buffer (default 1024)
  uint32_t connectTimeoutMs;        // TCP timeout (default 5000)
};
```

### NtripStats Structure

```cpp
struct NtripStats {
  uint32_t totalFrames;             // Valid RTCM frames received
  uint32_t crcErrors;               // Failed CRC checks
  uint32_t bytesReceived;           // Total bytes from caster
  uint32_t reconnects;              // Reconnection count
  uint32_t totalUptime;             // Milliseconds streaming
  uint16_t lastMessageType;         // Last RTCM message ID
  unsigned long lastFrameTime;      // Last valid frame timestamp
  unsigned long connectionStart;    // Connection start time
  NtripError lastError;             // Last error code
  String lastErrorMessage;          // Error description
};
```

### NtripState Enum

```cpp
enum class NtripState {
  DISCONNECTED,  // Not connected
  CONNECTING,    // Attempting connection
  STREAMING,     // Connected and streaming
  LOCKED_OUT     // Too many failures, stopped
};
```

### NtripError Enum

```cpp
enum class NtripError {
  NONE,
  TCP_CONNECT_FAILED,
  HTTP_AUTH_FAILED,
  HTTP_MOUNT_NOT_FOUND,
  HTTP_TIMEOUT,
  HTTP_UNKNOWN_ERROR,
  STREAM_VALIDATION_FAILED,
  ZOMBIE_STREAM_DETECTED,
  MAX_RETRIES_EXCEEDED
};
```

## 🔧 Advanced Usage

### Custom Error Handling

```cpp
void loop() {
  if (ntripClient.state() == NtripState::LOCKED_OUT) {
    NtripError err = ntripClient.getLastError();
    
    switch(err) {
      case NtripError::HTTP_AUTH_FAILED:
        Serial.println("Check your username/password!");
        break;
      case NtripError::HTTP_MOUNT_NOT_FOUND:
        Serial.println("Mount point doesn't exist!");
        break;
      default:
        Serial.println(ntripClient.getErrorMessage());
    }
    
    // Clear lockout after user intervention
    delay(60000);
    ntripClient.reset();
  }
}
```

### Real-Time Statistics Display

```cpp
void displayStats() {
  NtripStats stats = ntripClient.getStats();
  
  Serial.printf("Uptime: %lu sec | Frames: %lu | Errors: %lu\n",
                stats.totalUptime / 1000,
                stats.totalFrames,
                stats.crcErrors);
  
  Serial.printf("Last RTCM: %d (%lu ms ago)\n",
                stats.lastMessageType,
                millis() - stats.lastFrameTime);
  
  Serial.printf("Bandwidth: %.2f KB/s\n",
                (float)stats.bytesReceived / stats.totalUptime);
}
```

### Configuration Hot-Reload

The included example automatically monitors the JSON file and restarts the client when configuration changes are detected.

## 🎯 RTCM Message Types

Common message types you'll see:

| Type | Description |
|------|-------------|
| 1005 | Station coordinates (base position) |
| 1074 | GPS MSM4 observations |
| 1077 | GPS MSM7 observations (high precision) |
| 1084 | GLONASS MSM4 |
| 1087 | GLONASS MSM7 |
| 1094 | Galileo MSM4 |
| 1097 | Galileo MSM7 |
| 1124 | BeiDou MSM4 |
| 1127 | BeiDou MSM7 |
| 1230 | GLONASS code-phase biases |

## 📈 Performance Characteristics

- **Latency**: <5ms from caster to GNSS (fast-path optimization)
- **Memory**: ~8KB stack + 1KB buffer per connection
- **CPU**: ~2% on Core 0 during streaming
- **Validation Time**: Typically 100-500ms for 3 frames
- **Recovery Time**: 30 seconds default retry interval

## 🐛 Troubleshooting

### "Connection failed" repeatedly
- Check WiFi connectivity
- Verify host/port are correct
- Test with `telnet rtk2go.com 2101`

### "HTTP 401 Authentication Failed"
- Verify username/password
- Some casters require email as username
- Try password "none" (common for public casters)

### "Mount point not found"
- Check mount name spelling (case-sensitive)
- Visit caster's source table (e.g., rtk2go.com:2101)

### "Stream validated but no GPS fix"
- Check GNSS receiver configuration
- Ensure RTCM3 input is enabled
- Verify UART connections (RX/TX not swapped)
- Check baud rate matches (115200 default)

### "Zombie stream detected"
- Caster may be sending invalid data
- Try different mount point
- Check network stability

## 🔒 Security Notes

- Passwords are sent via HTTP Basic Auth (base64, not encrypted)
- Use trusted networks or VPN for sensitive applications
- Consider implementing HTTPS support for production

## 📝 License

MIT License - See LICENSE file for details

## 📮 Support

For issues and questions:
- Check troubleshooting section
- Review examples/
- Open GitHub issue with logs

## 🙏 Acknowledgments

- RTCM SC-104 for the RTCM 3.x standard
- ESP32 community for libraries and support
- NTRIP caster operators (RTK2Go, etc.)

---

**Made with ❤️ for the RTK/GNSS community**
