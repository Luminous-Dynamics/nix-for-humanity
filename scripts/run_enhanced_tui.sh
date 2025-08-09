#!/bin/bash
# Run the enhanced Nix for Humanity TUI with progress indicators and educational errors

cd "$(dirname "$0")"

echo "🌟 Launching Enhanced Nix for Humanity TUI..."
echo "✨ Features:"
echo "  • Educational error handling"
echo "  • Progress indicators for long operations"
echo "  • Native Python-Nix API performance"
echo ""
echo "Press Ctrl+P to see progress indicator demo!"
echo ""

export NIX_HUMANITY_PYTHON_BACKEND=true
python tui/main_with_progress.py