#!/usr/bin/env bash
# Use the simpler flake.nix that includes textual directly

set -e

echo "🔄 Switching to simple flake configuration..."
echo "This avoids poetry2nix circular dependency issues"
echo ""

# Backup current flake
if [ -f "flake.nix" ] && [ ! -f "flake.nix.poetry2nix-backup" ]; then
    echo "📦 Backing up current flake.nix..."
    cp flake.nix flake.nix.poetry2nix-backup
fi

# Copy the simple flake
echo "📝 Using simple flake with direct textual dependency..."
cp flake-with-textual.nix flake.nix

# Clear direnv cache to force reload
if [ -d ".direnv" ]; then
    echo "🧹 Clearing direnv cache..."
    rm -rf .direnv/flake-*
fi

echo ""
echo "✅ Simple flake activated!"
echo ""
echo "Now run:"
echo "  direnv reload    # If using direnv"
echo "  nix develop      # Enter the development shell"
echo ""
echo "Then you can:"
echo "  run-tui-app      # Launch the TUI"
echo "  python test_tui_components.py  # Test components"
echo ""
echo "To restore poetry2nix flake later:"
echo "  cp flake.nix.poetry2nix-backup flake.nix"