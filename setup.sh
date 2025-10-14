#!/bin/bash
# Quick setup script for Linux/macOS users
# Run this script to set up Transcribair

set -e

echo "============================================================"
echo "Transcribair Quick Setup (Linux/macOS)"
echo "============================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "Python found!"
python3 --version
echo

# Run the setup script
python3 setup.py

if [ $? -eq 0 ]; then
    echo
    echo "============================================================"
    echo "Setup complete!"
    echo "============================================================"
    echo
    echo "To run Transcribair:"
    echo "  ./run.sh"
    echo "  or"
    echo "  source venv/bin/activate && python app.py"
    echo

    # Make run.sh executable
    chmod +x run.sh 2>/dev/null || true
else
    echo
    echo "Setup failed! Check the error messages above."
    exit 1
fi
