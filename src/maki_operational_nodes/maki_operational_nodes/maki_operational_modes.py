import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

VALID_MODES = {"demo", "presentation", "full-feature"}


class MakiOperationalModes(Node):
    """
    High-level mode selector for Maki.

    Modes:
      - demo: enable face tracking via maki_expression / maki_behavior
      - presentation: placeholder for future behavior
      - full-feature: placeholder for full ASR + behaviors

    Interfaces:
      - Input:
          /maki/set_mode (std_msgs/String)  -> requests mode change
      - Output:
          /maki/mode      (std_msgs/String) -> current active mode
          /maki/face_tracking_enable (std_msgs/Bool) -> demo mode face tracking
    """

    def __init__(self) -> None:
        super().__init__('maki_operational_modes')

        # Parameters
        self.declare_parameter('mode', 'demo')
        self.declare_parameter('mode_topic', '/maki/mode')
        self.declare_parameter('set_mode_topic', '/maki/set_mode')
        self.declare_parameter('face_tracking_topic', '/maki/face_tracking_enable')

        self.mode = self.get_parameter('mode').value
        self.mode_topic = self.get_parameter('mode_topic').value
        self.set_mode_topic = self.get_parameter('set_mode_topic').value
        self.face_tracking_topic = self.get_parameter('face_tracking_topic').value

        # Publishers
        self.mode_pub = self.create_publisher(String, self.mode_topic, 10)
        self.face_tracking_pub = self.create_publisher(Bool, self.face_tracking_topic, 10)

        # Subscribers
        self.mode_sub = self.create_subscription(
            String,
            self.set_mode_topic,
            self._on_set_mode_msg,
            10,
        )

        self.get_logger().info(f"MakiOperationalModes started with initial mode: {self.mode!r}")
        self.get_logger().info(f"Publishing current mode on: {self.mode_topic}")
        self.get_logger().info(f"Listening for mode changes on: {self.set_mode_topic}")
        self.get_logger().info(f"Face tracking control topic: {self.face_tracking_topic}")

        # Apply initial mode on startup
        self._apply_mode(self.mode)

    # -----------------------
    # Mode change handling
    # -----------------------
    def _on_set_mode_msg(self, msg: String) -> None:
        new_mode = msg.data.strip().lower()
        if not new_mode:
            return

        if new_mode not in VALID_MODES:
            self.get_logger().warn(
                f"Requested unknown mode {new_mode!r}. "
                f"Valid modes: {sorted(VALID_MODES)}"
            )
            return

        if new_mode == self.mode:
            self.get_logger().info(f"Mode already {new_mode!r}, ignoring request.")
            return

        self.get_logger().info(f"Mode change requested: {self.mode!r} -> {new_mode!r}")
        self.mode = new_mode

        # Reflect into parameter for introspection
        self.set_parameters([rclpy.parameter.Parameter(
            'mode',
            rclpy.parameter.Parameter.Type.STRING,
            self.mode,
        )])

        self._apply_mode(self.mode)

    def _apply_mode(self, mode: str) -> None:
        """
        Central place where each mode's behavior is defined.
        """
        self.get_logger().info(f"Applying mode: {mode!r}")

        # Reset or adjust things that depend on the mode
        if mode == "demo":
            self._enter_demo_mode()
        elif mode == "presentation":
            self._enter_presentation_mode()
        elif mode == "full-feature":
            self._enter_full_feature_mode()
        else:
            self.get_logger().warn(f"Mode {mode!r} not implemented.")

        # Always publish the newly active mode
        self._publish_mode(mode)

    # -----------------------
    # Individual mode logic
    # -----------------------
    def _enter_demo_mode(self) -> None:
        """
        DEMO MODE:
          - Turn on face tracking via maki_expression / maki_behavior.
        """
        self.get_logger().info("Entering DEMO mode: enabling face tracking.")
        self._set_face_tracking(True)

    def _enter_presentation_mode(self) -> None:
        """
        PRESENTATION MODE:
          Placeholder. Add specific behavior later.
        """
        self.get_logger().info("Entering PRESENTATION mode (currently no-op).")
        # Example: disable face tracking for now
        self._set_face_tracking(False)

    def _enter_full_feature_mode(self) -> None:
        """
        FULL-FEATURE MODE:
          Placeholder for full ASR + LLM + behaviors.
        """
        self.get_logger().info("Entering FULL-FEATURE mode (currently no-op).")
        # Example: enable face tracking as well
        self._set_face_tracking(True)

    # -----------------------
    # Helpers
    # -----------------------
    def _set_face_tracking(self, enabled: bool) -> None:
        msg = Bool()
        msg.data = bool(enabled)
        self.face_tracking_pub.publish(msg)
        state = "ON" if enabled else "OFF"
        self.get_logger().info(f"Face tracking set to: {state} on {self.face_tracking_topic}")

    def _publish_mode(self, mode: str) -> None:
        msg = String()
        msg.data = mode
        self.mode_pub.publish(msg)
        self.get_logger().info(f"Published active mode: {mode!r} on {self.mode_topic}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MakiOperationalModes()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
