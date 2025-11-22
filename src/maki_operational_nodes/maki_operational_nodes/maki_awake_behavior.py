import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String


class MakiAwakeBehavior(Node):
    """
    Listens to /maki/awake and drives /maki/expression.

    - When Maki is asleep (False) -> send 'sleepy'
    - When Maki wakes up (True) -> send 'wide_awake'
    - While Maki is asleep, we periodically resend 'sleepy'
      so that on startup (when other nodes might come up late)
      he will eventually settle into the sleep pose.
    """

    def __init__(self):
        super().__init__('maki_awake_behavior')

        # Parameters
        self.declare_parameter('awake_topic', '/maki/awake')
        self.declare_parameter('expression_topic', '/maki/expression')

        awake_topic = self.get_parameter('awake_topic').value
        expression_topic = self.get_parameter('expression_topic').value

        self.get_logger().info(
            f"MakiAwakeBehavior: listening to {awake_topic}, "
            f"publishing expressions on {expression_topic}"
        )

        # Pub/sub
        self._expr_pub = self.create_publisher(String, expression_topic, 10)
        self._awake_sub = self.create_subscription(
            Bool,
            awake_topic,
            self._on_awake,
            10,
        )

        # Track awake state
        self._awake = False
        self._last_awake = None

        # Periodic timer to "enforce" sleepy pose while asleep
        # (runs every 2 seconds, but only sends when _awake == False)
        self._sleep_enforcer_timer = self.create_timer(2.0, self._sleep_enforcer_cb)

    # ------------------------------------------------------------------ #
    # Timer: periodically keep sleepy pose while asleep
    # ------------------------------------------------------------------ #
    def _sleep_enforcer_cb(self):
        # If we are asleep, periodically re-send 'sleepy'.
        # This fixes startup races: once DXL+expressions are ready,
        # one of these will move the robot into the sleep pose.
        if not self._awake:
            self.get_logger().debug("Enforcing sleepy pose while asleep.")
            self._send_expression('sleepy')

    # ------------------------------------------------------------------ #
    # /maki/awake callback
    # ------------------------------------------------------------------ #
    def _on_awake(self, msg: Bool):
        awake = bool(msg.data)

        # Only react to actual changes
        if self._last_awake is not None and awake == self._last_awake:
            return

        self._last_awake = awake
        self._awake = awake

        if awake:
            self.get_logger().info("Maki woke up -> wide_awake expression.")
            self._send_expression('wide_awake')
        else:
            self.get_logger().info("Maki went to sleep -> sleepy expression.")
            self._send_expression('sleepy')

    # ------------------------------------------------------------------ #
    # Helper to send expression names
    # ------------------------------------------------------------------ #
    def _send_expression(self, name: str):
        msg = String()
        msg.data = name
        self._expr_pub.publish(msg)
        self.get_logger().info(f"Requested expression: {name!r}")


def main(args=None):
    rclpy.init(args=args)
    node = MakiAwakeBehavior()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
