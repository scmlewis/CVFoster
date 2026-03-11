@echo off
REM CVFoster Setup and Run Script for Windows

echo.
echo 🚀 CVFoster Phase 1 MVP Setup
echo =============================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Download spacy model
echo.
echo Downloading spacy language model...
python -m spacy download en_core_web_sm

REM Create directories
if not exist "data\samples" mkdir data\samples
if not exist "data\jobs" mkdir data\jobs

echo.
echo ✅ Setup complete!
echo.
echo To run the app:
echo   streamlit run app.py
echo.
echo Then visit: http://localhost:8501
echo.
pause
