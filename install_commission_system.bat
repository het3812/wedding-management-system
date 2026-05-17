@echo off
echo ============================================
echo Commission Tracking System Installation
echo ============================================
echo.
echo This will install the 2.5%% commission tracking system
echo for the Wedding Management Platform.
echo.
echo Prerequisites:
echo - MySQL/XAMPP must be running
echo - wedding_db database must exist
echo.
pause

echo.
echo Installing commission system database schema...
echo.

mysql -u root wedding_db < database_commission_system.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo SUCCESS! Commission system installed.
    echo ============================================
    echo.
    echo Next steps:
    echo 1. Restart your Flask application
    echo 2. Login as Admin
    echo 3. Navigate to /admin/commissions
    echo.
    echo Features available:
    echo - Commission Dashboard with charts
    echo - Automated 2.5%% commission calculation
    echo - Collection and waiving management
    echo - Vendor commission reports
    echo - CSV export functionality
    echo.
    echo For detailed usage, see COMMISSION_SYSTEM_GUIDE.md
    echo.
) else (
    echo.
    echo ============================================
    echo ERROR: Installation failed!
    echo ============================================
    echo.
    echo Possible issues:
    echo - MySQL is not running
    echo - Database 'wedding_db' does not exist
    echo - MySQL credentials are incorrect
    echo.
    echo Please check and try again.
    echo.
)

pause
