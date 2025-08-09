#!/bin/bash
# Launch the main connected TUI for Nix for Humanity

echo "🌟 Launching Nix for Humanity - Main TUI"
echo "========================================"
echo ""
echo "This interface connects our powerful backend with a beautiful UI:"
echo "  ✅ Natural language NixOS commands"
echo "  🚀 Native operations with instant performance"
echo "  📦 Advanced features (flakes, profiles, etc.)"
echo "  📊 Real-time performance statistics"
echo ""
echo "Try these commands:"
echo "  • 'install firefox' - See how package installation works"
echo "  • 'list generations' - Instant system generations (0ms!)"
echo "  • 'native' - See native operations performance demo"
echo "  • 'advanced' - Explore flakes, profiles, and more"
echo "  • 'help' - See all available commands"
echo ""

# Check if we're in the right directory
if [ ! -f "tui/main_connected.py" ]; then
    echo "❌ Error: Please run this from the nix-for-humanity directory"
    exit 1
fi

# Set environment for native backend
export NIX_HUMANITY_PYTHON_BACKEND=true

# Launch the TUI
python3 tui/main_connected.py