#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32MultiArray, Float64MultiArray, Bool


class FaceToMaki(Node):
    """
    Bridge node:

      - Subscribes to /maki/largest_face_bbox (Int32MultiArray: [x, y, w, h])
      - Publishes /maki/face_pos (Float64MultiArray: [x_offset, y_offset])

    x_offset, y_offset are normalized offsets in [-1, +1], where:
      x_offset < 0  => face is left of center
      x_offset > 0  => face is right of center
      y_offset > 0  => face is above center (Maki should look up)
      y_offset < 0  => face is below center (Maki should look down)

    These are consumed by the 'look_at_user' behavior in MakiBehavior.

    NOW MODIFIED:
      - Only publishes face_pos when /maki/awake == True
    """

    def __init__(self):
        super().__init__("face_to_maki")

        # ---- Awake state ----
        self.awake = False
        self.awake_sub = self.create_subscription(
            Bool,
            "/maki/awake",
            self._on_awake,
            10,
        )

        # Parameters
        self.declare_parameter("bbox_topic", "/maki/largest_face_bbox")
        self.declare_parameter("out_topic", "/maki/face_pos")

        # Match your camera settings: 640x480
        self.declare_parameter("image_width", 640)
        self.declare_parameter("image_height", 480)

        # Optional flips if you find directions inverted
        self.declare_parameter("invert_x", False)
        self.declare_parameter("invert_y", False)

        bbox_topic = self.get_parameter("bbox_topic").value
        out_topic = self.get_parameter("out_topic").value

        self.image_width = int(self.get_parameter("image_width").value)
        self.image_height = int(self.get_parameter("image_height").value)

        self.invert_x = bool(self.get_parameter("invert_x").value)
        self.invert_y = bool(self.get_parameter("invert_y").value)

        # Publisher to what MakiBehavior already listens to
        self.out_pub = self.create_publisher(Float64MultiArray, out_topic, 10)

        # Subscriber to face tracker bbox
        self.bbox_sub = self.create_subscription(
            Int32MultiArray,
            bbox_topic,
            self._on_bbox,
            10,
        )

        self.get_logger().info(
            f"FaceToMaki started.\n"
            f"  Subscribing bbox: {bbox_topic}\n"
            f"  Publishing face_pos: {out_topic}\n"
            f"  image_width={self.image_width}, image_height={self.image_height}"
        )

    # -------------------------
    # Awake callback
    # -------------------------
    def _on_awake(self, msg: Bool):
        self.awake = bool(msg.data)
        self.get_logger().info(f"FaceToMaki: awake = {self.awake}")

    # -------------------------
    # Bbox callback
    # -------------------------
    def _on_bbox(self, msg: Int32MultiArray):
        # If Maki is sleeping, don't send any tracking commands
        if not self.awake:
            return

        data = list(msg.data)
        if len(data) < 4:
            return

        x, y, w, h = data[0], data[1], data[2], data[3]

        # Face not found: your tracker uses [-1, -1, -1, -1]
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            # Option 1: do nothing => Maki holds last pose
            # Option 2: you could slowly move back to neutral here
            return

        if self.image_width <= 0 or self.image_height <= 0:
            self.get_logger().warn("Invalid image dimensions, skipping.")
            return

        # center of the face in pixel coordinates
        cx = x + w * 0.5
        cy = y + h * 0.5

        # convert to [-1,1] offsets from image center
        # x: left negative, right positive
        # y: up positive, down negative
        x_off = (cx - self.image_width / 2.0) / (self.image_width / 2.0)
        y_off = (self.image_height / 2.0 - cy) / (self.image_height / 2.0)

        if self.invert_x:
            x_off = -x_off
        if self.invert_y:
            y_off = -y_off

        # clamp to [-1, 1] just in case
        x_off = max(-1.0, min(1.0, x_off))
        y_off = max(-1.0, min(1.0, y_off))

        out = Float64MultiArray()
        out.data = [x_off, y_off]
        self.out_pub.publish(out)

        # Optional debug:
        # self.get_logger().info(
        #     f"bbox=({x},{y},{w},{h}) -> offsets=({x_off:.2f}, {y_off:.2f})"
        # )


def main(args=None):
    rclpy.init(args=args)
    node = FaceToMaki()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
