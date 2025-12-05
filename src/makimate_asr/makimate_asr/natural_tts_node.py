import queue
import threading
import time
import subprocess
import shlex
from typing import Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

# Optional pyttsx3 support (fallback backend)
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class NaturalTTS(Node):
    """
    Natural-sounding TTS node using Piper or pyttsx3.

    Streaming behavior (for /llm/stream sending incremental chunks/tokens):

    - Subscribes to /llm/stream, where each message is the next chunk of text
      (a word, piece, or punctuation).
    - Maintains an internal text buffer.
    - Appends each chunk to that buffer with sane spacing and punctuation rules
      (no spaces before , . ! ? etc.).
    - When the buffer has at least N words and reaches a sentence boundary
      (., !, ?), it flushes up to that sentence as a phrase to a worker queue.
    - A timer also flushes any leftover buffer after idle time (end of answer).
    - ASR is muted once at the start of speaking, and re-enabled only after
      all audio has finished for the utterance.
    """

    def __init__(self):
        super().__init__("natural_tts")

        # ---------- Parameters ----------
        self.declare_parameter("input_topic", "/llm/stream")
        self.declare_parameter("asr_enable_topic", "/asr/enable")
        self.declare_parameter("backend", "piper_cli")

        # pyttsx3 params
        self.declare_parameter("rate", 170)
        self.declare_parameter("volume", 1.0)
        self.declare_parameter("voice", "")

        # Piper params
        self.declare_parameter(
            "piper_command", "/home/makimate/MakiMate/piper_bin/piper/piper"
        )
        self.declare_parameter("piper_model", "")
        self.declare_parameter(
            "piper_audio_command", "aplay -r 22050 -f S16_LE -t raw -"
        )
        self.declare_parameter("length_scale", 0.75)
        self.declare_parameter("noise_scale", 0.6)
        self.declare_parameter("noise_w", 0.4)
        self.declare_parameter("sentence_silence", 0.25)

        # ---------- Read parameters ----------
        input_topic = self.get_parameter("input_topic").value
        asr_enable_topic = self.get_parameter("asr_enable_topic").value
        self.backend = self.get_parameter("backend").value.lower().strip()

        self.rate = int(self.get_parameter("rate").value)
        self.volume = float(self.get_parameter("volume").value)
        self.voice_name = self.get_parameter("voice").value

        self.piper_command = self.get_parameter("piper_command").value
        self.piper_model = self.get_parameter("piper_model").value
        self.piper_audio_command = self.get_parameter("piper_audio_command").value
        self.length_scale = float(self.get_parameter("length_scale").value)
        self.noise_scale = float(self.get_parameter("noise_scale").value)
        self.noise_w = float(self.get_parameter("noise_w").value)
        self.sentence_silence = float(self.get_parameter("sentence_silence").value)

        # ---------- Backend init ----------
        self.engine: Optional["pyttsx3.Engine"] = None
        if self.backend == "pyttsx3":
            self._init_pyttsx3()
        else:
            if self.backend not in ("piper_cli", "piper_python"):
                self.get_logger().warn(
                    f"Unknown backend '{self.backend}', defaulting to piper_cli."
                )
            # We currently only support the CLI path; piper_python just aliases to this
            self.backend = "piper_cli"
            self._init_piper()

        # ---------- ASR publisher ----------
        self.asr_enable_pub = self.create_publisher(Bool, asr_enable_topic, 10)

        # ---------- Speak queue + worker ----------
        self._queue: queue.Queue[str] = queue.Queue()
        self._worker_thread = threading.Thread(
            target=self._speak_loop, daemon=True
        )
        self._worker_thread.start()

        # Track whether we’re in the middle of an utterance (for ASR control)
        self._currently_speaking = False
        # Track last time any TTS activity happened (enqueue or audio finished)
        self._last_tts_activity_time = time.time()
        # How long with no TTS activity before we say "utterance finished"
        self._utterance_done_seconds = 1.0

        # ---------- Streaming buffer state ----------
        self._buffer = ""  # text we are accumulating to speak
        self._buf_lock = threading.Lock()
        # Last time we got any tokens from the LLM (for buffer idle flush)
        self._last_chunk_time = time.time()

        # Heuristics for flushing buffer:
        # - flush normal chunks: at least this many words AND at a sentence end
        self._flush_min_words = 20
        # - hard limits so it never grows forever (even if no period)
        self._flush_hard_max_words = 60
        self._flush_max_chars = 400
        # - idle time before flushing leftover at end of answer
        self._idle_flush_seconds = 0.5

        # NEW: first-sentence & grouping behavior
        # Track whether we've already sent the first sentence for this answer.
        self._first_sentence_sent = False
        # After the first sentence, how many sentences per chunk?
        # You can change this number (e.g., 2 or 3).
        self._sentences_per_chunk_after_first = 3

        # Timer to flush after idle (LLM-side)
        self._buffer_timer = self.create_timer(
            0.2, self._buffer_flush_timer_cb
        )

        # ---------- Subscriber ----------
        self.sub = self.create_subscription(
            String,
            input_topic,
            self._on_stream_text,
            10,
        )

        self.get_logger().info(
            f"NaturalTTS running. Backend={self.backend}, "
            f"input_topic={input_topic}, asr_enable_topic={asr_enable_topic}"
        )

    # ======================================================================
    # Streaming logic (incremental chunks)
    # ======================================================================
    def _on_stream_text(self, msg: String):
        """
        Handle incoming incremental chunks from /llm/stream.
        Each msg.data is just the next piece of text (word/piece/punctuation).
        """
        raw = msg.data
        # Normalize newlines to spaces, but keep punctuation intact
        chunk = raw.replace("\n", " ")
        if not chunk.strip():
            return

        now = time.time()

        with self._buf_lock:
            self._last_chunk_time = now  # LLM activity time

            stripped = chunk.strip()

            # Punctuation tokens we want to attach directly to previous word
            punct_tokens = {
                ",",
                ".",
                "!",
                "?",
                ";",
                ":",
                "...",
                ",'",
                ".'",
                "!'",
                "?'",
                "?”",
                "!”",
                '"',
                "''",
            }

            def is_apostrophe_clitic(tok: str) -> bool:
                """
                True for things like "'t", "'s", "’t", "’s" that should attach
                to the previous word with no space.
                """
                if len(tok) < 2:
                    return False
                if tok[0] in {"'", "’"} and tok[1].isalpha():
                    return True
                return False

            if stripped in punct_tokens:
                # Attach punctuation directly to previous text, no preceding space
                self._buffer = self._buffer.rstrip() + stripped
            elif is_apostrophe_clitic(stripped) and self._buffer:
                # Attach contractions like "'t", "'s" to the previous word
                self._buffer = self._buffer.rstrip() + stripped
            else:
                # Normal word-ish chunk: ensure exactly one space before it
                if self._buffer and not self._buffer.endswith(" "):
                    self._buffer += " "
                self._buffer += stripped

            # Decide if we should flush a sentence from the buffer
            to_speak = self._pop_flush_segment_locked()

        # We do the speaking enqueuing OUTSIDE the lock
        if to_speak:
            self.get_logger().info(
                f"Streaming TTS buffered chunk: {to_speak!r}"
            )
            # Mark TTS activity when we enqueue this
            self._last_tts_activity_time = time.time()
            self._queue.put(to_speak)


    def _pop_flush_segment_locked(self) -> str:
        """
        Decide if part of the buffer is ready to be spoken, and if so,
        return that part and keep the remainder in the buffer.

        Rules:
        - The very first complete sentence of an answer is flushed by itself,
          as soon as we see a sentence boundary ('.', '!', '?').
        - After that, we flush groups of N sentences at a time, where N is
          _sentences_per_chunk_after_first, when we have enough words.
        - If buffer has fewer than _flush_min_words and is not too large,
          do nothing (return "").
        - If buffer grows beyond hard limits (words or chars), flush all.
        """
        if not self._buffer:
            return ""

        buf = self._buffer
        words = buf.strip().split()
        word_count = len(words)
        char_count = len(buf)

        # Hard safety flush: buffer way too long, just send everything
        if word_count >= self._flush_hard_max_words or char_count >= self._flush_max_chars:
            phrase = buf.strip()
            self._buffer = ""
            # After this, we consider the first sentence "sent"
            self._first_sentence_sent = True
            return phrase

        # Find all sentence boundaries
        sentence_end_positions = []
        for i, ch in enumerate(buf):
            if ch in {".", "!", "?"}:
                sentence_end_positions.append(i)

        # If we have at least one sentence boundary and haven't sent the first
        # sentence yet, flush JUST the first sentence immediately, regardless
        # of _flush_min_words.
        if not self._first_sentence_sent and sentence_end_positions:
            first_pos = sentence_end_positions[0]
            phrase = buf[: first_pos + 1].strip()
            remainder = buf[first_pos + 1 :].lstrip()
            self._buffer = remainder
            self._first_sentence_sent = True
            return phrase

        # Normal sentence-based flushing (after the first sentence)
        if word_count >= self._flush_min_words and sentence_end_positions:
            # Decide up to which sentence we flush:
            # - if we have at least _sentences_per_chunk_after_first sentences,
            #   flush up to that many sentences
            # - otherwise, flush up to the last available sentence
            if len(sentence_end_positions) >= self._sentences_per_chunk_after_first:
                cutoff_pos = sentence_end_positions[self._sentences_per_chunk_after_first - 1]
            else:
                cutoff_pos = sentence_end_positions[-1]

            phrase = buf[: cutoff_pos + 1].strip()
            remainder = buf[cutoff_pos + 1 :].lstrip()
            self._buffer = remainder
            return phrase

        # Not enough words yet, or no sentence boundary found
        return ""

    def _buffer_flush_timer_cb(self):
        """
        Periodically flush any leftover buffer if the stream has gone idle
        (end of response).
        This is based on LLM inactivity, not TTS.
        """
        now = time.time()
        to_speak = ""

        with self._buf_lock:
            if (
                self._buffer
                and (now - self._last_chunk_time) >= self._idle_flush_seconds
            ):
                # End-of-answer: speak whatever is left, even if it doesn't
                # meet the min-word / sentence boundary rule.
                to_speak = self._buffer.strip()
                self._buffer = ""
                # Reset for the next answer so its first sentence is again
                # spoken alone.
                self._first_sentence_sent = False

        if to_speak:
            self.get_logger().info(
                f"Idle flush TTS chunk: {to_speak!r}"
            )
            # Mark TTS activity when we enqueue this
            self._last_tts_activity_time = time.time()
            self._queue.put(to_speak)

    # ======================================================================
    # Backend init
    # ======================================================================
    def _init_pyttsx3(self):
        if pyttsx3 is None:
            self.get_logger().error(
                "pyttsx3 backend selected but pyttsx3 is not installed."
            )
            return

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", self.rate)
        self.engine.setProperty("volume", self.volume)

        if self.voice_name:
            voices = self.engine.getProperty("voices")
            for v in voices:
                if self.voice_name.lower() in v.name.lower():
                    self.engine.setProperty("voice", v.id)
                    self.get_logger().info(f"Using pyttsx3 voice: {v.name}")
                    break

        self.get_logger().info("pyttsx3 backend initialized.")

    def _init_piper(self):
        if not self.piper_model:
            self.get_logger().error(
                "piper_cli backend requested but no 'piper_model' set."
            )
            return
        self.get_logger().info(
            f"Piper backend ready:\n"
            f"  command={self.piper_command}\n"
            f"  model={self.piper_model}"
        )

    # ======================================================================
    # ASR control
    # ======================================================================
    def _set_asr_enabled(self, enabled: bool):
        msg = Bool()
        msg.data = bool(enabled)
        self.asr_enable_pub.publish(msg)
        state = "enabled" if enabled else "disabled"
        self.get_logger().info(f"ASR {state} from TTS.")

    # ======================================================================
    # Worker thread (utterance-level ASR control)
    # ======================================================================
    def _speak_loop(self):
        self.get_logger().info("TTS worker thread running.")
        while rclpy.ok():
            try:
                text = self._queue.get(timeout=0.5)
            except queue.Empty:
                # If we were speaking and there has been no TTS activity
                # for a while, treat this as end-of-utterance.
                if self._currently_speaking:
                    now = time.time()
                    if (
                        now - self._last_tts_activity_time
                    ) >= self._utterance_done_seconds:
                        self.get_logger().info(
                            "Utterance finished, re-enabling ASR."
                        )
                        self._set_asr_enabled(True)
                        self._currently_speaking = False
                continue

            # We got some text to speak.
            # If this is the *first* chunk of an utterance, disable ASR once.
            if not self._currently_speaking:
                self._set_asr_enabled(False)
                self._currently_speaking = True

            try:
                if self.backend == "pyttsx3":
                    self._speak_pyttsx3(text)
                else:
                    self._speak_piper_cli(text)
            except Exception as e:
                self.get_logger().error(f"TTS error: {e}")
            # No artificial sleep here; we just loop and either grab the next
            # chunk or, if none arrives for _utterance_done_seconds, we
            # consider the utterance finished and unmute once.

    # ======================================================================
    # Backend speak methods
    # ======================================================================
    def _speak_pyttsx3(self, text: str):
        if self.engine is None:
            self.get_logger().error(
                "pyttsx3 engine not initialized."
            )
            return
        self.get_logger().info(f"[pyttsx3] Speaking: {text!r}")
        self.engine.say(text)
        self.engine.runAndWait()
        # Mark TTS activity finishing
        self._last_tts_activity_time = time.time()

    def _speak_piper_cli(self, text: str):
        if not self.piper_model:
            self.get_logger().error("No Piper model configured.")
            return

        piper_cmd = [
            self.piper_command,
            "--model",
            self.piper_model,
            "--output-raw",
            "--length_scale",
            str(self.length_scale),
            "--noise_scale",
            str(self.noise_scale),
            "--noise_w",
            str(self.noise_w),
            "--sentence_silence",
            str(self.sentence_silence),
        ]

        piper_cmd_str = " ".join(shlex.quote(c) for c in piper_cmd)
        full_cmd = f"{piper_cmd_str} | {self.piper_audio_command}"

        self.get_logger().info(f"[piper_cli] Speaking: {text!r}")
        self.get_logger().debug(f"[piper_cli] Pipeline: {full_cmd}")

        proc = subprocess.Popen(
            full_cmd, shell=True, stdin=subprocess.PIPE
        )

        try:
            if proc.stdin:
                proc.stdin.write((text.strip() + "\n").encode("utf-8"))
                proc.stdin.close()
            proc.wait()
        except Exception as e:
            self.get_logger().error(
                f"[piper_cli] Error while running Piper: {e}"
            )
        finally:
            if proc.poll() is None:
                proc.kill()
            # Mark TTS activity finishing after the audio completes
            self._last_tts_activity_time = time.time()

    # ======================================================================
    # Cleanup
    # ======================================================================
    def destroy_node(self):
        self.get_logger().info("Shutting down NaturalTTS node...")
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = NaturalTTS()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
