# Quick Start Guide

Get RTK corrections flowing in 5 minutes! 🚀

## Step 1: Install Dependencies

In Arduino IDE or PlatformIO, install:
- **ArduinoJson** (v6 or v7)
- ESP32 board support

## Step 2: Copy Library Files

Copy this repository to your Arduino libraries directory:
- **Windows**: `Documents/Arduino/libraries/`
- **Mac**: `~/Documents/Arduino/libraries/`
- **Linux**: `~/Arduino/libraries/`

Or extract the ZIP directly into that folder.

## Step 3: Find a Mount Point

Visit http://rtk2go.com:2101 in your browser to see available stations.

Choose one near you (within 50km is ideal). Note the:
- Mount point name (e.g., `RTCM3_XYZ`)
- Distance from your location

## Step 4: Wire Your GNSS Receiver

Connect your GNSS receiver to ESP32:

```
ZED-F9P    →    ESP32
───────────────────────
TX         →    GPIO 16 (Serial2 RX)
RX         →    GPIO 17 (Serial2 TX)
GND        →    GND
```

## Step 5: Upload the Minimal Example

1. Open Arduino IDE
2. File → Examples → NtripClient_Enhanced → minimal
3. Edit these lines:
   ```cpp
   const char* WIFI_SSID = "YourWiFiName";
   const char* WIFI_PASS = "YourPassword";
   
   cfg.mount = "YOUR_MOUNT_POINT";  // From Step 3
   cfg.user = "your@email.com";
   ```
4. Upload to ESP32
5. Open Serial Monitor (115200 baud)

## Step 6: Watch for RTK Fix

You should see:
```
WiFi OK
NTRIP started!
✅ RTK OK | 127 frames | 45 KB
```

On your GNSS receiver, the fix status should change to **RTK FIXED** or **RTK FLOAT**.

## Troubleshooting

### "Connection failed" in Serial Monitor
- Check WiFi credentials
- Verify `rtk2go.com` is reachable: `ping rtk2go.com`
- Try port 80 instead of 2101

### "HTTP 401 Auth Failed"
- Some casters require specific username format
- Try your email address as username
- Password is usually "none" for public casters

### "No RTK fix" on GNSS
- Check UART connections (TX ↔ RX, not TX → TX)
- Verify baud rate is 115200 on both ESP32 and GNSS
- Ensure GNSS has RTCM3 input enabled
- Wait 30-60 seconds for initial fix

### "Stream validated but no fix"
- GNSS might need configuration via u-center (u-blox) or similar
- Enable RTCM3 on UART1/UART2
- Check antenna has clear sky view

## Next Steps

Once it's working:

1. **Use the JSON config** (examples/basic) for easier management
2. **Enable statistics** to monitor performance
3. **Adjust timeouts** if on unstable network
4. Read `docs/CONFIGURATION.md` for advanced tuning

## Common Mount Point Examples

### North America (RTK2Go)
```cpp
cfg.host = "rtk2go.com";
cfg.mount = "STATION_NAME";  // Check rtk2go.com:2101
cfg.user = "your@email.com";
```

### Europe (RTCM-NTRIP.org)
```cpp
cfg.host = "www.rtcm-ntrip.org";
cfg.mount = "STATION_NAME";
cfg.user = "username";       // May require registration
cfg.pass = "password";
```

### Private Base Station
```cpp
cfg.host = "192.168.1.100";  // Your base station IP
cfg.mount = "BASE1";
cfg.user = "rover";
cfg.pass = "your_password";
```

## Getting Help

- Check `README.md` for full API docs
- See `examples/advanced/` for error handling
- Review `docs/CONFIGURATION.md` for tuning

**Need more help?** Open an issue with:
- Serial Monitor output
- Your configuration (hide password!)
- GNSS receiver model
