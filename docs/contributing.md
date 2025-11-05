# Contributing to MakiMate

Thanks for your interest in contributing! This guide will walk you through **Git**, **Docker/Buildx**, **ROS 2 (Jazzy)**, and **VS Code** workflows so you can be productive without breaking things. It’s written for Linux and Windows (WSL 2); macOS users can follow the Linux steps with minor adjustments.

---

## Table of Contents
1. [Project Philosophy](#project-philosophy)
2. [Prerequisites](#prerequisites)
3. [Repository Structure](#repository-structure)
4. [Quick Start (5‑minute smoke test)](#quick-start-5minute-smoke-test)
5. [Git: Branching, Commits, Pull Requests](#git-branching-commits-pull-requests)
6. [Development Environments](#development-environments)
   - [Linux](#linux)
   - [Windows via WSL 2](#windows-via-wsl-2)
   - [macOS](#macos)
7. [Docker Dev Workflow](#docker-dev-workflow)
   - [Build a local dev image](#build-a-local-dev-image)
   - [Iterate with bind mounts (fast inner loop)](#iterate-with-bind-mounts-fast-inner-loop)
   - [Common Docker commands](#common-docker-commands)
8. [ROS 2 Basics for This Repo](#ros-2-basics-for-this-repo)
   - [Workspace layout](#workspace-layout)
   - [Build with colcon](#build-with-colcon)
   - [Source environments](#source-environments)
   - [Run nodes & launch files](#run-nodes--launch-files)
   - [Messages/Services (interfaces)](#messagesservices-interfaces)
9. [Testing, Linting, CI](#testing-linting-ci)
10. [VS Code Setup](#vs-code-setup)
11. [Multi‑arch Images & Releases (Maintainers)](#multiarch-images--releases-maintainers)
12. [Troubleshooting](#troubleshooting)
13. [Security & Access](#security--access)
14. [FAQ](#faq)

---

## Project Philosophy
- **Reproducibility:** Everyone builds, runs, and tests inside the same Dockerized ROS 2 environment.
- **Clarity:** Small, reviewable pull requests with clear commit history.
- **Safety:** Main stays green; releases are tagged and images are versioned.

---

## Prerequisites

### All contributors
- A GitHub account with access to the repository.
- Git installed (WSL or Linux package manager is fine).
- VS Code (optional but recommended) with the extensions listed below.

### Linux
- Docker Engine with Buildx & Compose plugin.
- User is in the `docker` group (optional on some setups):
  ```bash
  sudo usermod -aG docker $USER && newgrp docker
  ```

### Windows via WSL 2 (Recommended)
- Windows 10 (21H2+) or Windows 11
- WSL 2 with **Ubuntu 24.04 LTS**
- Docker Desktop (enable WSL integration for Ubuntu)

### macOS
- Docker Desktop for Mac (Buildx included)

---

## Repository Structure
```
MakiMate/
├── LICENSE
├── README.md
├── deploy/
├── docker/
│   ├── base/
│   │   └── Dockerfile
│   └── robot/
│       ├── Dockerfile
│       └── entrypoint.sh
├── docs/
│   └── SETUP.md
├── hw/
├── interfaces/
└── src/
    └── makimate_bringup/
        ├── launch/
        │   └── bringup.launch.py
        ├── makimate_bringup/
        │   ├── __init__.py
        │   └── hello.py
        ├── package.xml
        ├── resource/
        │   └── makimate_bringup
        ├── setup.cfg
        └── setup.py
```

---

## Quick Start (5‑minute smoke test)
```bash
# 1) Clone (HTTPS or SSH)
git clone https://github.com/Intelligent-Robotics-Lab/MakiMate.git
cd MakiMate

# 2) Build local dev image (single-arch)
docker buildx build . \
  -f docker/robot/Dockerfile \
  --platform linux/amd64 \
  -t makimate:dev \
  --load

# 3) Run the container (hello demo)
docker run --rm -it makimate:dev
# Expected: [INFO] [hello_node]: Hello from MakiMate!
```
If it doesn’t print the hello line, try the interactive shell:
```bash
docker run -it --entrypoint bash makimate:dev
source /opt/ros/jazzy/setup.bash
source /ws/install/setup.bash
ros2 launch makimate_bringup bringup.launch.py
```

---

## Git: Branching, Commits, Pull Requests

### Fork vs. Branch
- **Org members:** Create branches in this repo.
- **External contributors:** Fork the repo, push to your fork, open a PR.

### Branch naming
```
feature/<short-description>
fix/<issue-or-bug>
chore/<task>
docs/<topic>
```
Examples: `feature/pid-controller`, `fix/launch-namespace`, `docs/setup-windows`.

### Commit style (Conventional Commits flavor)
Use small, purposeful commits:
```
feat: add PID controller for wheel motors
fix: correct topic name in bringup.launch.py
chore: bump base image to ros:jazzy-ros-base
docs: expand Windows setup for WSL 2
```

### Pull Requests
- One feature/bug per PR.
- Include **what/why/how** in the PR description.
- Link related issues.
- Add tests or launch snippets where applicable.
- Ensure `colcon build` passes inside the dev container.

### Code Review Checklist
- [ ] Code builds in container (`colcon build --merge-install`).
- [ ] Launch files/nodes run (`ros2 run` / `ros2 launch`).
- [ ] Lint passes (see below).
- [ ] Clear naming, comments, and docstrings.
- [ ] No hard-coded paths/secrets.

---

## Development Environments

### Linux
- Install Docker Engine + Buildx.
- Clone and work under your **Linux filesystem** (not remote mounts).

### Windows via WSL 2
- Keep the repo in the **WSL filesystem** (e.g., `~/MakiMate`), not under `/mnt/c/...`.
- Ensure Docker Desktop is running and WSL integration is enabled for your Ubuntu distro.
- Use VS Code **Remote – WSL**.

### macOS
- Use Docker Desktop for Mac.
- Everything else mirrors the Linux steps.

---

## Docker Dev Workflow

### Build a local dev image
```bash
docker buildx build . \
  -f docker/robot/Dockerfile \
  --platform linux/amd64 \
  -t makimate:dev \
  --load
```

### Iterate with bind mounts (fast inner loop)
Mount your working directory into the container so edits are instant:
```bash
docker run --rm -it \
  -v "$PWD/src":/ws/src \
  -v "$PWD/interfaces":/ws/interfaces \
  makimate:dev
```
Inside the container:
```bash
cd /ws
colcon build --merge-install
source /opt/ros/jazzy/setup.bash
source /ws/install/setup.bash
ros2 run makimate_bringup hello
```

### Common Docker commands
```bash
# List images/containers
docker images
docker ps -a

# Clean unused data (⚠ removes unused images/volumes)
docker system prune -af

# If buildx builder isn’t initialized
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap
```

---

## ROS 2 Basics for This Repo

### Workspace layout
- `ws` is the working directory **inside** the container (`/ws`).
- `src/` contains packages (e.g., `makimate_bringup`).
- `interfaces/` holds messages/services if applicable.

### Build with colcon
```bash
cd /ws
colcon build --merge-install
```

### Source environments
```bash
# Base ROS environment
source /opt/ros/jazzy/setup.bash
# Workspace overlays (after a successful build)
source /ws/install/setup.bash
```
Add these to the container’s entrypoint or your interactive shell session before running tools.

### Run nodes & launch files
```bash
# Run a single node
ros2 run makimate_bringup hello

# Launch multiple nodes
ros2 launch makimate_bringup bringup.launch.py
```

### Messages/Services (interfaces)
- Define messages/services under `interfaces/` as ROS 2 packages.
- Update `package.xml` and `setup.py`/CMakeLists accordingly.
- Rebuild with `colcon build --merge-install` and re‑source your overlays.

---

## Testing, Linting, CI

### Python style
- Follow **PEP 8**.
- Recommended tools: `ament_flake8`, `ament_black`, `ruff` (optional).

### Running linters (example)
```bash
# Inside the container at /ws
colcon test
colcon test-result --verbose
```
Add a `test` directory in each package and integrate with `ament` test macros.

### Pre-commit (optional but encouraged)
Add a `.pre-commit-config.yaml` with Black/Flake8/Ruff and install hooks:
```bash
pip3 install pre-commit
pre-commit install
```

### CI (GitHub Actions)
- Builds PRs using the Dockerfile.
- Runs `colcon build` + tests.
- Blocks merges if CI fails.

---

## VS Code Setup

### Recommended extensions
- **Remote – WSL** (Windows), or **Dev Containers** if you use a `.devcontainer` later
- **Docker**
- **Python** (for Python packages)
- **ROS** (optional; for message highlighting/tools)

### Open the repo in WSL (Windows)
From WSL terminal:
```bash
cd ~/MakiMate
code .
```
Bottom-left should show `WSL: Ubuntu-24.04`.

### Optional: Dev Container
You can add a `.devcontainer/devcontainer.json` to open the repo inside the Docker dev image automatically. A minimal example:
```json
{
  "name": "MakiMate Dev",
  "remoteUser": "root",
  "image": "makimate:dev",
  "runArgs": [
    "-v", "${localWorkspaceFolder}/src:/ws/src",
    "-v", "${localWorkspaceFolder}/interfaces:/ws/interfaces"
  ],
  "postCreateCommand": "bash -lc 'source /opt/ros/jazzy/setup.bash && cd /ws && colcon build --merge-install'",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-azuretools.vscode-docker",
        "ms-python.python",
        "ms-vscode-remote.remote-wsl",
        "ms-vscode-remote.remote-containers",
        "ms-iot.vscode-ros"
      ]
    }
  }
}
```

---

## Multi‑arch Images & Releases (Maintainers)

### Login to GHCR
```bash
docker login ghcr.io
# Username: <your GitHub username>
# Password: <Personal Access Token with read:packages, write:packages>
```

### Build and push multi‑arch images (desktop + Raspberry Pi)
> **Use lowercase org/repo names** for GHCR
```bash
docker buildx build . \
  -f docker/robot/Dockerfile \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/intelligent-robotics-lab/makimate:latest \
  -t ghcr.io/intelligent-robotics-lab/makimate:vX.Y.Z \
  --push
```
- `latest` is for convenience.
- `vX.Y.Z` is the immutable, referenced tag.

### Pull & run
```bash
docker pull ghcr.io/intelligent-robotics-lab/makimate:latest
docker run --rm -it ghcr.io/intelligent-robotics-lab/makimate:latest
```

---

## Troubleshooting

### Docker command not found (WSL)
- Ensure Docker Desktop is running (🐳 in system tray).
- Docker Desktop → Settings → Resources → **WSL Integration** enabled for Ubuntu.
- Check context: `docker context ls` (use `default`).

### Permission denied talking to Docker socket (Linux)
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Buildx not available
```bash
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap
```

### “Release file … not valid yet” (apt time skew)
```bash
sudo timedatectl set-ntp true
sudo timedatectl status
```

### No space left on device
```bash
docker system prune -af
```
> ⚠ This removes **all** unused images/containers/volumes.

### GUI tools in WSL (gedit, rqt_graph)
- **Windows 11:** WSLg supports GUIs natively → `gedit &`, `rqt_graph &`.
- **Windows 10:** Install VcXsrv on Windows and `export DISPLAY=$(grep -oP "(?<=nameserver ).+" /etc/resolv.conf):0` in WSL.

---

## Security & Access
- **PATs/Tokens:** Never commit tokens. Use `--password-stdin` when logging into GHCR:
  ```bash
  echo "$GHCR_TOKEN" | docker login ghcr.io -u <github-username> --password-stdin
  ```
- **Packages:** Only maintainers push to `ghcr.io/intelligent-robotics-lab/makimate:latest`.
- **Secrets in code:** Use environment variables or mount secret files at runtime; don’t commit them.

---

## FAQ

**Q: Do I need to install ROS 2 locally?**  
A: No. Use the container.

**Q: My `docker run makimate:dev` fails after a `--push` build.**  
A: `--push` doesn’t load locally. Either `docker pull ghcr.io/intelligent-robotics-lab/makimate:latest` or rebuild with `--load`.

**Q: Where should I keep the repo on Windows?**  
A: Inside the WSL filesystem (e.g., `~/MakiMate`), not under `/mnt/c/...`.

**Q: How do I reset a broken container environment?**  
A: `docker system prune -af` then rebuild the image.

**Q: Who merges PRs?**  
A: Maintainers after at least one approving review and green CI.

---

Happy hacking! If you get stuck, open a GitHub Discussion or a thread in **#dev-setup** on Discord (@pourya9698).

