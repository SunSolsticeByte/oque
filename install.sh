#!/usr/bin/env bash

# Config
APP_NAME="oque"
INSTALL_DIR="/usr/local/bin"
# LINK TO YOUR RAW PYTHON FILE
SOURCE_URL="https://raw.githubusercontent.com/SunSolsticeByte/oque/main/oque.py"

echo "--- Installing $APP_NAME ---"

# 1. Install Python Deps (Quietly)
echo "Checking dependencies..."
if ! python3 -m pip install requests tqdm yt-dlp --break-system-packages > /dev/null 2>&1; then
    python3 -m pip install requests tqdm yt-dlp > /dev/null 2>&1
fi

# 2. Download the Source Code
echo "Downloading core logic..."
curl -sL "$SOURCE_URL" -o "oque_temp.py"

# 3. Install
if [ -s "oque_temp.py" ]; then
    echo "Installing binary..."
    sudo mv "oque_temp.py" "$INSTALL_DIR/$APP_NAME"
    sudo chmod +x "$INSTALL_DIR/$APP_NAME"
    
    echo "Done."
    echo "Type 'oque version' to verify."
else
    echo "Error: Failed to download oque.py from GitHub."
    echo "Check your internet or if the file exists in the repo."
    rm -f "oque_temp.py"
fi
