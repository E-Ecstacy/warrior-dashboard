@echo off
echo Warrior Dashboard Setup
echo =======================
echo.

if not exist requirements.txt (
    echo ERROR: requirements.txt not found!
    echo Please run this script from the warrior-dashboard-refactored directory
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Setting up environment...
if not exist .env (
    copy .env.example .env
    echo Created .env file
    echo IMPORTANT: Edit .env and set SECRET_KEY=your-random-key-here
) else (
    echo .env already exists
)

echo.
echo Step 3: Setting up database...
set FLASK_APP=run.py

if not exist migrations (
    flask db init
    echo Database initialized
) else (
    echo Database already initialized
)

flask db migrate -m "Initial schema"
flask db upgrade

echo.
echo Setup complete!
echo.
echo To run the application:
echo   python run.py
echo.
echo Then visit: http://localhost:5000/auth/register
echo.
pause
