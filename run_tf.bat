@echo off
REM Script untuk menjalankan Term Frequency Calculator

echo.
echo ============================================================
echo  Term Frequency (TF) Calculator - 100 Abstract
echo ============================================================
echo.

REM Cek apakah file main ada
if not exist "tf_main.py" (
    echo Error: tf_main.py tidak ditemukan
    echo Pastikan menjalankan script ini dari folder root project
    exit /b 1
)

REM Jalankan main script
echo Menjalankan TF Calculator...
echo.

python tf_main.py

if %errorlevel% neq 0 (
    echo.
    echo Error: TF Calculator gagal dijalankan
    exit /b 1
)

echo.
echo ============================================================
echo  Selesai!
echo ============================================================
echo.
echo File output: tf_results.csv (di folder root project)
echo.
pause
