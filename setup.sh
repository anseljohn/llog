#!/bin/bash
set -e

# Create Python virtual environment if not exists
echo "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make main.py executable
echo "Making main.py executable..."
chmod +x main.py

# Symlink 'wlog' to a directory in user's PATH (e.g., ~/.local/bin)
TARGET_BIN="$HOME/.local/bin"
mkdir -p "$TARGET_BIN"
echo "Creating symlink '$TARGET_BIN/wlog' pointing to $(pwd)/main.py..."
ln -sf "$(pwd)/main.py" "$TARGET_BIN/wlog"

# Ensure ~/.local/bin is in PATH
if ! echo "$PATH" | grep -q "$TARGET_BIN"; then
    echo "Adding $TARGET_BIN to your PATH in ~/.bashrc..."
    echo "export PATH=\"\$PATH:$TARGET_BIN\"" >> ~/.bashrc
    export PATH="$PATH:$TARGET_BIN"
    echo "$TARGET_BIN has been added to your PATH for future sessions."
    echo "Please reload your shell."
fi

# Create log directory if not exists
mkdir -p ~/.wlog/logs

echo "Setup complete! You can now run 'wlog <message>' or 'wlog --summarize today' from any directory."