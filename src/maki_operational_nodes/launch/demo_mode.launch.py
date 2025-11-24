from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo


def generate_launch_description():
    # Common shell prefix: ROS 2 + MakiMate workspace
    shell_prefix = (
        "source /opt/ros/jazzy/setup.bash && "
        "source ~/MakiMate/install/setup.bash && "
    )

    # 1) Camera: headless camera_ros node (NO image_view / Qt)
    camera = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run camera_ros camera_node "
              "--ros-args "
              "-p camera:=0 "
              "-p role:=video "
              "-p sensor_mode:='640:480' "
              "-p width:=640 "
              "-p height:=480 "
              "-p format:=BGR888 "
        ],
        output="screen",
    )

    # 2) Vision: face tracking and mapping to Maki coordinates
    face_tracker = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_vision face_tracker",
        ],
        output="screen",
    )

    face_to_maki = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_vision face_to_maki",
        ],
        output="screen",
    )

    # 3) Dynamixel / Maki behavior stack
    dxl_hw = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_dxl maki_dxl_6",
        ],
        output="screen",
    )

    expressions = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_dxl maki_expressions",
        ],
        output="screen",
    )

    # Enable monologue only in demo mode
    behavior = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_dxl maki_behavior "
              "--ros-args "
              "-p enable_monologue:=true"
        ],
        output="screen",
    )

    # 4) TTS: Piper on /llm/stream (monologue output)
    tts_node = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_asr natural_tts_node "
              "--ros-args "
              "-p backend:=piper_python "
              "-p piper_model:=/home/makimate/MakiMate/piper_models/en_US-john-medium.onnx "
              "-p input_topic:=/llm/stream"
        ],
        output="screen",
    )

    # 5) Keep Maki awake in demo mode
    awake_publisher = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "sleep 2 && "
              "ros2 topic pub /maki/awake std_msgs/msg/Bool \"data: true\" -r 1.0",
        ],
        output="screen",
    )

    # Expression: 'wide_awake' so Maki goes immediately to wake pose
    wake_expression = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "sleep 4 && "
              "ros2 topic pub --once /maki/expression std_msgs/msg/String \"data: 'wide_awake'\"",
        ],
        output="screen",
    )

    # 6) Behavior mode: start in look_at_user so that:
    #    - when no face: randomized search (circle_scan) kicks in
    #    - when a face is found and locked for 3s: monologue is triggered
    behavior_mode = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "sleep 5 && "
              "ros2 topic pub --once /maki/behavior std_msgs/msg/String "
              "\"data: 'look_at_user'\"",
        ],
        output="screen",
    )

    return LaunchDescription(
        [
            LogInfo(
                msg=(
                    "Starting Maki DEMO MODE "
                    "(face tracking + randomized search + voice monologue)."
                )
            ),
            camera,
            face_tracker,
            face_to_maki,
            dxl_hw,
            expressions,
            behavior,
            tts_node,
            awake_publisher,
            wake_expression,
            behavior_mode,
        ]
    )
