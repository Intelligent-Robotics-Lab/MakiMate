import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class LLMSay(Node):
    def __init__(self):
        super().__init__('llm_say')
        self.declare_parameter('request_topic', '/llm/request')
        topic = self.get_parameter('request_topic').get_parameter_value().string_value
        self.pub = self.create_publisher(String, topic, 10)

        # Determine the text to send
        text = "how are you" if len(sys.argv) < 2 else " ".join(sys.argv[1:])
        self.get_logger().info(f"Publishing prompt: {text!r} to {topic}")
        self.pub.publish(String(data=text))

        # give DDS a moment to ship the message
        self.create_timer(0.5, self._shutdown)

    def _shutdown(self):
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = LLMSay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
