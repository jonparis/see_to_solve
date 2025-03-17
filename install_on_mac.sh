#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting See to Solve installation for macOS..."

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.11 or later from python.org"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r "$SCRIPT_DIR/src/requirements.txt"

# Function to download and install Stockfish
install_stockfish_binary() {
    echo "Downloading Stockfish..."
    
    # Determine Mac architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        STOCKFISH_URL="https://stockfishchess.org/files/stockfish-mac-arm64"
        echo "Detected Apple Silicon (M1/M2) Mac"
    else
        STOCKFISH_URL="https://stockfishchess.org/files/stockfish-mac-x86-64"
        echo "Detected Intel Mac"
    fi
    
    # Create bin directory if it doesn't exist
    mkdir -p "$SCRIPT_DIR/src/bin"
    
    # Download Stockfish
    echo "Downloading from: $STOCKFISH_URL"
    if curl -L "$STOCKFISH_URL" -o "$SCRIPT_DIR/src/bin/stockfish"; then
        chmod +x "$SCRIPT_DIR/src/bin/stockfish"
        echo "Stockfish downloaded and installed successfully"
        return 0
    else
        echo "Failed to download Stockfish"
        return 1
    fi
}

# Try to install Stockfish
echo "Setting up Stockfish..."

# First try: Homebrew installation
if command -v brew &> /dev/null; then
    echo "Homebrew found, attempting to install Stockfish..."
    if brew install stockfish; then
        echo "Stockfish installed successfully via Homebrew"
    else
        echo "Homebrew installation failed, trying direct download..."
        install_stockfish_binary
    fi
else
    echo "Homebrew not found, downloading Stockfish binary directly..."
    install_stockfish_binary
fi

# Verify Stockfish installation
if ! command -v stockfish &> /dev/null && [ ! -f "$SCRIPT_DIR/src/bin/stockfish" ]; then
    echo "Error: Stockfish installation failed. Please install manually:"
    echo "1. Download Stockfish from https://stockfishchess.org/download/"
    echo "2. Extract the downloaded file"
    echo "3. Move the 'stockfish' executable to $SCRIPT_DIR/src/bin/"
    echo "4. Make it executable with: chmod +x $SCRIPT_DIR/src/bin/stockfish"
    exit 1
fi

# Create temporary AppleScript
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << EOL
tell application "Terminal"
    do script "cd '$SCRIPT_DIR/src' && python3 main.py"
    activate
end tell
EOL

# Create the app bundle
APP_NAME="See to Solve Service"
APP_PATH="/Applications/$APP_NAME.app"

# Remove existing app if it exists
if [ -d "$APP_PATH" ]; then
    rm -rf "$APP_PATH"
fi

# Compile the AppleScript into an app
osacompile -o "$APP_PATH" "$TEMP_SCRIPT"

# Clean up temporary file
rm "$TEMP_SCRIPT"

# Copy icon if it exists
if [ -f "$SCRIPT_DIR/see_to_solve_chrome_ext/assets/icon-128.png" ]; then
    # Create iconset directory
    ICONSET_DIR="$(mktemp -d)/applet.iconset"
    mkdir -p "$ICONSET_DIR"

    # Copy and resize icon for different sizes
    cp "$SCRIPT_DIR/see_to_solve_chrome_ext/assets/icon-128.png" "$ICONSET_DIR/icon_128x128.png"
    sips -z 128 128 "$ICONSET_DIR/icon_128x128.png"
    sips -z 64 64 "$ICONSET_DIR/icon_128x128.png" --out "$ICONSET_DIR/icon_64x64.png"
    sips -z 32 32 "$ICONSET_DIR/icon_128x128.png" --out "$ICONSET_DIR/icon_32x32.png"
    sips -z 16 16 "$ICONSET_DIR/icon_128x128.png" --out "$ICONSET_DIR/icon_16x16.png"

    # Create icns file
    iconutil -c icns "$ICONSET_DIR" -o "$APP_PATH/Contents/Resources/applet.icns"

    # Clean up
    rm -rf "$(dirname "$ICONSET_DIR")"
fi

echo "Installation complete! You can find 'See to Solve Service' in your Applications folder."

# Run the service
open "$APP_PATH" 