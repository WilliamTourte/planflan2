@echo off
REM Complete setup script for Node.js and JSDoc in virtual environment
REM Run this after activating .venv

echo.
echo ================================================================================
echo  Complete Sphinx Documentation Setup
echo ================================================================================
echo.

REM Step 1: Install nodeenv
echo Step 1: Installing nodeenv...
pip install nodeenv
if errorlevel 1 (
    echo ❌ Failed to install nodeenv
    exit /b 1
)
echo ✅ nodeenv installed

echo.
echo Step 2: Installing Node.js in virtual environment...
echo This may take a minute...
nodeenv -p
if errorlevel 1 (
    echo ❌ Failed to install Node.js
    exit /b 1
)
echo ✅ Node.js installed in virtual environment

echo.
echo Step 3: Verifying Node.js installation...
node --version
npm --version
if errorlevel 1 (
    echo ❌ Node.js verification failed
    exit /b 1
)
echo ✅ Node.js verified

echo.
echo Step 4: Installing JSDoc globally in virtual environment...
npm install -g jsdoc
if errorlevel 1 (
    echo ❌ Failed to install JSDoc
    exit /b 1
)
echo ✅ JSDoc installed

echo.
echo Step 5: Verifying JSDoc installation...
jsdoc --version
if errorlevel 1 (
    echo ❌ JSDoc verification failed
    exit /b 1
)
echo ✅ JSDoc verified

echo.
echo ================================================================================
echo  ✅ Setup Complete!
echo ================================================================================
echo.
echo You can now build documentation with:
echo   python build_sphinx_docs.py
echo.
echo Or serve locally with:
echo   python build_sphinx_docs.py serve
echo.
echo ================================================================================
