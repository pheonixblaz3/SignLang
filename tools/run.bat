@echo off
REM SignSpeak Project Launcher - Production Ready
REM American Sign Language Recognition System

setlocal enabledelayedexpansion
cd /d "%~dp0\.."

echo.
echo ========================================
echo   SignSpeak ASL Recognition System
echo ========================================
echo.

REM Get Python executable path from venv
set PYTHON_EXE=.venv\Scripts\python.exe
set PIP_EXE=.venv\Scripts\pip.exe

REM Verify .venv exists and Python is available
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Virtual environment or Python not found at: %PYTHON_EXE%
    echo [*] Attempting to find Python in system...
    where python >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Python not found in PATH. Please install Python 3.10+
        pause
        exit /b 1
    )
    echo [WARNING] Using system Python instead
    set PYTHON_EXE=python
    set PIP_EXE=pip
) else (
    echo [✓] Virtual environment found
)

REM Verify dependencies are installed
echo.
echo [*] Checking dependencies...
"%PIP_EXE%" list 2>nul | findstr "fastapi uvicorn" >nul
if !errorlevel! neq 0 (
    echo [*] Installing dependencies from requirements.txt...
    "%PIP_EXE%" install -q -r requirements.txt 2>nul
    if !errorlevel! neq 0 (
        echo [WARNING] Dependency installation may have issues, but continuing...
    )
)
echo [✓] Dependencies ready

REM Run the FastAPI server
echo.
echo ========================================
echo   Starting FastAPI Server
echo ========================================
echo.
echo [INFO] Server available at:
echo   - Web UI: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo.
echo [INFO] Press Ctrl+C to stop the server
echo.

"%PYTHON_EXE%" -m uvicorn main:app --host 0.0.0.0 --port 8000

pause
