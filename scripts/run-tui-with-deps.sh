#!/usr/bin/env bash
# Run the TUI with proper dependencies

set -e

echo "🌟 Preparing to launch Nix for Humanity TUI..."
echo "================================================"

# Check if we're in Nix shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "⚠️  Not in Nix shell. Please run: nix develop"
    exit 1
fi

# Option 1: Try to use poetry if available
if command -v poetry &> /dev/null; then
    echo "✨ Found poetry, using poetry environment..."
    cd "$(dirname "$0")"
    poetry install --with tui
    poetry run python -m nix_humanity.interfaces.tui
    exit 0
fi

# Option 2: Create a virtual environment
echo "📦 Creating temporary virtual environment with TUI dependencies..."
VENV_DIR="$(mktemp -d)/tui-venv"
python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "📥 Installing required dependencies..."
pip install textual rich

echo "🚀 Launching TUI..."
cd "$(dirname "$0")"
PYTHONPATH="$(pwd):$PYTHONPATH" python -m nix_humanity.interfaces.tui

# Cleanup
deactivate
rm -rf "$VENV_DIR"