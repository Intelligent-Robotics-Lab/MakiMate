from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo


def generate_launch_description():
    # Common shell prefix for processes that use ROS + Maki workspace
    shell_prefix = (
        "source /opt/ros/jazzy/setup.bash && "
        "source ~/MakiMate/install/setup.bash && "
    )

    # 1) Dynamixel controller (motors)
    dxl_controller = ExecuteProcess(
        cmd=[
            'bash',
            '-lc',
            shell_prefix
            + "ros2 run makimate_dxl maki_dxl_6"
        ],
        output='screen',
    )

    # 2) Expressions node (poses like listening, sleepy, etc.)
    dxl_expressions = ExecuteProcess(
        cmd=[
            'bash',
            '-lc',
            shell_prefix
            + "ros2 run makimate_dxl maki_expressions"
        ],
        output='screen',
    )

    # 3) Behavior node (look_at_user, find_me, etc.)
    behavior_node = ExecuteProcess(
        cmd=[
            'bash',
            '-lc',
            shell_prefix
            + "ros2 run makimate_dxl maki_behavior"
        ],
        output='screen',
    )

    # 4) Camera node (640x480 @ ~30 fps, autofocus tuned)
    camera_node = ExecuteProcess(
        cmd=[
            'bash',
            '-lc',
            shell_prefix
            + "ros2 run camera_ros camera_node --ros-args "
              "-p camera:=0 "
              "-p role:=video "
              "-p sensor_mode:='640:480' "
              "-p width:=640 "
              "-p height:=480 "
              "-p format:=BGR888 "
              "-p FrameDurationLimits:='[33333,33333]' "
              "-p AfMode:=2 "
              "-p AfSpeed:=1 "
              "-p AfRange:=0"
        ],
        output='screen',
    )

    # 5) Face tracker (OpenCV Haar, publishes bbox + debug image)
    face_tracker = ExecuteProcess(
        cmd=[
            'bash',
            '-lc',
            shell_prefix
            + "ros2 run makimate_vision face_tracker --ros-args "
              "-p input_image_topic:=/camera/image_raw "
              "-p output_image_topic:=/camera/face_image "
              "-p show_debug_window:=true "
              "-p detect_every_n:=5 "
              "-p downscale_factor:=0.3 "
              "-p roi_expansion:=0.5 "
              "-p full_frame_every:=20"
        ],
        output='screen',
    )

    # 6) Face → Maki bridge (bbox -> /maki/face_pos)
    face_to_maki = ExecuteProcess(
        cmd=[
            'bash',
            '-lc',
            shell_prefix
            + "ros2 run makimate_vision face_to_maki --ros-args "
              "-p image_width:=640 "
              "-p image_height:=480"
        ],
        output='screen',
    )

    # 7) Auto-start face tracking behavior once: look_at_user
    auto_look_at_user = ExecuteProcess(
        cmd=[
            'bash',
            '-lc',
            shell_prefix
            + "sleep 5 && "
              "ros2 topic pub /maki/behavior std_msgs/String "
              "\"data: 'look_at_user'\" --once"
        ],
        output='screen',
    )

    return LaunchDescription([
        LogInfo(msg='Starting Maki DEMO stack: motors + camera + face tracking'),
        dxl_controller,
        dxl_expressions,
        behavior_node,
        camera_node,
        face_tracker,
        face_to_maki,
        auto_look_at_user,
    ])
