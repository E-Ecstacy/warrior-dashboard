@echo off
REM Warrior Dashboard Setup Script for Windows
REM Run this to set everything up automatically

echo ⚔️  WARRIOR DASHBOARD - SETUP
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo 📦 Installing Flask...
    pip install Flask
    if errorlevel 0 (
        echo ✅ Flask installed successfully
    ) else (
        echo ❌ Failed to install Flask
        pause
        exit /b 1
    )
) else (
    echo ✅ Flask already installed
)

echo.

REM Create data directory if it doesn't exist
if not exist "data" (
    echo 📁 Creating data directory...
    mkdir data
    echo ✅ Data directory created
) else (
    echo ✅ Data directory exists
)

echo.
echo ================================
echo ✅ SETUP COMPLETE!
echo ================================
echo.
echo 🚀 To start the dashboard:
echo    python app.py
echo.
echo 📖 Then open: http://localhost:5000
echo.
echo ⚔️  May your stats grow strong!
echo.
pause
