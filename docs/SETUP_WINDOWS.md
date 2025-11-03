# 🧠 MakiMate Setup Guide for Windows

Welcome to **MakiMate**, a cross-platform **ROS 2 Jazzy** codebase for the Maki robot! This guide walks you through setting up a development environment on **Windows 10 (21H2+)** or **Windows 11** using **Docker** and **WSL 2 (Windows Subsystem for Linux)**. By following these steps, you’ll be able to develop, test, and deploy robot software in a consistent ROS 2 environment.

---

## 🚀 Overview

MakiMate uses:
- **ROS 2 Jazzy**: Robotics middleware for nodes, topics, and services.
- **Docker**: Ensures isolated, reproducible build environments.
- **GitHub**: Facilitates version control and team collaboration.
- **VS Code** (optional): Recommended editor with ROS 2 and Docker support.

**Benefits**:
- ✅ Run the same ROS 2 environment as your team.
- ✅ Develop and test locally with ease.
- ✅ Share code that builds identically across systems.

---

## 🪟 Windows Setup (One-Time)

### 1️⃣ Install WSL 2 + Ubuntu
1. Open **“Turn Windows features on or off”** via Windows Search and enable:
   - ✅ **Windows Subsystem for Linux**
   - ✅ **Virtual Machine Platform**
2. Reboot your computer if prompted.
3. Open **Microsoft Store**, search for **Ubuntu 24.04 LTS**, and install it.
4. Launch Ubuntu from the Start Menu to set up a username and password.
5. In **PowerShell (Admin)**, set WSL 2 as the default:
   ```powershell
   wsl --set-default-version 2
   ```
   💡 This creates a lightweight Linux environment for running Docker and ROS 2.

### 2️⃣ Install Docker Desktop
1. Download and install **Docker Desktop for Windows**: [https://www.docker.com/get-started/](https://www.docker.com/get-started/).
2. Open **Docker Desktop** → **Settings** → **Resources** → **WSL Integration**.
3. Enable:
   - ✅ **Enable integration with my default WSL distro**.
   - ✅ Toggle on **Ubuntu-24.04**.
4. Click **Apply & Restart**.
5. Verify Docker is working in WSL Ubuntu:
   - Open the Ubuntu terminal (Start Menu → Ubuntu).
   - Run:
     ```bash
     docker run hello-world
     ```
     **Expected Output**: A message confirming Docker is working.

### 3️⃣ Install VS Code (Optional)
1. Download **VS Code**: [https://code.visualstudio.com/](https://code.visualstudio.com/).
2. Install these extensions:
   - **Dev Containers**
   - **Remote – WSL**
   - **Docker**
   - **ROS** (optional, for ROS 2 support)
3. Open the Ubuntu terminal, navigate to your project folder, and run `code .` to launch VS Code in WSL (look for “WSL: Ubuntu-24.04” in the bottom-left corner).

### 4️⃣ Install Git and Basic Packages
1. In the Ubuntu terminal:
   ```bash
   sudo apt update
   sudo apt install -y git build-essential curl python3-pip
   ```

### 5️⃣ (Optional) Set Up GitHub SSH Authentication
1. Generate an SSH key:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""
   ```
2. Display the public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
3. Copy the output, go to **GitHub** → **Settings** → **SSH and GPG keys** → **New SSH key**, and paste it.

---

## 🧠 Clone the Repository
1. In the Ubuntu terminal:
   ```bash
   git clone https://github.com/Intelligent-Robotics-Lab/MakiMate.git
   cd MakiMate
   ```
   Or, if using SSH:
   ```bash
   git clone git@github.com:Intelligent-Robotics-Lab/MakiMate.git
   cd MakiMate
   ```

---

## ⚙️ Build the Docker Image
MakiMate uses **Docker Buildx** to create images for desktop (x86_64) and Raspberry Pi 5 (ARM64).

### Option 1: Local Build (Recommended for Beginners)
```bash
docker buildx build . \
  -f docker/robot/Dockerfile \
  --platform linux/amd64 \
  -t makimate:dev \
  --load
```

### Option 2: Multi-Architecture Build (for Desktop + Raspberry Pi)
```bash
docker login ghcr.io
docker buildx build . \
  -f docker/robot/Dockerfile \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/Intelligent-Robotics-Lab/makimate:latest \
  -t ghcr.io/Intelligent-Robotics-Lab/makimate:v0.1.0 \
  --push
```
💡 The multi-architecture build takes longer due to compiling for multiple platforms.

---

## 🧩 Run the Container
1. Run the container to verify ROS 2:
   ```bash
   docker run --rm -it makimate:dev
   ```
   **Expected Output**:
   ```
   [INFO] [hello_node]: Hello from MakiMate!
   ```

2. Explore inside the container:
   ```bash
   docker run -it --entrypoint bash makimate:dev
   ```
3. Inside the container:
   ```bash
   source /opt/ros/jazzy/setup.bash
   source /ws/install/setup.bash
   ros2 launch makimate_bringup bringup.launch.py
   ```
4. Exit: `exit` or `Ctrl+D`.

---

## 🏗️ Project Structure

```
MakiMate/
├── LICENSE                     # Project license file
├── README.md                   # Project overview
├── deploy/                     # Deployment scripts/configurations
├── docker/                     # Docker configurations
│   ├── base/                   # Base Docker image
│   │   └── Dockerfile
│   └── robot/                  # Robot-specific configurations
│       ├── Dockerfile
│       └── entrypoint.sh
├── docs/                       # Documentation
│   └── SETUP.md
├── hw/                         # Hardware-related code
├── interfaces/                 # ROS 2 interfaces (msg, srv, etc.)
└── src/                        # ROS 2 packages
    └── makimate_bringup/
        ├── launch/             # Launch files
        │   └── bringup.launch.py
        ├── makimate_bringup/   # Python package
        │   ├── __init__.py
        │   └── hello.py
        ├── package.xml         # ROS 2 package manifest
        ├── resource/           # Resource files
        │   └── makimate_bringup
        ├── setup.cfg           # Python package config
        └── setup.py            # Build script
```

💡 The `__init__.py` file ensures Python and ROS 2 recognize the package.

---

## 🧰 Common Commands

| Action | Command | Run Where |
|--------|---------|-----------|
| Rebuild image | `docker buildx build . -f docker/robot/Dockerfile -t makimate:dev --load` | WSL Ubuntu |
| Run container | `docker run -it --entrypoint bash makimate:dev` | WSL Ubuntu |
| Source ROS 2 | `source /opt/ros/jazzy/setup.bash` | Container |
| Build workspace | `colcon build --merge-install` | Container |
| Run node | `ros2 run makimate_bringup hello` | Container |
| Launch nodes | `ros2 launch makimate_bringup bringup.launch.py` | Container |
| Push code | `git add . && git commit -m "Update" && git push` | WSL Ubuntu |

---

## 💡 Troubleshooting

1. **Docker Command Not Found**:
   - Ensure **Docker Desktop** is running (check the 🐳 icon in the system tray).
   - Verify WSL integration in **Docker Desktop → Settings → Resources → WSL Integration**.
   - Restart Docker Desktop or your computer.

2. **Permission Denied**:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```
   🔁 Log out and back in.

3. **“Package not found” in ROS 2**:
   ```bash
   colcon build --merge-install
   source /opt/ros/jazzy/setup.bash
   source /ws/install/setup.bash
   ```

4. **Buildx Missing**:
   ```bash
   docker buildx create --name mybuilder --use
   docker buildx inspect --bootstrap
   ```

5. **No Space Left**:
   ```bash
   docker system prune -af
   ```

---

## 🧠 Cross-Platform Development
This setup ensures:
- ✅ Consistent ROS 2 environment across systems.
- ✅ Same image runs on desktop and Raspberry Pi.
- ✅ No manual ROS 2 installation required.

---

## 🫶 Need Help?
Reach out on Discord (@pourya9698) or open a thread in the **#dev-setup** channel.

---

## 🎉 You’re Done!
You now have a fully functional ROS 2 Jazzy environment for MakiMate on Windows. Happy coding! 🤖
