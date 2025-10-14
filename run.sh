#!/bin/bash
# Quick run script for Linux/macOS users
# Run this script to start Transcribair after setup

echo "Starting Transcribair..."
echo

# Check if venv exists
if [ ! -f "venv/bin/python" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run ./setup.sh first to install Transcribair."
    echo
    exit 1
fi

# Run the application
venv/bin/python app.py

if [ $? -ne 0 ]; then
    echo
    echo "Application exited with an error."
    read -p "Press Enter to continue..."
fi
