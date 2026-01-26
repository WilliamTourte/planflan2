@echo off
REM Clean build and rebuild documentation

echo Cleaning old documentation build...
rmdir /s /q source\_build 2>nul

echo Building documentation...
python build_sphinx_docs.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✅ Documentation built successfully!
    echo.
    echo Serving on http://localhost:8000...
    cd source\_build\html
    python -m http.server 8000
) else (
    echo.
    echo ❌ Build failed
    exit /b 1
)
