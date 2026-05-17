# Motor Control System 🚀

Motor control system for delivery robot using ESP32 and RPi5.

## Hardware Setup

### Components
- **RPi5** - Main computer with sensor fusion
- **ESP32** - Motor controller
- **Hoverboard Motherboard** - Controls BLDC motors
- **2x 6-inch BLDC Motors** - Wheel drive (left & right)

### Connections
```
RPi5 (USB) ←→ ESP32 (USB)
ESP32 (Serial2, pins 16-17) ←→ Hoverboard Motherboard
Hoverboard ←→ 2x BLDC Motors
```

## Protocol

The communication protocol between RPi5 and ESP32:

```
Byte:  0-1    2-3    4-5    6-7
Field: START  STEER  SPEED  CHECKSUM
Type:  uint16 int16  int16  uint16
Size:  8 bytes total
```

### Field Descriptions

| Field | Range | Meaning |
|-------|-------|---------|
| START | 0xABCD | Magic number (fixed header) |
| STEER | -150 to +150 | Steering (-150=left, 0=straight, +150=right) |
| SPEED | -150 to +150 | Speed (-150=backward, 0=stop, +150=forward) |
| CHECKSUM | calculated | XOR of START ^ STEER ^ SPEED |

### Example Values

- Forward: `START=0xABCD, STEER=0, SPEED=100`
- Turn left: `START=0xABCD, STEER=-100, SPEED=0`
- Arc right: `START=0xABCD, STEER=75, SPEED=100`

## Installation

### 1. ESP32 Setup

1. Install Arduino IDE or PlatformIO
2. Open `esp32_firmware.ino`
3. Select ESP32 board and COM port
4. Upload to ESP32

### 2. RPi5 Setup

```bash
# Clone or install this repo
cd /home/pi/motor-control

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from motor_control import MotorController
import time

# Connect to motor controller
motor = MotorController(port='/dev/ttyUSB0', baudrate=115200)

# Move forward
motor.forward(speed=100)
time.sleep(2)

# Turn right
motor.turn_right(speed=80)
time.sleep(1)

# Arc left while moving forward
motor.arc_left(steer_speed=75, forward_speed=100)
time.sleep(2)

# Stop
motor.stop()

# Disconnect
motor.close()
```

### API Reference

#### MotorController Class

```python
class MotorController(port='/dev/ttyUSB0', baudrate=115200, timeout=1)
```

**Methods:**

- `forward(speed=100)` - Move forward
- `backward(speed=100)` - Move backward
- `turn_left(speed=100)` - Turn left in place
- `turn_right(speed=100)` - Turn right in place
- `arc_left(steer_speed=75, forward_speed=100)` - Arc forward-left
- `arc_right(steer_speed=75, forward_speed=100)` - Arc forward-right
- `stop()` - Stop all motors
- `send_command(steer, speed)` - Send raw command
- `close()` - Disconnect

**Parameters:**

- `speed` (int): Motor speed 0-150 (clamped internally)
- `steer_speed` (int): Steering intensity 0-150
- `forward_speed` (int): Forward speed 0-150

## Testing

Run the comprehensive test suite:

```bash
python test_motors.py
```

This will run:
1. **Basic Movements** - Forward, backward, left, right
2. **Arc Movements** - Forward while turning
3. **Speed Levels** - Test different speeds
4. **Dance Pattern** - Fun verification pattern
5. **Interactive Mode** - Manual command testing

### Interactive Mode Commands

```
f [speed]  - Forward (default: 100)
b [speed]  - Backward (default: 100)
l [speed]  - Turn left (default: 100)
r [speed]  - Turn right (default: 100)
s          - Stop
q          - Quit
```

## Troubleshooting

### Connection Issues

```
❌ Failed to connect to motor controller
```

**Solutions:**
- Check USB cable is connected
- Run `ls /dev/ttyUSB*` to find ESP32 port
- Check ESP32 firmware is uploaded
- Try different USB port

### Checksum Errors

```
❌ Checksum error - Command rejected
```

**Causes:**
- Serial connection noise
- Baud rate mismatch (should be 115200)
- ESP32 firmware issue

**Solutions:**
- Re-upload ESP32 firmware
- Try different USB cable (shorter, better shielded)
- Check serial connection is stable

### Motors Not Moving

**Solutions:**
- Verify hoverboard is powered on
- Check hoverboard motherboard is connected to ESP32
- Test with existing ESP32 dance code
- Check motor cables are connected

## Integration with Sensor Fusion

When integrating with the main sensor_fusion system:

```python
from motor_control import MotorController
from sensor_fusion import SensorFusion

# Initialize both systems
sensors = SensorFusion()
motor = MotorController()

# Example: Move robot based on sensor data
while True:
    gps = sensors.get_gps()
    lidar = sensors.get_lidar()
    
    # Navigate based on sensors
    # (to be implemented in navigation module)
    
    # Send motor commands
    motor.forward(100)
    time.sleep(0.1)
```

## Future Improvements

- [ ] PID speed control
- [ ] Odometry tracking (distance traveled)
- [ ] Motor feedback via encoders
- [ ] Acceleration/deceleration profiles
- [ ] Emergency stop button
- [ ] Motor diagnostics

## Files

- `esp32_firmware.ino` - ESP32 motor controller firmware
- `motor_control.py` - RPi5 Python library
- `test_motors.py` - Test suite
- `requirements.txt` - Python dependencies
- `README.md` - This file

## License

[Your License]

## Author

Built for delivery robot project 🚀
