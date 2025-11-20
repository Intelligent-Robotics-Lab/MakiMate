from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='server_llm',
            executable='llm_bridge',
            name='llm_bridge',
            output='screen',
            parameters=[{
                # CHANGE THIS to your laptop IP/port
                'laptop_host': 'http://35.50.73.78:8000/',
                'endpoint_path': '/chat/stream',
                'request_topic': '/llm/request',
                'stream_topic': '/llm/stream',
                'response_topic': '/llm/response',
                'timeout_sec': 300.0,
            }]
        )
    ])
