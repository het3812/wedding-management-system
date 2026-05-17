@echo off
REM ============================================
REM Fix Booking Constraint Issue
REM ============================================

echo.
echo ================================================
echo   Fixing Booking Constraint Issue
echo ================================================
echo.
echo This will fix the error when booking vendors
echo without selecting a specific service.
echo.
pause

python fix_booking_issue.py

echo.
echo ================================================
echo   Done!
echo ================================================
echo.
echo You can now book vendors with "General Inquiry"
echo.
pause
