from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo


def generate_launch_description():
    # Common shell prefix: ROS 2 + MakiMate workspace
    shell_prefix = (
        "source /opt/ros/jazzy/setup.bash && "
        "source ~/MakiMate/install/setup.bash && "
    )

    # 1) Camera: camera_ros pipeline
    #    (preview disabled inside camera.launch.py by removing ImageView)
    camera = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 launch camera_ros camera.launch.py",
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

    behavior = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "ros2 run makimate_dxl maki_behavior",
        ],
        output="screen",
    )

    # 4) Fake the "awake" signals like the command router would
    #    /maki/awake := True
    set_awake_true = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "sleep 2 && "
              "ros2 topic pub --once /maki/awake std_msgs/msg/Bool \"data: true\"",
        ],
        output="screen",
    )

    # Expression: 'wide_awake' so Maki goes immediately to wake pose
    wake_expression = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "sleep 3 && "
              "ros2 topic pub --once /maki/expression std_msgs/msg/String \"data: 'wide_awake'\"",
        ],
        output="screen",
    )

    # 5) Spoof /maki/behavior so maki_behavior switches into
    #    the face-follow state instead of just idle scanning.
    #
    # IMPORTANT: the string below ("face_follow") is a best guess.
    # For a perfect match, see the note after this file.
    behavior_mode = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            shell_prefix
            + "sleep 4 && "
              "ros2 topic pub --once /maki/behavior std_msgs/msg/String "
              "\"data: 'face_follow'\"",
        ],
        output="screen",
    )

    # NOTE: No ASR / TTS / LLM / command router here on purpose.

    return LaunchDescription(
        [
            LogInfo(
                msg=(
                    "Starting Maki DEMO MODE "
                    "(no AI, starts awake, face tracking + idle scan)."
                )
            ),
            camera,
            face_tracker,
            face_to_maki,
            dxl_hw,
            expressions,
            behavior,
            set_awake_true,
            wake_expression,
            behavior_mode,
        ]
    )
