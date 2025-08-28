#!/usr/bin/env bash
# Minimal build script for Luminous Nix v0.1.0-alpha
# Focuses on working components only

set -e

echo "🏗️ Building Minimal Luminous Nix v0.1.0-alpha"
echo "============================================="

# Clean previous builds
rm -rf dist-minimal
mkdir -p dist-minimal

# Create standalone Python package
echo "📦 Creating standalone Python package..."
mkdir -p dist-minimal/luminous-nix

# Copy essential files
cp -r src/luminous_nix dist-minimal/luminous-nix/
cp bin/ask-nix-real dist-minimal/luminous-nix/ask-nix
chmod +x dist-minimal/luminous-nix/ask-nix

# Create a minimal requirements file
cat > dist-minimal/luminous-nix/requirements-minimal.txt << 'EOF'
click>=8.0.0
rich>=13.0.0
EOF

# Create installation script
cat > dist-minimal/install.sh << 'EOF'
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
EOF

chmod +x dist-minimal/install.sh

# Create README
cat > dist-minimal/README.md << 'EOF'
# Luminous Nix v0.1.0-alpha - Minimal Distribution

## What This Is

A **REAL** natural language interface for NixOS that actually executes commands.
No mocks, no fake responses - real NixOS integration.

## What Works

- ✅ List installed packages
- ✅ Show help
- ✅ System information
- ✅ Dry-run package installation
- ⚠️ Package search (slow but functional)

## Installation

```bash
./install.sh
```

## Usage

```bash
# List installed packages
luminous-nix list

# Get help
luminous-nix help

# Dry-run install
luminous-nix "install vim" --dry-run

# System info
luminous-nix info
```

## Known Limitations

This is alpha software with ~40% functionality implemented:
- Voice interface not included (dependencies missing)
- GUI not included (not connected)
- Learning system not included (never implemented)
- Search is slow (needs optimization)

## The Truth

This project was discovered to be 90% mocked. This release represents
the first REAL implementation that actually executes NixOS commands.

## Requirements

- NixOS or Nix package manager
- Python 3.8+
- Basic command line knowledge

## Support

This is alpha software. Expect bugs. Report issues on GitHub.
EOF

# Create tarball
echo "📦 Creating distribution tarball..."
cd dist-minimal
tar czf luminous-nix-v0.1.0-alpha-minimal.tar.gz *
cd ..

echo "✅ Build complete!"
echo "📦 Distribution: dist-minimal/luminous-nix-v0.1.0-alpha-minimal.tar.gz"
echo "📏 Size: $(du -h dist-minimal/luminous-nix-v0.1.0-alpha-minimal.tar.gz | cut -f1)"