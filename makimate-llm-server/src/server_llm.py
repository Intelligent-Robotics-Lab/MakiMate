# server_llm.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from chat_llm import ChatLLM

app = FastAPI()
chat = ChatLLM()  # uses DEFAULT_MODEL from chat_llm.py

class ChatIn(BaseModel):
    message: str

@app.post("/chat/stream")
def chat_stream(inp: ChatIn):
    text = inp.message.strip()
    low = text.lower()

    # ----- command: /reset -----
    if low == "/reset":
        chat.reset(keep_system=True)
        # Return an empty plain-text response so the client gets ""
        return PlainTextResponse("", status_code=200)
        # or: return PlainTextResponse(status_code=204)

    # ----- command: /sys <text> -----
    if low.startswith("/sys"):
        new_sys = text[len("/sys"):].strip()
        if not new_sys:
            return PlainTextResponse("Usage: /sys <your system prompt>")
        chat.set_system_prompt(new_sys)
        return PlainTextResponse("System prompt updated.")

    # ----- command: /save [file] -----
    if low.startswith("/save"):
        path = text[len("/save"):].strip() or "transcript.txt"
        try:
            chat.save_transcript(path)
            return PlainTextResponse(f"Saved transcript to {path}")
        except Exception as e:
            return PlainTextResponse(f"Failed to save: {e}")

    # ----- normal streamed chat -----
    def token_gen():
        for delta in chat.chat_stream(text):
            # send plain text chunks
            yield delta
    return StreamingResponse(token_gen(), media_type="text/plain")
