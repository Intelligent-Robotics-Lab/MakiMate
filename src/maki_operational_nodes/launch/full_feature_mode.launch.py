from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description():
    # Placeholder launch file for FULL-FEATURE mode.
    # Later you can add ASR + LLM + TTS + behaviors + expressions here.
    return LaunchDescription([
        LogInfo(msg='Full-feature mode stack launch (placeholder) started.'),
    ])
