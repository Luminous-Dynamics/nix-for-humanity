#!/usr/bin/env bash
# Quick development environment entry script

echo "🌟 Entering Nix for Humanity development environment..."
echo ""
echo "Note: If this fails with flake errors, run:"
echo "  nix flake update"
echo "  (This may take several minutes to download dependencies)"
echo ""

# Enter the development shell
exec nix develop --impure