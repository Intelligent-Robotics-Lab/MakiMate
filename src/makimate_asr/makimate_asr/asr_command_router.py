import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class ASRCommandRouter(Node):
    """
    Listens to raw ASR text and:
    - Keeps an "awake/asleep" state.
    - Wakes up on 'hello' (when asleep) and sends a greeting to TTS.
    - Says goodbye and goes to sleep on 'good bye' / 'goodbye' (when awake).
    - Only forwards utterances to the LLM when awake.
    - Publishes awake/asleep on /maki/awake for LED control.
    """

    def __init__(self):
        super().__init__('asr_command_router')

        # Topics
        self.declare_parameter('asr_topic', '/asr/text')
        self.declare_parameter('llm_request_topic', '/llm/request')
        self.declare_parameter('llm_response_topic', '/llm/response')
        self.declare_parameter('awake_topic', '/maki/awake')

        # Phrases
        self.declare_parameter('wake_phrase', 'hello')
        self.declare_parameter('sleep_phrase', 'good bye')
        self.declare_parameter(
            'greeting_text',
            "Hello, I'm MakiMate. I'm happy to talk with you. How can I help you today?"
        )
        self.declare_parameter(
            'farewell_text',
            "Goodbye! I look forward to seeing you again."
        )

        asr_topic = self.get_parameter('asr_topic').value
        llm_request_topic = self.get_parameter('llm_request_topic').value
        llm_response_topic = self.get_parameter('llm_response_topic').value
        awake_topic = self.get_parameter('awake_topic').value

        self.wake_phrase = self.get_parameter('wake_phrase').value.lower()
        self.sleep_phrase = self.get_parameter('sleep_phrase').value.lower()
        self.greeting_text = self.get_parameter('greeting_text').value
        self.farewell_text = self.get_parameter('farewell_text').value

        # Start asleep
        self.awake = False

        # Publishers
        self.llm_request_pub = self.create_publisher(String, llm_request_topic, 10)
        self.llm_response_pub = self.create_publisher(String, llm_response_topic, 10)
        self.awake_pub = self.create_publisher(Bool, awake_topic, 10)

        # Subscriber to raw ASR text
        self.asr_sub = self.create_subscription(
            String,
            asr_topic,
            self._on_asr_text,
            10,
        )

        self._publish_awake()
        self.get_logger().info(
            f"ASRCommandRouter started. Initial state: asleep. "
            f"Wake phrase='{self.wake_phrase}', sleep phrase='{self.sleep_phrase}'."
        )

    def _publish_awake(self):
        msg = Bool()
        msg.data = bool(self.awake)
        self.awake_pub.publish(msg)
        self.get_logger().info(f"Published awake={self.awake}")

    def _on_asr_text(self, msg: String):
        text = msg.data.strip()
        if not text:
            return

        lower = text.lower()
        self.get_logger().info(
            f"ASRCommandRouter received: {text!r} (awake={self.awake})"
        )

        # Waking up
        if not self.awake and self.wake_phrase in lower:
            self.awake = True
            self._publish_awake()
            self.get_logger().info("Wake phrase detected. MakiMate is now AWAKE.")
            self._speak(self.greeting_text)
            return

        # Going to sleep
        if self.awake and (self.sleep_phrase in lower or 'goodbye' in lower):
            self.get_logger().info("Sleep phrase detected. MakiMate is going to SLEEP.")
            self._speak(self.farewell_text)

            # Send /reset to LLM whenever the robot goes to sleep
            reset_msg = String()
            reset_msg.data = "/reset"
            self.llm_request_pub.publish(reset_msg)
            self.get_logger().info("Sent /reset command to LLM after going to sleep.")

            self.awake = False
            self._publish_awake()
            return

        # If asleep, ignore everything except wake phrase
        if not self.awake:
            self.get_logger().info(
                f"Ignoring ASR while asleep: {text!r}"
            )
            return

        # If awake and not a special command, forward to LLM
        out = String()
        out.data = text
        self.llm_request_pub.publish(out)
        self.get_logger().info(f"Forwarded to LLM: {text!r}")

    def _speak(self, text: str):
        """Publish directly to LLM response so TTS will say it."""
        msg = String()
        msg.data = text
        self.llm_response_pub.publish(msg)
        self.get_logger().info(f"Saying (direct TTS): {text!r}")



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


if __name__ == '__main__':
    main()
