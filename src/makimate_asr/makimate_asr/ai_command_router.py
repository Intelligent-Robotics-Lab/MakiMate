import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class ASRCommandRouter(Node):
    """
    Extended to support multiple sleep phrases
    (e.g., 'good bye', 'goodnight', 'good night')
    """

    def __init__(self):
        super().__init__("ai_command_router")

        # ---- Parameters ----
        self.declare_parameter("asr_topic", "/asr/text")
        self.declare_parameter("llm_request_topic", "/llm/request")
        self.declare_parameter("llm_response_topic", "/llm/response")
        self.declare_parameter("awake_topic", "/maki/awake")
        self.declare_parameter("tts_topic", "/llm/stream")
        self.declare_parameter("asr_enable_topic", "/asr/enable")

        # Wake and sleep phrases
        self.declare_parameter("wake_phrase", "hello")
        self.declare_parameter("sleep_phrase", "good bye")
        self.declare_parameter("wake_greeting",
                               "Hello! I'm awake and ready to talk. My name is Maki Mate, how may I help you.")
        self.declare_parameter("sleep_farewell",
                               "Goodbye! I'm going back to sleep now.")

        asr_topic = self.get_parameter("asr_topic").value
        llm_request_topic = self.get_parameter("llm_request_topic").value
        awake_topic = self.get_parameter("awake_topic").value
        tts_topic = self.get_parameter("tts_topic").value
        asr_enable_topic = self.get_parameter("asr_enable_topic").value

        self._wake_phrase = self.get_parameter("wake_phrase").value.lower()
        self._sleep_phrase = self.get_parameter("sleep_phrase").value.lower()
        self._wake_greeting = self.get_parameter("wake_greeting").value
        self._sleep_farewell = self.get_parameter("sleep_farewell").value

        # --------------------------------------------------
        # NEW: list of phrases that put Maki to sleep
        # --------------------------------------------------
        self._sleep_phrases = [
            self._sleep_phrase,
            "goodbye",
            "good night",
            "goodnight",
            "night night",
            "good night maki",
            "goodnight maki",
            "good my"
        ]

        # ---- Publishers ----
        self._llm_req_pub = self.create_publisher(String, llm_request_topic, 10)
        self._awake_pub = self.create_publisher(Bool, awake_topic, 10)
        self._tts_pub = self.create_publisher(String, tts_topic, 10)

        # ---- Subscribers ----
        self._asr_sub = self.create_subscription(String, asr_topic, self._on_asr, 10)
        self._asr_enable_sub = self.create_subscription(Bool, asr_enable_topic, self._on_asr_enable, 10)

        # ---- State ----
        self._awake = False
        self._pending_sleep = False

        self._publish_awake(False)
        self.get_logger().info("ASRCommandRouter started.")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _publish_awake(self, value: bool):
        msg = Bool()
        msg.data = value
        self._awake_pub.publish(msg)
        self._awake = value
        self.get_logger().info(f"Published awake={value}")

    def _speak_immediate(self, text: str):
        if not text:
            return
        msg = String()
        msg.data = text
        self._tts_pub.publish(msg)
        self.get_logger().info(f"[Router->TTS] {text!r}")

    # ------------------------------------------------------------------ #
    # Callbacks
    # ------------------------------------------------------------------ #
    def _on_asr(self, msg: String):
        text = msg.data.strip()
        low = text.lower()

        if not text:
            return

        self.get_logger().info(
            f"ASRCommandRouter received: {text!r} (awake={self._awake}, pending_sleep={self._pending_sleep})"
        )

        # While asleep: only react to wake phrase
        if not self._awake:
            if self._wake_phrase in low:
                self._pending_sleep = False
                self._publish_awake(True)
                self._speak_immediate(self._wake_greeting)
            return

        # --------------------------------------------------
        # NEW: Check any sleep phrase in list
        # --------------------------------------------------
        if any(phrase in low for phrase in self._sleep_phrases):
            self._speak_immediate(self._sleep_farewell)
            self._pending_sleep = True
            self.get_logger().info(
                f"Sleep phrase detected in: {text!r}. "
                "Waiting for ASR re-enable before sleeping."
            )
            return

        # Normal conversation
        out = String()
        out.data = text
        self._llm_req_pub.publish(out)
        self.get_logger().info("[Router->LLM] forwarded user text.")

    def _on_asr_enable(self, msg: Bool):
        enabled = bool(msg.data)
        if self._pending_sleep and enabled:
            self._pending_sleep = False
            self._publish_awake(False)
            self.get_logger().info("ASR re-enabled → Maki going to sleep.")


def main(args=None):
    rclpy.init(args=args)
    node = ASRCommandRouter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
