#!/bin/bash

# ================================
# MakiMate ASR/LLM/TTS Launcher
# Raspberry Pi 5 – Ubuntu 24.04
# ================================

# Function to open a new GNOME terminal safely
launch() {
  gnome-terminal -- bash -c "$1; exec bash"
}

# -----------------------------------------------
# 1) Command Router
# -----------------------------------------------
launch "
echo 'Starting Command Router...'
source ~/asr_venv/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MakiMate/install/setup.bash

python -m makimate_asr.asr_command_router \
  --ros-args \
    -p asr_topic:=/asr/text \
    -p llm_request_topic:=/llm/request \
    -p llm_response_topic:=/llm/response \
    -p awake_topic:=/maki/awake
"

# -----------------------------------------------
# 2) ASR (Vosk + Respeaker)
# -----------------------------------------------
launch "
echo 'Starting ASR...'
source ~/asr_venv/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MakiMate/install/setup.bash

python -m makimate_asr.respeaker_vosk_asr \
  --ros-args \
    -p sample_rate:=16000.0 \
    -p device:=6 \
    -p model_path:=/home/makimate/vosk_models/vosk-model-small-en-us-0.15 \
    -p publish_llm:=false \
    -p asr_topic:=/asr/text \
    -p llm_request_topic:=/llm/request \
    -p enable_topic:=/asr/enable
"

# -----------------------------------------------
# 3) LLM Bridge
# -----------------------------------------------
launch "
echo 'Starting LLM Bridge...'
source ~/asr_venv/bin/activate
source /opt/ros/jazzy/setup.bash
cd ~/MakiMate/src/server_llm/server_llm

python llm_bridge_node.py \
  --ros-args \
    -p laptop_host:='http://35.50.73.78:8000' \
    -p endpoint_path:='/chat/stream' \
    -p request_topic:=/llm/request \
    -p stream_topic:=/llm/stream \
    -p response_topic:=/llm/response \
    -p asr_enable_topic:=/asr/enable
"

# -----------------------------------------------
# 4) Natural TTS (Piper)
# -----------------------------------------------
launch "
echo 'Starting TTS...'
source ~/asr_venv/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MakiMate/install/setup.bash

ros2 run makimate_asr natural_tts_node \
  --ros-args \
    -p backend:=piper_python \
    -p piper_model:=/home/makimate/MakiMate/piper_models/en_US-john-medium.onnx \
    -p input_topic:=/llm/stream
"

# -----------------------------------------------
# 5) LED Node (ReSpeaker LED Ring)
# -----------------------------------------------
launch "
echo 'Starting LED Controller...'
source ~/asr_venv/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/MakiMate/install/setup.bash

python -m makimate_asr.asr_led_node \
  --ros-args \
    -p enable_topic:=/asr/enable \
    -p awake_topic:=/maki/awake
"

echo "All nodes launched!"
