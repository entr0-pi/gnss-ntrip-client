# Configuration Guide

## NTRIP Caster Configuration

### Popular Public Casters

#### RTK2Go (North America)
```json
{
  "host": "rtk2go.com",
  "port": 2101,
  "mount": "YOUR_MOUNT_NAME",
  "user": "your_email@example.com",
  "pass": "none"
}
```
- Free, community-driven
- Registration: https://www.rtk2go.com
- Source table: http://rtk2go.com:2101

#### RTCM-NTRIP.org (Europe)
```json
{
  "host": "www.rtcm-ntrip.org",
  "port": 2101,
  "mount": "YOUR_MOUNT_NAME",
  "user": "your_username",
  "pass": "your_password"
}
```

#### Emlid Caster (Requires Account)
```json
{
  "host": "caster.emlid.com",
  "port": 2101,
  "mount": "YOUR_MOUNT_NAME",
  "user": "your_username",
  "pass": "your_password"
}
```

### Finding a Mount Point

1. **View Source Table**: Visit `http://your-caster.com:2101` in browser
2. **Look for Nearby Stations**: Choose stations within 10-50km for best results
3. **Check Message Types**: Prefer MSM7 (high precision) over MSM4

Example source table entry:
```
MountPoint: STATION_NAME
Identifier: Station Name
Format: RTCM 3.3
Latitude: 40.12345
Longitude: -105.67890
Messages: 1005,1077,1087,1097,1127,1230
```

## Configuration Parameters

### Basic Settings

```json
{
  "ntrip": {
    "enabled": true,              // Enable/disable NTRIP
    "host": "rtk2go.com",         // Caster hostname
    "port": 2101,                 // Caster port (usually 2101)
    "mount": "MOUNT_NAME",        // Mount point name
    "user": "email@example.com",  // Username or email
    "pass": "none",               // Password (often "none")
    "max_tries": 5                // Max connection attempts before lockout
  }
}
```

### Advanced Settings

```json
{
  "ntrip": {
    // ... basic settings ...
    
    "retry_delay_ms": 30000,        // Wait 30s between retry attempts
    "health_timeout_ms": 60000,     // Reconnect if no data for 60s
    "passive_sample_ms": 5000,      // Check stream health every 5s
    "required_valid_frames": 3,     // Need 3 valid RTCM frames to validate
    "buffer_size": 1024,            // Read buffer size (bytes)
    "connect_timeout_ms": 5000      // TCP connection timeout
  }
}
```

### Parameter Tuning

#### Slow/Unstable Networks
```json
{
  "retry_delay_ms": 60000,          // Wait longer between retries
  "health_timeout_ms": 120000,      // Allow longer gaps in data
  "connect_timeout_ms": 10000       // Longer TCP timeout
}
```

#### High-Rate Streams (10 Hz base stations)
```json
{
  "buffer_size": 2048,              // Larger buffer
  "passive_sample_ms": 2000,        // Check more frequently
  "required_valid_frames": 5        // Stricter validation
}
```

#### Low-Power/Battery Mode
```json
{
  "buffer_size": 512,               // Smaller buffer
  "passive_sample_ms": 10000,       // Check less frequently
  "health_timeout_ms": 300000       // 5 minute timeout
}
```

## GNSS Receiver Configuration

### u-blox ZED-F9P

**Recommended Settings:**
- Baudrate: 115200 (matches Serial2 in code)
- RTCM3 Input: USB+UART1+UART2
- Output: NMEA on USB/UART2, UBX on UART1

**u-center Configuration:**
1. View → Messages View
2. UBX → CFG → PRT (Ports)
3. UART1: Enable RTCM3 input
4. Baudrate: 115200
5. Send Configuration

### Trimble/NavCom Receivers

```
$JATT,NCOM,5,115200,N,8,1,N
$JASC,GPGGA,10
$JSAVE
```

### Common Issues

#### No RTK Fix Despite Corrections
- Check GNSS receiver survey-in status
- Verify RTCM messages include 1005 (base position)
- Ensure receiver is configured for RTK mode
- Check antenna has clear sky view

#### Intermittent Disconnections
- Increase `health_timeout_ms`
- Check WiFi signal strength
- Consider using wired Ethernet if available

## Serial Port Configuration

### Default (Serial2)
```cpp
Serial2.begin(115200, SERIAL_8N1, 16, 17);
// RX=GPIO16, TX=GPIO17
```

### Custom GPIO Pins
```cpp
// Example: Use GPIO 25 (RX) and GPIO 26 (TX)
Serial2.begin(115200, SERIAL_8N1, 25, 26);
```

### Different Serial Port
```cpp
// Use Serial1 instead
Serial1.begin(115200, SERIAL_8N1, 9, 10);

// Update in main.ino:
if (ntripClient.begin(newConfig, Serial1)) { // Changed from Serial2
  // ...
}
```

## Filesystem Configuration

### LittleFS Partitions

If you need more space for logs/configs, edit `partitions.csv`:

```csv
# Name,   Type, SubType, Offset,  Size,    Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x140000,
app1,     app,  ota_1,   0x150000,0x140000,
spiffs,   data, spiffs,  0x290000,0x170000,
```

Then in platformio.ini:
```ini
board_build.partitions = partitions.csv
```

## Example Configurations

### Surveying/Mapping Application
```json
{
  "ntrip": {
    "enabled": true,
    "host": "rtk2go.com",
    "port": 2101,
    "mount": "NEARBY_BASE",
    "user": "survey@company.com",
    "pass": "none",
    "max_tries": 10,
    "retry_delay_ms": 20000,
    "health_timeout_ms": 90000,
    "required_valid_frames": 5,
    "buffer_size": 2048
  }
}
```

### Drone/UAV Application
```json
{
  "ntrip": {
    "enabled": true,
    "host": "private-caster.com",
    "port": 2101,
    "mount": "BASE_STATION_01",
    "user": "drone_fleet",
    "pass": "secure_password",
    "max_tries": 3,
    "retry_delay_ms": 10000,
    "health_timeout_ms": 30000,
    "passive_sample_ms": 2000,
    "buffer_size": 4096
  }
}
```

### Fixed Base Station Monitor
```json
{
  "ntrip": {
    "enabled": true,
    "host": "rtk2go.com",
    "port": 2101,
    "mount": "MY_BASE_STATION",
    "user": "monitor@email.com",
    "pass": "none",
    "max_tries": 100,
    "retry_delay_ms": 60000,
    "health_timeout_ms": 300000,
    "passive_sample_ms": 30000
  }
}
```

## Troubleshooting Configuration

### Enable Debug Logging

Add to your code:
```cpp
void setup() {
  // Increase verbosity
  esp_log_level_set("*", ESP_LOG_VERBOSE);
}
```

### Test Caster Manually

Use `telnet` or `netcat`:
```bash
telnet rtk2go.com 2101
GET /YOUR_MOUNT HTTP/1.0
User-Agent: NTRIP Test
Authorization: Basic base64_encoded_user:pass

# Should see: ICY 200 OK
# Followed by binary RTCM data
```

### Configuration Validation

The library validates:
- ✅ Host is not empty
- ✅ Port is 1-65535
- ✅ Mount point is not empty
- ✅ Max tries >= 1

Invalid configs will fail at `begin()`.
