@echo off
echo ========================================
echo RATING & REVIEW SYSTEM INSTALLER
echo ========================================
echo.

echo This script will install the rating and review system.
echo.
echo Prerequisites:
echo - MySQL/XAMPP running
echo - wedding_db database exists
echo - Python Flask application installed
echo.

pause

echo.
echo Step 1: Installing database enhancements...
echo.

mysql -u root -p wedding_db < database_review_enhancement.sql

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Database tables created successfully!
) else (
    echo [ERROR] Database installation failed!
    echo Please check:
    echo - MySQL is running
    echo - wedding_db database exists
    echo - MySQL credentials are correct
    pause
    exit /b 1
)

echo.
echo Step 2: Verifying installation...
echo.

mysql -u root -p wedding_db -e "SHOW TABLES LIKE 'review%%';"

echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Restart your Flask application: python app.py
echo 2. Login as host and book a vendor
echo 3. Vendor marks booking as completed
echo 4. Host writes a review
echo 5. Test all features!
echo.
echo Documentation:
echo - Quick Start: REVIEW_SYSTEM_QUICK_START.md
echo - Full Guide: RATING_REVIEW_SYSTEM_GUIDE.md
echo.

pause
