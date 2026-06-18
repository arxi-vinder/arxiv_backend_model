#!/bin/bash
# Script untuk menjalankan Term Frequency Calculator

echo ""
echo "============================================================"
echo "  Term Frequency (TF) Calculator - 100 Abstract"
echo "============================================================"
echo ""

# Cek apakah file main ada
if [ ! -f "tf_main.py" ]; then
    echo "Error: tf_main.py tidak ditemukan"
    echo "Pastikan menjalankan script ini dari folder root project"
    exit 1
fi

# Jalankan main script
echo "Menjalankan TF Calculator..."
echo ""

python tf_main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: TF Calculator gagal dijalankan"
    exit 1
fi

echo ""
echo "============================================================"
echo "  Selesai!"
echo "============================================================"
echo ""
echo "File output: tf_results.csv (di folder root project)"
echo ""
