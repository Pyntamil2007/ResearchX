@echo off
echo =================================================================
echo   ResearchX - Web Research Analyzer: Full-Stack Launcher
echo =================================================================
echo.
echo [1/2] Starting Backend Server (FastAPI on Port 8000)...
start "ResearchX Backend API" cmd /k "cd /d %~dp0backend && .\.venv\Scripts\python.exe run.py"

echo [2/2] Starting Frontend Server (React Vite on Port 5173)...
start "ResearchX Frontend UI" cmd /k "cd /d %~dp0frontend && set PATH=C:\Program Files\nodejs;C:\Users\pynta\AppData\Roaming\npm;%%PATH%% && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo Both servers are launching!
echo Backend:  http://127.0.0.1:8000 (API Docs: http://127.0.0.1:8000/docs)
echo Frontend: http://127.0.0.1:5173
echo.
echo Opening browser at http://127.0.0.1:5173/login ...
timeout /t 3 >nul
start http://127.0.0.1:5173/login
