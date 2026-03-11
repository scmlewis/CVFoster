@echo off
setlocal

echo.
echo ========================================
echo Starting CVFoster
echo ========================================
echo.

set PYTHON_PATH=C:\Users\Lewis\AppData\Local\Python\bin\python.exe

echo Checking Python...
"%PYTHON_PATH%" --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please run: install_deps.bat
    pause
    exit /b 1
)

echo.
echo Starting Streamlit app...
echo Opening browser to http://localhost:8501 ...
echo.
echo To stop the app, press Ctrl+C
echo.

"%PYTHON_PATH%" -m streamlit run app.py

pause
