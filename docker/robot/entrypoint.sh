#!/usr/bin/env bash
set -e

# Source base ROS 2
source /opt/ros/jazzy/setup.bash || true

# Prefer the overlay's local_setup (it reliably prepends /ws/install)
if [ -f /ws/install/local_setup.bash ]; then
  source /ws/install/local_setup.bash
elif [ -f /ws/install/setup.bash ]; then
  source /ws/install/setup.bash
fi

# Defensive: make sure overlay is first on the paths
export AMENT_PREFIX_PATH="/ws/install:${AMENT_PREFIX_PATH}"
export CMAKE_PREFIX_PATH="/ws/install:${CMAKE_PREFIX_PATH}"
export PYTHONPATH="/ws/install/lib/python3/dist-packages:${PYTHONPATH}"

exec "$@"
