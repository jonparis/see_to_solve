#!/bin/bash

echo "Starting See to Solve Service..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate virtual environment
source "$SCRIPT_DIR/../venv/bin/activate"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed! Please install Python 3.11 or later."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "requirements.txt not found! Please make sure you're in the correct directory."
    exit 1
fi

# Check if Stockfish exists
if ! command -v stockfish &> /dev/null && [ ! -f "$SCRIPT_DIR/stockfish" ]; then
    echo "Stockfish not found! Please make sure Stockfish is installed."
    exit 1
fi

# Start the Flask service
echo "Starting Flask service..."
echo "The service will be available at http://127.0.0.1:8080"
echo "Press Ctrl+C to stop the service"
python3 "$SCRIPT_DIR/main.py" 