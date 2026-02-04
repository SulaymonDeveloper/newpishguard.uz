@echo off
echo ======================================
echo PhishGuard.uz Training Platform
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
pip install -r requirements.txt >nul 2>&1

REM Initialize database if it doesn't exist
if not exist "phishguard.db" (
    echo Initializing database...
    python -c "from app import init_db; init_db()"
)

echo.
echo Starting server...
echo.
echo Access the application at: http://localhost:5000
echo.
echo Admin credentials:
echo    Username: admin
echo    Password: sulaymon123
echo.
echo Press Ctrl+C to stop the server
echo ======================================
echo.

python app.py
pause
