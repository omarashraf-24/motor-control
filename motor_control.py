"""
Motor Control Library for RPi5
Communicates with ESP32 to control hoverboard BLDC motors
"""

import serial
import struct
import time
from typing import Optional

class MotorController:
    """
    Control hoverboard motors via ESP32
    
    Protocol:
    - START: 0xABCD (magic number)
    - STEER: -150 to +150 (left to right)
    - SPEED: -150 to +150 (backward to forward)
    - CHECKSUM: START ^ STEER ^ SPEED
    """
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200, timeout: float = 1.0):
        """
        Initialize motor controller connection
        
        Args:
            port: Serial port (e.g., '/dev/ttyUSB0' on RPi5)
            baudrate: Serial baudrate (must match ESP32: 115200)
            timeout: Serial read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.connected = False
        
        self._connect()
    
    def _connect(self) -> None:
        """Establish serial connection to ESP32"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.connected = True
            print(f"✅ Connected to motor controller on {self.port}")
            time.sleep(1)  # Wait for ESP32 to initialize
        except serial.SerialException as e:
            self.connected = False
            raise Exception(f"Failed to connect to {self.port}: {e}")
    
    def _send_command(self, steer: int, speed: int) -> bool:
        """
        Send raw command to ESP32
        
        Args:
            steer: Steering value -150 to +150
            speed: Speed value -150 to +150
        
        Returns:
            True if sent successfully
        """
        if not self.connected:
            raise Exception("Not connected to motor controller")
        
        # Clamp values
        steer = max(-150, min(150, steer))
        speed = max(-150, min(150, speed))
        
        # Protocol: START(2) + STEER(2) + SPEED(2) + CHECKSUM(2) = 8 bytes
        start = 0xABCD
        checksum = start ^ steer ^ speed
        
        try:
            # Pack as little-endian unsigned/signed shorts
            data = struct.pack('<HHHH', start, steer & 0xFFFF, speed & 0xFFFF, checksum & 0xFFFF)
            self.serial.write(data)
            return True
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return False
    
    def send_command(self, steer: int, speed: int) -> bool:
        """
        Public method to send raw command
        
        Args:
            steer: Steering value -150 to +150
            speed: Speed value -150 to +150
        
        Returns:
            True if sent successfully
        """
        return self._send_command(steer, speed)
    
    def forward(self, speed: int = 100) -> bool:
        """Move forward"""
        speed = max(0, min(150, speed))
        return self._send_command(0, speed)
    
    def backward(self, speed: int = 100) -> bool:
        """Move backward"""
        speed = max(0, min(150, speed))
        return self._send_command(0, -speed)
    
    def turn_left(self, speed: int = 100) -> bool:
        """Turn left in place"""
        speed = max(0, min(150, speed))
        return self._send_command(-speed, 0)
    
    def turn_right(self, speed: int = 100) -> bool:
        """Turn right in place"""
        speed = max(0, min(150, speed))
        return self._send_command(speed, 0)
    
    def arc_left(self, steer_speed: int = 75, forward_speed: int = 100) -> bool:
        """Arc forward-left"""
        steer_speed = max(0, min(150, steer_speed))
        forward_speed = max(0, min(150, forward_speed))
        return self._send_command(-steer_speed, forward_speed)
    
    def arc_right(self, steer_speed: int = 75, forward_speed: int = 100) -> bool:
        """Arc forward-right"""
        steer_speed = max(0, min(150, steer_speed))
        forward_speed = max(0, min(150, forward_speed))
        return self._send_command(steer_speed, forward_speed)
    
    def stop(self) -> bool:
        """Stop all motors"""
        return self._send_command(0, 0)
    
    def close(self) -> None:
        """Close serial connection"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.connected = False
            print("🔌 Connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == '__main__':
    try:
        motor = MotorController()
        
        # Move forward
        motor.forward(100)
        time.sleep(2)
        
        # Turn right
        motor.turn_right(80)
        time.sleep(1)
        
        # Stop
        motor.stop()
        
        motor.close()
    except Exception as e:
        print(f"Error: {e}")
