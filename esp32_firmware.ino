/*
  ESP32 Motor Controller Firmware
  Receives motor commands from RPi5 via USB Serial
  Sends commands to hoverboard motherboard via Serial2
  
  Protocol:
  - START: 0xABCD (magic number)
  - STEER: -150 to +150 (left to right)
  - SPEED: -150 to +150 (backward to forward)
  - CHECKSUM: START ^ STEER ^ SPEED
  
  Connections:
  - USB: Connected to RPi5
  - Serial2 (pins 16, 17): Connected to hoverboard motherboard
*/

#define RX2 16  // Serial2 RX pin
#define TX2 17  // Serial2 TX pin

#define PROTOCOL_START 0xABCD
#define SERIAL_BAUD 115200
#define HOVERBOARD_BAUD 115200

// Command structure
struct Command {
  uint16_t start;
  int16_t steer;
  int16_t speed;
  uint16_t checksum;
};

void setup() {
  // Serial0: USB communication with RPi5
  Serial.begin(SERIAL_BAUD);
  
  // Serial2: Hoverboard communication
  Serial2.begin(HOVERBOARD_BAUD, SERIAL_8N1, RX2, TX2);
  
  delay(1000);
  
  Serial.println("╔════════════════════════════════════════╗");
  Serial.println("║   ESP32 Motor Controller v1.0          ║");
  Serial.println("║   Ready to receive motor commands      ║");
  Serial.println("╚════════════════════════════════════════╝");
  
  Serial.print("Listening on Serial (USB): ");
  Serial.print(SERIAL_BAUD);
  Serial.println(" baud");
  
  Serial.print("Sending to Serial2 (Hoverboard): ");
  Serial.print(HOVERBOARD_BAUD);
  Serial.println(" baud");
}

void loop() {
  // Check if data available from RPi5
  if (Serial.available() >= sizeof(Command)) {
    Command cmd;
    
    // Read command bytes
    if (Serial.readBytes((byte*)&cmd, sizeof(Command)) == sizeof(Command)) {
      // Validate command
      if (validateCommand(cmd)) {
        // Forward to hoverboard
        forwardToHoverboard(cmd);
        
        // Log for debugging
        logCommand(cmd);
      } else {
        Serial.println("❌ Checksum error - Command rejected");
      }
    }
  }
  
  // Forward any hoverboard responses back to RPi5
  if (Serial2.available()) {
    byte b = Serial2.read();
    Serial.write(b);
  }
}

/*
 * Validate command checksum
 * Checksum = START ^ STEER ^ SPEED
 */
bool validateCommand(const Command& cmd) {
  if (cmd.start != PROTOCOL_START) {
    Serial.println("❌ Invalid START marker");
    return false;
  }
  
  uint16_t expected_checksum = cmd.start ^ cmd.steer ^ cmd.speed;
  
  if (cmd.checksum != expected_checksum) {
    Serial.print("❌ Checksum mismatch. Expected: 0x");
    Serial.print(expected_checksum, HEX);
    Serial.print(" Got: 0x");
    Serial.println(cmd.checksum, HEX);
    return false;
  }
  
  return true;
}

/*
 * Forward command to hoverboard motherboard
 * Convert Command struct to hoverboard protocol
 */
void forwardToHoverboard(const Command& cmd) {
  // Hoverboard protocol: send steer and speed as bytes
  // [START_LOW, START_HIGH, STEER_LOW, STEER_HIGH, SPEED_LOW, SPEED_HIGH, CHECKSUM_LOW, CHECKSUM_HIGH]
  
  byte data[8];
  
  // START (little-endian)
  data[0] = cmd.start & 0xFF;
  data[1] = (cmd.start >> 8) & 0xFF;
  
  // STEER (little-endian)
  data[2] = cmd.steer & 0xFF;
  data[3] = (cmd.steer >> 8) & 0xFF;
  
  // SPEED (little-endian)
  data[4] = cmd.speed & 0xFF;
  data[5] = (cmd.speed >> 8) & 0xFF;
  
  // CHECKSUM (little-endian)
  data[6] = cmd.checksum & 0xFF;
  data[7] = (cmd.checksum >> 8) & 0xFF;
  
  // Send to hoverboard
  Serial2.write(data, 8);
}

/*
 * Log command for debugging
 */
void logCommand(const Command& cmd) {
  Serial.print("✅ Command: STEER=");
  Serial.print(cmd.steer);
  Serial.print(" SPEED=");
  Serial.print(cmd.speed);
  Serial.print(" (0x");
  Serial.print(cmd.checksum, HEX);
  Serial.println(")");
}
