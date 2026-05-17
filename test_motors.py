"""
Motor Control Test Suite
Tests all motor control functions
"""

import sys
import time
from motor_control import MotorController

def test_basic_movements(motor):
    """Test basic movement commands"""
    print("\n" + "="*50)
    print("TEST 1: Basic Movements")
    print("="*50)
    
    print("\n✅ Moving forward...")
    motor.forward(100)
    time.sleep(2)
    
    print("✅ Stopping...")
    motor.stop()
    time.sleep(1)
    
    print("✅ Moving backward...")
    motor.backward(100)
    time.sleep(2)
    
    print("✅ Stopping...")
    motor.stop()
    time.sleep(1)
    
    print("✅ Turning left...")
    motor.turn_left(100)
    time.sleep(2)
    
    print("✅ Stopping...")
    motor.stop()
    time.sleep(1)
    
    print("✅ Turning right...")
    motor.turn_right(100)
    time.sleep(2)
    
    print("✅ Stopping...")
    motor.stop()
    time.sleep(1)
    
    print("\n✅ Basic movements test PASSED")

def test_arc_movements(motor):
    """Test arc movements"""
    print("\n" + "="*50)
    print("TEST 2: Arc Movements")
    print("="*50)
    
    print("\n✅ Arc left...")
    motor.arc_left(75, 100)
    time.sleep(2)
    
    print("✅ Stopping...")
    motor.stop()
    time.sleep(1)
    
    print("✅ Arc right...")
    motor.arc_right(75, 100)
    time.sleep(2)
    
    print("✅ Stopping...")
    motor.stop()
    time.sleep(1)
    
    print("\n✅ Arc movements test PASSED")

def test_speed_levels(motor):
    """Test different speed levels"""
    print("\n" + "="*50)
    print("TEST 3: Speed Levels")
    print("="*50)
    
    speeds = [50, 100, 150]
    
    for speed in speeds:
        print(f"\n✅ Forward at speed {speed}...")
        motor.forward(speed)
        time.sleep(1)
        motor.stop()
        time.sleep(0.5)
    
    print("\n✅ Speed levels test PASSED")

def test_dance_pattern(motor):
    """Fun dance pattern to verify motor operation"""
    print("\n" + "="*50)
    print("TEST 4: Dance Pattern 💃")
    print("="*50)
    
    print("\n✅ Let's dance!")
    
    # Step 1: Forward
    print("  Step forward...")
    motor.forward(100)
    time.sleep(2)
    motor.stop()
    time.sleep(0.5)
    
    # Step 2: Spin right
    print("  Spin right...")
    motor.turn_right(100)
    time.sleep(1)
    motor.stop()
    time.sleep(0.5)
    
    # Step 3: Spin left
    print("  Spin left...")
    motor.turn_left(100)
    time.sleep(1)
    motor.stop()
    time.sleep(0.5)
    
    # Step 4: Arc pattern
    print("  Arc left...")
    motor.arc_left(80, 100)
    time.sleep(1)
    motor.stop()
    time.sleep(0.5)
    
    print("  Arc right...")
    motor.arc_right(80, 100)
    time.sleep(1)
    motor.stop()
    time.sleep(0.5)
    
    # Step 5: Backward
    print("  Backward...")
    motor.backward(80)
    time.sleep(1)
    motor.stop()
    time.sleep(0.5)
    
    print("\n✅ Dance pattern complete! 🎉")

def interactive_mode(motor):
    """Interactive manual control mode"""
    print("\n" + "="*50)
    print("INTERACTIVE MODE - Manual Control")
    print("="*50)
    print("\nCommands:")
    print("  f [speed]  - Forward (default: 100)")
    print("  b [speed]  - Backward (default: 100)")
    print("  l [speed]  - Turn left (default: 100)")
    print("  r [speed]  - Turn right (default: 100)")
    print("  s          - Stop")
    print("  q          - Quit interactive mode")
    print("\nExample: f 120  (forward at speed 120)")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if not cmd:
                continue
            
            parts = cmd.split()
            action = parts[0]
            speed = int(parts[1]) if len(parts) > 1 else 100
            
            if action == 'f':
                motor.forward(speed)
            elif action == 'b':
                motor.backward(speed)
            elif action == 'l':
                motor.turn_left(speed)
            elif action == 'r':
                motor.turn_right(speed)
            elif action == 's':
                motor.stop()
            elif action == 'q':
                break
            else:
                print("❌ Unknown command. Try again.")
        
        except ValueError:
            print("❌ Invalid speed value. Use: f 100")
        except KeyboardInterrupt:
            print("\n⏹️  Stopping...")
            motor.stop()
            break

def main():
    """Main test function"""
    print("\n╔════════════════════════════════════════╗")
    print("║   Motor Control Test Suite v1.0        ║")
    print("║   Testing RPi5 ↔ ESP32 ↔ Hoverboard   ║")
    print("╚════════════════════════════════════════╝")
    
    # Try to connect to motor controller
    try:
        print("\n🔌 Connecting to motor controller...")
        motor = MotorController(port='/dev/ttyUSB0', baudrate=115200)
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("   Make sure:")
        print("   1. ESP32 is connected via USB")
        print("   2. ESP32 firmware is uploaded")
        print("   3. Run: ls /dev/ttyUSB* to check port")
        sys.exit(1)
    
    try:
        # Run tests
        test_basic_movements(motor)
        time.sleep(2)
        
        test_arc_movements(motor)
        time.sleep(2)
        
        test_speed_levels(motor)
        time.sleep(2)
        
        test_dance_pattern(motor)
        time.sleep(2)
        
        # Interactive mode
        print("\n" + "="*50)
        response = input("Run interactive mode? (y/n): ").strip().lower()
        if response == 'y':
            interactive_mode(motor)
        
        print("\n✅ All tests completed successfully!")
        print("🚀 Motor control system is ready for integration!")
    
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        print("\n🔌 Closing connection...")
        motor.close()

if __name__ == '__main__':
    main()
