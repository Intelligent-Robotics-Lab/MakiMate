import rclpy
from rclpy.node import Node

class Hello(Node):
    def __init__(self):
        super().__init__('hello_node')
        self.timer = self.create_timer(1.0, self.tick)
    def tick(self):
        self.get_logger().info('Hello from MakiMate!')

def main():
    rclpy.init()
    node = Hello()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
