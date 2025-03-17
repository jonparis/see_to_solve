# See to Solve

A Chrome extension that helps analyze chess positions using Stockfish and machine learning.

## Quick Start Guide

### Prerequisites
1. Install Python 3.11 or later from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"
2. Download or clone the See to Solve folder

### Installation Steps

1. **Install the Chrome Extension**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" in the top right corner
   - Click "Load unpacked"
   - Select the `see_to_solve_chrome_ext` folder from the See to Solve folder

2. **Set Up the Service**
   Choose your operating system:

   #### Windows
   - Double-click `install_on_windows.vbs`
   - A shortcut will be automatically created on your desktop
   - The service will start automatically

   #### macOS
   - Open Terminal
   - Navigate to the See to Solve folder
   - Run: `chmod +x install_on_mac.sh && ./install_on_mac.sh`
   - The application will be created in your Applications folder

### Using the Service

1. **Start the Service**
   - Windows: Double-click the "See to Solve Service" shortcut on your desktop
   - macOS: Double-click the "See to Solve Service" application in your Applications folder

2. **Using the Extension**
   - The service will run in the background (Windows) or in a Terminal window (macOS)
   - Keep the Terminal window open on macOS
   - To stop the service:
     - Windows: Use Task Manager to end the Python process
     - macOS: Close the Terminal window or press Ctrl+C

### Troubleshooting

If you see any error messages:
1. Make sure Python is installed (download from [python.org](https://www.python.org/downloads/))
2. Make sure you're running the service from the correct folder
3. Try closing and reopening the service
4. If problems persist, contact support

## Technical Details

The service runs on http://127.0.0.1:8080 and uses:
- Flask for the web server
- Stockfish for chess analysis
- PyTorch for position evaluation

## Development

For developers interested in contributing or modifying the code:
1. Clone the repository
2. Install dependencies: `pip install -r src/requirements.txt`
3. Run the service: `python src/main.py`
