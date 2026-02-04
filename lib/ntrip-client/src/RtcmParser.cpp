#include "RtcmParser.h"

static constexpr uint32_t CRC24Q_POLY = 0x1864CFB;

uint32_t RtcmParser::crc24q(uint32_t crc, uint8_t byte) {
  crc ^= (uint32_t)byte << 16;
  for (int i = 0; i < 8; i++)
    crc = (crc & 0x800000) ? (crc << 1) ^ CRC24Q_POLY : (crc << 1);
  return crc & 0xFFFFFF;
}

uint16_t RtcmParser::extractMessageType() {
  // RTCM 3.x message type is the first 12 bits of the payload:
  //   Byte 0: message type bits [11:4] (all 8 bits)
  //   Byte 1: message type bits [3:0] in upper nibble (bits 7-4)
  // Reference station ID follows in remaining bits
  if (length >= 2) {
    uint16_t msgType = ((uint16_t)payloadBuf[0] << 4) |
                       ((payloadBuf[1] >> 4) & 0x0F);
    return msgType;
  }
  return 0;
}

RtcmResult RtcmParser::feed(uint8_t b) {
  RtcmResult result;
  
  switch (state) {
    case SYNC:
      if (b == 0xD3) {
        crc = crc24q(0, b);
        state = LEN1;
      }
      break;
      
    case LEN1:
      length = (b & 0x03) << 8;
      crc = crc24q(crc, b);
      state = LEN2;
      break;
      
    case LEN2:
      length |= b;
      crc = crc24q(crc, b);
      index = 0;
      state = PAYLOAD;
      break;
      
    case PAYLOAD:
      // Store first 12 bytes for message type extraction
      if (index < sizeof(payloadBuf)) {
        payloadBuf[index] = b;
      }
      
      crc = crc24q(crc, b);
      if (++index >= length) {
        state = CRC;
        index = 0;
      }
      break;
      
    case CRC:
      crcBuf[index++] = b;
      if (index >= 3) {
        uint32_t recv = ((uint32_t)crcBuf[0] << 16) |
                        ((uint32_t)crcBuf[1] << 8) |
                         (uint32_t)crcBuf[2];
        
        result.valid = (crc == recv);
        result.crcError = !result.valid;
        result.length = length;
        
        if (result.valid) {
          result.messageType = extractMessageType();
        }
        
        reset();
        return result;
      }
      break;
  }
  
  return result;
}

void RtcmParser::reset() {
  state = SYNC;
  length = 0;
  index = 0;
  crc = 0;
}

const char* RtcmParser::getStateName() const {
  switch (state) {
    case SYNC: return "SYNC";
    case LEN1: return "LEN1";
    case LEN2: return "LEN2";
    case PAYLOAD: return "PAYLOAD";
    case CRC: return "CRC";
    default: return "UNKNOWN";
  }
}
