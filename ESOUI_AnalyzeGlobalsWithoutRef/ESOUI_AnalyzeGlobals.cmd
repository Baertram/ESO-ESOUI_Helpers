@echo off
:: Get current dir as workdir
cd /d "%~dp0"

title ESO UI Global Scanner

echo ===================================================
echo   Starting - ESO UI Global Scanner...
echo ===================================================
echo.

:: Check Python is found and in PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Assure that Python is installed and the option 
    echo "Add Python to PATH" was used at the installation.
	echo Else: Manualyl add the Python exectuables folder to your envrironment PATH variabe.
    echo.
    pause
    exit /b
)

:: Run the Python-Script
python ESOUI_AnalyzeGlobalsWithoutRef.py --debug

echo.
echo ==========================================================
echo   Scanner action completed - Check the output directory
echo ==========================================================
echo.
pause
