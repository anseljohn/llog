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

# Make main.py executable and symlink as llog
echo "Making main.py executable and creating symlink 'llog'..."
chmod +x llog.py
ln -sf llog.py llog

# Create log directory if not exists
mkdir -p ~/.llog/logs

echo "Setup complete! You can now run './llog <message>' or './llog --summarize today'"