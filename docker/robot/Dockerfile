# docker/robot/Dockerfile
FROM ros:jazzy-ros-base

# Use bash for RUN so "source" works
SHELL ["/bin/bash", "-lc"]

RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions python3-pip python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws
COPY src/ src/
COPY interfaces/ interfaces/
COPY hw/ hw/

# Resolve deps but don't fail if none are declared yet
RUN source /opt/ros/jazzy/setup.bash && rosdep update || true && rosdep install --from-paths . -iry || true

# Build the workspace (Python ament)
RUN source /opt/ros/jazzy/setup.bash && colcon build --merge-install --event-handlers console_direct+

# Default command: source both setups and launch
# Sensible defaults even before sourcing (helps shells/tools)
ENV AMENT_PREFIX_PATH="/ws/install:/opt/ros/jazzy" \
    CMAKE_PREFIX_PATH="/ws/install:/opt/ros/jazzy" \
    PYTHONPATH="/ws/install/lib/python3/dist-packages"

# Always source environments before running any command
COPY docker/robot/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Default command runs your node
CMD ["ros2","launch","makimate_bringup","bringup.launch.py"]

