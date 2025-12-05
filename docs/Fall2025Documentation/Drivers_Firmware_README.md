# **Drivers_Firmware_README.md**

This document contains all instructions related to **drivers**, **firmware**, and **device permissions** for:

* The Raspberry Pi Camera
* Dynamixel motors (via OpenCM9.04)
* The ReSpeaker 4-Mic Array (microphone + LED ring)
* And how these hardware access layers support the full ROS2 audio + vision + motor stack.

This file is intended to be used **directly as a README**, with no additional editing required.

---

# **1. System-Level Device & Driver Packages**

Install core system tools and hardware utilities needed for camera, USB, audio, and firmware operations:

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

These tools provide:

* **v4l-utils** → camera debugging and device listing
* **usbutils** → identify USB devices (`lsusb`)
* **pulseaudio** → audio routing for ASR/TTS
* Build tools → required for building `libcamera` + `rpicam-apps`

---

# **2. User & Group Permissions for Hardware Access**

Grant your user full access to:

* Serial ports (Dynamixel)
* Audio devices (ReSpeaker)
* Video devices (camera)
* USB devices (ReSpeaker LED ring, OpenCM)

```bash
sudo usermod -aG dialout,audio,video,plugdev $(whoami)
sudo reboot
```

Required so that:

* **OpenCM9.04** appears as `/dev/ttyACM*` and is usable without `sudo`
* **ReSpeaker microphone + LED ring** work inside the ASR/TTS pipeline
* **Raspberry Pi camera** nodes can access `/dev/video*` or libcamera backend

---

# **3. Dynamixel Motors (OpenCM9.04) – Firmware & Driver Setup**

### 3.1 Install Dynamixel SDK + supporting libraries

```bash
source ~/asr_venv/bin/activate

pip install setuptools
pip install PyYAML

deactivate

sudo apt install -y ros-jazzy-dynamixel-sdk
sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev
chmod +x /home/makimate/MakiMate/piper_bin/piper
```

### 3.2 Udev Rules for Dynamixel

If `system_configs/udev/99-dynamixel.rules` is included in the repo, run:

```bash
cd ~/MakiMate/piper_bin
./install_piper.py
```

This:

* Installs Piper TTS
* Installs udev rules (Dynamixel + ReSpeaker if applicable)
* Ensures OpenCM9.04 is readable without `sudo`

---

# **4. Raspberry Pi Camera – Firmware & Tools (Pi 5 + Ubuntu 24.04)**

Raspberry Pi 5 uses the **libcamera / rpicam** pipeline.
You MUST enable the camera via config files and manually install `rpicam-apps`.

### 4.1 Apply system camera configs and install ROS camera manager:

```bash
cd ~/MakiMate/system_configs
./install_configs.sh
sudo apt install ros-jazzy-camera-info-manager
sudo reboot
```

### 4.2 Build & Install `libcamera` and `rpicam-apps` (manual method)

Ubuntu 24.04 usually does **not** provide `rpicam-apps`.
You must build them from source — the commands below do exactly that.

#### Check if `rpicam-apps` exists:

```bash
sudo apt update
apt-cache policy rpicam-apps
```

If no candidate exists → proceed with manual build.

#### Install build dependencies:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y git python3-pip python3-jinja2 meson cmake ninja-build build-essential
sudo apt install -y libboost-dev libgnutls28-dev openssl libtiff5-dev pybind11-dev \
                    python3-yaml python3-ply libglib2.0-dev libgstreamer-plugins-base1.0-dev
sudo apt install -y libboost-program-options-dev libdrm-dev libexif-dev \
                    libepoxy-dev libjpeg-dev libtiff5-dev libpng-dev
sudo apt install -y qtbase5-dev libqt5core5a libqt5gui5 libqt5widgets5
sudo apt install -y v4l-utils
```

#### Build libcamera (Raspberry Pi fork):

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

ninja -C build
sudo ninja -C build install
```

#### Build rpicam-apps:

```bash
cd ~
git clone https://github.com/raspberrypi/rpicam-apps.git
cd rpicam-apps

meson setup build \
  -Denable_libav=disabled \
  -Denable_drm=enabled \
  -Denable_egl=enabled \
  -Denable_qt=enabled \
  -Denable_opencv=disabled \
  -Denable_tflite=disabled \
  -Denable_hailo=disabled

meson compile -C build
sudo meson install -C build
sudo ldconfig
```

### 4.3 Test camera:

```bash
rpicam-hello -t 0 --autofocus-mode continuous
```

---

# **5. ReSpeaker 4-Mic Array – Audio + LED Ring Permissions**

### 5.1 Verify via ALSA

```bash
arecord -l
```

You should see:

```
card 1: seeed4micvoicec ...
```

### 5.2 Optional: set default audio device

```bash
sudo nano /etc/asound.conf
```

Example:

```
defaults.pcm.card 1
defaults.ctl.card 1
```

Restart:

```bash
pulseaudio -k
pulseaudio --start
```

### 5.3 Required groups

```bash
sudo usermod -aG plugdev $USER
sudo usermod -aG audio $USER
sudo usermod -aG dialout $USER
sudo reboot
```

### 5.4 Udev rule for LED ring control

Find device:

```bash
lsusb
```

Add rule:

```bash
sudo tee /etc/udev/rules.d/99-respeaker.rules >/dev/null << 'EOF'
SUBSYSTEM=="usb", ATTRS{idVendor}=="CCCC", ATTRS{idProduct}=="DDDD", MODE="0666", GROUP="plugdev"
EOF
```

Reload:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 5.5 LED ring test

```bash
source ~/asr_venv/bin/activate

python3 - << "EOF"
from time import sleep
from pixel_ring import pixel_ring

pixel_ring.set_brightness(16)
pixel_ring.listen()
sleep(2)

pixel_ring.off()
sleep(2)

pixel_ring.think()
sleep(2)

pixel_ring.off()
EOF
```

---

# **6. How These Drivers Support the ROS2 Pipeline**

These low-level drivers & permissions enable the following ROS2 nodes to function correctly:

### **Audio / ASR**

* `respeaker_vosk_asr.py`
* `asr_led_node.py`

### **Motors**

* `maki_dxl_6.py`
* `maki_expressions.py`
* `maki_behavior.py`

### **LLM Integration**

* `llm_bridge_node.py`

### **TTS (IMPORTANT UPDATE)**

## **Natural TTS (`natural_tts.py`) — NEW PRIMARY TTS SYSTEM**

Natural TTS:

* Uses the **Piper TTS engine** (GPU/CPU-optimized ONNX runtime)
* Uses the **en_US-john-medium.onnx** voice model
  (Your default production-quality voice)
* Provides **streaming speech**, meaning TTS begins speaking before the LLM finishes sending text
* Publishes to `/asr/enable` to **mute ASR while speaking**, preventing echo/re-recognition
* Is faster, clearer, and more natural than pyttsx3

### **Simple TTS (`simple_tts_node.py`) — OBSOLETE**

The legacy Simple TTS node:

* Used `pyttsx3`
* Spoke only final answers (no streaming)
* Produced robotic, low-quality audio

It is now:

> **Completely replaced by Natural TTS**
> **Kept only for documentation and fallback purposes**

Natural TTS is the **only recommended and supported TTS path** moving forward.

### Hardware interaction (TTS pipeline)

Natural TTS requires:

* Working **audio output**
* Working **ASR enable/disable** permission to mute listening
* No root access (all handled via group/udev settings above)

---

# **7. Diagnostics**

Useful debugging commands for camera, motors, and USB devices:

### USB devices:

```bash
lsusb
```

### Serial ports:

```bash
ls /dev/tty*
```

### Video devices:

```bash
v4l2-ctl --list-devices
```

---

# **8. How the Firmware + Drivers Enable the Full Robot Stack**

These hardware capabilities unlock the ROS2 functionality:

| Hardware               | ROS Nodes That Depend On It | Purpose                        |
| ---------------------- | --------------------------- | ------------------------------ |
| ReSpeaker Microphone   | `respeaker_vosk_asr.py`     | Voice input                    |
| ReSpeaker LED Ring     | `asr_led_node.py`           | Listening indicator            |
| ReSpeaker Output Audio | `natural_tts.py`            | High-quality streaming TTS     |
| OpenCM9.04 Servo Bus   | `maki_dxl_6.py`             | Neck, eyelid, and eye movement |
| Pi Camera              | `face_tracker_node.py`      | Face detection for interaction |
| USB Permissions        | All of the above            | Runs without `sudo`            |

Natural TTS integrates tightly with:

* `llm_bridge_node.py` (streaming text)
* `/asr/enable` (ASR mute signal)
* The Piper binary installed in `piper_bin/`

---

# **🧭 Navigation**

🔙 Back to Main Documentation
➡️ [`../../README.md`](Overall_README.md)
