#!/usr/bin/env bash
# Quick TUI launcher with temporary environment

set -e

echo "🌟 Launching Nix for Humanity TUI..."
echo "=================================="

cd "$(dirname "$0")"

# Create temporary virtual environment if needed
VENV_DIR="/tmp/nix-humanity-tui-venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating temporary environment..."
    python3 -m venv "$VENV_DIR"
    
    echo "📥 Installing TUI dependencies..."
    "$VENV_DIR/bin/pip" install textual rich blessed pyperclip click colorama python-dotenv pyyaml --quiet
fi

# Set Python path
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo ""
echo "🚀 Launching the consciousness-first TUI..."
echo ""

# Run the TUI
"$VENV_DIR/bin/python" -m nix_humanity.interfaces.tui