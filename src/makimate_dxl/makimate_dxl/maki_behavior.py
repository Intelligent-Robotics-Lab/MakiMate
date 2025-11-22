#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray


class MakiBehavior(Node):
    def __init__(self):
        super().__init__('maki_behavior')

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

        # Our own list of active timers (don't clash with Node's internals)
        self._timers = []
        self.phase = 0.0

        # For simple smoothing of head/eye motion
        self.last_yaw = 0.0
        self.last_pitch = 0.0
        self.last_eye_yaw = 0.0
        self.last_eye_pitch = 0.0

        # Commanded head angles for look_at_user
        self.yaw_cmd = 0.0
        self.pitch_cmd = 0.0

        # Flag to gate look_at_user behavior
        self.look_at_user_enabled = False

        # Subscribe to face position (normalized [x, y]) for look_at_user
        # This subscription is always active, but only used when
        # look_at_user_enabled is True.
        self.face_pos_sub = self.create_subscription(
            Float64MultiArray,
            '/maki/face_pos',
            self.on_face_pos,
            10
        )

        self.get_logger().info("MakiBehavior ready. Listening on /maki/behavior")

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

        # Reset smoothing state so we don't "jump" from old values
        # Reset commanded head pose for look_at_user
        self.yaw_cmd = 0.0
        self.pitch_cmd = 0.0

        self.get_logger().info("Stopped all behaviors.")


    # Behavior dispatcher
    def on_behavior(self, msg: String):
        behavior = msg.data.strip().lower()
        self.get_logger().info(f"Received behavior command: {behavior!r}")

        # Always stop previous behavior
        self.stop_all()

        if behavior == "find_me":
            self.get_logger().info("Starting behavior: FIND_ME")
            self.start_find_me()

        elif behavior == "circle_scan":
            self.get_logger().info("Starting behavior: CIRCLE_SCAN")
            self.start_circle_scan()

        elif behavior == "eye_scan":
            self.get_logger().info("Starting behavior: EYE_SCAN")
            self.start_eye_scan()

        elif behavior == "blink_loop":
            self.get_logger().info("Starting behavior: BLINK_LOOP")
            self.start_blink_loop()

        elif behavior == "idle_breathe":
            self.get_logger().info("Starting behavior: IDLE_BREATHE")
            self.start_idle_breathe()

        elif behavior == "nod_yes":
            self.get_logger().info("Starting behavior: NOD_YES")
            self.start_nod_yes()

        # Old 'shake_no' now maps to the calm version by default
        elif behavior == "shake_no" or behavior == "calm_shake_no":
            self.get_logger().info("Starting behavior: CALM_SHAKE_NO")
            self.start_calm_shake_no()

        elif behavior == "big_shake_no":
            self.get_logger().info("Starting behavior: BIG_SHAKE_NO")
            self.start_big_shake_no()

        elif behavior == "look_at_user":
            self.get_logger().info("Starting behavior: LOOK_AT_USER")
            self.start_look_at_user()

        elif behavior == "maki_stop":
            self.get_logger().info("Behavior: MAKI_STOP → expression 'listening'")
            # Hand off to expression system
            self.expr_pub.publish(String(data='listening'))

        else:
            self.get_logger().warn(f"Unknown behavior: {behavior}")

    # ==========================================
    # Behavior 1 — find_me: head pans left-right
    # ==========================================
    def start_find_me(self):
        def step_timer():
            # gentle left-right sweeping
            self.phase += 0.035
            yaw = 18.0 * math.sin(self.phase)
            # [neck_yaw, neck_pitch, eyes_pitch, eyes_yaw, lid_left, lid_right]
            arr = [yaw, 0.0, 0.0, 0.0, 20.0, -20.0]
            self.send(arr)

        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior 2 — circle_scan: head moves in circle
    # ==========================================
    def start_circle_scan(self):
        def step_timer():
            self.phase += 0.04
            yaw = 15.0 * math.sin(self.phase)
            pitch = 8.0 * math.cos(self.phase)
            arr = [yaw, pitch, 0.0, 0.0, 20.0, -20.0]
            self.send(arr)

        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior 3 — eye_scan: eyes look around
    # ==========================================
    def start_eye_scan(self):
        def step_timer():
            self.phase += 0.08
            eye_yaw = 20.0 * math.sin(self.phase)
            eye_pitch = 5.0 * math.cos(self.phase)
            arr = [0.0, 0.0, eye_pitch, eye_yaw, 20.0, -20.0]
            self.send(arr)

        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior 4 — blink_loop: blink every ~3 sec
    # ==========================================
    def start_blink_loop(self):
        counter = {"t": 0}

        def step_timer():
            counter["t"] += 1
            t = counter["t"] % 60  # 60 * 0.05 = 3 seconds

            if t < 5:
                # closing blink: move lids toward closed
                arr = [0.0, 0.0, 0.0, 0.0, -18.0, 22.0]
            elif t < 10:
                # open again (your chosen "open" values)
                arr = [0.0, 0.0, 0.0, 0.0, 20.0, -20.0]
            else:
                # neutral lids (slightly open)
                arr = [0.0, 0.0, 0.0, 0.0, 10.0, -9.0]

            self.send(arr)

        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior 5 — idle_breathe: subtle idle motion
    # (eyes more open & stronger flutter)
    # ==========================================
    def start_idle_breathe(self):
        def step_timer():
            self.phase += 0.015  # very slow

            # subtle head pitch breathing
            pitch = 3.0 * math.sin(self.phase)

            # eyelids centered around wide-open [20, -20]
            # with ~3x more flutter amplitude
            flutter = 6.0 * math.sin(self.phase * 0.7)
            left_lid = 20.0 + flutter      # left: positive = open
            right_lid = -20.0 - flutter    # right: negative = open

            arr = [0.0, pitch, 0.0, 0.0, left_lid, right_lid]
            self.send(arr)

        t = self.create_timer(0.04, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior 6 — nod_yes: head nodding "yes"
    # (eyes fairly open: ~[16, -16])
    # ==========================================
    def start_nod_yes(self):
        def step_timer():
            self.phase += 0.10
            pitch = -10.0 * math.cos(self.phase)  # nodding
            # eyes fairly open but slightly less than full
            arr = [0.0, pitch, 0.0, 0.0, 16.0, -16.0]
            self.send(arr)

        t = self.create_timer(0.03, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior 7a — calm_shake_no: gentle "no"
    # small amplitude, slow, sinusoidal
    # with eyes stabilizing gaze (counter-yaw)
    # ==========================================
    def start_calm_shake_no(self):
        def step_timer():
            # gentle, slow sinusoidal shake
            self.phase += 0.055
            yaw = 9.0 * math.sin(self.phase)  # gentle shake

            # eyes counter-rotate to keep gaze more fixed in world
            eye_yaw = -yaw

            # [neck_yaw, neck_pitch, eyes_pitch, eyes_yaw, lid_left, lid_right]
            arr = [yaw, 0.0, 0.0, eye_yaw, 20.0, -20.0]
            self.send(arr)

        t = self.create_timer(0.04, step_timer)
        self._timers.append(t)


    # ==========================================
    # Behavior 7b — big_shake_no (improved):
    # - faster left/right head swing
    # - eyes stabilize (counter-rotate)
    # - random blink every 6–12 seconds
    # ==========================================
    def start_big_shake_no(self):

        import random

        state = {
            "yaw": 0.0,
            "target": 12.0,      # expressive amplitude
            "dwell": 0,
            "eye_yaw": 0.0,
            "blink_t": 0,
            "blink_interval": random.randint(120, 240),  
            # 120 * 0.05 = 6 sec
            # 240 * 0.05 = 12 sec
        }

        def step_timer():
            # --------------------------
            # Faster head movement
            # --------------------------
            alpha = 0.28    # was 0.22 → faster transitions
            yaw = state["yaw"] + alpha * (state["target"] - state["yaw"])
            state["yaw"] = yaw

            # Dwell at ends before switching
            if abs(state["target"] - yaw) < 1.0:
                state["dwell"] += 1
                if state["dwell"] > 5:         # quicker flip
                    state["target"] = -state["target"]
                    state["dwell"] = 0

            # --------------------------
            # Eye stabilization
            # --------------------------
            target_eye_yaw = -1.35 * yaw       # stronger compensation

            eye_alpha = 0.35                   # quicker eye correction
            eye_yaw = (eye_alpha * target_eye_yaw +
                       (1 - eye_alpha) * state["eye_yaw"])
            state["eye_yaw"] = eye_yaw

            # --------------------------
            # Randomized blinking
            # --------------------------
            state["blink_t"] += 1

            if state["blink_t"] >= state["blink_interval"]:
                # During blink cycle (~12 frames = 0.6s)
                b = state["blink_t"] - state["blink_interval"]

                if b < 6:                       # closing
                    lid_left = -14.0
                    lid_right = 18.0
                elif b < 12:                    # opening
                    lid_left = 20.0
                    lid_right = -20.0
                else:
                    # Reset blink timing
                    state["blink_t"] = 0
                    state["blink_interval"] = random.randint(120, 240)
                    lid_left = 8.0
                    lid_right = -9.0
            else:
                # Normal neutral eyelids
                lid_left = 8.0
                lid_right = -9.0

            # --------------------------
            # Send final command
            # --------------------------
            arr = [yaw, 0.0, 0.0, eye_yaw, lid_left, lid_right]
            self.send(arr)

        # Faster rate makes motion look deliberate but still stable
        t = self.create_timer(0.045, step_timer)
        self._timers.append(t)




    # ==========================================
    # Behavior 8 — look_at_user: track face position
    # (eyes wide open: [20, -20])
    # ==========================================
    def start_look_at_user(self):
        # Enable the look-at-user behavior; on_face_pos will handle updates
        self.look_at_user_enabled = True

        # Reset commanded pose so we start from "now"
        self.yaw_cmd = self.last_yaw
        self.pitch_cmd = self.last_pitch

        self.get_logger().info("Look-at-user mode enabled. Waiting for /maki/face_pos...")


    def on_face_pos(self, msg: Float64MultiArray):
        # Only act if look_at_user is active
        if not self.look_at_user_enabled:
            return

        if len(msg.data) != 2:
            return

        x, y = msg.data  # normalized offsets, e.g. -1..+1

        # -------------------------------
        # Deadzone: avoid micro-jitter
        # -------------------------------
        DEADZONE = 0.05  # 5% of frame
        if abs(x) < DEADZONE:
            x = 0.0
        if abs(y) < DEADZONE:
            y = 0.0

        # -------------------------------
        # Controller gains (tweakable)
        # -------------------------------
        MAX_YAW = 38.0      # near your ±40° safe limit
        MAX_PITCH = 16.0    # near your ±18° safe limit

        # How much to move per frame for a given error
        # (units: degrees per frame at |error| == 1.0)
        K_YAW = 1.0         # bigger => more aggressive centering
        K_PITCH = 0.8       # slightly gentler in pitch

        # -------------------------------
        # Incremental control:
        #   yaw_cmd += K * error
        #   pitch_cmd += K * error
        # This "walks" the head toward the face
        # and can use the full range.
        # -------------------------------

        # Invert x so Maki turns TOWARD the face
        self.yaw_cmd += K_YAW * (-x)

        # Invert y so face at top => look UP
        self.pitch_cmd += K_PITCH * (-y)

        # Clamp to mechanical-safe range
        if self.yaw_cmd > MAX_YAW:
            self.yaw_cmd = MAX_YAW
        elif self.yaw_cmd < -MAX_YAW:
            self.yaw_cmd = -MAX_YAW

        if self.pitch_cmd > MAX_PITCH:
            self.pitch_cmd = MAX_PITCH
        elif self.pitch_cmd < -MAX_PITCH:
            self.pitch_cmd = -MAX_PITCH

        # Store as "last" so other behaviors can start from here if needed
        self.last_yaw = self.yaw_cmd
        self.last_pitch = self.pitch_cmd

        # Eyes wide open while tracking
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
