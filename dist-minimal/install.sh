#!/bin/bash
# Minimal installation script for Luminous Nix

echo "📦 Installing Luminous Nix v0.1.0-alpha (minimal)"
echo "================================================="

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Install to user's local bin
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Copy the script
cp luminous-nix/ask-nix "$INSTALL_DIR/luminous-nix"
chmod +x "$INSTALL_DIR/luminous-nix"

# Install Python dependencies
pip3 install --user -q click rich

echo "✅ Installation complete!"
echo ""
echo "Add this to your PATH if needed:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "Usage:"
echo "  luminous-nix help"
echo "  luminous-nix list"
echo "  luminous-nix \"install firefox\""
