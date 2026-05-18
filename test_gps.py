#!/usr/bin/env python3
"""
GPS NEO-M8N Test via I2C
Tests latitude/longitude reading from NEO-M8N GPS module
"""

import serial
import time
import struct

class NEOM8N:
    """NEO-M8N GPS Module I2C Interface"""
    
    # I2C Address
    I2C_ADDR = 0x42
    
    # UBX Protocol
    UBX_SYNC1 = 0xB5
    UBX_SYNC2 = 0x62
    
    # Message Classes
    NAV_CLASS = 0x01
    
    # Message IDs
    NAV_PVT = 0x07  # Position, Velocity, Time
    
    def __init__(self, i2c_bus=1):
        """Initialize I2C connection to GPS module"""
        try:
            import smbus2
            self.bus = smbus2.SMBus(i2c_bus)
            self.connected = True
            print(f"✅ Connected to I2C bus {i2c_bus}")
        except Exception as e:
            print(f"❌ Failed to connect to I2C: {e}")
            self.connected = False
    
    def read_raw(self, length=32):
        """Read raw data from GPS module (max 32 bytes per I2C transaction)"""
        try:
            # RPi5 I2C has 32-byte limit, read in chunks
            data = []
            for offset in range(0, length, 32):
                chunk_size = min(32, length - offset)
                chunk = self.bus.read_i2c_block_data(self.I2C_ADDR, offset, chunk_size)
                data.extend(chunk)
            return bytes(data)
        except Exception as e:
            print(f"❌ I2C Read Error: {e}")
            return None
    
    def parse_ubx_pvt(self, data):
        """Parse UBX NAV-PVT message"""
        if len(data) < 28:
            return None
        
        try:
            # UBX message structure (simplified)
            # Bytes 0-1: Sync chars (0xB5, 0x62)
            # Bytes 2-3: Class, ID
            # Bytes 4-5: Length
            # Bytes 6+: Payload
            
            # Extract position data (rough parse)
            # Latitude at offset 20-23 (degrees * 1e7)
            # Longitude at offset 24-27 (degrees * 1e7)
            
            if data[0] == self.UBX_SYNC1 and data[1] == self.UBX_SYNC2:
                msg_class = data[2]
                msg_id = data[3]
                
                if msg_class == self.NAV_CLASS and msg_id == self.NAV_PVT:
                    # Parse latitude and longitude
                    lat_raw = struct.unpack('<i', data[20:24])[0]
                    lon_raw = struct.unpack('<i', data[24:28])[0]
                    
                    latitude = lat_raw / 1e7
                    longitude = lon_raw / 1e7
                    
                    # Satellite count
                    num_sv = data[35] if len(data) > 35 else 0
                    
                    return {
                        'latitude': latitude,
                        'longitude': longitude,
                        'satellites': num_sv,
                        'raw': data[:32]
                    }
        except Exception as e:
            print(f"⚠️  Parse Error: {e}")
        
        return None
    
    def read_position(self):
        """Read GPS position"""
        if not self.connected:
            return None
        
        data = self.read_raw(32)
        if data:
            return self.parse_ubx_pvt(data)
        return None
    
    def close(self):
        """Close I2C connection"""
        if self.connected:
            self.bus.close()


def test_gps():
    """Test GPS module"""
    print("╔════════════════════════════════════════╗")
    print("║   NEO-M8N GPS Test (I2C)              ║")
    print("║   Testing Latitude Reading            ║")
    print("╚════════════════════════════════════════╝\n")
    
    gps = NEOM8N(i2c_bus=1)
    
    if not gps.connected:
        print("❌ Failed to connect to GPS module")
        print("   Check I2C connection:")
        print("   - SDA → RPi5 GPIO3 (Pin 5)")
        print("   - SCL → RPi5 GPIO2 (Pin 3)")
        print("   - GND → RPi5 GND")
        print("   - VCC → RPi5 3.3V")
        return
    
    print("📡 Reading GPS data...\n")
    
    max_attempts = 30
    attempts = 0
    
    while attempts < max_attempts:
        try:
            position = gps.read_position()
            
            if position:
                print(f"✅ Fix acquired!")
                print(f"   Latitude:  {position['latitude']:.6f}°")
                print(f"   Longitude: {position['longitude']:.6f}°")
                print(f"   Satellites: {position['satellites']}")
                print(f"\n✅ GPS TEST PASSED\n")
                break
            else:
                print(f"⏳ Waiting for GPS fix... ({attempts + 1}/{max_attempts})")
                time.sleep(1)
                attempts += 1
        
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)
            attempts += 1
    
    if attempts >= max_attempts:
        print(f"❌ No GPS fix after {max_attempts} attempts")
        print("   Check:")
        print("   - GPS antenna connected")
        print("   - I2C address correct (0x42)")
        print("   - Module powered on")
    
    gps.close()


if __name__ == '__main__':
    test_gps()
