@echo off
REM ============================================
REM Vendor Management System - Windows Installation
REM ============================================

echo.
echo ================================================
echo   Vendor Management System - Installation
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
echo   Running Vendor System Setup
echo ================================================
echo.

REM Run the setup script
python setup_vendor_enhancement.py

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
echo New Features Added:
echo   - Enhanced vendor profiles
echo   - Real-time chat system
echo   - Vendor gallery
echo   - Rating and review system
echo   - Advanced filtering
echo   - Booking system
echo   - Auto-blocking policy
echo.
echo Next steps:
echo 1. Start Flask app: python app.py
echo 2. Access marketplace: http://127.0.0.1:5000/marketplace
echo 3. Vendor dashboard: http://127.0.0.1:5000/vendor/
echo.
echo Documentation:
echo - VENDOR_QUICK_START.md - Quick reference
echo - VENDOR_SYSTEM_IMPLEMENTATION.md - Complete guide
echo - VENDOR_CHECKLIST.md - Testing checklist
echo.
pause
