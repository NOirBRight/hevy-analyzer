@echo off
title Hevy Data Analyzer
echo ========================================
echo   Hevy Data Analyzer
echo ========================================
echo.
echo Starting application...
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install streamlit streamlit-float pandas requests pillow altair
)

REM Run the app
echo.
echo Opening browser at http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
streamlit run app.py --server.headless=true --browser.gatherUsageStats=false

pause
