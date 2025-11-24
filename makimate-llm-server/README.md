# MakiMate LLM Server

This repo contains the local LLM HTTP server used by MakiMate.
It runs on Windows and exposes a `/chat/stream` endpoint used by the Raspberry Pi via ROS2.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
