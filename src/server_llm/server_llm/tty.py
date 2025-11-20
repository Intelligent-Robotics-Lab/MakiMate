import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class LLMTty(Node):
    """
    Simple TTY-style viewer for /llm/stream.
    Prints streaming chunks in-place (no extra newlines).
    """

    def __init__(self):
        super().__init__('llm_tty')
        self.declare_parameter('stream_topic', '/llm/stream')
        topic = self.get_parameter('stream_topic').get_parameter_value().string_value
        self.sub = self.create_subscription(String, topic, self._on_chunk, 10)
        self.get_logger().info(f"Listening to streaming topic: {topic}")

    def _on_chunk(self, msg: String):
        text = msg.data
        # If we want newline tokens to actually break the line:
        if text == "\n":
            print()
            sys.stdout.flush()
        else:
            print(text, end="", flush=True)

def main(args=None):
    rclpy.init(args=args)
    node = LLMTty()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
