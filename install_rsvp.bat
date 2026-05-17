@echo off
REM ============================================
REM Wedding RSVP System - Windows Installation
REM ============================================

echo.
echo ================================================
echo   Wedding RSVP System - Installation Script
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if XAMPP MySQL is running
echo Checking MySQL connection...
python -c "import mysql.connector; mysql.connector.connect(host='localhost', user='root', password='')" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Cannot connect to MySQL
    echo.
    echo Please ensure:
    echo 1. XAMPP is installed
    echo 2. MySQL is running in XAMPP Control Panel
    echo 3. Database 'wedding_db' exists
    echo.
    echo Press any key to continue anyway...
    pause >nul
) else (
    echo [OK] MySQL connection successful
)

echo.
echo ================================================
echo   Running RSVP System Setup
echo ================================================
echo.

REM Run the setup script
python setup_rsvp.py

if errorlevel 1 (
    echo.
    echo [ERROR] Setup failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ================================================
echo   Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Start the Flask application: python app.py
echo 2. Login as host at http://127.0.0.1:5000/host/login
echo 3. Add guests and share RSVP links
echo.
echo For more information, see:
echo - RSVP_QUICK_START.md
echo - RSVP_SYSTEM_GUIDE.md
echo.
pause
