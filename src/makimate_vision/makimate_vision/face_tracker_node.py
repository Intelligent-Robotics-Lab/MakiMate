import os
from typing import Tuple, Optional, List

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

from std_msgs.msg import Int32MultiArray

import cv2


class FaceTracker(Node):
    """
    Subscribes to a camera image, runs face detection at a reduced rate,
    and republishes an image with squares drawn around all detected faces.

    It also publishes the bounding box of the largest face as:
      Int32MultiArray [x, y, w, h]
    """

    def __init__(self):
        super().__init__('face_tracker')

        # Parameters
        self.declare_parameter('input_image_topic', '/camera/image_raw')
        self.declare_parameter('output_image_topic', '/camera/face_image')
        self.declare_parameter(
            'cascade_path',
            '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
        )
        self.declare_parameter('show_debug_window', False)

        # How often to run detection / how we speed it up
        self.declare_parameter('detect_every_n', 5)        # detect every N frames
        self.declare_parameter('downscale_factor', 0.3)    # 0.3–0.4 works well
        self.declare_parameter('roi_expansion', 0.5)       # expand ROI around last face
        self.declare_parameter('full_frame_every', 20)     # force full-frame search sometimes

        # Topic for largest face bbox
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

        # Subscriber and publisher (keep only latest frame to avoid backlog)
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

        # Publisher for largest face bbox [x, y, w, h]
        self.largest_face_pub = self.create_publisher(
            Int32MultiArray, self.largest_face_topic, 10
        )

        self.get_logger().info(
            f"FaceTracker listening on {self.input_topic}, "
            f"publishing image to {self.output_topic}, "
            f"largest face bbox to {self.largest_face_topic}. "
            f"detect_every_n={self.detect_every_n}, "
            f"downscale_factor={self.downscale_factor}"
        )

    def image_callback(self, msg: Image):
        if self.face_cascade is None:
            return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"cv_bridge conversion failed: {e}")
            return

        self.frame_count += 1

        # Decide whether to run detection on this frame
        run_detection = False
        if self.frame_count % self.detect_every_n == 0:
            run_detection = True
        if self.full_frame_every > 0 and self.frame_count % self.full_frame_every == 0:
            run_detection = True

        if run_detection:
            self.last_faces = self.detect_faces(frame)
            self.last_largest_face = self.pick_largest(self.last_faces)

        # Draw all known faces
        for (x, y, w, h) in self.last_faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Optional low-latency preview
        if self.show_debug:
            cv2.imshow("Face Tracker", frame)
            cv2.waitKey(1)

        # Publish processed image
        try:
            out_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            out_msg.header = msg.header
            self.pub.publish(out_msg)
        except Exception as e:
            self.get_logger().error(f"cv_bridge to Image failed: {e}")

        # Publish largest face bbox [x, y, w, h] or [-1, -1, -1, -1] if none
        bbox_msg = Int32MultiArray()
        if self.last_largest_face is not None:
            x, y, w, h = self.last_largest_face
            bbox_msg.data = [int(x), int(y), int(w), int(h)]
        else:
            bbox_msg.data = [-1, -1, -1, -1]
        self.largest_face_pub.publish(bbox_msg)

    def pick_largest(
        self, faces: List[Tuple[int, int, int, int]]
    ) -> Optional[Tuple[int, int, int, int]]:
        if not faces:
            return None
        return max(faces, key=lambda r: r[2] * r[3])

    def detect_faces(self, frame) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces and return a list of bounding boxes (x, y, w, h)
        in original image coordinates.

        Uses:
        - ROI search around previous largest face when possible.
        - Full-frame search periodically or when no face is known.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h_img, w_img = gray.shape[:2]

        scale = self.downscale_factor
        if scale <= 0.0 or scale >= 1.0:
            scale = 0.3

        faces_full: List[Tuple[int, int, int, int]] = []

        # Try ROI search if we had a face and this is not a forced full-frame scan
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
            roi_small = cv2.resize(
                roi_gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR
            )

            faces_roi = self.face_cascade.detectMultiScale(
                roi_small,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(30, 30),
            )

            for (fx, fy, fw, fh) in faces_roi:
                fx_full = int(fx / scale) + x0
                fy_full = int(fy / scale) + y0
                fw_full = int(fw / scale)
                fh_full = int(fh / scale)
                faces_full.append((fx_full, fy_full, fw_full, fh_full))

            # If ROI found faces, return them
            if faces_full:
                return faces_full

            # Otherwise, fall through to full-frame search

        # Full-frame search
        small_gray = cv2.resize(
            gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR
        )

        faces = self.face_cascade.detectMultiScale(
            small_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )

        for (x, y, w, h) in faces:
            x_full = int(x / scale)
            y_full = int(y / scale)
            w_full = int(w / scale)
            h_full = int(h / scale)
            faces_full.append((x_full, y_full, w_full, h_full))

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
