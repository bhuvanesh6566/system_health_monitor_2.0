@echo off
title AIOps System Health Monitor
cd /d "%~dp0"

echo.
echo  =========================================
echo   AIOps: Intelligent System Health Monitor
echo  =========================================
echo.
echo  Starting API backend and React frontend...
echo  Dashboard will open at http://localhost:5173
echo.

:: Start API in a new window
start "AIOps - API Server" cmd /k "cd /d "%~dp0backend" && python -m uvicorn api:app --host 0.0.0.0 --port 8000"

:: Wait 3 seconds for API to boot before starting frontend
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
start "AIOps - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo  Both services are starting in separate windows.
echo  Open http://localhost:5173 in your browser.
echo  Close those windows to stop the services.
echo.
pause
