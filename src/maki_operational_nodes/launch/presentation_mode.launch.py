from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    shell_prefix = (
        "source ~/asr_venv/bin/activate && "
        "source /opt/ros/jazzy/setup.bash && "
        "source ~/MakiMate/install/setup.bash && "
    )

    # 1) ASR: ReSpeaker + Vosk
    asr_node = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "python -m makimate_asr.respeaker_vosk_asr "
              "--ros-args "
              "-p sample_rate:=16000.0 "
              "-p device:=3 "
              "-p model_path:=/home/makimate/vosk_models/vosk-model-small-en-us-0.15 "
              "-p publish_llm:=false "
              "-p asr_topic:=/asr/text "
              "-p llm_request_topic:=/llm/request "
              "-p enable_topic:=/asr/enable"
        ],
        output="screen",
    )

    # 2) Command router
    cmd_router = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_asr asr_command_router "
              "--ros-args "
              "-p asr_topic:=/asr/text "
              "-p llm_request_topic:=/llm/request "
              "-p llm_response_topic:=/llm/response "
              "-p awake_topic:=/maki/awake "
        ],
        output="screen",
    )

    # 3) LLM bridge
    llm_bridge = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "cd ~/MakiMate/src/server_llm/server_llm && "
              "python llm_bridge_node.py "
              "--ros-args "
              "-p laptop_host:='http://35.50.73.78:8000' "
              "-p endpoint_path:='/chat/stream' "
              "-p request_topic:=/llm/request "
              "-p stream_topic:=/llm/stream "
              "-p response_topic:=/llm/response "
              "-p asr_enable_topic:=/asr/enable "
              "--log-level asr_led_controller:=error"
        ],
        output="screen",
    )

    # 4) TTS
    tts_node = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_asr natural_tts_node "
              "--ros-args "
              "-p backend:=piper_python "
              "-p piper_model:=/home/makimate/piper_models/en_US-john-medium.onnx "
              "-p input_topic:=/llm/stream"
        ],
        output="screen",
    )

    # 5) LED ring
    led_node = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "python -m makimate_asr.asr_led_node "
              "--ros-args "
              "-p enable_topic:=/asr/enable "
              "-p awake_topic:=/maki/awake "
              "--log-level asr_led_controller:=error"
        ],
        output="screen",
    )

    # 6) Maki expressions (names -> joint goals)
    maki_expressions = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_dxl maki_expressions"
        ],
        output="screen",
    )

    # 7) Awake -> expression bridge
    maki_behavior_awake = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run maki_operational_nodes maki_awake_behavior "
              "--ros-args "
              "-p awake_topic:=/maki/awake "
              "-p expression_topic:=/maki/expression "
        ],
        output="screen",
    )

    # 8) DXL controller (actual motors)
    maki_dxl_node = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_dxl maki_dxl_6"
        ],
        output="screen",
    )

    # 9) Higher-level motion behavior (your existing one)
    maki_behavior_node = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_dxl maki_behavior"
        ],
        output="screen",
    )

    return LaunchDescription([
        asr_node,
        cmd_router,
        llm_bridge,
        tts_node,
        led_node,
        maki_expressions,
        maki_behavior_awake,
        maki_dxl_node,
        maki_behavior_node,
    ])
