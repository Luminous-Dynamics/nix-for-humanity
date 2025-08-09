#!/usr/bin/env bash
# Enhanced TUI launcher with all new features

set -e

echo "🌟 Launching ENHANCED Nix for Humanity TUI..."
echo "============================================"
echo ""
echo "✨ New Features in this version:"
echo "  • 🎤 Voice activity visualization"
echo "  • 🌐 Network status monitoring" 
echo "  • 🧠 Learning progress tracking"
echo "  • ✨ Complex particle systems"
echo "  • 🔮 Sacred geometry patterns"
echo ""

cd "$(dirname "$0")"

# Create temporary virtual environment if needed
VENV_DIR="/tmp/nix-humanity-enhanced-tui-venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating temporary environment..."
    python3 -m venv "$VENV_DIR"
    
    echo "📥 Installing enhanced TUI dependencies..."
    "$VENV_DIR/bin/pip" install textual rich blessed pyperclip click colorama python-dotenv pyyaml --quiet
fi

# Set Python path
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Check if we should run test or full app
if [ "$1" = "--test" ]; then
    echo "🧪 Running enhanced features test..."
    echo ""
    "$VENV_DIR/bin/python" test-enhanced-features.py
else
    echo "🚀 Launching the enhanced consciousness-first TUI..."
    echo ""
    "$VENV_DIR/bin/python" showcase-enhanced-tui.py
fi