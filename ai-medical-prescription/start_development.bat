@echo off
echo Starting AI Medical Prescription Verification System
echo =====================================================

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setting up environment...
if not exist .env (
    copy .env.example .env
    echo Please configure your .env file with API credentials
    echo.
)

echo Starting system...
python run_system.py

pause
