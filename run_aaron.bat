@echo off
title 🚀 Aaron Assistant Launcher
echo =============================
echo   Starting Aaron Assistant
echo =============================
echo.

:: Change to project directory (this .bat file's folder)
cd /d "%~dp0"

:: Activate virtual environment
call venv\Scripts\activate

:: Upgrade pip silently
python -m pip install --upgrade pip >nul 2>&1

:: Install dependencies from requirements.txt
echo Installing required Python packages...
pip install --upgrade --no-cache-dir -r requirements.txt

:: Run the assistant
echo.
echo Launching Aaron Assistant... Please wait.
python run_desktop.py

:: End message
echo.
echo =============================
echo   Aaron Assistant has exited.
echo   Press any key to close...
echo =============================
pause >nul
