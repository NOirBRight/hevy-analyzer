@echo off
echo Starting Hevy Analyzer...

REM Change directory to the script's location
cd /d "%~dp0"

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found at .venv\Scripts\activate.bat
    echo Please make sure you have created the virtual environment.
    pause
    exit /b
)

echo Virtual environment activated.
echo Running Streamlit app...
streamlit run app.py

pause