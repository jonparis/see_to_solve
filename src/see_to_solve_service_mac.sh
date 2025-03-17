#!/bin/bash

echo "Starting See to Solve Service..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed! Please install Python 3.11 or later."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed! Please install pip."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "requirements.txt not found! Please make sure you're in the correct directory."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r "$SCRIPT_DIR/requirements.txt"
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies!"
    exit 1
fi

# Check if Stockfish exists
if [ ! -f "$SCRIPT_DIR/stockfish" ]; then
    echo "Stockfish not found! Please make sure the stockfish executable is in the current directory."
    exit 1
fi

# Make sure stockfish is executable
chmod +x "$SCRIPT_DIR/stockfish"

# Start the Flask service
echo "Starting Flask service..."
echo "The service will be available at http://127.0.0.1:8080"
echo "Press Ctrl+C to stop the service"
python3 "$SCRIPT_DIR/main.py" 