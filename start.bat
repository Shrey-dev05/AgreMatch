@echo off
title Hackathon Aggregator Launcher
echo ========================================================
echo   Launching Hackathon Aggregator (Frontend + Backend)
echo ========================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

:: Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH! Please install Node.js 18+.
    pause
    exit /b 1
)

echo [1/3] Starting FastAPI Backend on http://localhost:8000...
start "Agreggator Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

echo [2/3] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo [3/3] Starting Next.js Frontend on http://localhost:3000...
echo.
echo Opening portal in your default browser...
start http://localhost:3000/hackathons

cd frontend
npm.cmd run dev

pause
