/*
  OpenCM9.04: U2D2-like transparent bridge + utility commands (with Dynamixel2Arduino)

  - Transparent bridge so Dynamixel Wizard / SDK can talk as if this were a U2D2.
  - Utility commands over USB (start with '#') use Dynamixel2Arduino to SCAN/SETID/SETBAUD.
*/

#include <Dynamixel2Arduino.h>

#ifndef LED_BUILTIN
#define LED_BUILTIN 13
#endif

#define USB SerialUSB
#define DXL Serial1
const int DIR_PIN = 28;

Dynamixel2Arduino dxl(DXL);
float proto_ver = 2.0f;          // default protocol
uint32_t dxl_baud = 57600;       // default baud (XL430 factory)

// ----- low-level bridge helpers -----
void dxlBegin(uint32_t bps) {
  dxl_baud = bps;
  DXL.end();
  delay(5);
  DXL.setDxlMode(true);          // map Serial1 to the DXL port pins
  pinMode(DIR_PIN, OUTPUT);
  digitalWrite(DIR_PIN, LOW);    // start in RX
  DXL.begin(dxl_baud);
}

inline void dirTX() { digitalWrite(DIR_PIN, HIGH); }
inline void dirRX() { digitalWrite(DIR_PIN, LOW);  }

// Write a burst from USB -> DXL, with proper half-duplex toggle
void usbToDxlBurst() {
  int n = USB.available();
  if (n <= 0) return;
  dirTX();
  while (n--) DXL.write((uint8_t)USB.read());
  DXL.flush();
  dirRX();
  digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
}

// Stream any available DXL bytes back to USB
void dxlToUsbStream() {
  while (DXL.available()) USB.write((uint8_t)DXL.read());
}

// ----- utility command parser (lines starting with '#') -----
bool readUsbLine(String &out) {
  while (USB.available()) {
    char c = USB.read();
    if (c == '\r') continue;
    if (c == '\n') return true;
    out += c;
  }
  return false;
}

void cmd_HELP() {
  USB.println(F("#HELP            - show this"));
  USB.println(F("#SCAN            - ping IDs 0..252"));
  USB.println(F("#SETID o n       - set ID from o to n"));
  USB.println(F("#SETBAUD n       - set bus baud (e.g., 57600, 1000000)"));
  USB.println(F("#PROTO 1|2       - set protocol version"));
}

void suspendBridge() {
  // drain any in-flight USB bytes before library ops
  while (USB.available()) (void)USB.read();
  delay(2);
}

void resumeBridge() {
  // nothing special; passthrough continues next loop
}

void cmd_SCAN() {
  suspendBridge();
  dxl.begin(dxl_baud);
  dxl.setPortProtocolVersion(proto_ver);
  USB.print(F("[SCAN] proto=")); USB.print(proto_ver);
  USB.print(F(" baud=")); USB.println(dxl_baud);

  int found = 0;
  for (int id = 0; id <= 252; id++) {
    if (dxl.ping(id)) {
      USB.print(F("  ID ")); USB.print(id); USB.println(F(" : PRESENT"));
      found++;
    }
    // brief yield so USB stays responsive
    if ((id % 16) == 0) { dxlToUsbStream(); delay(1); }
  }
  USB.print(F("[SCAN] total=")); USB.println(found);
  resumeBridge();
}

void cmd_SETID(int old_id, int new_id) {
  suspendBridge();
  dxl.begin(dxl_baud);
  dxl.setPortProtocolVersion(proto_ver);
  bool ok = dxl.setID(old_id, new_id);
  USB.print(F("[SETID] ")); USB.print(old_id);
  USB.print(F(" -> ")); USB.print(new_id);
  USB.println(ok ? F(" [OK]") : F(" [FAIL]"));
  resumeBridge();
}

void cmd_SETBAUD(uint32_t bps) {
  // Change *bus* baud on the bridge; motors stay at current baud
  dxlBegin(bps);
  USB.print(F("[SETBAUD] DXL side = ")); USB.println(dxl_baud);
}

void cmd_PROTO(int v) {
  proto_ver = (v == 1) ? 1.0f : 2.0f;
  USB.print(F("[PROTO] ")); USB.println(proto_ver, 1);
}

void handleUsbCommands() {
  // Only treat lines that start with '#'
  if (!USB.available()) return;
  if ((char)USB.peek() != '#') return;

  String line;
  if (!readUsbLine(line)) return;
  line.trim();                    // '#CMD ...'
  if (!line.startsWith("#")) return;

  // Parse
  if (line.equalsIgnoreCase("#HELP")) { cmd_HELP(); return; }
  if (line.equalsIgnoreCase("#SCAN")) { cmd_SCAN(); return; }

  if (line.startsWith("#SETID")) {
    int s1 = line.indexOf(' ');
    int s2 = line.indexOf(' ', s1 + 1);
    if (s1 > 0 && s2 > s1) {
      int old_id = line.substring(s1 + 1, s2).toInt();
      int new_id = line.substring(s2 + 1).toInt();
      if (old_id >= 0 && new_id >= 0) { cmd_SETID(old_id, new_id); return; }
    }
    USB.println(F("[ERR] usage: #SETID <old> <new>"));
    return;
  }

  if (line.startsWith("#SETBAUD")) {
    int s = line.indexOf(' ');
    if (s > 0) { cmd_SETBAUD((uint32_t)line.substring(s + 1).toInt()); return; }
    USB.println(F("[ERR] usage: #SETBAUD <bps>"));
    return;
  }

  if (line.startsWith("#PROTO")) {
    int s = line.indexOf(' ');
    if (s > 0) { cmd_PROTO(line.substring(s + 1).toInt()); return; }
    USB.println(F("[ERR] usage: #PROTO 1|2"));
    return;
  }

  USB.println(F("[ERR] unknown command. Try #HELP"));
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  USB.begin(115200);              // host baud ignored by CDC, but needed to open
  dxlBegin(dxl_baud);

  USB.println(F("OpenCM U2D2 Bridge + Utils"));
  USB.println(F("Use as a normal U2D2. For utilities, type commands starting with '#'."));
  USB.println(F("Try: #HELP"));
}

void loop() {
  // Utility commands (lines starting with '#') — safe alongside passthrough
  handleUsbCommands();

  // Transparent bridge
  usbToDxlBurst();
  dxlToUsbStream();
}
