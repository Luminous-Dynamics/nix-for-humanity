#!/bin/bash
# Test Luminous Nix installation

echo "Testing Luminous Nix..."

# Test standalone
if [ -x "./luminous-nix" ]; then
    echo "Testing standalone executable..."
    ./luminous-nix search "firefox" || exit 1
    echo "✅ Standalone works"
fi

# Test Python import
python3 -c "from luminous_nix.api.intelligent_api import LuminousNixAPI; print('✅ Python import works')" || exit 1

echo ""
echo "✅ All tests passed!"
