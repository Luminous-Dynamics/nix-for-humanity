#!/usr/bin/env bash
# Simpler, faster standalone build

set -e

echo "🚀 Quick standalone build..."

# Clean
rm -rf dist-simple
mkdir -p dist-simple

# Create a simple launcher script
cat > dist-simple/luminous-nix << 'EOF'
#!/usr/bin/env bash
# Luminous Nix Launcher - Standalone Version

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Install with: nix-env -iA nixpkgs.python3"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set up Python path to embedded modules
export PYTHONPATH="$SCRIPT_DIR/lib:$PYTHONPATH"

# Check if running from installed location or development
if [ -d "$SCRIPT_DIR/lib/luminous_nix" ]; then
    # Running from installed location with embedded libs
    exec python3 -m luminous_nix.cli "$@"
elif [ -f "$HOME/.local/share/luminous-nix/lib/luminous_nix/cli/__init__.py" ]; then
    # Running from user install
    export PYTHONPATH="$HOME/.local/share/luminous-nix/lib:$PYTHONPATH"
    exec python3 -m luminous_nix.cli "$@"
else
    echo "❌ Luminous Nix modules not found."
    echo "   Please reinstall or check installation."
    exit 1
fi
EOF

chmod +x dist-simple/luminous-nix

# Bundle the Python modules
echo "📦 Bundling Python modules..."
mkdir -p dist-simple/lib
cp -r src/luminous_nix dist-simple/lib/

# Create a minimal requirements file for dependencies
cat > dist-simple/requirements.txt << 'EOF'
click>=8.0.0
rich>=13.0.0
pydantic>=2.0.0
EOF

# Create installer script
cat > dist-simple/install.sh << 'EOF'
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
EOF

chmod +x dist-simple/install.sh

# Create a tarball for distribution
echo "📦 Creating distribution archive..."
cd dist-simple
tar czf luminous-nix-standalone.tar.gz *
cd ..

echo "✅ Quick standalone build complete!"
echo ""
echo "📍 Files created:"
echo "   dist-simple/luminous-nix           - Launcher script"
echo "   dist-simple/lib/                   - Python modules"
echo "   dist-simple/install.sh              - Installer"
echo "   dist-simple/luminous-nix-standalone.tar.gz - Distribution archive"
echo ""
echo "📋 To distribute:"
echo "   1. Share the .tar.gz file"
echo "   2. User extracts: tar xzf luminous-nix-standalone.tar.gz"
echo "   3. User runs: ./install.sh"
echo "   4. User uses: luminous-nix help"