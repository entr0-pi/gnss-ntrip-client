#pragma once
#include <Arduino.h>

/**
 * Result structure returned by RTCM parser
 */
struct RtcmResult {
  bool valid = false;        // True if complete valid frame received
  bool crcError = false;     // True if CRC check failed
  uint16_t messageType = 0;  // RTCM message ID (1005, 1077, etc.)
  uint16_t length = 0;       // Payload length in bytes
};

/**
 * RTCM 3.x frame parser with CRC24Q validation
 * 
 * Frame structure:
 * - Preamble: 0xD3 (1 byte)
 * - Length: 10 bits (2 bytes, max 1023)
 * - Payload: variable length
 * - CRC24Q: 24 bits (3 bytes)
 */
class RtcmParser {
public:
  /**
   * Feed a single byte to the parser
   * @param byte Input byte
   * @return Result structure with validation status
   */
  RtcmResult feed(uint8_t byte);
  
  /**
   * Reset parser to initial state
   */
  void reset();
  
  /**
   * Get current parser state (for debugging)
   */
  const char* getStateName() const;

private:
  uint32_t crc24q(uint32_t crc, uint8_t byte);
  uint16_t extractMessageType();
  
  enum State { SYNC, LEN1, LEN2, PAYLOAD, CRC };
  State state = SYNC;
  
  uint16_t length = 0;
  uint16_t index = 0;
  uint32_t crc = 0;
  uint8_t crcBuf[3];
  uint8_t payloadBuf[12];  // Buffer for first 12 bytes (enough for msg type)
};
