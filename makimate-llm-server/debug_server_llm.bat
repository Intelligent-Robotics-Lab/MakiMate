@echo off
title MakiMate LLM Debug Tools

echo Checking if server is reachable...
curl http://localhost:8000/docs

echo.
echo Sending test query...
curl -N -X POST http://localhost:8000/chat/stream ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"Explain in detail how a rocket guidance system works during launch, ascent, and orbital insertion. Describe the roles of inertial measurement units, PID loops, thrust vector control, Kalman filtering, and how the system rejects noise and disturbances. Include explanations of both high-level behavior and low-level control signals. Make the explanation at least eight paragraphs long.\"}"

echo.
echo Press any key to exit...
pause >nul
