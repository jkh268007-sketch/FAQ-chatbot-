@echo off
echo ==============================
echo   STARTING FAQ CHATBOT
echo ==============================

echo.
echo [1/3] Starting OLLAMA...
start cmd /k "ollama run tinyllama"

timeout /t 5

echo.
echo [2/3] Starting FASTAPI Backend...
start cmd /k "cd /d %~dp0 && uvicorn main:app --reload --port 8000"

timeout /t 5

echo.
echo [3/3] Opening Website (Live View)...
start http://127.0.0.1:5500/static/index.html

echo.
echo ✅ ALL DONE
pause
