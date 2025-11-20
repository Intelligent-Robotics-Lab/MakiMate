import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool

try:
    from pixel_ring import pixel_ring
except ImportError:
    pixel_ring = None


class ASRLEDController(Node):
    def __init__(self):
        super().__init__('asr_led_controller')

        self.declare_parameter('enable_topic', '/asr/enable')
        self.enable_topic = self.get_parameter('enable_topic').value

        self.get_logger().info(f"ASRLEDController listening on: {self.enable_topic}")

        if pixel_ring is None:
            self.get_logger().warn(
                "pixel_ring library not found. LED control is disabled. "
                "Make sure it is installed in asr_venv."
            )
            self.led_available = False
        else:
            self.led_available = True
            # Optional: set a default brightness
            try:
                pixel_ring.set_brightness(16)
            except Exception as e:
                self.get_logger().warn(f"Could not set brightness: {e}")

        self.sub = self.create_subscription(
            Bool,
            self.enable_topic,
            self._on_enable,
            10,
        )

    def _on_enable(self, msg: Bool):
        enabled = bool(msg.data)
        self.get_logger().info(f"ASR enable changed: {enabled}")
        self._set_led_enabled(enabled)

    def _set_led_enabled(self, enabled: bool):
        if not self.led_available:
            return

        try:
            if enabled:
                # Show “listening” pattern when ASR is on
                self.get_logger().info("Turning ASR LEDs ON (listen mode).")
                pixel_ring.listen()   # or pixel_ring.mono(0x0000ff) if you prefer solid blue
            else:
                self.get_logger().info("Turning ASR LEDs OFF.")
                pixel_ring.off()
        except Exception as e:
            self.get_logger().error(f"Error while controlling LEDs: {e}")



def main(args=None):
    rclpy.init(args=args)
    node = ASRLEDController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
