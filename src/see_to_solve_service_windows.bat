@echo off
echo Starting See to Solve Service...

REM Get the directory where the batch file is located
set "SCRIPT_DIR=%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.11 or later.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is not installed! Please install pip.
    pause
    exit /b 1
)

REM Check if requirements.txt exists
if not exist "%SCRIPT_DIR%requirements.txt" (
    echo requirements.txt not found! Please make sure you're in the correct directory.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r "%SCRIPT_DIR%requirements.txt"
if errorlevel 1 (
    echo Failed to install dependencies!
    pause
    exit /b 1
)

REM Check if Stockfish exists
if not exist "%SCRIPT_DIR%stockfish.exe" (
    echo Stockfish not found! Please make sure stockfish.exe is in the current directory.
    pause
    exit /b 1
)

REM Start the Flask service
echo Starting Flask service...
echo The service will be available at http://127.0.0.1:8080
echo Press Ctrl+C to stop the service
cd /d "%SCRIPT_DIR%"
python main.py

pause 