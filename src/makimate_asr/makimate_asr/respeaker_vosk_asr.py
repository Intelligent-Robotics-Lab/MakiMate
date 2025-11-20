import queue
import threading
from typing import Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

import sounddevice as sd
from vosk import Model, KaldiRecognizer


class ReSpeakerVoskASR(Node):
    def __init__(self):
        super().__init__('respeaker_vosk_asr')

        # -------------------------
        # Declare parameters ONCE
        # -------------------------
        self.declare_parameter('sample_rate', 16000.0)  # float
        # device: integer index, -1 means "use default input device"
        self.declare_parameter('device', -1)
        self.declare_parameter(
            'model_path',
            '/home/makimate/vosk_models/vosk-model-small-en-us-0.15'
        )
        self.declare_parameter('publish_llm', True)
        self.declare_parameter('asr_topic', '/asr/text')
        self.declare_parameter('llm_request_topic', '/llm/request')
        self.declare_parameter('enable_topic', '/asr/enable')  # NEW: mute/unmute channel


        # -------------------------
        # Read parameters
        # -------------------------
        self.sample_rate = float(self.get_parameter('sample_rate').value)

        dev_param = self.get_parameter('device').value
        try:
            self.device = int(dev_param)
        except (TypeError, ValueError):
            self.get_logger().warn(
                f"Invalid device param {dev_param!r}, using default (-1)."
            )
            self.device = -1  # default device

        self.model_path = self.get_parameter('model_path').value
        self.publish_llm = bool(self.get_parameter('publish_llm').value)
        self.asr_topic = self.get_parameter('asr_topic').value
        self.llm_topic = self.get_parameter('llm_request_topic').value

        enable_topic = self.get_parameter('enable_topic').value
        self.listening_enabled = True  # default: ASR is on


        # -------------------------
        # Publishers
        # -------------------------
        self.asr_pub = self.create_publisher(String, self.asr_topic, 10)
        self.llm_pub = self.create_publisher(String, self.llm_topic, 10)

        # Subscriber for enable/disable
        self.enable_sub = self.create_subscription(
            Bool,
            enable_topic,
            self._on_enable,
            10,
        )


        # -------------------------
        # Load Vosk model
        # -------------------------
        self.get_logger().info(f"Loading Vosk model from: {self.model_path}")
        try:
            self.model = Model(self.model_path)
        except Exception as e:
            self.get_logger().error(f"Failed to load Vosk model: {e}")
            raise

        self.recognizer = KaldiRecognizer(self.model, int(self.sample_rate))
        self.recognizer.SetWords(True)

        # -------------------------
        # Audio queue and stream
        # -------------------------
        self.audio_q: queue.Queue = queue.Queue()
        self.stream: Optional[sd.InputStream] = None

        self.get_logger().info("Initializing audio stream...")
        self._start_audio_stream()

        # Worker thread to process audio
        self.worker_thread = threading.Thread(target=self._asr_loop, daemon=True)
        self.worker_thread.start()
        self.get_logger().info("ReSpeakerVoskASR node started.")

    # ----------------------------------
    # Audio callback and stream handling
    # ----------------------------------
    def _audio_callback(self, indata, frames, time, status):
        if status:
            self.get_logger().warn(f"Audio status: {status}")
        data = (indata * 32767).astype('int16').tobytes()
        self.audio_q.put(data)

    def _on_enable(self, msg: Bool):
        new_state = bool(msg.data)
        if new_state == self.listening_enabled:
            return

        self.listening_enabled = new_state
        if not new_state:
            self.get_logger().info("ASR disabled: flushing input queue.")
            # Clear queued audio so we don't process TTS audio later
            try:
                with self.audio_q.mutex:
                    self.audio_q.queue.clear()
            except Exception:
                pass
        else:
            self.get_logger().info("ASR enabled: will resume publishing text.")



    def _start_audio_stream(self):
        try:
            # -1 means "use default input device"
            device_arg = None if self.device < 0 else self.device

            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                device=device_arg,
                callback=self._audio_callback,
            )
            self.stream.start()
            self.get_logger().info(
                f"Audio input stream started at {self.sample_rate} Hz, "
                f"device={device_arg if device_arg is not None else 'default'}"
            )
        except Exception as e:
            self.get_logger().error(f"Failed to open audio stream: {e}")
            raise

    # ----------------------------------
    # ASR loop
    # ----------------------------------
    def _asr_loop(self):
        self.get_logger().info("ASR processing thread running.")
        while rclpy.ok():
            try:
                data = self.audio_q.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    text = self._extract_text(result)
                    if text:
                        self._publish_text(text)
            except Exception as e:
                # If Vosk gets into a bad state, log and recreate recognizer
                self.get_logger().error(f"ASR error in AcceptWaveform: {e}. Recreating recognizer.")
                try:
                    self.recognizer = KaldiRecognizer(self.model, int(self.sample_rate))
                    self.recognizer.SetWords(True)
                except Exception as e2:
                    self.get_logger().error(f"Failed to reinitialize recognizer: {e2}")


    def _extract_text(self, result_json: str) -> Optional[str]:
        import json
        try:
            res = json.loads(result_json)
            text = res.get("text", "").strip()
            return text if text else None
        except Exception as e:
            self.get_logger().warn(f"Failed to parse Vosk result: {e}")
            return None

    def _publish_text(self, text: str):
        if not self.listening_enabled:
            self.get_logger().info(f"ASR muted, ignoring text: {text!r}")
            return

        msg = String()
        msg.data = text
        self.get_logger().info(f"ASR text: {text!r}")
        self.asr_pub.publish(msg)

        if self.publish_llm:
            self.get_logger().info(f"Forwarding to LLM topic: {self.llm_topic}")
            self.llm_pub.publish(msg)


    # ----------------------------------
    # Cleanup
    # ----------------------------------
    def destroy_node(self):
        self.get_logger().info("Shutting down ReSpeakerVoskASR node...")
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                self.get_logger().warn(f"Error stopping audio stream: {e}")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ReSpeakerVoskASR()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
