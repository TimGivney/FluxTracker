@echo off
title FluxTracker v2.8 - Team Permissions Fix
echo ======================================================
echo FluxTracker v2.8 - Team Permissions Fix Utility
echo ======================================================
echo.
echo This script will help ensure that all team members
echo have the correct permissions to run FluxTracker from
echo the NAS.
echo.
echo 1. Unblocking all files in this folder...
powershell -Command "Get-ChildItem -Recurse | Unblock-File"
echo.
echo 2. Ensuring 'Modify' permissions for current users...
echo (Note: This may require administrator privileges)
icacls . /grant Users:(OI)(CI)M /T /C
echo.
echo 3. Checking for stale lock files...
if exist "app.lock" (
    echo [!] Found 'app.lock'. Deleting to allow fresh access...
    del "app.lock"
)
echo.
echo ======================================================
echo Done! All files are now unblocked and permissions set.
echo Your team should now be able to run FluxTracker.
echo ======================================================
pause
