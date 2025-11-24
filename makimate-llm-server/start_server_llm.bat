@echo off
title MakiMate LLM Server

REM Move to your server directory
cd /d C:\Users\baong\Desktop\MakiMate\makimate-llm-server\src

REM Optional: activate virtual environment
call .\.venv\Scripts\activate.bat

echo Starting MakiMate FastAPI LLM Server...
echo Model: qwen2.5:7b-instruct
echo --------------------------------------

uvicorn server_llm:app --host 0.0.0.0 --port 8000 --log-level info

echo.
echo Server stopped.
pause
