@echo off
REM Quick start script for GSTSaathi backend development (Windows)

echo === GSTSaathi Backend Quick Start ===

REM Check Python version
echo Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt

REM Copy .env.example to .env if .env doesn't exist
if not exist ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo IMPORTANT: Edit .env and add your GEMINI_API_KEY
)

REM Create necessary directories
if not exist "uploads\invoices" mkdir uploads\invoices
if not exist "uploads\gstr2b" mkdir uploads\gstr2b
if not exist "exports" mkdir exports
if not exist "gst_law_db" mkdir gst_law_db

REM Run database migrations (create tables)
echo Initializing database...
python -c "from app.database import init_db; init_db()"

REM Start the server
echo.
echo === Starting FastAPI server ===
echo API Docs: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
