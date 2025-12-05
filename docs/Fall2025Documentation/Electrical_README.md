# Electrical_README.md

This document explains the **electrical side of MakiMate**:

* How the **OpenCM9.04** powers and controls all Dynamixel motors
* How to **measure and set safe motor limits** in `maki_dxl_6.py`
* How the **speaker system** is wired (USB DAC + 5 V amplifier + 2" driver)
* Where to find the official guide to build the **power distribution harness**

All of this assumes:

* **Raspberry Pi 5** running **Ubuntu 24.04**
* **OpenCM9.04** as the motor controller
* **XL430-class Dynamixel** servos (Protocol 2.0, 57600 bps)

---

## 1. OpenCM9.04 in MakiMate (Motor Power + USB Bridge)

The **Robotis OpenCM9.04** is the central motor controller for MakiMate. It combines:

* USB serial connection to the **Raspberry Pi**
* **TTL Dynamixel bus** for all 6 head/face motors
* Motor power distribution (12 V)

This replaces:

* The **U2D2** USB–Dynamixel adapter
* The **SMPS2Dynamixel** power board
* Any separate 5 V logic supply

### 1.1 Required hardware

* OpenCM9.04 (with or without expansion board, depending on build)
* Right-angle **Micro-USB** cable (for clearance inside the head)
* 12 V DC power supply for the Dynamixel motors
* 6 × Dynamixel XL430-W250-T servos (Maki head joints)
* Daisy-chain Dynamixel cables between motors

### 1.2 Wiring overview

* The **12 V input** goes into the OpenCM / expansion board and is distributed to the Dynamixel bus.

* The motors are chained:

  ```text
  OpenCM9.04 → Motor 1 → Motor 2 → Motor 3 → Motor 4 → Motor 5 → Motor 6
  ```

* The OpenCM’s **Micro-USB** port connects, via a right-angle cable and panel extension, to one of the Pi’s USB-A ports.

Once wired, the Pi sees the OpenCM as a USB serial device (typically `/dev/ttyACM0`) and the ROS2 node `maki_dxl_6.py` talks to the motors through it.

---

## 2. OpenCM9.04 Firmware (U2D2-Style Bridge)

> If you have already flashed the provided MakiMate OpenCM firmware, you can skim this section; it is included here for completeness.

### 2.1 Install Arduino Legacy IDE

The OpenCM9.04 uses the legacy Arduino 1.8.x toolchain:

1. Download **Arduino IDE 1.8.19** from the legacy section:
   [https://www.arduino.cc/en/software#legacy-ide](https://www.arduino.cc/en/software#legacy-ide)
2. Install it on your Windows/macOS/Linux machine.

### 2.2 Install the Robotis / OpenCM board package

1. Open **Arduino IDE 1.8.x**

2. Go to **File → Preferences**

3. In **Additional Boards Manager URLs**, add:

   ```text
   https://raw.githubusercontent.com/ROBOTIS-GIT/OpenCM9.04/master/arduino/opencm_release/package_opencm9.04_index.json
   ```

4. Click **OK**

5. Go to **Tools → Board → Boards Manager…**

6. Search for **Robotis** and install the **OpenCM9.04** core.

### 2.3 Flash the MakiMate firmware

1. Connect the OpenCM9.04 to your PC with a Micro-USB cable.

2. In Arduino IDE:

   * **Tools → Board → Robotis → OpenCM9.04**
   * **Tools → Port →** select the USB serial port for the OpenCM

3. Create a new sketch and paste in the **OpenCM bridge firmware** (from the MakiMate docs / repo—see [`OpenCM9.04_Firmware_Code.ino`](../../makimate-llm-server/src/OpenCM9.04_Firmware_Code.ino) in your project).

4. Click **Sketch → Upload**.

After upload, the board:

* Acts as a **transparent USB↔Dynamixel bridge** (like a U2D2)
* Provides extra **utility commands** over USB (e.g., scanning, setting baud/ID)

---

## 3. Dynamixel Motor Wiring & Baud Rate

### 3.1 Daisy-chain the 6 motors

MakiMate uses 6 head/face joints:

| ID | Joint      | Description        |
| -- | ---------- | ------------------ |
| 1  | neck_yaw   | Head left/right    |
| 2  | neck_pitch | Head up/down (nod) |
| 3  | eyes_pitch | Eyes up/down       |
| 4  | eyes_yaw   | Eyes left/right    |
| 5  | lid_left   | Left eyelid        |
| 6  | lid_right  | Right eyelid       |

Connect the Dynamixel bus like this:

```text
OpenCM TTL → ID 1 → ID 2 → ID 3 → ID 4 → ID 5 → ID 6
```

Make sure each motor has the **correct ID** before assembling into the head.

### 3.2 Set baud rate to 57 600 bps

MakiMate’s ROS2 nodes expect **57 600 bps, Protocol 2.0**.

You can configure this with **Dynamixel Wizard 2.0**:

1. Connect OpenCM9.04 to your PC via USB.
2. Open **Dynamixel Wizard 2.0** (from Robotis).
3. Select the correct COM port and baud rate (e.g., 57 600).
4. Scan for motors (Protocol 2.0).
5. For each motor, set:

   * **Baud Rate** → 57 600
   * **Protocol** → 2.0
   * **ID** → 1–6 as listed above

Save settings and verify a scan finds **all 6 motors** at the correct IDs.

---

## 4. Setting Motor Limits in `maki_dxl_6.py`

Once the hardware works, you must configure **safe mechanical limits** in software so ROS never drives a joint into a hard stop.

### 4.1 How Dynamixel ticks map to angles

* Dynamixel **XL430** motors use **0–4095** ticks to represent one full revolution (360°).
* That’s **4096 steps total**, so:

  ```text
  ~11.38 ticks ≈ 1 degree
  ```

The Maki head does **not** use full 360° on any joint; each joint has a smaller physical range limited by the printed plastic parts and linkages.

### 4.2 Why limits matter

If limits are wrong, ROS can command:

* Over-rotation of the neck
* Eyelids colliding with the shell
* Eyes binding at the edges of travel

Correct limits:

* Prevent damage to plastic parts
* Keep movements smooth and controllable
* Ensure neutral position (0°) is correctly centered

---

## 5. STEP 1 – Connect Motors to Dynamixel Wizard

You will need:

* OpenCM9.04 with firmware flashed
* USB Micro-B cable
* Dynamixel Wizard 2.0 installed (Windows/macOS/Linux)
* MakiMate powered on

### 5.1 Connection

1. Plug the OpenCM9.04 into your computer via USB.
2. Open **Dynamixel Wizard 2.0**.
3. Select the **COM port** corresponding to the OpenCM.
4. Set **Baud Rate** to **57 600**.
5. Use the **Scan** tool:

   * Choose **Protocol 2.0**
   * Baudrate: **57 600**
   * Click **Start Scan**

You should see motors with IDs **1–6** detected.

---

## 6. STEP 2 – Find Mechanical MIN and MAX for Each Joint

> ⚠️ Safety: Move each joint **slowly** by hand. If you feel resistance, **stop immediately**. Never force past a hard stop.

For **each motor ID 1–6**:

### A. Select the motor

* Click on the motor’s **ID** in Dynamixel Wizard (e.g., ID 1 for `neck_yaw`).

### B. Disable torque

* Go to the **Control Table** view.
* Set **Torque Enable = 0**.
* This lets you rotate the shaft by hand.

### C. Move to mechanical MIN

* Gently move the joint to its **minimum** safe position:

  * Neck yaw: twist the head fully left
  * Neck pitch: tilt fully down, just before the mechanism binds
  * Eyes yaw/pitch: rotate to the left/right or up/down extreme
  * Eyelids: fully closed or fully open extreme, depending which side is lower

* Note the **Present Position** tick value (for example: `Present Position = 1840`).

* This number is your **MIN**.

### D. Move to mechanical MAX

* Gently move the joint to the **opposite extreme**, again stopping at the first firm resistance.
* Note the **Present Position** tick value (e.g.: `Present Position = 2660`).
* This number is your **MAX**.

### E. Record everything

Use this table as you go:

| Motor ID | Joint      | Min Tick | Max Tick |
| -------- | ---------- | -------- | -------- |
| 1        | neck_yaw   | XXXX     | YYYY     |
| 2        | neck_pitch | XXXX     | YYYY     |
| 3        | eyes_pitch | XXXX     | YYYY     |
| 4        | eyes_yaw   | XXXX     | YYYY     |
| 5        | lid_left   | XXXX     | YYYY     |
| 6        | lid_right  | XXXX     | YYYY     |

Write the actual values you read from Dynamixel Wizard for each joint.

---

## 7. STEP 3 – Enter Limits into `maki_dxl_6.py`

Open:

```text
~/MakiMate/src/makimate_dxl/makimate_dxl/maki_dxl_6.py
```

Locate the block:

```python
# ----------------------------------------------------
# ROBOT-SPECIFIC LIMITS (EDIT HERE FOR DIFFERENT ROBOTS)
# ----------------------------------------------------
ROBOT_LIMITS = {
    1: {"min": 2640, "max": 3641},  # neck_yaw
    2: {"min": 1855, "max": 2324},  # neck_pitch
    3: {"min": 2352, "max": 2635},  # eyes_pitch
    4: {"min": 1679, "max": 2495},  # eyes_yaw
    5: {"min": 2378, "max": 3057},  # lid_left
    6: {"min": 1021, "max": 1699},  # lid_right
}
```

Replace the numeric values with **your own** measured ticks.

Example (do NOT copy these blindly; they’re just a template):

```python
ROBOT_LIMITS = {
    1: {"min": 1900, "max": 2700},  # neck_yaw
    2: {"min": 1800, "max": 2300},  # neck_pitch
    3: {"min": 2300, "max": 2600},  # eyes_pitch
    4: {"min": 1700, "max": 2500},  # eyes_yaw
    5: {"min": 2400, "max": 3050},  # lid_left
    6: {"min": 1000, "max": 1700},  # lid_right
}
```

Save the file and rebuild:

```bash
cd ~/MakiMate
colcon build
```

---

## 8. STEP 4 – Test Limits from ROS2

On the Pi:

1. Start the Dynamixel node:

   ```bash
   cd ~/MakiMate
   source /opt/ros/jazzy/setup.bash
   source install/setup.bash
   ros2 run makimate_dxl maki_dxl_6
   ```

2. In another terminal, send a neutral command:

   ```bash
   cd ~/MakiMate
   source /opt/ros/jazzy/setup.bash
   source install/setup.bash
   ros2 topic pub /maki/joint_goals std_msgs/Float64MultiArray "{data: [0,0,0,0,0,0]}"
   ```

3. Try small single-joint moves:

   ```bash
   ros2 topic pub /maki/joint_goals std_msgs/Float64MultiArray "{data: [10,0,0,0,0,0]}"
   ros2 topic pub /maki/joint_goals std_msgs/Float64MultiArray "{data: [-10,0,0,0,0,0]}"
   ```

If the joints stop cleanly within their mechanical range with no grinding or hard impacts, your limits are correct.
If anything feels off, go back to Dynamixel Wizard, re-measure, and update `ROBOT_LIMITS`.

### 8.1 How neutral is computed

Inside `maki_dxl_6.py` you’ll see something like:

```python
self.neutral_ticks = {
    i: int((self.min_ticks[i] + self.max_ticks[i]) / 2)
}
```

So:

* **Neutral tick** = midpoint between your min and max.
* A command of `0°` is mapped to this midpoint.
* Commanded degrees are converted to ticks using the **4096 ticks / 360°** scale, but always clamped between your min/max.

---

## 9. Speaker System – USB DAC + 5 V Amplifier + 2" Driver

MakiMate uses a **custom internal speaker assembly** mounted in the back of the head.

### 9.1 Components

* **2" full-range speaker driver**

  * Mounted on a bracket in the back of the Maki head shell
  * Provides a good balance between loudness and form factor

* **USB-to-AUX DAC**

  * Small USB sound card (USB in → 3.5 mm stereo out)
  * Plugged into a USB port on the Raspberry Pi
  * The audio output (3.5 mm jack) feeds the amplifier’s input

* **5 V audio power amplifier**

  * Class-D mini amplifier module
  * Powered from the Pi’s **5 V rail** (or a dedicated 5 V from the power harness)
  * Audio input: 3.5 mm output of the USB DAC
  * Speaker output: wired directly to the 2" driver terminals

### 9.2 Wiring layout

1. **USB DAC**

   * Connect the USB DAC to a free USB-A port on the Pi.
   * The Pi will see it as an additional sound card (used by TTS).

2. **DAC to amplifier**

   * Use a short **3.5 mm male-to-male** cable from the DAC’s headphone jack to the amplifier’s audio input (L/R and GND).
   * If the amp has screw terminals for input, you may need to cut a cable and terminate the wires.

3. **Amplifier power**

   * Supply **5 V and GND** from the internal power distribution harness (or from a regulated 5 V rail).
   * The current draw is modest, but ensure the wiring gauge is appropriate and the 5 V source is stable.

4. **Amplifier to speaker driver**

   * Wire the amplifier’s **speaker outputs** to the 2" driver:

     * `SPK+` → speaker positive terminal
     * `SPK−` → speaker negative terminal
   * Mount the driver so the cone points outward through the back grill of the Maki head.

5. **Software**

   * In ALSA/PulseAudio, set the default output to the **USB DAC**.

   * Test with:

     ```bash
     aplay /usr/share/sounds/alsa/Front_Center.wav
     ```

   * If you hear clean audio from the built-in speaker, the TTS nodes (e.g., `natural_tts_node.py`) will use the same device.

---

## 10. Power Distribution Harness

MakiMate uses a **custom harness** to fan out power to:

* OpenCM9.04 (12 V for motors)
* Raspberry Pi 5 and 5 V accessories (USB DAC + amplifier)
* Rocker power switch and connectors

The original wiring steps (heat-shrink, 2-pin/4-pin connectors, DC jack, rocker switch, 5 V regulator, etc.) are documented by Hello-Robo for the MAKI platform.

Rather than duplicating every splice step here, use the official tutorial:

👉 **Full power harness tutorial:**
[https://www.hello-robo.com/tutorials](https://www.hello-robo.com/tutorials)

Under the MAKI **Wiring / Power** section you will find:

* Step-by-step images for splicing 2-pin connectors
* How to wire the DC power jack and rocker power switch
* How to connect the 5 V USB regulator module
* How to solder the 4-pin header and optional X3P headers to the OpenCM9.04
* Example pictures of the finished harness layout

The MakiMate project follows the **same wiring pattern** as this tutorial, with the key differences:

* **OpenCM9.04** is used to both **power and communicate** with the Dynamixels (no separate U2D2).
* The **Raspberry Pi 5** and speaker electronics tap into the appropriate 5 V and 12 V runs from that harness.

Use the Hello-Robo instructions for the **physical construction**, and then route the harness leads to:

* 12 V → OpenCM + any other 12 V loads
* 5 V → Raspberry Pi 5, USB DAC, 5 V amplifier
* Switch legs → front panel rocker switch and DC barrel jack

---

## 🧭 Navigation

🔙 Back to Main Documentation
➡️ [`../../README.md`](Overall_README.md)
