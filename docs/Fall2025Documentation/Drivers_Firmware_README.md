# Drivers_Firmware_README.md

This document collects all instructions related to **drivers, firmware, and device permissions** for the Raspberry Pi camera, Dynamixel motors (via OpenCM9.04), and the ReSpeaker 4-Mic Array with LED ring. Everything below is intended to be directly copy–pasted into the `Drivers_Firmware_README.md` file.

---

## 1. System-Level Device & Driver Packages

Install core system tools and hardware-related utilities (camera, USB, audio, build tools):

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    git curl wget htop net-tools unzip \
    python3-pip python3-venv python3-dev build-essential \
    ffmpeg pulseaudio \
    v4l-utils usbutils
```

Reboot:

```bash
sudo reboot
```

These packages provide:

* `v4l-utils` – tools for Video4Linux (camera debug/listing).
* `usbutils` – `lsusb` and related tools for USB devices (ReSpeaker, OpenCM, etc.).
* `pulseaudio` – user-space audio system for microphones/speakers.
* Build tools for building camera drivers (`libcamera`, `rpicam-apps`) from source.

---

## 2. User & Group Permissions for Hardware Access

Grant your user full access to serial ports, audio devices, video devices, and plug-and-play USB hardware:

```bash
sudo usermod -aG dialout,audio,video,plugdev $(whoami)
sudo reboot
```

This is required so that:

* The **OpenCM9.04** (Dynamixel motors) on `/dev/tty*` is accessible without `sudo` (via `dialout`).
* The **ReSpeaker 4-Mic Array** and other ALSA audio devices work without `sudo` (via `audio`).
* The **Raspberry Pi camera** and other video devices are accessible (via `video`).
* USB devices (ReSpeaker LED ring, OpenCM, etc.) can be controlled (via `plugdev`).

---

## 3. Dynamixel Motors (OpenCM9.04) – Driver & Permissions

### 3.1 Install Dynamixel SDK and Supporting Libraries

From your Pi:

```bash
source ~/asr_venv/bin/activate

pip install setuptools
pip install PyYAML  # capitalization doesn’t matter: PyYAML / pyyaml

deactivate

sudo apt install -y ros-jazzy-dynamixel-sdk
sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev
chmod +x /home/makimate/MakiMate/piper_bin/piper
```

* `ros-jazzy-dynamixel-sdk` provides the **drivers and ROS2 bindings** needed to talk to Dynamixel servos via OpenCM9.04.
* `portaudio` libraries are needed for some audio/ASR components used in the same system.

### 3.2 Udev Rules for Dynamixel (via `system_configs/udev`)

If your repo contains `system_configs/udev/99-dynamixel.rules`, it will be installed as part of the Piper install step (below) and ensures that Dynamixel devices are accessible without `sudo`.

Run:

```bash
cd ~/MakiMate/piper_bin
./install_piper.py
```

This script:

* Installs the Piper TTS binary.
* Installs any udev rules provided in `system_configs/udev/`, such as `99-dynamixel.rules`.
* Ensures that the OpenCM9.04 and other related devices have correct permissions on plug-in.

> If you modify or add your own udev rules, re-run `./install_piper.py` or manually copy the `*.rules` files into `/etc/udev/rules.d/` and reload udev (see below in the ReSpeaker section for the exact pattern).

---

## 4. Raspberry Pi Camera (Pi 5 – Ubuntu 24.04)

The Raspberry Pi 5 uses the **libcamera/rpicam** stack. You must both enable the camera at the firmware level and install the camera tools (`rpicam-apps`).

### 4.1 Apply System Configs and Install ROS Camera Info Manager

From your MakiMate repo:

```bash
cd ~/MakiMate/system_configs
./install_configs.sh
sudo apt install ros-jazzy-camera-info-manager
```

* `install_configs.sh` configures `/boot/firmware/config.txt` and other system files so the Pi camera is enabled at boot.
* `ros-jazzy-camera-info-manager` provides the ROS2 camera calibration/metadata support.

Reboot after this step:

```bash
sudo reboot
```

---

### 4.2 Install Raspberry Pi Camera Tools (rpicam-apps)

On Ubuntu 24.04 for Pi, `rpicam-apps` is often **not** available via `apt`, so you build it from source.

#### 4.2.1 Check if `rpicam-apps` is available (optional)

```bash
sudo apt update
apt-cache policy rpicam-apps
```

If `Candidate:` is `(none)` or no version is listed, you must build from source.

---

#### 4.2.2 Install Build Dependencies

```bash
sudo apt update
sudo apt full-upgrade -y

# Essential build tools
sudo apt install -y git python3-pip python3-jinja2 meson cmake ninja-build build-essential

# libcamera (RPi fork) dependencies
sudo apt install -y libboost-dev libgnutls28-dev openssl libtiff5-dev pybind11-dev \
                    python3-yaml python3-ply libglib2.0-dev libgstreamer-plugins-base1.0-dev

# rpicam-apps dependencies
sudo apt install -y libboost-program-options-dev libdrm-dev libexif-dev \
                    libepoxy-dev libjpeg-dev libtiff5-dev libpng-dev

# For desktop Ubuntu (GUI preview window)
sudo apt install -y qtbase5-dev libqt5core5a libqt5gui5 libqt5widgets5

# Video4Linux utils (handy for debugging)
sudo apt install -y v4l-utils
```

---

#### 4.2.3 Build Raspberry Pi’s `libcamera` Fork

```bash
cd ~
git clone https://github.com/raspberrypi/libcamera.git
cd libcamera

meson setup build --buildtype=release \
  -Dpipelines=rpi/vc4,rpi/pisp \
  -Dipas=rpi/vc4,rpi/pisp \
  -Dv4l2=true \
  -Dgstreamer=enabled \
  -Dtest=false \
  -Dlc-compliance=disabled \
  -Dcam=disabled \
  -Dqcam=disabled \
  -Ddocumentation=disabled \
  -Dpycamera=enabled

# Build (takes a while on the Pi 5)
ninja -C build

# Install
sudo ninja -C build install
cd ~
```

---

#### 4.2.4 Build and Install `rpicam-apps`

```bash
cd ~
git clone https://github.com/raspberrypi/rpicam-apps.git
cd rpicam-apps

# For Ubuntu Desktop (with preview window)
meson setup build \
  -Denable_libav=disabled \
  -Denable_drm=enabled \
  -Denable_egl=enabled \
  -Denable_qt=enabled \
  -Denable_opencv=disabled \
  -Denable_tflite=disabled \
  -Denable_hailo=disabled

# Build
meson compile -C build

# Install
sudo meson install -C build

# Refresh linker cache
sudo ldconfig

cd ~
```

After this, binaries like `rpicam-hello`, `rpicam-still`, etc. will be available in your `PATH`.

---

### 4.3 Verify Camera Operation

After reboot:

```bash
rpicam-hello -t 0 --autofocus-mode continuous
```

You should see a camera preview window with continuous autofocus.

If there are issues, check the CSI camera bus:

```bash
dmesg | grep -i csi
```

You can also list video devices:

```bash
v4l2-ctl --list-devices
```

---

## 5. ReSpeaker 4-Mic Array (Mic + LED Ring) – Drivers & Permissions

This section covers:

* Ensuring ALSA sees the ReSpeaker device.
* Granting group/udev permissions so the **microphone and LED ring** can be used without `sudo`.

### 5.1 Verify the Device in ALSA

List available audio capture devices:

```bash
arecord -l
```

You should see a device similar to:

```
card 1: seeed4micvoicec [seeed-4mic-voicecard], device 0: ...
```

### 5.2 (Optional) Set Default ALSA Device

Edit `/etc/asound.conf`:

```bash
sudo nano /etc/asound.conf
```

Example contents:

```text
defaults.pcm.card 1
defaults.ctl.card 1
```

Restart PulseAudio:

```bash
pulseaudio -k
pulseaudio --start
```

This helps make the ReSpeaker the default input device for ASR.

---

### 5.3 Add User to Relevant Groups

Make sure your user is in the `plugdev`, `audio`, and `dialout` groups:

```bash
sudo usermod -aG plugdev $USER
sudo usermod -aG audio $USER
sudo usermod -aG dialout $USER
sudo reboot
```

---

### 5.4 Create udev Rule for ReSpeaker USB Device (Mic + LED Ring)

1. **Find the USB IDs**:

   ```bash
   lsusb
   ```

   The ReSpeaker device will look like:

   ```text
   Bus 001 Device 004: ID CCCC:DDDD SEEED ReSpeaker 4 Mic Array
   ```

   Here:

   * `CCCC` = `idVendor`
   * `DDDD` = `idProduct`

2. **Create udev rule**:

   ```bash
   sudo tee /etc/udev/rules.d/99-respeaker.rules >/dev/null << 'EOF'
   SUBSYSTEM=="usb", ATTRS{idVendor}=="CCCC", ATTRS{idProduct}=="DDDD", MODE="0666", GROUP="plugdev"
   EOF
   ```

   Replace `CCCC` and `DDDD` with the actual values you saw from `lsusb`.

3. **Reload udev rules**:

   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

4. **Re-add user groups (if needed) and reboot**:

   ```bash
   sudo usermod -aG plugdev $USER
   sudo usermod -aG audio $USER
   sudo usermod -aG dialout $USER

   sudo reboot
   ```

After reboot, the ReSpeaker microphone and LED ring should be accessible without `sudo`.

---

### 5.5 Quick LED Test (Requires `pixel-ring` in `asr_venv`)

Activate your ASR virtual environment:

```bash
source ~/asr_venv/bin/activate
```

Run this inline Python test:

```bash
python3 - << "EOF"
from time import sleep
from pixel_ring import pixel_ring

print("LED ON (listen mode) for 2 seconds...")
pixel_ring.set_brightness(16)
pixel_ring.listen()
sleep(2)

print("LED OFF for 2 seconds...")
pixel_ring.off()
sleep(2)

print("LED THINK mode for 2 seconds...")
pixel_ring.think()
sleep(2)

pixel_ring.off()
print("LED test complete.")
EOF
```

If the udev rule and groups are correct, the LED ring will change patterns without requiring `sudo`.

---

## 6. Camera & Motor Diagnostics (Optional but Recommended)

### 6.1 USB Devices

List all USB devices to check that ReSpeaker and OpenCM9.04 are seen by the system:

```bash
lsusb
```

### 6.2 Serial Ports (for OpenCM9.04 / Dynamixels)

```bash
ls /dev/tty*
```

Typical devices include `/dev/ttyACM0` or `/dev/ttyUSB0` for OpenCM9.04.
You should be able to access them without `sudo` after joining the `dialout` group.

### 6.3 Video Devices (Camera)

```bash
v4l2-ctl --list-devices
```

This helps confirm that the CSI camera or any USB cameras are registered and available.

---

## 7. How These Drivers & Permissions Are Used (Context)

These device drivers and permissions are required by the ROS2 nodes that:

* Capture audio from the **ReSpeaker 4-Mic Array** and feed it to Vosk ASR.
* Control the **LED ring** for ASR listening/idle indicators.
* Send commands to the **OpenCM9.04** to drive the Dynamixel motors.
* Bridge between ASR/LLM/TTS while muting/unmuting ASR correctly.

In the MakiMate project, key ROS2 nodes include:

* `respeaker_vosk_asr.py` – microphone → Vosk ASR → ROS topics (requires audio and ReSpeaker access) 
* `asr_led_node.py` – controls ReSpeaker LED ring based on ASR enable state (requires USB + `pixel_ring` access) 
* `simple_tts_node.py` – uses TTS and toggles ASR enable/disable via `/asr/enable` topic. 
* `llm_bridge_node.py` – sends ASR text to an external LLM server and streams responses back into ROS (works together with the TTS and ASR nodes). 

Correct hardware drivers and permissions are necessary for these nodes to run reliably without `sudo`.

---

## 🧭 Navigation

🔙 Back to Main Documentation
➡️ [`../../README.md`](Overall_README.md)

