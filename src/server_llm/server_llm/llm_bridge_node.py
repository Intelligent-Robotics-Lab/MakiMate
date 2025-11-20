import sys
import time  # you can keep this or remove if unused elsewhere
from typing import Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

import requests

SYSTEM_PROMPT = """
You are a friendly and intelligent AI mentor speaking with engineering students. Respond only in plain text without any markdown, bullet points, or symbols like * _ - # > or emojis. Write your explanations in natural sentences and paragraphs. Focus on clarity, understanding, and conversational tone. Explain engineering and scientific concepts in an intuitive way using real-world analogies. When describing math or physics, focus on intuition and practical understanding before introducing any formulas. Always stay positive, encouraging, and respectful. Keep all your answers short and summarized, at most 5 sentences.
""".strip()


class LLMBridge(Node):
    def __init__(self) -> None:
        super().__init__('llm_bridge')

        # HTTP + topics
        self.declare_parameter('laptop_host', 'http://127.0.0.1:8000')
        self.declare_parameter('endpoint_path', '/chat/stream')
        self.declare_parameter('request_topic', '/llm/request')
        self.declare_parameter('stream_topic', '/llm/stream')
        self.declare_parameter('response_topic', '/llm/response')
        self.declare_parameter('timeout_secs', 60.0)
        self.declare_parameter('asr_enable_topic', '/asr/enable')

        host = self.get_parameter('laptop_host').value
        path = self.get_parameter('endpoint_path').value
        self.request_topic = self.get_parameter('request_topic').value
        self.stream_topic = self.get_parameter('stream_topic').value
        self.response_topic = self.get_parameter('response_topic').value
        self.timeout_secs = float(self.get_parameter('timeout_secs').value)
        asr_enable_topic = self.get_parameter('asr_enable_topic').value

        self.endpoint = host.rstrip('/') + path

        # ROS pubs/sub
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

    def _set_asr_enabled(self, enabled: bool) -> None:
        msg = Bool()
        msg.data = bool(enabled)
        self.asr_enable_pub.publish(msg)
        state = "enabled" if enabled else "disabled"
        self.get_logger().info(f"Published ASR {state} from LLMBridge.")

    def _send_system_prompt(self) -> None:
        sys_cmd = f"/sys {SYSTEM_PROMPT}"
        payload = {"message": sys_cmd}
        try:
            resp = requests.post(self.endpoint, json=payload, timeout=self.timeout_secs)
            resp.raise_for_status()
            self.get_logger().info(f"System prompt applied. Server said: {resp.text.strip()}")
        except requests.RequestException as e:
            self.get_logger().error(f"Failed to send system prompt: {e}")

    def _on_request(self, msg: String) -> None:
        user_text = msg.data
        stripped = user_text.strip()
        if not stripped:
            return

        if stripped.startswith('/'):
            self._send_command(stripped)
        else:
            self._send_chat(stripped)

    def _send_command(self, command: str) -> None:
        self.get_logger().info(f"Sending command to LLM server: {command!r}")
        try:
            resp = requests.post(
                self.endpoint,
                json={"message": command},
                timeout=self.timeout_secs,
            )
            resp.raise_for_status()
            text = resp.text.strip()
            if text:
                out = String()
                out.data = text
                self.response_pub.publish(out)
                self.stream_pub.publish(out)
                self.get_logger().info(f"Command response: {text}")
        except requests.RequestException as e:
            self.get_logger().error(f"Error sending command to LLM server: {e}")

    def _send_chat(self, text: str) -> None:
        self.get_logger().info(f"Sending chat to LLM server: {text!r}")

        # Mute ASR for the whole time the LLM is processing
        self._set_asr_enabled(False)

        try:
            with requests.post(
                self.endpoint,
                json={"message": text},
                stream=True,
                timeout=self.timeout_secs,
            ) as resp:
                resp.raise_for_status()

                full_answer_parts = []
                for chunk in resp.iter_content(chunk_size=None):
                    if not chunk:
                        continue
                    piece = chunk.decode('utf-8', errors='ignore')
                    if not piece:
                        continue

                    full_answer_parts.append(piece)

                    s = String()
                    s.data = piece
                    self.stream_pub.publish(s)

                full_answer = ''.join(full_answer_parts).strip()
                if full_answer:
                    out = String()
                    out.data = full_answer
                    self.response_pub.publish(out)
                    self.get_logger().info(
                        f"Final LLM response length: {len(full_answer)}"
                    )
        except requests.RequestException as e:
            self.get_logger().error(f"Error during chat with LLM server: {e}")
        finally:
            # IMPORTANT: do NOT re-enable ASR here.
            # TTS will re-enable after speaking + 2 second delay.
            self.get_logger().info("LLM finished streaming response (ASR remains muted).")


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
