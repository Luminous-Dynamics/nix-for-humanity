#!/usr/bin/env bash
# Rebuild the Nix development environment with TUI dependencies

set -e

echo "🌟 Rebuilding Nix development environment with TUI support..."
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "flake.nix" ]; then
    echo "❌ Error: flake.nix not found. Please run from project root."
    exit 1
fi

# Check if direnv needs reloading
if command -v direnv &> /dev/null; then
    echo "📦 Reloading direnv..."
    direnv reload
fi

# Update flake inputs if requested
if [ "$1" = "--update" ]; then
    echo "🔄 Updating flake inputs..."
    nix flake update
fi

# Enter the development shell
echo "🚀 Entering development shell with TUI dependencies..."
echo ""
echo "This will ensure poetry2nix includes:"
echo "  • textual (TUI framework)"
echo "  • rich (formatting)"
echo "  • All other optional dependencies"
echo ""

# Use nix develop to enter the shell with the script
nix develop --command bash -c '
echo "✅ Development environment loaded!"
echo ""
echo "🔍 Checking TUI dependencies..."

# Try importing textual
python3 -c "import textual; print(\"  ✅ Textual version:\", textual.__version__)" 2>/dev/null || echo "  ❌ Textual not available"
python3 -c "import rich; print(\"  ✅ Rich version:\", rich.__version__)" 2>/dev/null || echo "  ❌ Rich not available"

echo ""
echo "🎯 Available commands:"
echo "  run-tui-app    - Launch the TUI directly (Nix-managed)"
echo "  python test_tui_components.py - Test TUI components"
echo "  python -m nix_humanity.interfaces.tui - Run TUI module"
echo ""
echo "📝 Note: All dependencies are managed by Nix via poetry2nix."
echo "         No pip install needed!"
'