````markdown
# LLM_Hosting_README.md

This README explains how to host the **local LLM server** for MakiMate on a **Windows PC** using:

- **Ollama** (for running the model locally)
- **Qwen2.5 7B Instruct** as the LLM (`qwen2.5:7b-instruct`)
- A **Python virtual environment** for the FastAPI server
- The provided **batch files** for starting the LLM server

All commands and paths in this guide assume **Windows 10/11**.

---

## 1. Repository Layout (LLM Server)

Your local LLM hosting repo (typically cloned somewhere like `C:\MakiMate\makimate-llm-server`) looks like this:

```text
makimate-llm-server/
├── README.md
├── debug_server_llm.bat
├── requirements.txt
├── src
│   ├── __pycache__
│   │   ├── chat_llm.cpython-313.pyc
│   │   └── server_llm.cpython-313.pyc
│   ├── chat_llm.py
│   ├── debug_client.py
│   └── server_llm.py
└── start_server_llm.bat
````

Key files:

* `src/server_llm.py` – FastAPI server that exposes `/chat/stream` to the robot
* `src/chat_llm.py` – Wraps calls to the local Ollama model
* `start_server_llm.bat` – Normal startup script for the LLM server
* `debug_server_llm.bat` – Debug-friendly startup (e.g., nohidden console, extra logs)

---

## 2. Install Ollama on Windows

Ollama is the local model runtime that actually runs **Qwen2.5 7B Instruct** on your GPU/CPU.

1. Open a browser on your Windows machine.
2. Go to: **[https://ollama.com/](https://ollama.com/)**
3. Download the **Windows installer**.
4. Run the installer and follow the prompts (keep defaults unless you know what you’re doing).
5. After installation, open **Command Prompt** or **PowerShell** and check:

   ```powershell
   ollama --version
   ```

   If you get a version string (e.g., `ollama 0.x.x`), it’s installed correctly.

---

## 3. Download the Qwen2.5 7B Instruct Model

The model we use is:

> **`qwen2.5:7b-instruct`**

This is pulled and managed by **Ollama**, so you only need one command.

In **Command Prompt** or **PowerShell**:

```powershell
ollama pull qwen2.5:7b-instruct
```

Ollama will:

* Download the model weights
* Register them under the name `qwen2.5:7b-instruct`
* Store them in its local model cache

You can test it quickly (optional):

```powershell
ollama run qwen2.5:7b-instruct
```

Type a short question to confirm it generates responses, then exit with `Ctrl+C`.

---

## 4. Clone the makimate-llm-server Repository (Windows)

On your Windows PC:

1. Choose a directory (example: `C:\MakiMate`).
2. Open **PowerShell** or **Command Prompt**.
3. Run:

   ```powershell
   cd C:\MakiMate
   git clone https://github.com/Intelligent-Robotics-Lab/makimate-llm-server.git
   cd makimate-llm-server
   ```

You should now see:

```text
C:\MakiMate\makimate-llm-server> dir
```

with `start_server_llm.bat`, `debug_server_llm.bat`, `requirements.txt`, and the `src` folder.

---

## 5. Set Up a Python Virtual Environment (Windows)

We’ll create a dedicated venv for the LLM server so it doesn’t conflict with other Python installs.

> **Note:** Use Python 3.10–3.12 (whichever you have, as long as it’s compatible with the requirements).

### 5.1. Create the venv

From inside `makimate-llm-server`:

```powershell
cd C:\MakiMate\makimate-llm-server
python -m venv venv
```

This creates a `venv` folder in the repo.

### 5.2. Activate the venv

```powershell
.\venv\Scripts\activate
```

You should see something like `(venv)` at the start of your prompt.

### 5.3. Install Python dependencies

With the venv **active**:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:

* FastAPI
* Uvicorn
* HTTP clients
* Any other dependencies used by `server_llm.py` and `chat_llm.py`

---

## 6. How the LLM Server Works (High-Level Overview)

* **Ollama** hosts the `qwen2.5:7b-instruct` model locally on your Windows PC.

* `src/chat_llm.py` talks to Ollama’s local HTTP API (e.g., `http://localhost:11434/`) and streams generated tokens.

* `src/server_llm.py` is a **FastAPI** service that exposes an endpoint like:

  ```text
  http://<windows_pc_ip>:8000/chat/stream
  ```

* On the **Raspberry Pi**, the `llm_bridge_node.py` connects to that endpoint and:

  * Sends user messages from `/llm/request`
  * Streams responses back into ROS (`/llm/stream` and `/llm/response`)

The batch files `start_server_llm.bat` and `debug_server_llm.bat` are convenience wrappers to:

* Activate the venv
* Start `server_llm.py` using Uvicorn
* Optionally add logging or debug flags

---

## 7. Configure Ollama Model Name (If Needed)

By default, your Python code in `chat_llm.py` should be set to use **`qwen2.5:7b-instruct`**.

Open it in a text editor (VS Code / Notepad++ / etc.):

```text
C:\MakiMate\makimate-llm-server\src\chat_llm.py
```

Look for the model name, e.g.:

```python
MODEL_NAME = "qwen2.5:7b-instruct"
```

If it differs, change it to exactly:

```python
MODEL_NAME = "qwen2.5:7b-instruct"
```

Save the file.

---

## 8. Starting the LLM Server (Normal Mode)

The easiest way to start the server is via the **provided batch file**.

### 8.1. Ensure Ollama is running

Usually Ollama runs automatically after installation. If needed, you can start it manually by launching the **Ollama app** or by running:

```powershell
ollama serve
```

in a terminal.

### 8.2. Use `start_server_llm.bat`

In **File Explorer**, navigate to:

```text
C:\MakiMate\makimate-llm-server
```

Double-click:

```text
start_server_llm.bat
```

Typical behavior of `start_server_llm.bat` (conceptual):

* Activates `venv`
* Runs something like:

  ```powershell
  uvicorn src.server_llm:app --host 0.0.0.0 --port 8000 --reload
  ```

Once it’s started, you should see logs indicating that the FastAPI server is listening on port **8000**.

> **Note:** Keep this terminal **open** while the robot is using the LLM. Closing it stops the LLM server.

---

## 9. Starting the LLM Server (Debug Mode)

For more detailed output (or if `start_server_llm.bat` hides the console), use:

```text
debug_server_llm.bat
```

This is useful if:

* You want to see raw logs and tracebacks
* You’re changing code in `server_llm.py` or `chat_llm.py` and need quick feedback

Right-click the `.bat` → “Run as administrator” is sometimes helpful if ports or PATH cause problems, though typically not required.

---

## 10. Testing the LLM Server from Windows

With the server running, you can test via browser or curl.

### 10.1. Browser test

Open your browser and go to:

```text
http://localhost:8000/docs
```

You should see the FastAPI **Swagger UI**.

* Look for a `/chat/stream` endpoint.
* You can send a test message from there to confirm you get streamed responses.

### 10.2. Python debug client

The repo also includes `src/debug_client.py` for testing.

From inside the venv, in the repo folder:

```powershell
cd C:\MakiMate\makimate-llm-server
.\venv\Scripts\activate
python .\src\debug_client.py
```

It should send a test prompt to the local LLM server and print the response.

---

## 11. Connecting the Raspberry Pi (Robot) to the Windows LLM Server

On the **Raspberry Pi**, the node `llm_bridge_node.py` in the MakiMate project needs to know the IP address of the **Windows PC**.

Typical setup:

1. Find your Windows machine’s LAN IP:

   ```powershell
   ipconfig
   ```

   Look for something like `IPv4 Address . . . . . . . . . . : 192.168.1.50`.

2. On the Pi, in the MakiMate repo, edit:

   ```bash
   nano ~/MakiMate/src/makimate_asr/makimate_asr/llm_bridge_node.py
   ```

3. Set `laptop_host` to that IP:

   ```python
   # Example:
   self.host = "http://192.168.1.50:8000"
   ```

4. Rebuild / restart the ROS 2 nodes on the Pi.

Now the robot will send LLM requests to your Windows PC at `http://<windows-ip>:8000/chat/stream`.

---

## 12. Typical Workflow (End-to-End)

1. **On Windows PC**

   * Start Ollama (if not auto-started)
   * Ensure `qwen2.5:7b-instruct` is pulled
   * Run `start_server_llm.bat` inside `makimate-llm-server`
2. **On Raspberry Pi**

   * Launch the desired MakiMate mode:

     * `demo_mode` (no LLM needed)
     * `presentation_mode` or `full_feature_mode` (LLM required)
3. **Interaction**

   * Speak to the robot
   * ASR on Pi → `llm_bridge_node.py` → Windows LLM server → response → TTS → robot speaks back

---

## 13. Troubleshooting Tips

* **Port already in use (8000):**

  * Stop any other service using port 8000 or update the port in `start_server_llm.bat` and `llm_bridge_node.py` to match.
* **Ollama not found:**

  * Make sure Ollama is installed and added to PATH, or open Ollama’s app manually and then start the server.
* **No response from `/chat/stream`:**

  * Check `debug_server_llm.bat` logs for Python errors.
  * Make sure `MODEL_NAME` in `chat_llm.py` is correctly set to `qwen2.5:7b-instruct`.
* **Robot cannot reach Windows PC:**

  * Verify both devices are on the same network.
  * Use `ping <windows-ip>` from the Pi.
  * Ensure Windows firewall allows inbound connections on port 8000.

---

## 🧭 Navigation

🔙 Back to Main Documentation
➡️ [`../../README.md`](Overall_README.md)

```
```

