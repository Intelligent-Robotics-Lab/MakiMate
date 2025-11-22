import subprocess
from typing import Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

VALID_MODES = {"demo", "presentation", "full-feature"}


class MakiLaunchManager(Node):
    """
    Listens to /maki/mode and launches/stops the appropriate ROS2 launch stack.

    For now:
      - demo         -> launches demo_asr_llm_tts.launch.py
      - presentation -> stops any running stack (placeholder)
      - full-feature -> stops any running stack (placeholder)
    """

    def __init__(self) -> None:
        super().__init__('maki_launch_manager')

        # Parameters for launch commands (you can adjust these later)
        self.declare_parameter(
            'demo_launch_cmd',
            "source /opt/ros/jazzy/setup.bash && "
            "source ~/MakiMate/install/setup.bash && "
            "ros2 launch maki_operational_nodes demo_mode.launch.py"
        )

        self.declare_parameter(
            'presentation_launch_cmd',
            "source /opt/ros/jazzy/setup.bash && "
            "source ~/MakiMate/install/setup.bash && "
            "ros2 launch maki_operational_nodes presentation_mode.launch.py"
        )

        self.declare_parameter(
            'full_feature_launch_cmd',
            "source /opt/ros/jazzy/setup.bash && "
            "source ~/MakiMate/install/setup.bash && "
            "ros2 launch maki_operational_nodes full_feature_mode.launch.py"
        )

        self.demo_launch_cmd = self.get_parameter('demo_launch_cmd').value
        self.presentation_launch_cmd = self.get_parameter('presentation_launch_cmd').value
        self.full_feature_launch_cmd = self.get_parameter('full_feature_launch_cmd').value

        self.mode_sub = self.create_subscription(
            String,
            '/maki/mode',
            self._on_mode,
            10,
        )

        self.current_mode: Optional[str] = None
        self.current_process: Optional[subprocess.Popen] = None

        self.get_logger().info("MakiLaunchManager initialized, waiting for /maki/mode messages.")

    # -----------------------
    # Mode callback
    # -----------------------
    def _on_mode(self, msg: String) -> None:
        new_mode = msg.data.strip().lower()
        if not new_mode:
            return

        if new_mode not in VALID_MODES:
            self.get_logger().warn(
                f"Launch manager received unknown mode {new_mode!r}. "
                f"Valid modes: {sorted(VALID_MODES)}"
            )
            return

        if new_mode == self.current_mode:
            # No change
            return

        self.get_logger().info(f"Launch manager: mode change {self.current_mode!r} -> {new_mode!r}")
        self._stop_current_stack()
        self.current_mode = new_mode
        self._start_stack_for_mode(new_mode)

    # -----------------------
    # Start/stop helpers
    # -----------------------
    def _start_stack_for_mode(self, mode: str) -> None:
        if mode == 'demo':
            launch_cmd = self.demo_launch_cmd
        elif mode == 'presentation':
            launch_cmd = self.presentation_launch_cmd
        elif mode == 'full-feature':
            launch_cmd = self.full_feature_launch_cmd
        else:
            self.get_logger().warn(f"No launch command configured for mode {mode!r}")
            return

        if not launch_cmd:
            self.get_logger().info(f"No launch stack configured for mode {mode!r} (doing nothing).")
            return

        shell_cmd = f"bash -lc '{launch_cmd}'"
        self.get_logger().info(f"Starting stack for mode {mode!r} with command: {shell_cmd}")

        try:
            # Start the launch as a background process
            self.current_process = subprocess.Popen(
                shell_cmd,
                shell=True
            )
        except Exception as e:
            self.get_logger().error(f"Failed to start launch stack for mode {mode!r}: {e}")
            self.current_process = None

    def _stop_current_stack(self) -> None:
        if self.current_process is None:
            return

        self.get_logger().info("Stopping current launch stack...")
        try:
            self.current_process.terminate()
            self.current_process.wait(timeout=10.0)
            self.get_logger().info("Launch stack terminated cleanly.")
        except subprocess.TimeoutExpired:
            self.get_logger().warn("Launch stack did not terminate, killing...")
            self.current_process.kill()
        except Exception as e:
            self.get_logger().error(f"Error while stopping launch stack: {e}")
        finally:
            self.current_process = None

    def destroy_node(self):
        # Ensure cleanup on shutdown
        self._stop_current_stack()
        super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MakiLaunchManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
