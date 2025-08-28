#!/usr/bin/env bash
# Luminous Nix Installer

set -e

echo "📦 Installing Luminous Nix..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Install with:"
    echo "   nix-env -iA nixpkgs.python3"
    exit 1
fi

# Install to user directory
INSTALL_DIR="$HOME/.local/share/luminous-nix"
BIN_DIR="$HOME/.local/bin"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Copy files
cp -r lib "$INSTALL_DIR/"
cp luminous-nix "$BIN_DIR/"

# Install Python dependencies
echo "📥 Installing dependencies..."
pip3 install --user --quiet click rich pydantic 2>/dev/null || {
    echo "⚠️ Could not install Python dependencies automatically."
    echo "   Please run: pip3 install --user click rich pydantic"
}

# Update PATH if needed
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "📝 Add to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
echo "✅ Installation complete!"
echo "   Run: luminous-nix help"
