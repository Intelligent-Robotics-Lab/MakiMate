import os
from typing import Tuple, Optional, List

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

from std_msgs.msg import Int32MultiArray, Bool

import cv2


class FaceTracker(Node):
    """
    Subscribes to a camera image, detects faces, and publishes:
      - processed image with boxes
      - largest face bbox

    NOW MODIFIED:
      - Tracking OUTPUTS only occur when /maki/awake == True
      - When asleep, no bbox and no face_image is published
    """

    def __init__(self):
        super().__init__('face_tracker')

        # ---- Awake flag ----
        self.awake = False
        self.awake_sub = self.create_subscription(
            Bool,
            '/maki/awake',
            self._on_awake,
            10
        )
        self.get_logger().info("FaceTracker: listening to /maki/awake")

        # Parameters
        self.declare_parameter('input_image_topic', '/camera/image_raw')
        self.declare_parameter('output_image_topic', '/camera/face_image')
        self.declare_parameter(
            'cascade_path',
            '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
        )
        self.declare_parameter('show_debug_window', False)

        self.declare_parameter('detect_every_n', 5)
        self.declare_parameter('downscale_factor', 0.3)
        self.declare_parameter('roi_expansion', 0.5)
        self.declare_parameter('full_frame_every', 20)

        self.declare_parameter('largest_face_topic', '/maki/largest_face_bbox')

        self.input_topic = self.get_parameter('input_image_topic').value
        self.output_topic = self.get_parameter('output_image_topic').value
        self.cascade_path = self.get_parameter('cascade_path').value
        self.show_debug = bool(self.get_parameter('show_debug_window').value)

        self.detect_every_n = int(self.get_parameter('detect_every_n').value)
        self.downscale_factor = float(self.get_parameter('downscale_factor').value)
        self.roi_expansion = float(self.get_parameter('roi_expansion').value)
        self.full_frame_every = int(self.get_parameter('full_frame_every').value)

        self.largest_face_topic = self.get_parameter('largest_face_topic').value

        self.bridge = CvBridge()

        # State
        self.frame_count = 0
        self.last_faces: List[Tuple[int, int, int, int]] = []
        self.last_largest_face: Optional[Tuple[int, int, int, int]] = None

        # Load Haar cascade
        if not os.path.exists(self.cascade_path):
            self.get_logger().error(
                f"Face cascade not found at {self.cascade_path}. "
                f"Install opencv data or pass cascade_path parameter."
            )
            self.face_cascade = None
        else:
            self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
            if self.face_cascade.empty():
                self.get_logger().error(
                    f"Failed to load cascade from {self.cascade_path}"
                )
                self.face_cascade = None
            else:
                self.get_logger().info(
                    f"Loaded face cascade from {self.cascade_path}"
                )

        # QoS to avoid backlog
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self.sub = self.create_subscription(
            Image,
            self.input_topic,
            self.image_callback,
            qos_profile,
        )

        self.pub = self.create_publisher(Image, self.output_topic, 10)

        self.largest_face_pub = self.create_publisher(
            Int32MultiArray, self.largest_face_topic, 10
        )

        self.get_logger().info("FaceTracker initialized.")

    # --------------------------
    #   Awake callback
    # --------------------------
    def _on_awake(self, msg: Bool):
        self.awake = bool(msg.data)
        self.get_logger().info(f"FaceTracker: awake = {self.awake}")

    # --------------------------
    #   Image callback
    # --------------------------
    def image_callback(self, msg: Image):
        if self.face_cascade is None:
            return

        # DEBUG: log first few frames
        if self.frame_count < 10:
            self.get_logger().info(
                f"image_callback: frame_count={self.frame_count}, awake={self.awake}"
            )

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"cv_bridge conversion failed: {e}")
            return

        self.frame_count += 1

        # Still run detection (we can disable later if you want)
        run_detection = (
            self.frame_count % self.detect_every_n == 0 or
            (self.full_frame_every > 0 and self.frame_count % self.full_frame_every == 0)
        )

        if run_detection:
            self.last_faces = self.detect_faces(frame)
            self.last_largest_face = self.pick_largest(self.last_faces)

        # --------------------------
        # IF SLEEPING → SUPPRESS ALL OUTPUTS
        # --------------------------
        if not self.awake:
            # Publish "no face" so behavior node knows not to move
            bbox_msg = Int32MultiArray()
            bbox_msg.data = [-1, -1, -1, -1]
            self.largest_face_pub.publish(bbox_msg)
            return

        # --------------------------
        # Awake → publish tracking outputs
        # --------------------------

        # Draw faces
        for (x, y, w, h) in self.last_faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Publish processed image
        try:
            out_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            out_msg.header = msg.header
            self.pub.publish(out_msg)
        except Exception as e:
            self.get_logger().error(f"cv_bridge to Image failed: {e}")

        # Publish bbox
        bbox_msg = Int32MultiArray()
        if self.last_largest_face is not None:
            x, y, w, h = self.last_largest_face
            bbox_msg.data = [x, y, w, h]
        else:
            bbox_msg.data = [-1, -1, -1, -1]
        self.largest_face_pub.publish(bbox_msg)

    # --------------------------
    # Helper functions
    # --------------------------
    def pick_largest(self, faces):
        if not faces:
            return None
        return max(faces, key=lambda r: r[2] * r[3])

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h_img, w_img = gray.shape[:2]
        scale = self.downscale_factor

        faces_full = []

        # If we have a last face, try ROI first
        use_roi = (
            self.last_largest_face is not None
            and not (self.full_frame_every > 0 and self.frame_count % self.full_frame_every == 0)
        )

        if use_roi:
            x, y, w, h = self.last_largest_face
            expand_x = int(w * self.roi_expansion)
            expand_y = int(h * self.roi_expansion)

            x0 = max(0, x - expand_x)
            y0 = max(0, y - expand_y)
            x1 = min(w_img, x + w + expand_x)
            y1 = min(h_img, y + h + expand_y)

            roi_gray = gray[y0:y1, x0:x1]
            roi_small = cv2.resize(roi_gray, None, fx=scale, fy=scale)

            faces_roi = self.face_cascade.detectMultiScale(
                roi_small, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30)
            )
            for fx, fy, fw, fh in faces_roi:
                faces_full.append((
                    int(fx / scale) + x0,
                    int(fy / scale) + y0,
                    int(fw / scale),
                    int(fh / scale)
                ))

            if faces_full:
                return faces_full

        # Full-frame search
        small_gray = cv2.resize(gray, None, fx=scale, fy=scale)
        faces = self.face_cascade.detectMultiScale(
            small_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        for (x, y, w, h) in faces:
            faces_full.append((
                int(x / scale),
                int(y / scale),
                int(w / scale),
                int(h / scale)
            ))

        return faces_full


def main(args=None):
    rclpy.init(args=args)
    node = FaceTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.show_debug:
            cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
