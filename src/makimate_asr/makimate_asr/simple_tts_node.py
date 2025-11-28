# *** THIS NODE HAS BEEN OBSOLETED ***

import queue
import threading
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

import pyttsx3


class SimpleTTS(Node):
    def __init__(self):
        super().__init__('simple_tts')

        self.declare_parameter('input_topic', '/llm/response')
        self.declare_parameter('rate', 170)
        self.declare_parameter('volume', 1.0)
        self.declare_parameter('voice', '')
        self.declare_parameter('asr_enable_topic', '/asr/enable')

        input_topic = self.get_parameter('input_topic').value
        rate = int(self.get_parameter('rate').value)
        volume = float(self.get_parameter('volume').value)
        voice = self.get_parameter('voice').value
        asr_enable_topic = self.get_parameter('asr_enable_topic').value

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

        if voice:
            voices = self.engine.getProperty('voices')
            for v in voices:
                if voice.lower() in v.name.lower():
                    self.get_logger().info(f"Using voice: {v.name}")
                    self.engine.setProperty('voice', v.id)
                    break
            else:
                self.get_logger().warn(
                    f"Requested voice {voice!r} not found, using default."
                )

        # ASR enable publisher
        self.asr_enable_pub = self.create_publisher(Bool, asr_enable_topic, 10)

        # Queue + worker thread
        self._queue: queue.Queue[str] = queue.Queue()
        self._worker_thread = threading.Thread(target=self._speak_loop, daemon=True)
        self._worker_thread.start()

        # Subscriber for LLM responses
        self.sub = self.create_subscription(
            String,
            input_topic,
            self._on_text,
            10,
        )

        self.get_logger().info(f"SimpleTTS node started, listening on: {input_topic}")

    def _set_asr_enabled(self, enabled: bool):
        msg = Bool()
        msg.data = bool(enabled)
        self.asr_enable_pub.publish(msg)
        state = "enabled" if enabled else "disabled"
        self.get_logger().info(f"Published ASR {state} from TTS.")

    def _on_text(self, msg: String):
        text = msg.data.strip()
        if not text:
            return
        self.get_logger().info(f"Queuing text for TTS: {text!r}")
        self._queue.put(text)

    def _speak_loop(self):
        self.get_logger().info("TTS worker thread running.")
        while rclpy.ok():
            try:
                text = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                # Make sure ASR is muted before we speak
                self._set_asr_enabled(False)

                self.get_logger().info(f"Speaking: {text!r}")
                self.engine.say(text)
                self.engine.runAndWait()
            finally:
                # Wait 2 seconds AFTER finishing TTS before re-enabling ASR
                self.get_logger().info(
                    "TTS finished. Waiting 2 seconds before re-enabling ASR..."
                )
                time.sleep(2.0)
                self._set_asr_enabled(True)

    def destroy_node(self):
        self.get_logger().info("Shutting down SimpleTTS node...")
        try:
            self.engine.stop()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SimpleTTS()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
