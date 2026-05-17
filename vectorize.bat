@echo off
REM Arxivinder Vectorization Script for Windows

echo.
echo ============================================================
echo Arxivinder Vectorization Tool
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist "app\cli.py" (
    echo Error: app\cli.py not found. Make sure you run this from backend_model directory
    pause
    exit /b 1
)

REM Show menu
echo.
echo Select an option:
echo 1. Vectorize all papers (default batch size 100)
echo 2. Vectorize all papers (custom batch size)
echo 3. Check cache info
echo 4. Check vectorization status
echo 5. Clear cache
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    python -m app.cli vectorize-all
) else if "%choice%"=="2" (
    set /p batch_size="Enter batch size (default 100): "
    if "%batch_size%"=="" set batch_size=100
    python -m app.cli vectorize-all --batch-size %batch_size%
) else if "%choice%"=="3" (
    python -m app.cli cache-info
) else if "%choice%"=="4" (
    python -m app.cli status
) else if "%choice%"=="5" (
    python -m app.cli clear-cache
) else if "%choice%"=="6" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please try again.
    pause
    goto start
)

echo.
echo Press any key to continue...
pause
