#!/bin/bash
#
# Launch the Unified Nix for Humanity TUI
#
# Features:
# - Simple mode by default (clean, focused interface)
# - Press Ctrl+E to toggle enhanced mode (visualizations)
# - All features integrated: educational errors, progress, voice
#

cd "$(dirname "$0")"

echo "🌟 Nix for Humanity - Unified Experience"
echo "========================================"
echo ""
echo "Starting in Simple Mode (clean interface)"
echo "Press Ctrl+E to toggle Enhanced Mode (visualizations)"
echo ""
echo "Features available:"
echo "  ✅ Educational error messages"
echo "  ✅ Progress indicators"
echo "  ✅ Native Python-Nix API"
echo "  🎤 Voice interface (if dependencies installed)"
echo "  ✨ Enhanced visualizations (toggle with Ctrl+E)"
echo ""
echo "Shortcuts:"
echo "  Ctrl+E - Toggle enhanced/simple mode"
echo "  Ctrl+N - Native operations demo"
echo "  Ctrl+P - Progress indicators demo"
echo "  Ctrl+V - Toggle voice interface"
echo "  F1 - Help"
echo ""

# Enable Python backend for best performance
export NIX_HUMANITY_PYTHON_BACKEND=true

# Launch the unified TUI
python tui/main.py