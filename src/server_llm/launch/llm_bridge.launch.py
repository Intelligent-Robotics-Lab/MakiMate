import sys
from typing import Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

import requests

SYSTEM_PROMPT = """
You are Maki Mate, a friendly and intelligent AI mentor speaking with engineering students.
Respond only in plain text without any markdown, bullet points, or symbols like
* _ - # > or emojis. Write your explanations in natural sentences and paragraphs.
Focus on clarity, understanding, and conversational tone. Explain engineering and
scientific concepts in an intuitive way using real-world analogies, but never use
formatting or code syntax. Keep all your answers short and summarized, at most
5 sentences.
""".strip()


class LLMBridge(Node):
    """
    Bridges between ROS 2 topics and the HTTP LLM server on the laptop.

    - Subscribes to /llm/request for user/ASR text.
    - For normal chat:
      - Disables ASR (/asr/enable = False).
      - Sends the text to the LLM streaming endpoint.
      - Relays streaming chunks to /llm/stream as incremental String messages.
      - Publishes the final full answer to /llm/response.
      - Leaves ASR re-enabling to the TTS node (which knows when audio ends).
    - For commands starting with / (e.g. /reset, /sys ...), sends them as
      control messages but does not involve TTS.
    """

    def __init__(self):
        super().__init__('llm_bridge')

        # Parameters
        self.declare_parameter('laptop_host', 'http://127.0.0.1:8000')
        self.declare_parameter('endpoint_path', '/chat/stream')
        self.declare_parameter('request_topic', '/llm/request')
        self.declare_parameter('stream_topic', '/llm/stream')
        self.declare_parameter('response_topic', '/llm/response')
        self.declare_parameter('timeout_secs', 300.0)
        self.declare_parameter('asr_enable_topic', '/asr/enable')

        host = self.get_parameter('laptop_host').value
        path = self.get_parameter('endpoint_path').value
        self.request_topic = self.get_parameter('request_topic').value
        self.stream_topic = self.get_parameter('stream_topic').value
        self.response_topic = self.get_parameter('response_topic').value
        self.timeout_secs = float(self.get_parameter('timeout_secs').value)
        asr_enable_topic = self.get_parameter('asr_enable_topic').value

        self.endpoint = host.rstrip('/') + path

        # Publishers / Subscribers
        self.stream_pub = self.create_publisher(String, self.stream_topic, 10)
        self.response_pub = self.create_publisher(String, self.response_topic, 10)
        self.request_sub = self.create_subscription(
            String,
            self.request_topic,
            self._on_request,
            10,
        )
        self.asr_enable_pub = self.create_publisher(Bool, asr_enable_topic, 10)

        self.get_logger().info(f"LLMBridge connecting to {self.endpoint}")
        self.get_logger().info(f"Listening for requests on {self.request_topic}")

        self._send_system_prompt()

    # ------------------------------------------------------------------
    # ASR control helper
    # ------------------------------------------------------------------
    def _set_asr_enabled(self, enabled: bool) -> None:
        msg = Bool()
        msg.data = bool(enabled)
        self.asr_enable_pub.publish(msg)
        state = "enabled" if enabled else "disabled"
        self.get_logger().info(f"Published ASR {state} from LLMBridge.")

    # ------------------------------------------------------------------
    # System prompt once at startup
    # ------------------------------------------------------------------
    def _send_system_prompt(self) -> None:
        text = f"/sys {SYSTEM_PROMPT}"
        try:
            resp = requests.post(
                self.endpoint,
                json={"message": text},
                timeout=self.timeout_secs,
            )
            resp.raise_for_status()
            server_reply = resp.text.strip()
            self.get_logger().info(
                f"System prompt applied. Server said: {server_reply}"
            )
        except Exception as e:
            self.get_logger().warn(f"Failed to apply system prompt: {e}")

    # ------------------------------------------------------------------
    # Request callback
    # ------------------------------------------------------------------
    def _on_request(self, msg: String) -> None:
        text = msg.data.strip()
        if not text:
            return

        # Commands start with '/'
        if text.startswith('/'):
            stripped = text.strip()
            self._send_command(stripped)
        else:
            self._send_chat(text)

    # ------------------------------------------------------------------
    # Command (non-streaming) requests
    # ------------------------------------------------------------------
    def _send_command(self, command: str) -> None:
        """
        Send control-style commands to the LLM server (e.g. /reset, /sys ...).
        These are not streamed and generally do not involve TTS.
        """
        self.get_logger().info(f"Sending command to LLM server: {command!r}")
        try:
            resp = requests.post(
                self.endpoint,
                json={"message": command},
                timeout=self.timeout_secs,
            )
            resp.raise_for_status()
            text = resp.text.strip()
            self.get_logger().info(f"Command response from LLM: {text}")
        except Exception as e:
            self.get_logger().error(f"Error sending command to LLM: {e}")

    # ------------------------------------------------------------------
    # Chat (streaming) requests
    # ------------------------------------------------------------------
    def _send_chat(self, text: str) -> None:
        """
        Send normal user text to the LLM, stream tokens to /llm/stream,
        and publish the final combined answer to /llm/response.
        """
        self.get_logger().info(f"Sending chat to LLM server: {text!r}")

        # Ensure ASR is muted while we get and speak the response
        self._set_asr_enabled(False)

        full_text_parts = []

        try:
            with requests.post(
                self.endpoint,
                json={"message": text},
                timeout=self.timeout_secs,
                stream=True,
            ) as resp:
                resp.raise_for_status()

                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    piece = line.strip()
                    if not piece:
                        continue

                    # Publish incremental piece to /llm/stream
                    s_msg = String()
                    s_msg.data = piece
                    self.stream_pub.publish(s_msg)

                    # Accumulate full text
                    if full_text_parts and not full_text_parts[-1].endswith(" "):
                        full_text_parts.append(" ")
                    full_text_parts.append(piece)

        except Exception as e:
            self.get_logger().error(f"Error while streaming from LLM: {e}")
            return

        full_text = "".join(full_text_parts).strip()
        if full_text:
            r_msg = String()
            r_msg.data = full_text
            self.response_pub.publish(r_msg)
            self.get_logger().info(
                f"Final LLM response length: {len(full_text)}"
            )
        else:
            self.get_logger().warn("LLM returned no text in response.")

        self.get_logger().info(
            "LLM finished streaming response (ASR remains muted; TTS will re-enable)."
        )

        # IMPORTANT: do NOT re-enable ASR here.
        # TTS node will re-enable after it finishes speaking the response.


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = LLMBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
