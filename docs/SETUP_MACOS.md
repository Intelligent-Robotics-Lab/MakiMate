# 🧠 MakiMate Setup Guide for macOS

Welcome to **MakiMate**, a cross-platform **ROS 2 Jazzy** codebase for the Maki robot! This guide walks you through setting up a development environment on **macOS** using **Docker**. By following these steps, you’ll be able to develop, test, and deploy robot software in a consistent ROS 2 environment.

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

## 🍎 macOS Setup (One-Time)

### 1️⃣ Install Docker
1. Download and install **Docker Desktop for macOS**: [https://www.docker.com/get-started/](https://www.docker.com/get-started/).
2. Start Docker Desktop (ensure the 🐳 icon appears in the menu bar).
3. Verify Docker:
   ```bash
   docker run hello-world
   ```
   **Expected Output**: A message confirming Docker is working.
4. Verify Buildx:
   ```bash
   docker buildx version
   ```
   If Buildx is missing:
   ```bash
   docker buildx create --name mybuilder --use
   docker buildx inspect --bootstrap
   ```

### 2️⃣ Install Git and Basic Packages
1. Install **Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Git and other tools:
   ```bash
   brew install git curl python3
   ```

### 3️⃣ Install VS Code (Optional)
1. Download **VS Code**: [https://code.visualstudio.com/](https://code.visualstudio.com/).
2. Install extensions:
   - **Dev Containers**
   - **Docker**
   - **ROS** (optional, for ROS 2 support)
3. Run `code .` in your project folder to open VS Code.

### 4️⃣ (Optional) Set Up GitHub SSH Authentication
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

---

## 🧩 Run the Container
1. Run the container:
   ```bash
   docker run --rm -it makimate:dev
   ```
   **Expected Output**:
   ```
   [INFO] [hello_node]: Hello from MakiMate!
   ```

2. Explore inside:
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

---

## 🧰 Common Commands

| Action | Command | Run Where |
|--------|---------|-----------|
| Rebuild image | `docker buildx build . -f docker/robot/Dockerfile -t makimate:dev --load` | Host |
| Run container | `docker run -it --entrypoint bash makimate:dev` | Host |
| Source ROS 2 | `source /opt/ros/jazzy/setup.bash` | Container |
| Build workspace | `colcon build --merge-install` | Container |
| Run node | `ros2 run makimate_bringup hello` | Container |
| Launch nodes | `ros2 launch makimate_bringup bringup.launch.py` | Container |
| Push code | `git add . && git commit -m "Update" && git push` | Host |

---

## 💡 Troubleshooting

1. **Docker Not Running**:
   - Ensure **Docker Desktop** is running (check the 🐳 icon in the menu bar).
   - Restart Docker Desktop if needed.

2. **Permission Denied**:
   Ensure Docker Desktop has the necessary permissions in macOS System Settings.

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
You now have a fully functional ROS 2 Jazzy environment for MakiMate on macOS. Happy coding! 🤖
