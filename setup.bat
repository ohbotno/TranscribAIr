@echo off
REM Quick setup script for Windows users
REM Double-click this file to set up Transcribair

echo ============================================================
echo Transcribair Quick Setup (Windows)
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Run the setup script
python setup.py

if errorlevel 1 (
    echo.
    echo Setup failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup complete!
echo ============================================================
echo.
echo To run Transcribair:
echo   1. Double-click "run.bat"
echo   or
echo   2. Open Command Prompt here and run: venv\Scripts\activate ^&^& python app.py
echo.
pause
