#!/usr/bin/env bash
# Test the TUI using Nix development environment

set -e

echo "🧪 Testing Nix for Humanity TUI in Nix environment..."
echo "===================================================="

# Check if we're already in nix shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "📦 Entering Nix development shell..."
    # Run the test inside nix develop
    nix develop --command bash "$0" "$@"
    exit $?
fi

echo "✅ In Nix shell environment"
echo ""

# Test 1: Check if textual is available
echo "1️⃣ Testing Textual import..."
python3 -c "
import textual
print(f'  ✅ Textual version: {textual.__version__}')
" || {
    echo "  ❌ Textual not available in Nix environment"
    exit 1
}

# Test 2: Check if rich is available
echo ""
echo "2️⃣ Testing Rich import..."
python3 -c "
import rich
print(f'  ✅ Rich version: {rich.__version__}')
" || {
    echo "  ❌ Rich not available in Nix environment"
    exit 1
}

# Test 3: Check if our TUI modules can be imported
echo ""
echo "3️⃣ Testing TUI component imports..."
python3 -c "
from nix_humanity.ui.consciousness_orb import ConsciousnessOrb
from nix_humanity.ui.adaptive_interface import AdaptiveInterface
from nix_humanity.ui.main_app import NixForHumanityTUI
print('  ✅ All TUI components imported successfully!')
" || {
    echo "  ❌ Failed to import TUI components"
    exit 1
}

# Test 4: Try to create the app (without running it)
echo ""
echo "4️⃣ Testing TUI app creation..."
python3 -c "
from nix_humanity.ui.main_app import NixForHumanityTUI
app = NixForHumanityTUI()
print('  ✅ TUI app created successfully!')
print(f'  📊 App has {len(app.BINDINGS)} key bindings')
" || {
    echo "  ❌ Failed to create TUI app"
    exit 1
}

echo ""
echo "🎉 All tests passed! The TUI is ready to run."
echo ""
echo "To launch the TUI, use one of these commands:"
echo "  • run-tui-app         (Nix-provided command)"
echo "  • ./bin/nix-tui       (Project script)"
echo "  • python -m nix_humanity.interfaces.tui"
echo ""
echo "🌟 The consciousness orb awaits your presence! 🔮"