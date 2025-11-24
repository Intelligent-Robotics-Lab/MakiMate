# Base: ROS 2 Jazzy on Ubuntu 24.04 (Noble), arm64-ready
FROM ros:jazzy-ros-base-noble

# Avoid interactive apt
ENV DEBIAN_FRONTEND=noninteractive

# Install tools and ROS build deps
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python-is-python3 \
    build-essential \
    cmake \
    git \
    portaudio19-dev \
    libasound2-dev \
    libopencv-dev \
    libcamera-dev \
    curl \
    ros-jazzy-camera-info-manager \
    ros-jazzy-image-transport \
    ros-jazzy-image-pipeline \
    ros-jazzy-rclcpp-components \
    ros-jazzy-cv-bridge \
 && rm -rf /var/lib/apt/lists/*




# Python libraries used by your nodes (ASR, TTS, LLM bridge, etc.)
RUN python3 -m pip install --no-cache-dir --break-system-packages \
    sounddevice \
    vosk \
    pyttsx3 \
    requests \
    dynamixel_sdk



# Create workspace
WORKDIR /maki_ws

# Copy your ROS2 source tree into the container
COPY src ./src

# Mirror expressions.yaml to the legacy path expected by maki_expressions
RUN mkdir -p /root/MakiMate/src/makimate_dxl/makimate_dxl && \
    cp /maki_ws/src/makimate_dxl/makimate_dxl/expressions.yaml \
       /root/MakiMate/src/makimate_dxl/makimate_dxl/expressions.yaml


# (Optional but nice) try to resolve ROS deps via rosdep
# This assumes the container has internet access at build time.
RUN rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y || echo "rosdep install had some failures; continuing anyway"

# Build the workspace
RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --symlink-install

# Runtime: source ROS + overlay via an entrypoint script
COPY ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]

# Default command (change mode here: demo_mode / presentation_mode / full_feature_mode)
CMD ["ros2", "launch", "maki_operational_nodes", "docker_presentation_mode.launch.py"]
# CMD ["ros2", "launch", "maki_operational_nodes", "docker_demo_mode.launch.py"]
