@echo off
echo ========================================
echo   Hevy Data Analyzer - Build Script
echo ========================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Building executable...
echo This may take a few minutes...
echo.

pyinstaller HevyAnalyzer.spec --clean

echo.
echo Copying required files to dist folder...
copy /Y app.py dist\HevyAnalyzer\
copy /Y exercises.csv dist\HevyAnalyzer\
copy /Y muscle_heatmap_svg.html dist\HevyAnalyzer\
copy /Y muscle_heatmap_3d.html dist\HevyAnalyzer\
copy /Y muscle_heatmap_svg_backup.html dist\HevyAnalyzer\

echo.
if exist "dist\HevyAnalyzer\HevyAnalyzer.exe" (
    echo ========================================
    echo   Build completed successfully!
    echo ========================================
    echo.
    echo Executable location:
    echo   dist\HevyAnalyzer\HevyAnalyzer.exe
    echo.
    echo To run the app, navigate to dist\HevyAnalyzer
    echo and double-click HevyAnalyzer.exe
) else (
    echo ========================================
    echo   Build failed!
    echo ========================================
    echo Please check the error messages above.
)

echo.
pause
