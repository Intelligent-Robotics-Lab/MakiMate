# 🤖 MakiMate

**MakiMate** is a cross-platform **ROS 2 Jazzy** codebase tailored for the **Maki robot**, which runs on **Ubuntu ARM64**. It enables seamless development, testing, and deployment of robot software on **Windows**, **Linux**, or **macOS** using **Docker**, ensuring a unified environment regardless of your development machine.

---

## 🧭 Overview

MakiMate empowers developers to:
- Write and test ROS 2 code locally without complex setup.
- Build Docker images compatible with **Maki’s Ubuntu ARM64** and desktop systems.
- Push/pull consistent environments via **GitHub Container Registry (GHCR)**.
- Contribute modular components like packages, interfaces, and hardware drivers.

---

## 🧩 Project Goals

- 🧠 **Cross-platform development**: Program Maki from Windows, Linux, or macOS.
- ⚙️ **Unified ROS 2 environment**: Consistent setup for all developers.
- 🚀 **CI/CD-ready**: Streamlined for continuous integration and deployment.
- 🧍‍♂️ **Collaborative codebase**: Modular features for team contributions.

---

## 🏗️ Project Structure

```
MakiMate/
├── LICENSE                     # Project license file
├── README.md                   # This file
├── deploy/                     # Deployment scripts/configurations
├── docker/                     # Docker configurations
│   ├── base/                   # Base Docker image
│   │   └── Dockerfile
│   └── robot/                  # Maki-specific configurations (Ubuntu ARM64)
│       ├── Dockerfile
│       └── entrypoint.sh
├── docs/                       # Documentation
│   ├── SETUP_WINDOWS.md        # Windows setup guide
│   ├── SETUP_LINUX.md          # Linux setup guide
│   └── SETUP_MACOS.md          # macOS setup guide
├── hw/                         # Hardware-related code
├── interfaces/                 # ROS 2 interfaces (msg, srv, etc.)
└── src/                        # ROS 2 packages
    └── makimate_bringup/
        ├── launch/             # Launch files
        │   └── bringup.launch.py
        ├── makimate_bringup/   # Python package
        │   ├── __init__.py
        │   └── hello.py
        ├── package.xml         # Package manifest
        ├── resource/           # Resource files
        │   └── makimate_bringup
        ├── setup.cfg           # Python package config
        └── setup.py            # Build script
```

---

## ⚙️ Getting Started

The Maki robot runs on **Ubuntu ARM64**, but you can develop for it from **Windows**, **Linux**, or **macOS**. Choose the setup guide for your operating system:
- **Windows**: [docs/SETUP_WINDOWS.md](docs/SETUP_WINDOWS.md)
- **Linux (Ubuntu 22.04/24.04)**: [docs/SETUP_LINUX.md](docs/SETUP_LINUX.md)
- **macOS**: [docs/SETUP_MACOS.md](docs/SETUP_MACOS.md)

Each guide covers:
1. Installing Docker and Git.
2. Cloning the repository.
3. Building the Docker image for Maki’s ARM64 environment.
4. Running the MakiMate environment.
5. Testing ROS 2 nodes.

---

## 🧠 Quick Start (For Experienced Users)

With **Docker** and **Buildx** configured:

```bash
# Clone the repository
git clone https://github.com/pourya-shahverdi/MakiMate.git
cd MakiMate

# Build the development image
docker buildx build . \
  -f docker/robot/Dockerfile \
  --platform linux/amd64 \
  -t makimate:dev \
  --load

# Run the container
docker run --rm -it makimate:dev
```

**Expected Output**:
```
[INFO] [hello_node]: Hello from MakiMate!
```

---

## 🧰 Common Commands

| Action | Command |
|--------|---------|
| Rebuild image | `docker buildx build . -f docker/robot/Dockerfile -t makimate:dev --load` |
| Run container | `docker run -it --entrypoint bash makimate:dev` |
| Run node | `source /opt/ros/jazzy/setup.bash && source /ws/install/setup.bash && ros2 run makimate_bringup hello` |
| Launch nodes | `source /opt/ros/jazzy/setup.bash && source /ws/install/setup.bash && ros2 launch makimate_bringup bringup.launch.py` |

---

## 🐳 Why Docker?

Docker ensures:
- Consistent environments for Maki’s **Ubuntu ARM64** and developer systems.
- Identical builds across Windows, Linux, macOS, and Raspberry Pi.
- No dependency conflicts or manual ROS 2 installation.

---

## 🔖 Versioning

We use semantic versioning:
- `latest`: Latest stable image.
- `v0.1.0`, `v0.2.0`, ...: Tagged release builds.

Images are stored at: [ghcr.io/pourya-shahverdi/makimate](ghcr.io/pourya-shahverdi/makimate).

---

## 🧑‍💻 Contributing

Contributions are welcome! Please:
- Work inside Docker to align with Maki’s Ubuntu ARM64 environment.
- Test builds before pushing.
- Keep commits small and meaningful.
- Follow ROS 2 Python package structure for new nodes.

---

## 🧩 Maintainers

- **Maintainer**: Pourya Shahverdi
- **Lab**: In Real-Life Intelligent Robotics Lab (IRL²), Oakland University
- **Focus**: ROS 2 for social and affective human-robot interaction

---

## 🫶 Need Help?

For support, use one of these options:
- **GitHub Issues**: Open an issue on the [MakiMate GitHub repository](https://github.com/pourya-shahverdi/MakiMate/issues):
  1. Go to the **Issues** tab.
  2. Click **New Issue**.
  3. Provide a clear title (e.g., "Docker Build Error on Windows") and describe your problem, including any error messages or steps to reproduce.
  4. Add labels like `bug`, `question`, or `help wanted` for clarity.
- **Discord**: Reach out to @pourya9698 .

---
