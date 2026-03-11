@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo CVFoster Setup & Installation
echo ========================================
echo.

set "PYTHON_PATH=C:\Users\Lewis\AppData\Local\Python\bin\python.exe"

echo Checking Python...
"%PYTHON_PATH%" --version
if errorlevel 1 (
    echo ERROR: Python not found!
    exit /b 1
)

echo.
echo Installing dependencies (this may take 3-5 minutes)...
echo.

"%PYTHON_PATH%" -m pip install streamlit python-docx PyMuPDF sentence-transformers faiss-cpu spacy torch transformers pytesseract python-dotenv textstat scikit-learn numpy pandas --upgrade

if errorlevel 1 (
    echo ERROR: Package installation failed!
    pause
    exit /b 1
)

echo.
echo Installing spacy language model...
"%PYTHON_PATH%" -m spacy download en_core_web_sm

if errorlevel 1 (
    echo WARNING: Spacy model download failed, but continuing...
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run CVFoster:
echo   cd "C:\Github\(Streamlit app)\CVFoster"
echo   C:\Users\Lewis\AppData\Local\Python\bin\python.exe -m streamlit run app.py
echo.
echo Or use the quick-start batch file: run_app.bat
echo.
pause
