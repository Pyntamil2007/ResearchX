@echo off
echo =================================================================
echo   Running ResearchX Full-Stack System & Integrity Test Suite
echo =================================================================
cd /d "%~dp0backend"
.\.venv\Scripts\python.exe -u verify_all_features.py
pause
