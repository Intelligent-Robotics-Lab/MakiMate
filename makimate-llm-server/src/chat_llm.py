#!/usr/bin/env python
# chat_llm.py — terminal chat + importable library (Ollama)
# Default model: deepseek-r1:7b
from __future__ import annotations
import sys
import argparse
from typing import Dict, List, Generator, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

import ollama
from ollama import ResponseError

DEFAULT_MODEL = "qwen2.5:7b-instruct"
console = Console()


class ChatLLM:
    """
    Importable wrapper for a local LLM served by Ollama.
    - Keeps conversation history
    - Stream or non-stream calls
    - Utilities to ensure daemon/model
    """
    def __init__(self, model: str = DEFAULT_MODEL, system_prompt: Optional[str] = None):
        self.model = model
        self.history: List[Dict[str, str]] = []
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

    # -------- housekeeping --------
    @staticmethod
    def ensure_ollama_daemon() -> None:
        """Raise SystemExit with a friendly message if daemon is unreachable."""
        try:
            _ = ollama.list()
        except Exception:
            console.print(
                Panel.fit(
                    "[bold red]Can't reach Ollama[/bold red]\n"
                    "Make sure the Ollama app/daemon is running.\n"
                    "On Windows, open the Ollama app or run:  [bold]ollama serve[/bold]",
                    box=box.ROUNDED,
                )
            )
            raise SystemExit(1)

    def ensure_model(self) -> None:
        """Ensure model is available; pull if missing (with progress)."""
        try:
            ollama.show(model=self.model)
            return
        except ResponseError:
            console.print(Panel.fit(f"Model [bold]{self.model}[/bold] not found locally — pulling...", box=box.ROUNDED))
            for chunk in ollama.pull(model=self.model, stream=True):
                status = chunk.get("status", "")
                completed = chunk.get("completed", 0)
                total = chunk.get("total", 0)
                if total:
                    console.print(f"{status}: {completed}/{total}", end="\r")
                else:
                    console.print(status, end="\r")
            console.print("\n[green]Pull complete.[/green]")

    # -------- conversation control --------
    def set_system_prompt(self, text: str) -> None:
        """Insert/replace the system prompt at the top of history."""
        if not text:
            return
        if self.history and self.history[0]["role"] == "system":
            self.history[0]["content"] = text
        else:
            self.history.insert(0, {"role": "system", "content": text})

    def reset(self, keep_system: bool = False):
        if keep_system:
            system_msgs = [m for m in self.history if m.get("role") == "system"]
            self.history = system_msgs
        else:
            self.history = []

    # -------- inference --------
    def chat_once(self, user_message: str) -> str:
        """Non-streaming single turn; returns the full assistant reply."""
        if not user_message.strip():
            return ""
        self.history.append({"role": "user", "content": user_message})
        try:
            resp = ollama.chat(model=self.model, messages=self.history)
            reply = resp["message"]["content"]
        except Exception as e:
            # rollback user turn if it failed
            self.history.pop()
            raise e
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """
        Streaming single turn; yields chunks of assistant text.
        The reply is appended to history automatically at the end.
        """
        if not user_message.strip():
            return
        self.history.append({"role": "user", "content": user_message})
        reply = ""
        try:
            stream = ollama.chat(model=self.model, messages=self.history, stream=True)
            for chunk in stream:
                delta = chunk["message"]["content"]
                reply += delta
                yield delta
        except Exception as e:
            # rollback user turn if it failed
            self.history.pop()
            raise e
        self.history.append({"role": "assistant", "content": reply})

    # -------- persistence (optional) --------
    def export_transcript(self) -> List[Dict[str, str]]:
        """Return a deep-ish copy of the history for saving/logging."""
        return [dict(m) for m in self.history]

    def save_transcript(self, path: str) -> None:
        """Save the conversation as a simple UTF-8 text file."""
        lines = []
        for m in self.history:
            role = m["role"]
            content = m["content"].replace("\r\n", "\n")
            lines.append(f"{role.upper()}:\n{content}\n{'-'*60}\n")
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)


# ---------------- CLI (keeps original terminal chat UX) ----------------
def _interactive_loop(model: str, system: Optional[str]) -> None:
    ChatLLM.ensure_ollama_daemon()
    chat = ChatLLM(model=model, system_prompt=system)
    chat.ensure_model()

    console.print(
        Panel.fit(
            f"Local LLM chat — [bold]{chat.model}[/bold]\n"
            "Type and press Enter.\n"
            "Commands: [bold]/reset[/bold], [bold]/sys <text>[/bold], [bold]/save <file>[/bold], [bold]/exit[/bold]",
            box=box.ROUNDED,
        )
    )

    while True:
        try:
            user = Prompt.ask("\n[bold]You[/bold]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye.[/dim]")
            break
        if not user:
            continue

        # commands
        low = user.lower()
        if low in {"/exit", "/quit"}:
            console.print("[dim]Bye.[/dim]")
            break
        if low == "/reset":
            chat.reset(keep_system=True)
            console.print("[green]Conversation cleared (system prompt kept).[/green]")
            continue
        if low.startswith("/sys"):
            new_sys = user[len("/sys"):].strip()
            if new_sys:
                chat.set_system_prompt(new_sys)
                console.print(Panel.fit("System prompt updated.", box=box.ROUNDED))
            else:
                console.print("[yellow]Usage:[/yellow] /sys <your system prompt>")
            continue
        if low.startswith("/save"):
            path = user[len("/save"):].strip() or "transcript.txt"
            try:
                chat.save_transcript(path)
                console.print(f"[green]Saved transcript to[/green] {path}")
            except Exception as e:
                console.print(f"[red]Failed to save:[/red] {e}")
            continue

        # regular chat (streamed)
        console.print("[bold cyan]Assistant[/bold cyan]> ", end="")
        try:
            for delta in chat.chat_stream(user):
                console.print(delta, end="", soft_wrap=True)
                sys.stdout.flush()
            print()
        except ResponseError as e:
            console.print(f"\n[red]Model error:[/red] {e}")
        except Exception as e:
            console.print(f"\n[red]Unexpected error:[/red] {e}")


def main():
    parser = argparse.ArgumentParser(description="Terminal chat with a local LLM via Ollama.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model tag (default: {DEFAULT_MODEL})")
    parser.add_argument("--system", default=None, help="Optional system prompt to steer behavior.")
    args = parser.parse_args()
    _interactive_loop(args.model, args.system)


if __name__ == "__main__":
    main()
