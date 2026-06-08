@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo FluxTracker Build System v2.2
echo ============================================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

:: 2. Create Virtual Environment (Optional but recommended for clean builds)
echo [1/4] Setting up build environment...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [WARNING] Could not create virtual environment. Continuing with system Python...
    ) else (
        echo [INFO] Virtual environment created.
    )
)

:: Activate venv if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: 3. Install/Update Dependencies
echo [2/4] Installing/Updating required dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. 
    echo Check your internet connection or try running: pip install -r requirements.txt
    pause
    exit /b 1
)

:: 4. Build the executable
echo [3/4] Building standalone executable (this may take a minute)...
:: We use --clean to ensure no old cache causes issues
:: We use --collect-all for pandas as it often has hidden dependencies
python -m PyInstaller --noconfirm --onefile --windowed --clean ^
    --add-data "logo.png;." ^
    --name "FluxTracker" ^
    "main.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller build failed. 
    echo Common fixes:
    echo 1. Close any running instances of the app.
    echo 2. Delete the \'build\' and \'dist\' folders and try again.
    echo 3. Ensure \'logo.png\' exists in this folder.
    pause
    exit /b 1
)

:: 5. Final Check
echo [4/4] Finalizing...
if exist "dist\FluxTracker.exe" (
    echo.
    echo ============================================================
    echo BUILD SUCCESSFUL!
    echo.
    echo Your standalone app is ready:
    echo --^> dist\FluxTracker.exe
    echo.
    echo You can move this .exe anywhere on your computer.
    echo ============================================================
) else (
    echo [ERROR] Build finished but executable was not found in \'dist\' folder.
)

pause
