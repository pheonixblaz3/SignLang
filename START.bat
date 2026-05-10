@echo off
cd /d "%~dp0"

cls
echo.
echo ╔════════════════════════════════════════╗
echo ║   SignSpeak - ASL Recognition System   ║
echo ╚════════════════════════════════════════╝
echo.

REM Direct path to Python in virtual environment
set VENV_PYTHON=%CD%\.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment not found at %VENV_PYTHON%
    pause
    exit /b 1
)

echo Starting FastAPI server...
echo.
echo Server available at:
echo   - http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

"%VENV_PYTHON%" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
