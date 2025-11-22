#!/usr/bin/env python3
import os
import yaml
from typing import Dict, List

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray


class MakiExpressions(Node):
    """
    Loads named expressions from a YAML file and plays them by publishing
    Float64MultiArray joint goals to /maki/joint_goals.

    YAML format:

    neutral:
      joints: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    happy:
      joints: [10.0, -5.0, 5.0, 0.0, 10.0, 10.0]
    """

    def __init__(self) -> None:
        super().__init__('maki_expressions')

        # Parameters
        self.declare_parameter(
            'expression_file',
            # default path – change if you move the yaml
            os.path.expanduser(
                '~/MakiMate/src/makimate_dxl/makimate_dxl/expressions.yaml'
            )
        )
        self.declare_parameter('expression_topic', '/maki/expression')
        self.declare_parameter('joint_goal_topic', '/maki/joint_goals')

        expr_file = self.get_parameter('expression_file').value
        expr_topic = self.get_parameter('expression_topic').value
        joint_topic = self.get_parameter('joint_goal_topic').value

        self.get_logger().info(f"Loading expressions from: {expr_file}")
        self.expressions: Dict[str, List[float]] = {}
        self._load_expressions(expr_file)

        # Publisher for joint goals
        self.joint_pub = self.create_publisher(Float64MultiArray, joint_topic, 10)
        self.get_logger().info(f"Publishing joint goals on: {joint_topic}")

        # Subscriber: which expression to play
        self.sub = self.create_subscription(
            String,
            expr_topic,
            self._on_expression,
            10,
        )
        self.get_logger().info(f"Listening for expressions on: {expr_topic}")

        if self.expressions:
            self.get_logger().info(
                f"Available expressions: {', '.join(sorted(self.expressions.keys()))}"
            )
        else:
            self.get_logger().warn("No expressions loaded!")

    def _load_expressions(self, path: str) -> None:
        if not os.path.exists(path):
            self.get_logger().error(f"Expression file not found: {path}")
            return

        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            self.get_logger().error(f"Failed to read expression file: {e}")
            return

        count = 0
        for name, entry in data.items():
            if not isinstance(entry, dict):
                self.get_logger().warn(f"Expression {name!r} is not a dict, skipping.")
                continue

            joints = entry.get('joints')
            if not isinstance(joints, list) or len(joints) != 6:
                self.get_logger().warn(
                    f"Expression {name!r} must have 'joints: [6 values]', skipping."
                )
                continue

            try:
                vals = [float(x) for x in joints]
            except Exception:
                self.get_logger().warn(
                    f"Expression {name!r} joints are not all numeric, skipping."
                )
                continue

            self.expressions[name.lower()] = vals
            count += 1

        self.get_logger().info(f"Loaded {count} expressions from {path}")

    def _on_expression(self, msg: String) -> None:
        name_raw = msg.data.strip()
        if not name_raw:
            return

        name = name_raw.lower()
        if name not in self.expressions:
            self.get_logger().warn(
                f"Requested expression {name_raw!r} not found. "
                f"Known: {', '.join(sorted(self.expressions.keys()))}"
            )
            return

        joints = self.expressions[name]
        self._publish_joints(joints)
        self.get_logger().info(
            f"Played expression {name_raw!r} with joints {joints}"
        )

    def _publish_joints(self, joints: List[float]) -> None:
        msg = Float64MultiArray()
        msg.data = joints
        self.joint_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MakiExpressions()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
