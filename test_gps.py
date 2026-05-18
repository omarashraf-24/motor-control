#!/usr/bin/env python3
"""
GPS NEO-M8N Test via UART (ttyAMA0)
Tests latitude/longitude reading from NEO-M8N GPS module
"""

import serial
import time

class NEOM8N:
    """NEO-M8N GPS Module UART Interface"""
    
    def __init__(self, port='/dev/ttyAMA0', baudrate=9600):
        """Initialize UART connection to GPS module"""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.connected = True
            print(f"✅ Connected to {port} at {baudrate} baud")
            time.sleep(1)  # Wait for stabilization
        except Exception as e:
            print(f"❌ Failed to connect to {port}: {e}")
            self.connected = False
    
    def parse_nmea(self, sentence):
        """Parse NMEA sentence and extract latitude"""
        try:
            if not sentence.startswith('$'):
                return None
            
            # Remove checksum
            if '*' in sentence:
                sentence = sentence.split('*')[0]
            
            parts = sentence.split(',')
            
            # Parse GGA sentence (Global Positioning System Fix Data)
            # $GPGGA,time,lat,N/S,lon,E/W,fix,sats,...
            if 'GGA' in parts[0]:
                if len(parts) >= 9:
                    latitude_str = parts[2]
                    lat_dir = parts[3]
                    longitude_str = parts[4]
                    lon_dir = parts[5]
                    fix_quality = parts[6]
                    num_sats = parts[7]
                    
                    if latitude_str and longitude_str and fix_quality != '0':
                        # Parse latitude (DDMM.MMMM format)
                        lat_deg = float(latitude_str[:2])
                        lat_min = float(latitude_str[2:])
                        latitude = lat_deg + lat_min / 60.0
                        if lat_dir == 'S':
                            latitude = -latitude
                        
                        # Parse longitude (DDDMM.MMMM format)
                        lon_deg = float(longitude_str[:3])
                        lon_min = float(longitude_str[3:])
                        longitude = lon_deg + lon_min / 60.0
                        if lon_dir == 'W':
                            longitude = -longitude
                        
                        return {
                            'latitude': latitude,
                            'longitude': longitude,
                            'satellites': int(num_sats) if num_sats else 0,
                            'fix_quality': int(fix_quality),
                            'raw': sentence
                        }
        except Exception as e:
            pass
        
        return None
    
    def read_position(self):
        """Read GPS position from UART"""
        if not self.connected:
            return None
        
        try:
            if self.ser.in_waiting:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    return self.parse_nmea(line)
        except Exception as e:
            print(f"❌ Read Error: {e}")
        
        return None
    
    def close(self):
        """Close UART connection"""
        if self.connected:
            self.ser.close()


def test_gps():
    """Test GPS module"""
    print("╔════════════════════════════════════════╗")
    print("║   NEO-M8N GPS Test (UART/ttyAMA0)    ║")
    print("║   Testing Latitude Reading            ║")
    print("╚════════════════════════════════════════╝\n")
    
    gps = NEOM8N(port='/dev/ttyAMA0', baudrate=9600)
    
    if not gps.connected:
        print("❌ Failed to connect to GPS module")
        print("   Check UART connection:")
        print("   - RX → RPi5 GPIO15 (Pin 10)")
        print("   - TX → RPi5 GPIO14 (Pin 8)")
        print("   - GND → RPi5 GND")
        print("   - VCC → RPi5 3.3V or 5V")
        return
    
    print("📡 Reading GPS data...\n")
    
    max_attempts = 60
    attempts = 0
    fix_count = 0
    
    while attempts < max_attempts:
        try:
            position = gps.read_position()
            
            if position:
                fix_count += 1
                print(f"✅ [{fix_count}] Fix acquired!")
                print(f"   Latitude:  {position['latitude']:.6f}°")
                print(f"   Longitude: {position['longitude']:.6f}°")
                print(f"   Satellites: {position['satellites']}")
                print(f"   Fix Quality: {position['fix_quality']}\n")
                
                if fix_count >= 3:
                    print(f"✅ GPS TEST PASSED - Received {fix_count} valid fixes\n")
                    break
            else:
                print(f"⏳ Waiting for GPS fix... ({attempts + 1}/{max_attempts})", end='\r')
            
            time.sleep(0.1)
            attempts += 1
        
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(0.5)
            attempts += 1
    
    if fix_count == 0:
        print(f"\n❌ No GPS fix after {max_attempts} attempts")
        print("   Check:")
        print("   - GPS antenna connected and outside")
        print("   - Module powered on")
        print("   - UART connections secure (RX/TX)")
        print("   - Correct baud rate (try 115200 if not working)")
    
    gps.close()


if __name__ == '__main__':
    test_gps()
