# **ROS2_README.md**

### *MakiMate ROS 2 Architecture, Nodes, Modes, and System Overview*

*(Raspberry Pi 5 – Ubuntu 24.04 – ROS 2 Jazzy)*

---

# **1. Introduction**

This README explains how **all ROS 2 components of MakiMate work together** across:

* **Audio / ASR / LLM / TTS stack**
* **Camera / Vision / Face tracking**
* **Motors / Expressions / Behavior**
* **System orchestration via operational modes**

The goal is to provide one clean, readable reference showing **how the full robot architecture is structured and how each ROS 2 node contributes to Maki’s functionality**.

---

# **2. ROS 2 Installation Summary (Jazzy on Ubuntu 24.04 – Pi 5)**

Install ROS 2 dependencies:

```bash
sudo apt install -y \
    git curl wget htop net-tools unzip \
    python3-pip python3-venv python3-dev build-essential \
    ffmpeg pulseaudio v4l-utils usbutils
```

Add repositories:

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository restricted
sudo add-apt-repository multiverse
```

Add ROS key + repo:

```bash
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu noble main" |
sudo tee /etc/apt/sources.list.d/ros2.list
```

Install ROS 2 Desktop + extras:

```bash
sudo apt update
sudo apt install -y ros-jazzy-desktop python3-colcon-common-extensions \
    ros-jazzy-cv-bridge ros-jazzy-image-transport ros-jazzy-rmw-fastrtps-cpp
```

Auto-source on every shell:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

# **3. Repository Structure Overview**

```
MakiMate/
│
├── camera_ros/               → Camera drivers + launch files
├── makimate_vision/          → Face tracking + pixel→servo mapping
├── makimate_asr/             → ASR, LED ring control, TTS, AI router
├── server_llm/               → Bridge to external LLM server
├── makimate_dxl/             → Motors, expressions, behavior
└── maki_operational_nodes/   → Launch files for demo/presentation/full modes
```

Each subsystem is modular, communicating only through ROS topics, making the architecture robust, extensible, and debuggable.

---

# **4. High-Level System Architecture**

Below is the **full data flow** integrating audio, AI, vision, and motion:

```
                    ┌─────────────────────────┐
                    │  Microphone (ReSpeaker) │
                    └──────────┬──────────────┘
                               │ audio stream
                               ▼
                    ┌─────────────────────────┐
                    │  respeaker_vosk_asr.py  │
                    │  (Speech-to-Text, Vosk) │
                    └──────────┬──────────────┘
                               │ /asr/text
                               ▼
             ┌───────────────────────────┐
             │    ai_command_router.py   │
             │ wake/sleep, routing to AI │
             └──────────┬──────────┬─────┘
                        │          │ /llm/request
        /maki/awake     │          ▼
                        ▼   ┌──────────────────────┐
           (robot state)    │   llm_bridge_node.py │
                             │  ROS ↔ LLM (HTTP)   │
                             └───────┬─────────────┘
                                     │ streamed tokens
                                     ▼
                      ┌─────────────────────────────┐
                      │      natural_tts_node.py     │
                      │   Piper TTS + ASR muting     │
                      └──────────┬───────────────────┘
                                 │ audio out
                                 ▼
                           SPEAKER OUTPUT
```

And the VISION → MOTOR pipeline:

```
                   CAMERA ROS NODE
                   /camera/image_raw
                               │
                               ▼
                     face_tracker_node.py
                     (detect face center)
                               │
                               ▼
                       face_to_maki.py
               (pixel position → yaw/pitch error)
                               │
                               ▼
                       maki_behavior.py
           (face tracking, idle scan, blinking)
                               │
                               ▼
              maki_expressions.py + expressions.yaml
                               │
                               ▼
                         maki_dxl_6.py
                     (Dynamixel motor driver)
```

---

# **5. ROS 2 Packages and Nodes**

## **5.1 Camera Package — `camera_ros`**

### **camera.launch.py**

Starts the Pi camera driver and publishes:

* `/camera/image_raw`
* `/camera/camera_info`

This provides the raw frames used by face tracking.

---

## **5.2 Vision Package — `makimate_vision`**

### **face_tracker_node.py**

* Subscribes to the camera feed.
* Performs face detection (OpenCV/DNN).
* Publishes:

  * Face bounding boxes
  * Normalized center offsets
  * Optional debug image

### **face_to_maki.py**

* Converts pixel-based face offsets into:

  * Angular yaw/pitch corrections
  * OR behavior commands
* Publishes to behavior/motor layer.

This is the bridge that lets Maki turn its head toward faces.

---

## **5.3 Motor / Motion Package — `makimate_dxl`**

### **maki_dxl_6.py**

Low-level driver for **6 Dynamixel servos**:

* Opens serial port
* Handles torque, limits, safety
* Subscribes to `/maki/joint_goals`
* Publishes current joint states

### **expressions.yaml**

A dictionary of **robot poses**, each listing 6 joint angles:

```yaml
wide_awake:
  joints: [0, -8, 8, 0, 18, -18]
sleepy:
  joints: [0, 18, 10, 0, -19, 25]
```

### **maki_expressions.py**

* Loads `expressions.yaml`
* Subscribes to `/maki/expression`
* Publishes `/maki/joint_goals`

This is the **pose lookup system**.

### **maki_behavior.py**

The motion "brain":

* Tracks face when available
* Performs idle scanning when alone
* Initiates blinking
* Switches poses on awake/sleep
* Publishes joint goals

### Utility tools

* `clear_hw_error.py`
* `dxl_dump_limits.py`
* `dxl_voltage_debug.py`

---

## **5.4 Speech + AI Package — `makimate_asr`**

### **respeaker_vosk_asr.py**

Microphone → Speech-to-Text:

* Vosk offline ASR model
* Publishes `/asr/text`
* Mutes when `/asr/enable=False`

### **asr_led_node.py**

Controls LED ring:

* `/asr/enable=True` → listening animation
* `/asr/enable=False` → LEDs off

### **ai_command_router.py**

Handles natural-language robot control:

* Wake word → `/maki/awake=True`
* Sleep phrase → `/maki/awake=False`
* Routes normal speech to `/llm/request`
* Prevents interaction while asleep

### **natural_tts_node.py**

Piper neural TTS:

* Subscribes to `/llm/stream`
* Publishes `/asr/enable=False` while speaking
* Re-enables ASR after finishing

### **simple_tts_node.py**

Legacy pyttsx3 version (fallback).

---

## **5.5 LLM Bridge Package — `server_llm`**

### **llm_bridge_node.py**

Connects ROS 2 to the external LLM (FastAPI server on laptop):

* Sends `/llm/request` → HTTP POST
* Streams responses → `/llm/stream`
* Publishes final answer → `/llm/response`
* Disables ASR while LLM is generating
* Loads the system prompt on startup

---

# **6. Operational Modes — `maki_operational_nodes`**

MakiMate has **three modes**, each defined by a launch file.

---

## **6.1 Demo Mode — `demo_mode.launch.py`**

Purpose: **Face tracking + expressive motion only**
(No speech, no ASR, no LLM)

Starts:

* camera node
* face tracker
* face→maki converter
* motor driver
* expression server
* behavior engine

Use case: silent demonstrations.

---

## **6.2 Presentation Mode — `presentation_mode.launch.py`**

Purpose: A **stable, predictable, stage-friendly interaction mode**.

Starts:

* ASR
* LLM bridge
* TTS
* LED ring
* Behavior
* Camera (optional)

Features:

* Wake/sleep interaction
* Conversational Q&A
* Limited head movement

---

## **6.3 Full Feature Mode — `full_feature_mode.launch.py` (WIP)**

Purpose: **Enable ALL robotic capabilities** simultaneously.

Includes:

* Full ASR pipeline
* LLM streaming
* Piper TTS
* Face tracking
* Full behavior engine
* Dynamic gestures
* All camera + motor systems

This will be the final complete user-facing mode.

---

# **7. Behavior System Overview**

Components:

| Layer      | Node                   | Purpose                                  |
| ---------- | ---------------------- | ---------------------------------------- |
| High-Level | `ai_command_router.py` | Sleep/wake → behavior control            |
| Behavior   | `maki_behavior.py`     | Face tracking, idle scanning, blinking   |
| Expression | `maki_expressions.py`  | Converts expression names → joint arrays |
| Motor      | `maki_dxl_6.py`        | Sends commands to Dynamixels             |

The behavior pipeline:

```
face tracker → face_to_maki → maki_behavior → maki_expressions → maki_dxl_6
```

---

# **8. End-to-End Conversation Loop**

A full interaction works like this:

1. **ASR enabled** → LED ring ON
2. User speaks
3. Vosk ASR publishes `/asr/text`
4. ai_command_router determines:

   * wake/sleep?
   * forward to `/llm/request`?
5. llm_bridge_node streams answer:

   * Disables ASR
   * Sends streaming tokens to `/llm/stream`
6. natural_tts_node converts stream to speech
7. After TTS finishes → re-enables ASR
8. Loop repeats

This ensures **natural, hands-free interaction**.

---

# **9. End-to-End Vision → Motion Loop**

1. Camera publishes frames
2. face_tracker_node detects people
3. face_to_maki computes angular offsets
4. maki_behavior decides:

   * Face tracking?
   * Idle scanning?
   * Blink?
5. maki_expressions produces joint arrays
6. maki_dxl_6 sends commands to motors

This results in **smooth, expressive, life-like motion**.

---

# **10. Diagram Summary**

### Audio/LLM/TTS System

```
Mic → ASR → Command Router → LLM Bridge → TTS → Speaker
```

### Vision/Motion System

```
Camera → Face Tracking → Control Mapping → Behavior → Expressions → Motors
```

### Mode System

```
demo / presentation / full_feature
          |
          → spawns appropriate nodes
```

---

# **11. Summary**

MakiMate’s ROS 2 architecture creates a **modular, layered robot system**:

* **ROS 2** handles message-passing and modularity
* **ASR + LLM + TTS** provide natural voice interaction
* **Vision + behavior engine** provides natural motion
* **Dynamixel control** provides smooth expressive movement
* **Launch modes** control robotic complexity based on environment

This README serves as the **central documentation for understanding how every ROS 2 component works together**.

---

## 🧭 Navigation

🔙 Back to Main Documentation
➡️ [`../../README.md`](Overall_README.md)
