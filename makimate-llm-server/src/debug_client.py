#!/usr/bin/env python3
"""
debug_client.py — simple terminal client to talk to server_llm.py for debugging.

Features
- Interactive prompt: type a message, see streamed response in real time
- Commands:
    /reset         -> calls POST /chat/reset (if exposed) to clear conversation
    /sys <prompt>  -> calls POST /chat/system to set system prompt
    /exit          -> quit

Usage
    python debug_client.py --url http://localhost:8000
    python debug_client.py --url http://192.168.1.50:8000

Requirements
    pip install requests
"""
from __future__ import annotations
import sys
import argparse
import json
import time
from typing import Optional

import requests


class LLMClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def stream_chat(self, message: str) -> int:
        """
        Send a message and stream the plain-text response as it arrives.
        Returns the HTTP status code.
        """
        url = f"{self.base_url}/chat/stream"
        headers = {"Content-Type": "application/json"}
        try:
            with requests.post(url, headers=headers, data=json.dumps({"message": message}),
                               timeout=self.timeout, stream=True) as r:
                r.raise_for_status()
                # Stream in tiny chunks for "real-time" feel
                for chunk in r.iter_content(chunk_size=1, decode_unicode=True):
                    if chunk:
                        print(chunk, end="", flush=True)
                print()  # newline after stream ends
                return r.status_code
        except requests.exceptions.RequestException as e:
            print(f"\n[HTTP error] {e}")
            return 0

    def set_system_prompt(self, prompt: str) -> bool:
        url = f"{self.base_url}/chat/system"
        headers = {"Content-Type": "application/json"}
        try:
            r = requests.post(url, headers=headers, data=json.dumps({"prompt": prompt}), timeout=self.timeout)
            if r.status_code == 200:
                print("[ok] system prompt updated.")
                return True
            else:
                print(f"[warn] /chat/system returned {r.status_code}: {r.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[HTTP error] {e}")
            return False

    def reset(self) -> bool:
        url = f"{self.base_url}/chat/reset"
        # Some setups may not have this route; inform user if missing
        try:
            r = requests.post(url, timeout=self.timeout)
            if r.status_code == 200:
                print("[ok] conversation reset.")
                return True
            else:
                print(f"[warn] /chat/reset returned {r.status_code}: {r.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[HTTP error] {e}")
            return False


def main():
    ap = argparse.ArgumentParser(description="Streaming debug client for server_llm.py")
    ap.add_argument("--url", default="http://localhost:8000",
                    help="Base URL of the LLM server (default: http://localhost:8000)")
    ap.add_argument("--timeout", type=float, default=120.0, help="HTTP timeout seconds (default: 120)")
    args = ap.parse_args()

    client = LLMClient(args.url, timeout=args.timeout)

    print(f"Connected to {client.base_url}")
    print("Type your message and press Enter.")
    print("Commands: /reset, /sys <prompt>, /exit")

    try:
        while True:
            try:
                user = input("\nYou> ").strip()
            except EOFError:
                print("\n[bye]")
                break
            if not user:
                continue

            low = user.lower()
            if low in {"/exit", "/quit"}:
                print("[bye]")
                break
            if low == "/reset":
                client.reset()
                continue
            if low.startswith("/sys"):
                prompt = user[len("/sys"):].strip()
                if prompt:
                    client.set_system_prompt(prompt)
                else:
                    print("Usage: /sys <system prompt text>")
                continue

            print("Assistant> ", end="", flush=True)
            status = client.stream_chat(user)
            if status == 0:
                print("[error] request failed.")

    except KeyboardInterrupt:
        print("\n[bye]")


if __name__ == "__main__":
    main()
