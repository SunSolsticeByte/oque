#!/usr/bin/env bash

# Config
APP_NAME="oque"
INSTALL_DIR="/usr/local/bin"
# Ensure this matches your GitHub raw link
SOURCE_URL="https://raw.githubusercontent.com/SunSolsticeByte/oque/main/oque.py"

echo "--- Installing $APP_NAME ---"

# 1. Install Dependencies Quietly
echo "Checking dependencies..."
if ! python3 -m pip install requests tqdm yt-dlp --break-system-packages > /dev/null 2>&1; then
    python3 -m pip install requests tqdm yt-dlp > /dev/null 2>&1
fi

# 2. Download Oque
echo "Downloading latest version..."
curl -sL "$SOURCE_URL" -o "oque_temp.py"

# 3. Install
if [ -s "oque_temp.py" ]; then
    echo "Installing binary..."
    sudo mv "oque_temp.py" "$INSTALL_DIR/$APP_NAME"
    sudo chmod +x "$INSTALL_DIR/$APP_NAME"
    
    echo "Done."
    echo "Type 'oque version' to verify installation."
else
    echo "Error: Failed to download oque.py. Check your internet or repo link."
    rm -f "oque_temp.py"
fi
