# Startup_README.md

> **What this is:**
> This is the **cut-throat setup guide** for MakiMate.
> Follow this from top to bottom to go from a **fresh Raspberry Pi 5 + Ubuntu 24.04** to **Maki running ROS 2, ASR, TTS, and vision**.
>
> All details (mechanical, wiring, LLM hosting, etc.) live in other READMEs – this file just tells you **what to do, in what order.**

---

## 0. Prerequisites (Hardware + Other Machines)

* **Robot hardware fully assembled**

  * Servos mounted and wired per **Mechanical_README** / **Electrical_README**
  * OpenCM9.04 flashed and wired
  * 2" speaker + USB DAC wired and working
* **Raspberry Pi 5**

  * Active cooling recommended
  * Official Raspberry Pi Camera (CSI)
  * ReSpeaker 4-Mic USB Array
* **Separate Windows PC** (optional but recommended)

  * Will host the local LLM using **Ollama + Qwen 2.5 7B Instruct**, see **LLM_Hosting_README.md**

Everything below is run on the **Pi 5** unless stated otherwise.

---

## 1. Flash & Boot Ubuntu 24.04 on the Pi 5

1. On another computer, open **Raspberry Pi Imager**.
2. OS:
   `Other general-purpose OS → Ubuntu 24.04 LTS (64-bit, Official Canonical)`
3. Select your SD card and flash.
4. Insert SD in Pi, connect:

   * HDMI or a **dummy HDMI plug**
   * Keyboard + mouse (or plan to SSH)
5. On first boot:

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## 2. Core System Packages

Install generic tools, Python, audio, USB/camera utils:

```bash
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

---

## 3. Install ROS 2 Jazzy (Desktop)

1. Enable extra repos:

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository restricted
sudo add-apt-repository multiverse
```

2. Add ROS 2 key + repo:

```bash
sudo apt install -y curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu noble main" \
| sudo tee /etc/apt/sources.list.d/ros2.list
```

3. Install ROS Jazzy desktop + extras:

```bash
sudo apt update
sudo apt install -y ros-jazzy-desktop \
    python3-colcon-common-extensions \
    ros-jazzy-cv-bridge \
    ros-jazzy-image-transport \
    ros-jazzy-rmw-fastrtps-cpp
```

4. Source ROS in every shell:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 4. Clone MakiMate Repo

```bash
cd ~
git clone https://github.com/Intelligent-Robotics-Lab/MakiMate.git
cd ~/MakiMate
```

---

## 5. Create ASR Virtual Environment

Install venv support:

```bash
sudo apt install -y python3.12-venv python3.12-full
```

Create `asr_venv`:

```bash
cd ~
python3 -m venv asr_venv
source ~/asr_venv/bin/activate
pip install --upgrade pip
```

Install ASR/TTS helper libraries:

```bash
pip install vosk sounddevice pyttsx3 requests pixel-ring
```

(We keep `pyttsx3` for legacy; **natural_tts** uses Piper instead.)

Deactivate:

```bash
deactivate
```

---

## 6. Install Hardware Libraries + Permissions

### 6.1 Dynamixel SDK + PortAudio

```bash
source ~/asr_venv/bin/activate
pip install setuptools
pip install PyYAML
deactivate

sudo apt install -y ros-jazzy-dynamixel-sdk
sudo apt install -y libportaudio2 libportaudiocpp0 portaudio19-dev
chmod +x /home/makimate/MakiMate/piper_bin/piper/piper
```

### 6.2 Add User to Hardware Groups

```bash
sudo usermod -aG dialout,audio,video,plugdev $(whoami)
sudo reboot
```

After reboot, your user can access:

* `/dev/tty*` (OpenCM / Dynamixels)
* Audio devices
* Camera
* USB (ReSpeaker LED ring)

Full details: **Drivers_Firmware_README.md**

---

## 7. Install Vosk ASR Model

```bash
mkdir -p ~/vosk_models
cd ~/vosk_models

wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
sudo apt install -y unzip
unzip vosk-model-small-en-us-0.15.zip
```

Resulting folder path (used later):

```text
/home/makimate/vosk_models/vosk-model-small-en-us-0.15
```

---

## 8. Configure Audio Input (ReSpeaker)

List capture devices:

```bash
arecord -l
```

If you want ReSpeaker as default ALSA device:

```bash
sudo nano /etc/asound.conf
```

Example:

```text
defaults.pcm.card 1
defaults.ctl.card 1
```

Restart PulseAudio:

```bash
pulseaudio -k
pulseaudio --start
```

### ReSpeaker LED permissions (one-time)

```bash
sudo usermod -aG plugdev $USER
sudo usermod -aG audio $USER
sudo usermod -aG dialout $USER
sudo reboot
```

Then create a udev rule (after checking `lsusb` for the actual IDs):

```bash
lsusb   # find ReSpeaker line: ID CCCC:DDDD ...
sudo tee /etc/udev/rules.d/99-respeaker.rules >/dev/null << 'EOF'
SUBSYSTEM=="usb", ATTRS{idVendor}=="CCCC", ATTRS{idProduct}=="DDDD", MODE="0666", GROUP="plugdev"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
```

Replace `CCCC` and `DDDD` with your IDs.

You can test the LED ring later from **Drivers_Firmware_README.md**.

---

## 9. Enable & Configure Raspberry Pi Camera

Maki uses the Pi 5 CSI camera with the **libcamera / rpicam** stack.

### 9.1 Apply System Configs + Camera Info Manager

```bash
cd ~/MakiMate/system_configs
./install_configs.sh
sudo apt install -y ros-jazzy-camera-info-manager
sudo reboot
```

This edits `/boot/firmware/config.txt` appropriately.

### 9.2 Build libcamera (RPi fork) + rpicam-apps

You only do this because `rpicam-apps` isn’t in Ubuntu 24.04 repos yet.

#### Check if `rpicam-apps` exists (optional):

```bash
sudo apt update
apt-cache policy rpicam-apps
# If Candidate: (none) → build from source
```

#### Install build dependencies:

```bash
sudo apt full-upgrade -y

sudo apt install -y git python3-pip python3-jinja2 meson cmake ninja-build build-essential

sudo apt install -y libboost-dev libgnutls28-dev openssl libtiff5-dev pybind11-dev \
                    python3-yaml python3-ply libglib2.0-dev libgstreamer-plugins-base1.0-dev

sudo apt install -y libboost-program-options-dev libdrm-dev libexif-dev \
                    libepoxy-dev libjpeg-dev libtiff5-dev libpng-dev

sudo apt install -y qtbase5-dev libqt5core5a libqt5gui5 libqt5widgets5
sudo apt install -y v4l-utils
```

#### Build libcamera:

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
cd ~
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
cd ~
```

Reboot:

```bash
sudo reboot
```

### 9.3 Verify Camera

```bash
rpicam-hello -t 0 --autofocus-mode continuous
```

You should see a live preview.

If not, check:

```bash
dmesg | grep -i csi
v4l2-ctl --list-devices
```

---

## 10. Install Piper Binaries & Udev Rules

Piper is the neural TTS backend used by **natural_tts_node**.

```bash
cd ~/MakiMate/piper_bin
./install_piper.py
```

This:

* Installs the `piper` binary
* Installs any udev rules (e.g., Dynamixel) found under `system_configs/udev/`

Piper models (e.g., `en_US-john-medium.onnx`) should already be under:

```text
~/MakiMate/piper_models/
```

Natural TTS uses this path:

```text
/home/makimate/MakiMate/piper_models/en_US-john-medium.onnx
```

---

## 11. Set Motor Hardware Limits (Safety)

Use **Electrical_README.md** / **Drivers_Firmware_README.md** for the full procedure.

High-level steps:

1. Connect OpenCM9.04 to a laptop running **Dynamixel Wizard 2.0**.
2. For each motor ID (1–6), find **min** and **max** mechanical ticks.
3. Record those and update:

```bash
nano ~/MakiMate/src/makimate_dxl/makimate_dxl/maki_dxl_6.py
```

In the `ROBOT_LIMITS` dict:

```python
ROBOT_LIMITS = {
    1: {"min": 2640, "max": 3641},  # neck_yaw
    2: {"min": 1855, "max": 2324},  # neck_pitch
    3: {"min": 2352, "max": 2635},  # eyes_pitch
    4: {"min": 1679, "max": 2495},  # eyes_yaw
    5: {"min": 2378, "max": 3057},  # lid_left
    6: {"min": 1021, "max": 1699},  # lid_right
}
```

Replace with **your measured values**. These limits clamp all commanded motion and protect the hardware.

---

## 12. Build the ROS 2 Workspace

```bash
cd ~/MakiMate
colcon build
```

After each code change, re-run `colcon build` and then:

```bash
source install/setup.bash
```

You can add this to your `.bashrc` if you like:

```bash
echo "source ~/MakiMate/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 13. Configure LLM Bridge (Link to Windows LLM Host)

On the **Windows PC**, follow **LLM_Hosting_README.md** to:

* Install **Ollama**
* Pull **`qwen2.5:7b-instruct`**
* Set up a Python venv
* Run `start_server_llm.bat` so the FastAPI server is listening on a port (e.g., `http://192.168.X.Y:8000`)

On the **Pi**, edit:

```bash
nano ~/MakiMate/src/makimate_asr/makimate_asr/llm_bridge_node.py
```

Set `laptop_host` to your Windows machine’s IP:

```python
self.declare_parameter("laptop_host", "http://192.168.X.Y:8000")
self.declare_parameter("endpoint_path", "/chat/stream")
```

Later, when running, LLMBridge will connect to this URL.

---

## 14. Quick Component Tests

### 14.1 ASR Test (ReSpeaker + Vosk)

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source ~/asr_venv/bin/activate
source install/setup.bash

python -m makimate_asr.respeaker_vosk_asr \
  --ros-args \
    -p sample_rate:=16000.0 \
    -p device:=2 \
    -p model_path:=/home/makimate/vosk_models/vosk-model-small-en-us-0.15 \
    -p publish_llm:=false \
    -p asr_topic:=/asr/text \
    -p llm_request_topic:=/llm/request \
    -p enable_topic:=/asr/enable
```

In another terminal, you can echo:

```bash
ros2 topic echo /asr/text
```

Speak into the mic; you should see transcribed text.

---

### 14.2 TTS Test (Natural TTS + Piper)

Terminal A:

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run makimate_asr natural_tts_node \
  --ros-args \
    -p backend:=piper_python \
    -p piper_model:="/home/makimate/MakiMate/piper_models/en_US-john-medium.onnx" \
    -p input_topic:="/tts/text"
```

Terminal B:

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 topic pub /tts/text std_msgs/msg/String \
  "data: 'Hello, I am Maki speaking with Piper TTS.'"
```

You should hear the **Piper “John” voice** from the internal speaker.
`natural_tts_node` **fully replaces** the old `simple_tts_node` (kept only for reference).

---

### 14.3 Camera Test

Terminal A:

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run camera_ros camera_node \
  --ros-args \
    -p camera:=0 \
    -p role:=video \
    -p sensor_mode:='640:480' \
    -p width:=640 \
    -p height:=480 \
    -p format:=BGR888
```

Terminal B (GUI):

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source install/setup.bash
rqt
```

Use `rqt_image_view` to view `/camera/image_raw`.

---

### 14.4 Motor + Expressions Test

Terminal A:

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run makimate_dxl maki_dxl_6
```

Terminal B:

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run makimate_dxl maki_expressions
```

Terminal C:

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 topic pub --once /maki/expression std_msgs/msg/String "data: 'wide_awake'"
```

Maki should move into the “wide_awake” pose.

---

## 15. Run Operational Modes

Each mode is a different combination of the same building blocks.

> Always make sure you’ve run `colcon build` and sourced `install/setup.bash` after any changes.

### 15.1 Presentation Mode (Recommended first full test)

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch maki_operational_nodes presentation_mode.launch.py
```

What you should see:

* Maki starts in a **sleep** posture.
* Wake word (e.g., “hello”) → Maki wakes up, greets, ASR+LLM+TTS loop starts.
* Sleep phrase (e.g., “goodbye”) → Maki says farewell and returns to sleep.

### 15.2 Demo Mode (vision + motion only)

```bash
ros2 launch maki_operational_nodes demo_mode.launch.py
```

* Face tracking, idle scanning, blinking.
* No ASR/LLM/TTS required.

### 15.3 Full Feature Mode (WIP)

```bash
ros2 launch maki_operational_nodes full_feature_mode.launch.py
```

* Intended “everything on” mode (ASR, LLM, TTS, motion, vision).
* Still under development – expect tweaks.

---

## 16. Optional: Docker Deployment

If you want to containerize the whole environment:

```bash
docker build -t makimate:latest ~/MakiMate
```

Run:

```bash
docker run --rm -it \
  --net=host \
  --privileged \
  -v /dev:/dev \
  -v ~/vosk_models:/home/makimate/vosk_models \
  -v ~/MakiMate/piper_models:/home/makimate/MakiMate/piper_models \
  -v ~/MakiMate/piper_bin:/home/makimate/MakiMate/piper_bin \
  makimate:latest
```

This is optional and not required for normal operation.

---

## 17. Final Reboot & One-Command Run

Reboot one last time:

```bash
sudo reboot
```

Then, for a full system check:

```bash
cd ~/MakiMate
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch maki_operational_nodes presentation_mode.launch.py
```

You should now have:

* Face tracking
* Wake/sleep behavior
* Local ASR (Vosk)
* Neural TTS (Piper “John” via `natural_tts_node`)
* LLM responses streamed from your Windows host
* Dynamixel motion + behaviors

At this point, **Maki is fully alive**.

---

## 🧭 Navigation

🔙 Back to Main Documentation
➡️ [`../../README.md`](Overall_README.md)
