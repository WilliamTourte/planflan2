@echo off
REM Complete setup and build script for Sphinx documentation
REM This script performs the full setup and builds documentation

echo.
echo ================================================================================
echo  COMPLETE SPHINX SETUP AND BUILD
echo ================================================================================
echo.

REM Ensure we're in the project directory
cd /d C:\Users\dhugonnard2025\PycharmProjects\PythonProject\planflan3

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .\.venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ❌ Failed to activate virtual environment
        exit /b 1
    )
    echo ✅ Virtual environment activated
)

echo.
echo ================================================================================
echo Step 1: Installing nodeenv
echo ================================================================================
echo.
pip install nodeenv
if errorlevel 1 (
    echo ❌ Failed to install nodeenv
    exit /b 1
)
echo ✅ nodeenv installed

echo.
echo ================================================================================
echo Step 2: Installing Node.js in virtual environment (this may take 1-2 minutes)
echo ================================================================================
echo.
nodeenv -p
if errorlevel 1 (
    echo ❌ Failed to install Node.js
    exit /b 1
)
echo ✅ Node.js installed

echo.
echo ================================================================================
echo Step 3: Verifying Node.js installation
echo ================================================================================
echo.
node --version
npm --version
if errorlevel 1 (
    echo ❌ Node.js verification failed
    exit /b 1
)
echo ✅ Node.js verified

echo.
echo ================================================================================
echo Step 4: Installing JSDoc
echo ================================================================================
echo.
npm install -g jsdoc
if errorlevel 1 (
    echo ❌ Failed to install JSDoc
    exit /b 1
)
echo ✅ JSDoc installed

echo.
echo ================================================================================
echo Step 5: Verifying JSDoc installation
echo ================================================================================
echo.
jsdoc --version
if errorlevel 1 (
    echo ❌ JSDoc verification failed
    exit /b 1
)
echo ✅ JSDoc verified

echo.
echo ================================================================================
echo Step 6: Building documentation
echo ================================================================================
echo.
python build_sphinx_docs.py
if errorlevel 1 (
    echo ❌ Documentation build failed
    exit /b 1
)
echo ✅ Documentation built successfully

echo.
echo ================================================================================
echo  ✅ SETUP COMPLETE!
echo ================================================================================
echo.
echo Documentation has been built and is ready to view!
echo.
echo To view the documentation locally, run:
echo   python build_sphinx_docs.py serve
echo.
echo Then visit: http://localhost:8000
echo.
echo ================================================================================
