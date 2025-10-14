@echo off
REM Quick run script for Windows users
REM Double-click this file to run Transcribair after setup

echo Starting Transcribair...
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first to install Transcribair.
    echo.
    pause
    exit /b 1
)

REM Add FFmpeg to PATH if it exists in the user's .transcribair directory
set "FFMPEG_DIR=%USERPROFILE%\.transcribair\ffmpeg"
if exist "%FFMPEG_DIR%\ffmpeg.exe" (
    echo Found FFmpeg at %FFMPEG_DIR%
    set "PATH=%FFMPEG_DIR%;%PATH%"
) else (
    echo Warning: FFmpeg not found at %FFMPEG_DIR%
    echo FFmpeg will be installed on first run if needed.
    echo.
)

REM Run the application
venv\Scripts\python.exe app.py

REM Pause if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
