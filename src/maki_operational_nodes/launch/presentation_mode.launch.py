from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description():
    # Placeholder launch file for PRESENTATION mode.
    # Add nodes here later (e.g., scripted motions, limited ASR, etc.).
    return LaunchDescription([
        LogInfo(msg='Presentation mode stack launch (placeholder) started.'),
    ])
