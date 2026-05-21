#!/bin/bash
# Arxivinder Vectorization Script for Unix/Linux/Mac

echo ""
echo "============================================================"
echo "Arxivinder Vectorization Tool"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if in correct directory
if [ ! -f "app/cli.py" ]; then
    echo "Error: app/cli.py not found. Make sure you run this from backend_model directory"
    exit 1
fi

# Show menu
echo ""
echo "Select an option:"
echo "1. Vectorize all papers (default batch size 100)"
echo "2. Vectorize all papers (custom batch size)"
echo "3. Check cache info"
echo "4. Check vectorization status"
echo "5. Clear cache"
echo "6. Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        python -m app.cli vectorize-all
        ;;
    2)
        read -p "Enter batch size (default 100): " batch_size
        batch_size=${batch_size:-100}
        python -m app.cli vectorize-all --batch-size $batch_size
        ;;
    3)
        python -m app.cli cache-info
        ;;
    4)
        python -m app.cli status
        ;;
    5)
        python -m app.cli clear-cache
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Please try again."
        exit 1
        ;;
esac

echo ""
read -p "Press any key to continue..."
