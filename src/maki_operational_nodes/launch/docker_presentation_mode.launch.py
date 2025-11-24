from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo


def generate_launch_description():
    # Inside the Docker image:
    # - ROS 2 Jazzy is at /opt/ros/jazzy
    # - The built workspace is at /maki_ws (from the Dockerfile)
    shell_prefix = (
        "source /opt/ros/jazzy/setup.bash && "
        "source /maki_ws/install/setup.bash && "
    )

    procs = []

    # -------------------------------
    # 1) ASR: ReSpeaker + Vosk
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix
                + (
                    "python -m makimate_asr.respeaker_vosk_asr "
                    "--ros-args "
                    "-p sample_rate:=16000.0 "
                    "-p device:=-1 "
                    "-p model_path:=/home/makimate/vosk_models/vosk-model-small-en-us-0.15 "
                    "-p publish_llm:=false "
                    "-p asr_topic:=/asr/text "
                    "-p llm_request_topic:=/llm/request "
                    "-p enable_topic:=/asr/enable"
                ),
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 2) ASR command router (wake/sleep + LLM forwarding)
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix
                + (
                    "ros2 run makimate_asr ai_command_router "
                    "--ros-args "
                    "-p asr_topic:=/asr/text "
                    "-p llm_request_topic:=/llm/request "
                    "-p llm_response_topic:=/llm/response "
                    "-p awake_topic:=/maki/awake "
                    "-p tts_topic:=/llm/stream "
                    "-p asr_enable_topic:=/asr/enable"
                ),
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 3) LLM bridge node (Pi <-> Windows LLM HTTP server)
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix
                + (
                    "cd /maki_ws/src/server_llm/server_llm && "
                    "python llm_bridge_node.py "
                    "--ros-args "
                    "-p laptop_host:='http://35.50.73.78:8000' "
                    "-p endpoint_path:='/chat/stream' "
                    "-p request_topic:=/llm/request "
                    "-p stream_topic:=/llm/stream "
                    "-p response_topic:=/llm/response "
                    "-p asr_enable_topic:=/asr/enable "
                    "--log-level asr_led_controller:=error"
                ),
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 4) TTS (Piper)
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix
                + (
                    "ros2 run makimate_asr natural_tts_node "
                    "--ros-args "
                    "-p backend:=piper_python "
                    "-p piper_model:=/home/makimate/MakiMate/piper_models/en_US-john-medium.onnx "
                    "-p input_topic:=/llm/stream"
                ),
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 5) ASR LED controller
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix
                + (
                    "python -m makimate_asr.asr_led_node "
                    "--ros-args "
                    "-p enable_topic:=/asr/enable "
                    "-p awake_topic:=/maki/awake "
                    "--log-level asr_led_controller:=error"
                ),
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 6) DXL expressions
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix + "ros2 run makimate_dxl maki_expressions",
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 7) DXL low-level control
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix + "ros2 run makimate_dxl maki_dxl_6",
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 8) High-level behavior (tracks / face, awake state, etc.)
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix
                + (
                    "ros2 run makimate_dxl maki_behavior "
                    "--ros-args "
                    "-p enable_monologue:=false"
                ),
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 9) Awake behavior (expression changes based on /maki/awake)
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix
                + (
                    "ros2 run maki_operational_nodes maki_awake_behavior "
                    "--ros-args "
                    "-p awake_topic:=/maki/awake "
                    "-p expression_topic:=/maki/expression"
                ),
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 10) Camera node (libcamera_ros-based)
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix
                + (
                    "ros2 run camera_ros camera_node "
                    "--ros-args "
                    "-p camera:=0 "
                    "-p role:=video "
                    "-p sensor_mode:='640:480' "
                    "-p width:=640 "
                    "-p height:=480 "
                    "-p format:=BGR888"
                ),
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 11) Face tracker (vision node)
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix + "ros2 run makimate_vision face_tracker",
            ],
            output="screen",
        )
    )

    # -------------------------------
    # 12) Face -> Maki servo mapping
    # -------------------------------
    procs.append(
        ExecuteProcess(
            cmd=[
                "bash",
                "-lc",
                shell_prefix + "ros2 run makimate_vision face_to_maki",
            ],
            output="screen",
        )
    )

    return LaunchDescription(
        [
            LogInfo(msg="Starting Maki DOCKER PRESENTATION MODE"),
            *procs,
        ]
    )
