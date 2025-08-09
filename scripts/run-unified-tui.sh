#!/usr/bin/env bash
# Launch the Unified Enhanced TUI - Best of both worlds!

set -e

echo "🌟 Nix for Humanity - Unified Enhanced TUI"
echo "=========================================="
echo ""
echo "✨ Features:"
echo "  • Enhanced consciousness orb with all visualizations"
echo "  • Connected to real NixOS backend"
echo "  • INSTANT native operations"
echo "  • Voice visualization ready"
echo "  • Network status monitoring"
echo "  • Learning progress tracking"
echo "  • Educational error handling"
echo "  • Sacred geometry in flow state"
echo ""

cd "$(dirname "$0")"

# Check if we're in nix develop environment
if [[ -z "$IN_NIX_SHELL" ]]; then
    echo "📦 Loading Nix development environment..."
    exec nix develop -c "$0" "$@"
fi

# Set Python path
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Enable new backend features
export NIX_HUMANITY_PYTHON_BACKEND=true
export NIX_HUMANITY_UNIFIED_TUI=true

echo "🚀 Launching unified TUI with all features..."
echo ""

# Run the unified TUI
python -m nix_humanity.ui.unified_enhanced_tui