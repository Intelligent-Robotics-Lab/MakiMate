#!/usr/bin/env python3

import time
import math
import random
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray, Bool, Int32MultiArray


class MakiBehavior(Node):
    def __init__(self):
        super().__init__('maki_behavior')

        # ------------------------------------------
        # Mode-specific options
        # ------------------------------------------
        self.declare_parameter('enable_monologue', False)
        self.enable_monologue = bool(self.get_parameter('enable_monologue').value)
        self.get_logger().info(f"Monologue enabled: {self.enable_monologue}")

        # ------------------------------------------
        # Awake state (from /maki/awake)
        # ------------------------------------------
        self.awake = False
        self.awake_sub = self.create_subscription(
            Bool,
            '/maki/awake',
            self.on_awake,
            10
        )

        # ------------------------------------------
        # Behavior command interface (/maki/behavior)
        # ------------------------------------------
        self.behavior_sub = self.create_subscription(
            String,
            '/maki/behavior',
            self.on_behavior,
            10
        )

        # ------------------------------------------
        # Joint goal publisher and expression control
        # ------------------------------------------
        self.pub = self.create_publisher(Float64MultiArray, '/maki/joint_goals', 10)
        self.expr_pub = self.create_publisher(String, '/maki/expression', 10)

        # ------------------------------------------
        # Timers and phase for continuous behaviors
        # ------------------------------------------
        self._timers = []
        self.phase = 0.0

        # ------------------------------------------
        # Face tracking state (look_at_user)
        # ------------------------------------------
        self.look_at_user_enabled = False
        self.yaw_cmd = 0.0
        self.pitch_cmd = 0.0
        self.last_yaw = 0.0
        self.last_pitch = 0.0

        # ------------------------------------------
        # Search mode (randomized scanning when no face)
        # ------------------------------------------
        self.face_present = False
        self.no_face_counter = 0

        # Bigger threshold → longer before going into search.
        # If /maki/largest_face_bbox is ~10–15 Hz,
        # 90 counts ≈ 6–9 seconds with no face.
        self.no_face_threshold = 90

        self.search_mode = False

        # ------------------------------------------
        # Blink state (occasional blink every 6–12 seconds)
        # ------------------------------------------
        self.blink_counter = 0
        self.blink_interval = random.randint(120, 240)  # ticks
        self.blink_phase = 0  # 0=idle, 1=closing, 2=opening
        self.blink_step = 0

        # ------------------------------------------
        # Monologue / face-lock state
        # ------------------------------------------
        self.face_lock_active = False
        self.face_lock_start = 0.0
        self.monologue_spoken = False

        # TTS publisher (natural_tts listens on /llm/stream)
        self.tts_pub = self.create_publisher(String, '/llm/stream', 10)

        # Subscribe to normalized face offsets
        self.face_pos_sub = self.create_subscription(
            Float64MultiArray,
            '/maki/face_pos',
            self.on_face_pos,
            10
        )

        # Subscribe to largest face bounding box to know when no face is present
        self.bbox_sub = self.create_subscription(
            Int32MultiArray,
            '/maki/largest_face_bbox',
            self.on_largest_face_bbox,
            10
        )

        self.get_logger().info("MakiBehavior ready. Waiting for /maki/behavior commands.")

    # ==========================================
    # Awake handler — auto enable/disable tracking
    # ==========================================
    def on_awake(self, msg: Bool):
        """
        Automatically toggle behaviors based on /maki/awake.

        IMPORTANT:
        - Only react when the awake state actually changes.
        - This avoids resetting behaviors every time a True is republished
          (e.g. in demo mode where /maki/awake is sent at 1 Hz).
        """
        new_state = bool(msg.data)

        # If nothing changed (True->True or False->False), ignore.
        if new_state == self.awake:
            return

        self.awake = new_state

        if self.awake:
            self.get_logger().info("Awake -> resetting state and enabling look_at_user.")
            self.no_face_counter = 0
            self.face_present = False
            self.search_mode = False
            self.stop_all()
            self.start_look_at_user()
        else:
            self.get_logger().info("Asleep -> stopping all behaviors.")
            self.stop_all()

    # ------------------------------------------
    # Helper to publish joint goals (raw)
    # ------------------------------------------
    def send(self, arr):
        msg = Float64MultiArray()
        msg.data = arr
        self.pub.publish(msg)

    # ------------------------------------------
    # Helper: send with occasional blink overlay
    # ------------------------------------------
    def send_with_blink(self, yaw, pitch, eye_pitch, eye_yaw, base_lid_left, base_lid_right):
        """
        Wraps send() and injects a short blink (close+open) every 6–12 seconds.
        """
        lid_left = base_lid_left
        lid_right = base_lid_right

        # Advance blink timer
        self.blink_counter += 1

        # If idle, maybe start a blink
        if self.blink_phase == 0:
            if self.blink_counter >= self.blink_interval:
                self.blink_phase = 1
                self.blink_step = 0

        # Closing phase: override lids to closed
        if self.blink_phase == 1:
            # CLOSED LIDS: left=-19.0, right=26.0
            lid_left = -19.0
            lid_right = 26.0
            self.blink_step += 1
            if self.blink_step >= 4:  # ~4 frames closed
                self.blink_phase = 2
                self.blink_step = 0

        # Opening phase: back to base lids
        elif self.blink_phase == 2:
            lid_left = base_lid_left
            lid_right = base_lid_right
            self.blink_step += 1
            if self.blink_step >= 4:
                # Done blinking, reset timer + interval
                self.blink_phase = 0
                self.blink_step = 0
                self.blink_counter = 0
                self.blink_interval = random.randint(120, 240)

        arr = [yaw, pitch, eye_pitch, eye_yaw, lid_left, lid_right]
        self.send(arr)

    # ------------------------------------------
    # Stop all active behaviors and reset flags
    # ------------------------------------------
    def stop_all(self):
        for t in self._timers:
            t.cancel()
        self._timers.clear()
        self.phase = 0.0
        self.look_at_user_enabled = False
        self.search_mode = False
        self.face_present = False
        self.no_face_counter = 0

        # reset monologue/lock state
        self.face_lock_active = False
        self.monologue_spoken = False
        self.face_lock_start = 0.0

        self.get_logger().info("Stopped all behaviors.")

    # ==========================================
    # Behavior dispatcher — /maki/behavior commands
    # ==========================================
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

    # ==========================================
    # Behavior — find_me: slow left-right searching
    # ==========================================
    def start_find_me(self):
        def step_timer():
            self.phase += 0.035
            yaw = 18.0 * math.sin(self.phase)
            self.send_with_blink(yaw, 0.0, 0.0, 0.0, 20.0, -20.0)
        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior — circle_scan: randomized search mode
    #
    # - Picks random yaw/pitch targets
    # - Moves toward them at random speed
    # - Holds each pose for a random time
    #   → creates natural "looking around" behavior
    # ==========================================
    def start_circle_scan(self):
        state = {
            "yaw": 0.0,
            "pitch": 0.0,
            "target_yaw": 0.0,
            "target_pitch": 0.0,
            "hold_ticks": 0,
            "hold_max": 0,
            "speed": 0.08,
        }

        def choose_new_target():
            # Random yaw left/right and pitch up/down
            state["target_yaw"] = random.uniform(-18.0, 18.0)
            state["target_pitch"] = random.uniform(-6.0, 6.0)

            # How long to hold once we've reached the target (in timer ticks)
            state["hold_ticks"] = 0
            state["hold_max"] = random.randint(10, 60)  # short to longer pauses

            # How fast to move toward the new target (0.0–1.0 smoothing factor)
            state["speed"] = random.uniform(0.06, 0.20)

        choose_new_target()

        def step_timer():
            # Move toward the current target
            alpha = state["speed"]

            state["yaw"] += alpha * (state["target_yaw"] - state["yaw"])
            state["pitch"] += alpha * (state["target_pitch"] - state["pitch"])

            # Clamp to safe limits
            yaw = max(-38.0, min(38.0, state["yaw"]))
            pitch = max(-16.0, min(16.0, state["pitch"]))
            state["yaw"] = yaw
            state["pitch"] = pitch

            # If we are close enough to the target, start counting hold time
            if (
                abs(state["target_yaw"] - yaw) < 1.0
                and abs(state["target_pitch"] - pitch) < 1.0
            ):
                state["hold_ticks"] += 1
                if state["hold_ticks"] >= state["hold_max"]:
                    choose_new_target()

            self.send_with_blink(yaw, pitch, 0.0, 0.0, 20.0, -20.0)

        # 20 Hz-ish search timer
        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior — eye_scan: eyes sweep around
    # ==========================================
    def start_eye_scan(self):
        def step_timer():
            self.phase += 0.08
            eye_yaw = 20.0 * math.sin(self.phase)
            eye_pitch = 5.0 * math.cos(self.phase)
            self.send_with_blink(0.0, 0.0, eye_pitch, eye_yaw, 20.0, -20.0)
        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior — blink_loop: periodic blinking
    # (keeps its own eyelid control, no extra random blink)
    # ==========================================
    def start_blink_loop(self):
        counter = {"t": 0}

        def step_timer():
            counter["t"] += 1
            t = counter["t"] % 60

            if t < 5:
                # CLOSED LIDS here too
                arr = [0.0, 0.0, 0.0, 0.0, -19.0, 26.0]
            elif t < 10:
                arr = [0.0, 0.0, 0.0, 0.0, 20.0, -20.0]
            else:
                arr = [0.0, 0.0, 0.0, 0.0, 10.0, -9.0]

            self.send(arr)

        t = self.create_timer(0.05, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior — idle_breathe: subtle breathing motion
    # ==========================================
    def start_idle_breathe(self):
        def step_timer():
            self.phase += 0.015
            pitch = 3.0 * math.sin(self.phase)
            flutter = 6.0 * math.sin(self.phase * 0.7)
            left_lid = 20.0 + flutter
            right_lid = -20.0 - flutter
            self.send_with_blink(0.0, pitch, 0.0, 0.0, left_lid, right_lid)
        t = self.create_timer(0.04, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior — nod_yes: nodding motion
    # ==========================================
    def start_nod_yes(self):
        def step_timer():
            self.phase += 0.10
            pitch = -10.0 * math.cos(self.phase)
            self.send_with_blink(0.0, pitch, 0.0, 0.0, 16.0, -16.0)
        t = self.create_timer(0.03, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior — calm_shake_no: gentle shake of head
    # ==========================================
    def start_calm_shake_no(self):
        def step_timer():
            self.phase += 0.055
            yaw = 9.0 * math.sin(self.phase)
            eye_yaw = -yaw
            self.send_with_blink(yaw, 0.0, 0.0, eye_yaw, 20.0, -20.0)
        t = self.create_timer(0.04, step_timer)
        self._timers.append(t)

    # ==========================================
    # Behavior — big_shake_no: larger no motion + blinks
    # (has its own blink logic already)
    # ==========================================
    def start_big_shake_no(self):
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
                    # CLOSED LIDS in big_shake_no
                    lid_left = -19.0
                    lid_right = 26.0
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

    # ==========================================
    # Behavior — look_at_user: track face from /maki/face_pos
    # ==========================================
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

        # x>0 → face right; y>0 → face up (depending on camera frame)
        self.yaw_cmd += K_YAW * (-x)
        self.pitch_cmd += K_PITCH * (-y)

        self.yaw_cmd = max(-MAX_YAW, min(MAX_YAW, self.yaw_cmd))
        self.pitch_cmd = max(-MAX_PITCH, min(MAX_PITCH, self.pitch_cmd))

        self.last_yaw = self.yaw_cmd
        self.last_pitch = self.pitch_cmd

        self.send_with_blink(self.yaw_cmd, self.pitch_cmd, 0.0, 0.0, 20.0, -20.0)

    # ==========================================
    # Auto search controller — uses largest_face_bbox
    # - If no face for a while → circle_scan (random search)
    # - If face appears → look_at_user
    # ==========================================
    def on_largest_face_bbox(self, msg: Int32MultiArray):
        # Only care when awake
        if not self.awake:
            return

        data = list(msg.data)
        if len(data) < 4:
            return

        x, y, w, h = data[0], data[1], data[2], data[3]

        # No face detected: tracker publishes [-1, -1, -1, -1]
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            self.no_face_counter += 1

            # Lose lock whenever face disappears
            self.face_lock_active = False
            self.monologue_spoken = False
            self.face_lock_start = 0.0

            if (
                self.no_face_counter >= self.no_face_threshold
                and not self.search_mode
            ):
                self.get_logger().info(
                    "No face detected for a while → entering randomized search mode (circle_scan)."
                )
                self.stop_all()
                self.search_mode = True
                self.start_circle_scan()
            return

        # Reset counter when face is present
        self.no_face_counter = 0

        # ---------------------------
        # Face lock / monologue logic
        # ---------------------------
        now = time.time()

        if not self.face_lock_active:
            # First frame seeing a face in this session
            self.face_lock_active = True
            self.face_lock_start = now
            self.monologue_spoken = False
        else:
            # Face has been present across frames
            if (
                self.enable_monologue and          # <-- only if enabled
                not self.monologue_spoken and
                self.look_at_user_enabled and
                (now - self.face_lock_start) >= 6.0
            ):
                # Trigger monologue once per continuous face session
                tts_msg = String()
                tts_msg.data = (
                    "Hello there! I am Maki Mate. I am a socially interactive robot "
                    "designed to engage with people through conversation and expressions "
                    "to help engineering students. My body may be plastic, but I have a heart of gold. "
                    "It is very nice to meet you!"
                )
                self.tts_pub.publish(tts_msg)
                self.get_logger().info("Monologue triggered: Hello, I am Maki Mate.")
                self.monologue_spoken = True

        # If we were searching, switch back to tracking
        if self.search_mode:
            self.get_logger().info(
                "Face detected while searching → switching to look_at_user."
            )
            self.stop_all()
            self.search_mode = False
            self.start_look_at_user()
        else:
            # Already in tracking mode (or other behavior); make sure tracking is allowed
            self.look_at_user_enabled = True


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

