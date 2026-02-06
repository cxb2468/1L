@echo off
TITLE Flask Japan Vocabulary App - Setup and Run
cd /d D:\1L\deployment

echo ==========================================
echo Flask Japan Vocabulary Application Setup
echo ==========================================

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher and make sure it's in your PATH.
    pause
    exit /b 1
)

echo Python found. Checking virtual environment...

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

echo Installing dependencies...
if exist "requirements_windows.txt" (
    python -m pip install -r requirements_windows.txt
) else (
    echo requirements_windows.txt not found!
    pause
    exit /b 1
)

if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo Starting Flask Japan Vocabulary Application...
echo Access the application at http://localhost:8000
echo Press Ctrl+C to stop the application.

set FLASK_CONFIG=production
set SECRET_KEY=your-production-secret-key-here
set DATABASE_URL=japan.db

waitress-serve --host=0.0.0.0 --port=8000 wsgi:application

pause