cd ~/MakiMate
cat > env/setup_makimate_pi.sh << 'EOF'
#!/usr/bin/env bash
set -e

### MakiMate Pi5 setup script
# Target: Ubuntu 24.04 + ROS 2 Jazzy on Raspberry Pi 5

# -------- 0) Basic sanity checks --------
if ! command -v lsb_release >/dev/null 2>&1; then
  echo "lsb_release not found. Are you on Ubuntu?"
  exit 1
fi

UBUNTU_CODENAME=$(lsb_release -sc)
if [[ "$UBUNTU_CODENAME" != "noble" ]]; then
  echo "Warning: this script was designed for Ubuntu 24.04 (noble)."
fi

# -------- 1) Update and core tools --------
echo "[1/4] Updating apt and installing core tools..."
sudo apt update

# Install core packages from apt-extra.txt
if [[ ! -f "env/apt-extra.txt" ]]; then
  echo "ERROR: env/apt-extra.txt not found. Please create it first."
  exit 1
fi

# Strip comments and blank lines before feeding to apt
APT_LIST=$(grep -vE '^\s*#' env/apt-extra.txt | sed '/^\s*$/d')

if [[ -n "$APT_LIST" ]]; then
  echo "$APT_LIST" | xargs -r sudo apt install -y
else
  echo "env/apt-extra.txt appears to be empty after filtering comments."
fi

# -------- 2) ROS 2 dependencies via rosdep --------
echo "[2/4] Installing ROS 2 package dependencies via rosdep..."

# Initialize rosdep if needed
if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  sudo rosdep init || true
fi

rosdep update
# Install dependencies for all packages under src/ (ignoring local builds)
rosdep install --from-paths src --ignore-src -y

# -------- 3) ASR / LLM Python venv --------
echo "[3/4] Creating and populating ASR venv..."

VENV_DIR="$HOME/asr_venv"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install ASR/LLM Python deps
if [[ -f "env/asr_requirements.txt" ]]; then
  pip install -r env/asr_requirements.txt
else
  echo "ERROR: env/asr_requirements.txt not found. Copy your venv freeze there."
  deactivate
  exit 1
fi

deactivate

# -------- 4) Helpful messages --------
echo "[4/4] Setup complete (apt + rosdep + ASR venv)."
echo
echo "To use MakiMate in a new terminal:"
echo "  source /opt/ros/jazzy/setup.bash"
echo "  cd ~/MakiMate"
echo "  source install/setup.bash  # after colcon build"
echo "  source \$HOME/asr_venv/bin/activate  # for ASR/LLM nodes"
echo
echo "Then build with:"
echo "  colcon build"
EOF

chmod +x env/setup_makimate_pi.sh

