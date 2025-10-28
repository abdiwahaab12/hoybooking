@echo off
echo ========================================
echo Resume/CV Website Setup Script
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Setting up database...
python database_setup.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the website:
echo   python run.py
echo.
echo Website: http://localhost:5000
echo Admin: http://localhost:5000/admin
echo Login: admin / admin123
echo.
pause
