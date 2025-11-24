#!/bin/bash
set -e

# Source ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# Source the built workspace
source /maki_ws/install/setup.bash

# Pass control to whatever CMD/command was given (ros2 launch ...)
exec "$@"
