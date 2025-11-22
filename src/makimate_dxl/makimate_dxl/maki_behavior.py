#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray, Bool


class MakiBehavior(Node):
    def __init__(self):
        super().__init__('maki_behavior')

        # --- Awake state (from /maki/awake) ---
        self.awake = False
        self.awake_sub = self.create_subscription(
            Bool,
            '/maki/awake',
            self.on_awake,
            10
        )

        # Subscriber for behavior commands
        self.behavior_sub = self.create_subscription(
            String,
            '/maki/behavior',
            self.on_behavior,
            10
        )

        # Publisher for joint goals
        self.pub = self.create_publisher(Float64MultiArray, '/maki/joint_goals', 10)

        # Publisher to expression node (for maki_stop → listening)
        self.expr_pub = self.create_publisher(String, '/maki/expression', 10)

        # Timer handles
        self._timers = []
        self.phase = 0.0

        # Face tracking (for look_at_user behavior)
        self.look_at_user_enabled = False
        self.yaw_cmd = 0.0
        self.pitch_cmd = 0.0
        self.last_yaw = 0.0
        self.last_pitch = 0.0

        # Subscribe to face position from vision pipeline
        self.face_pos_sub = self.create_subscription(
            Float64MultiArray,
            '/maki/face_pos',
            self.on_face_pos,
            10
        )

        self.get_logger().info("MakiBehavior ready. Waiting for /maki/behavior commands.")

    # ------------ AWAKE HANDLER ------------ #
    def on_awake(self, msg: Bool):
        """
        Automatically toggle look-at-user tracking based on /maki/awake.
        """
        self.awake = msg.data

        if self.awake:
            # When we wake up, begin tracking the user
            self.start_look_at_user()
            self.get_logger().info("Awake -> enabling look_at_user tracking.")
        else:
            # When we go to sleep, stop tracking
            if self.look_at_user_enabled:
                self.get_logger().info("Asleep -> disabling look_at_user tracking.")
            self.look_at_user_enabled = False

    # Helper to publish joint goals
    def send(self, arr):
        msg = Float64MultiArray()
        msg.data = arr
        self.pub.publish(msg)

    # Stop all active behaviors
    def stop_all(self):
        for t in self._timers:
            t.cancel()
        self._timers.clear()
        self.phase = 0.0
        self.look_at_user_enabled = False
        self.get_logger().info("Stopped all behaviors.")

    # Dispatcher
    def on_behavior(self, msg: String):
        behavior = msg.data.strip().lower()
        self.get_logger().info(f"Behavior command received: {behavior!r}")

        self.stop_all()

        if behavior == "find_me":
            self.start_find_me()

        elif behavior == "circle_scan":
            self.start_circle_scan()

        elif behavior == "eye_scan":
            self.start_eye_scan()

        elif behavior == "blink_loop":
            self.start_blink_loop()

        elif behavior == "idle_breathe":
            self.start_idle_breathe()

        elif behavior == "nod_yes":
            self.start_nod_yes()

        elif behavior == "shake_no" or behavior == "calm_shake_no":
            self.start_calm_shake_no()

        elif behavior == "big_shake_no":
            self.start_big_shake_no()

        elif behavior == "look_at_user":
            # Manual override if you ever want to trigger it explicitly
            self.start_look_at_user()

        elif behavior == "maki_stop":
            self.expr_pub.publish(String(data='listening'))

        else:
            self.get_logger().warn(f"Unknown behavior: {behavior}")

    # ============= BEHAVIORS ============= #

    def start_find_me(self):
        def step_timer():
            self.phase += 0.035
            yaw = 18.0 * math.sin(self.phase)
            arr = [yaw, 0.0, 0.0, 0.0, 20.0, -20.0]
            self.send(arr)
        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    def start_circle_scan(self):
        def step_timer():
            self.phase += 0.05
            yaw = 15.0 * math.sin(self.phase)
            pitch = 8.0 * math.cos(self.phase)
            arr = [yaw, pitch, 0.0, 0.0, 20.0, -20.0]
            self.send(arr)
        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    def start_eye_scan(self):
        def step_timer():
            self.phase += 0.08
            eye_yaw = 20.0 * math.sin(self.phase)
            eye_pitch = 5.0 * math.cos(self.phase)
            arr = [0.0, 0.0, eye_pitch, eye_yaw, 20.0, -20.0]
            self.send(arr)
        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    def start_blink_loop(self):
        counter = {"t": 0}

        def step_timer():
            counter["t"] += 1
            t = counter["t"] % 60

            if t < 5:
                arr = [0.0, 0.0, 0.0, 0.0, -18.0, 22.0]
            elif t < 10:
                arr = [0.0, 0.0, 0.0, 0.0, 20.0, -20.0]
            else:
                arr = [0.0, 0.0, 0.0, 0.0, 10.0, -9.0]

            self.send(arr)

        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    def start_idle_breathe(self):
        def step_timer():
            self.phase += 0.015
            pitch = 3.0 * math.sin(self.phase)
            flutter = 6.0 * math.sin(self.phase * 0.7)
            left_lid = 20.0 + flutter
            right_lid = -20.0 - flutter
            arr = [0.0, pitch, 0.0, 0.0, left_lid, right_lid]
            self.send(arr)
        t = self.create_timer(0.04, step_timer)
        self._timers.append(t)

    def start_nod_yes(self):
        def step_timer():
            self.phase += 0.10
            pitch = -10.0 * math.cos(self.phase)
            arr = [0.0, pitch, 0.0, 0.0, 16.0, -16.0]
            self.send(arr)
        t = self.create_timer(0.03, step_timer)
        self._timers.append(t)

    def start_calm_shake_no(self):
        def step_timer():
            self.phase += 0.055
            yaw = 9.0 * math.sin(self.phase)
            eye_yaw = -yaw
            arr = [yaw, 0.0, 0.0, eye_yaw, 20.0, -20.0]
            self.send(arr)
        t = self.create_timer(0.04, step_timer)
        self._timers.append(t)

    def start_big_shake_no(self):
        import random
        state = {
            "yaw": 0.0,
            "target": 12.0,
            "dwell": 0,
            "eye_yaw": 0.0,
            "blink_t": 0,
            "blink_interval": random.randint(120, 240),
        }

        def step_timer():
            alpha = 0.28
            yaw = state["yaw"] + alpha * (state["target"] - state["yaw"])
            state["yaw"] = yaw

            if abs(state["target"] - yaw) < 1.0:
                state["dwell"] += 1
                if state["dwell"] > 5:
                    state["target"] = -state["target"]
                    state["dwell"] = 0

            target_eye_yaw = -1.35 * yaw
            eye_alpha = 0.35
            eye_yaw = (
                eye_alpha * target_eye_yaw
                + (1 - eye_alpha) * state["eye_yaw"]
            )
            state["eye_yaw"] = eye_yaw

            state["blink_t"] += 1
            if state["blink_t"] >= state["blink_interval"]:
                b = state["blink_t"] - state["blink_interval"]
                if b < 6:
                    lid_left = -14.0
                    lid_right = 18.0
                elif b < 12:
                    lid_left = 20.0
                    lid_right = -20.0
                else:
                    state["blink_t"] = 0
                    state["blink_interval"] = random.randint(120, 240)
                    lid_left = 8.0
                    lid_right = -9.0
            else:
                lid_left = 8.0
                lid_right = -9.0

            arr = [yaw, 0.0, 0.0, eye_yaw, lid_left, lid_right]
            self.send(arr)

        t = self.create_timer(0.045, step_timer)
        self._timers.append(t)

    # ------------ LOOK_AT_USER ------------ #
    def start_look_at_user(self):
        self.look_at_user_enabled = True
        self.yaw_cmd = self.last_yaw
        self.pitch_cmd = self.last_pitch
        self.get_logger().info("Look-at-user mode enabled.")

    def on_face_pos(self, msg: Float64MultiArray):
        if not self.look_at_user_enabled:
            return

        if len(msg.data) != 2:
            return

        x, y = msg.data
        DEADZONE = 0.05
        if abs(x) < DEADZONE:
            x = 0.0
        if abs(y) < DEADZONE:
            y = 0.0

        MAX_YAW = 38.0
        MAX_PITCH = 16.0
        K_YAW = 1.0
        K_PITCH = 0.8

        # Note: x>0 means face is to the right → negative yaw_cmd to turn right (depending on your frame)
        self.yaw_cmd += K_YAW * (-x)
        self.pitch_cmd += K_PITCH * (-y)

        self.yaw_cmd = max(-MAX_YAW, min(MAX_YAW, self.yaw_cmd))
        self.pitch_cmd = max(-MAX_PITCH, min(MAX_PITCH, self.pitch_cmd))

        self.last_yaw = self.yaw_cmd
        self.last_pitch = self.pitch_cmd

        arr = [self.yaw_cmd, self.pitch_cmd, 0.0, 0.0, 20.0, -20.0]
        self.send(arr)


def main(args=None):
    rclpy.init(args=args)
    node = MakiBehavior()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
