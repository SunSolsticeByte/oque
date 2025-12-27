cat << 'EOF' > install.sh
#!/usr/bin/env bash

# Config
APP_NAME="oque"
INSTALL_DIR="/usr/local/bin"
SOURCE_FILE="oque.py"

echo "--- Installing $APP_NAME ---"

# 1. Install Python Deps (Quietly)
echo "Checking dependencies..."
# We use pip to install requests and tqdm. 
# We ignore output (> /dev/null) and only show if it fails completely.
if ! python3 -m pip install requests tqdm yt-dlp --break-system-packages > /dev/null 2>&1; then
    # Fallback for older pip versions without break-system-packages
    python3 -m pip install requests tqdm yt-dlp > /dev/null 2>&1
fi

# 2. Install the Script
if [ -f "$SOURCE_FILE" ]; then
    echo "Installing binary..."
    sudo cp "$SOURCE_FILE" "$INSTALL_DIR/$APP_NAME"
    sudo chmod +x "$INSTALL_DIR/$APP_NAME"
    
    echo "Done."
    echo "Type 'oque version' to verify."
else
    echo "Error: $SOURCE_FILE not found. Cannot install."
fi
EOF
