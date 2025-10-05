@echo off
REM AI Content Studio - Local Startup Script
REM This script starts both backend and frontend for local development

echo =====================================
echo AI Content Studio - Local Launch
echo =====================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Please create .env from .env.example:
    echo   copy .env.example .env
    echo.
    echo Then add your API keys to .env
    pause
    exit /b 1
)

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo.
echo [2/4] Installing/updating dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Initializing database...
python -c "from backend.database import init_db; import asyncio; asyncio.run(init_db())"

echo.
echo [4/4] Starting services...
echo.
echo =====================================
echo Backend will start on: http://localhost:8000
echo Frontend will start on: http://localhost:8501
echo.
echo Press Ctrl+C in each window to stop
echo =====================================
echo.

REM Start backend in new window
start "AI Content Studio - Backend" cmd /k "echo Starting Backend... && uvicorn backend.main:app --reload"

REM Wait a bit for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend in new window
start "AI Content Studio - Frontend" cmd /k "echo Starting Frontend... && cd frontend && streamlit run app.py"

echo.
echo [SUCCESS] Services starting!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
echo Check the new terminal windows for logs.
echo.
pause

