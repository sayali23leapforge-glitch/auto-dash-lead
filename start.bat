@echo off
echo Starting Meta Leads Dashboard...
echo.
echo Creating virtual environment if not exists...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r backend\requirements.txt

echo.
echo Starting Flask backend on http://localhost:5000...
echo.
python backend\app.py

pause
