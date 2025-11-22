#!/usr/bin/env bash

# Simple helper to start all main Maki nodes in separate terminals.

WS=~/MakiMate
ROS_SETUP="source /opt/ros/jazzy/setup.bash"
WS_SETUP="cd $WS && source install/setup.bash"

# Function to start a new gnome-terminal with a title and command
start_term() {
  local TITLE="$1"
  local CMD="$2"
  gnome-terminal --title="$TITLE" -- bash -lc "$ROS_SETUP; $WS_SETUP; $CMD; exec bash"
}

# 1) Dynamixel controller (motors)
start_term "DXL: maki_dxl_6" "ros2 run makimate_dxl maki_dxl_6"

# 2) Expressions node (for named poses: listening, sleepy, etc.)
start_term "DXL: maki_expressions" "ros2 run makimate_dxl maki_expressions"

# 3) Behavior node (find_me, circle_scan, look_at_user, etc.)
start_term "DXL: maki_behavior" "ros2 run makimate_dxl maki_behavior"

# 4) Camera node (640x480 @ ~30 fps, autofocus tuned)
start_term "Camera: camera_ros" "
ros2 run camera_ros camera_node --ros-args \
  -p camera:=0 \
  -p role:=video \
  -p sensor_mode:='640:480' \
  -p width:=640 \
  -p height:=480 \
  -p format:=BGR888 \
  -p FrameDurationLimits:='[33333,33333]' \
  -p AfMode:=2 \
  -p AfSpeed:=1 \
  -p AfRange:=0
"

# 5) Face tracker (OpenCV Haar cascade, publishes bbox + debug image)
start_term "Vision: face_tracker" "
ros2 run makimate_vision face_tracker --ros-args \
  -p input_image_topic:=/camera/image_raw \
  -p output_image_topic:=/camera/face_image \
  -p show_debug_window:=true \
  -p detect_every_n:=5 \
  -p downscale_factor:=0.3 \
  -p roi_expansion:=0.5 \
  -p full_frame_every:=20
"

# 6) Face → Maki bridge (bbox -> /maki/face_pos)
start_term "Vision: face_to_maki" "
ros2 run makimate_vision face_to_maki --ros-args \
  -p image_width:=640 \
  -p image_height:=480
"

echo "Launched all main Maki nodes."
echo "Now, in any terminal, you can do:"
echo "  ros2 topic pub /maki/behavior std_msgs/String \"data: 'look_at_user'\" --once"
