@echo off
REM Mobile Phone Data Scraper - Setup and Run Script (Windows)
REM This script creates a virtual environment, installs dependencies, and runs the scraper

setlocal enabledelayedexpansion

echo ==========================================
echo Mobile Phone Data Scraper - Setup
echo ==========================================
echo.

REM Get the directory where the script is located
cd /d "%~dp0"

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.11 or higher and try again.
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%
echo.

REM Check if virtual environment already exists
if exist ".venv" (
    echo Virtual environment already exists.
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q .venv
    ) else (
        echo Using existing virtual environment.
    )
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip -q

REM Install dependencies
echo.
echo Installing dependencies...
echo   - selenium
echo   - beautifulsoup4
echo   - lxml
echo   - aiohttp
echo   - aiofiles
echo   - requests
echo   - python-dotenv
echo.

pip install selenium beautifulsoup4 lxml aiohttp aiofiles requests python-dotenv -q
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo [OK] All dependencies installed
echo.

REM Display installed packages
echo Installed packages:
pip list | findstr /i "selenium beautifulsoup4 lxml aiohttp aiofiles requests"
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Starting the unified scraper interface...
echo.

REM Run the unified main scraper
python main.py

REM Deactivate virtual environment
call deactivate 2>nul

echo.
echo ==========================================
echo Script finished.
echo ==========================================
pause
