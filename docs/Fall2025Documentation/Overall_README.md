# 🤖 MakiMate — Senior Design Project (Fall 2025)

Welcome to the official documentation for **MakiMate**, a socially-interactive robotic companion developed by the **Oakland University Senior Design Class — Fall 2025**.

MakiMate blends embedded systems, ROS2 software, expressive servo control, and smart sensing to create an engaging robotic experience that interacts with the world around it.

This documentation serves as the centralized hub for system installation, hardware integration, and software deployment.

---

## 📚 Documentation Table of Contents

Select one of the following to explore the respective documentation:

### 0️⃣ BOM
BOM for each subsystem  
➡️ [`BOM_README.md`](BOM_README.md)

### 1️⃣ Ubuntu Setup
Operating system setup, development dependencies, package management  
➡️ [`Ubuntu_README.md`](Ubuntu_README.md)

### 2️⃣ Drivers & Firmware
Dynamixel servo control, sensor interfaces, and microcontroller firmware  
➡️ [`Drivers_Firmware_README.md`](Drivers_Firmware_README.md)

### 3️⃣ ROS 2 & Software Stack
Workspace design, ROS2 packages, launch files, nodes, and behavior logic  
➡️ [`ROS2_README.md`](ROS2_README.md)

### 3.1 Hosting Local LLM On Windows Laptop
Walkthrough on how to open the local LLM on the laptop for the AI functionality
➡️ [`LLM_Hosting_README.md`](LLM_Hosting_README.md)

### 4️⃣ Electrical Hardware
Wiring diagrams, component specifications, power systems  
➡️ [`Electrical_README.md`](Electrical_README.md)

### 5️⃣ Mechanical Hardware
CAD models, assembly instructions, mounting solutions, and part details  
➡️ [`Hardware_README.md`](Hardware_README.md)

### 6️⃣ New PI Setup
Walkthrough guide on how to get the project running on a new Pi from start to finish  
➡️ [`Startup_README.md`](Startup_README.md).

---

## 🧩 Repository Structure

```
📁 MakiMate
|-docs
├── CONTRIBUTION_GUIDE.md
├── Fall 2025 Documentation
│   └── BOM_README.md
│   └── Overall_README.md <----(THIS FILE)
│   └── Drivers_Firmware_README.md
│   └── LLM_HOSTING_README.md
│   └── ROS2_README.md
│   └── Electrical_README.md
│   └── Hardware_README.md
│   └── Startup_README.md
├── SETUP_LINUX.md
├── SETUP_MACOS.md
└── SETUP_WINDOWS.md
|-src
├── camera_ros
│   ├── launch
│   │   └── camera.launch.py
├── maki_operational_nodes
│   ├── launch
│   │   ├── demo_mode.launch.py
│   │   ├── docker_presentation_mode.launch.py
│   │   ├── full_feature_mode.launch.py
│   │   └── presentation_mode.launch.py
│   ├── maki_operational_nodes
│   │   ├── maki_awake_behavior.py
│   │   ├── maki_launch_manager.py
│   │   └── maki_operational_modes.py
├── makimate_asr
│   ├── makimate_asr
│   │   ├── ai_command_router.py
│   │   ├── asr_led_node.py
│   │   ├── natural_tts_node.py
│   │   ├── respeaker_vosk_asr.py
├── makimate_dxl
│   ├── makimate_dxl
│   │   ├── clear_hw_error.py
│   │   ├── dxl_dump_limits.py
│   │   ├── dxl_voltage_debug.py
│   │   ├── expressions.yaml
│   │   ├── maki_behavior.py
│   │   ├── maki_dxl_6.py
│   │   └── maki_expressions.py
├── makimate_vision
│   ├── makimate_vision
│   │   ├── face_to_maki.py
│   │   └── face_tracker_node.py
└── server_llm
    ├── launch
    │   └── llm_bridge.launch.py
    ├── server_llm
    │   ├── llm_bridge_node.py
    │   ├── say.py
    │   └── tty.py
```

---

## 👥 Contributors

Senior Design — Class of Fall 2025  
Faculty Advisor: *Dr. Geoffrey Louie*

---

## 🧭 Navigation

🔙 Back to Main Documentation  
➡️ [`../../README.md`](../../README.md)
