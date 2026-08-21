@echo off
echo ===================================================
echo   Starting ResearchX Frontend Server (React + Vite)
echo ===================================================
cd /d "%~dp0frontend"
set PATH=C:\Program Files\nodejs;C:\Users\pynta\AppData\Roaming\npm;%PATH%
npm run dev -- --host 127.0.0.1 --port 5173
pause
