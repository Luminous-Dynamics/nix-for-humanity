#!/bin/bash
# Build standalone Luminous Nix v0.1.0-alpha distribution
# This creates a package users can run without Poetry

set -e

echo "🚀 Building Luminous Nix v0.1.0-alpha Standalone"
echo "================================================="

# Configuration
VERSION="0.1.0-alpha"
DIST_DIR="dist-standalone"
PACKAGE_NAME="luminous-nix-v${VERSION}-standalone"
PYTHON_VERSION="3.11"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Clean previous builds
echo -e "${YELLOW}🧹 Cleaning previous builds...${NC}"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/$PACKAGE_NAME"

# Create directory structure
echo -e "${YELLOW}📁 Creating directory structure...${NC}"
mkdir -p "$DIST_DIR/$PACKAGE_NAME/luminous_nix"
mkdir -p "$DIST_DIR/$PACKAGE_NAME/bin"

# Copy core source files (with integrated backend)
echo -e "${YELLOW}📦 Copying core modules...${NC}"

# Core functionality
cp -r src/luminous_nix/core "$DIST_DIR/$PACKAGE_NAME/luminous_nix/"
cp -r src/luminous_nix/cli "$DIST_DIR/$PACKAGE_NAME/luminous_nix/"
cp -r src/luminous_nix/nix "$DIST_DIR/$PACKAGE_NAME/luminous_nix/"
cp -r src/luminous_nix/config "$DIST_DIR/$PACKAGE_NAME/luminous_nix/"
cp -r src/luminous_nix/utils "$DIST_DIR/$PACKAGE_NAME/luminous_nix/"

# Services (beautiful architecture)
if [ -d "src/luminous_nix/services" ]; then
    cp -r src/luminous_nix/services "$DIST_DIR/$PACKAGE_NAME/luminous_nix/"
fi

# AI integration (if user has Ollama)
if [ -d "src/luminous_nix/ai" ]; then
    cp -r src/luminous_nix/ai "$DIST_DIR/$PACKAGE_NAME/luminous_nix/"
fi

# UI components (working TUI)
if [ -d "src/luminous_nix/ui" ]; then
    mkdir -p "$DIST_DIR/$PACKAGE_NAME/luminous_nix/ui"
    # Copy essential UI files
    cp src/luminous_nix/ui/__init__.py "$DIST_DIR/$PACKAGE_NAME/luminous_nix/ui/"
    cp src/luminous_nix/ui/main_app.py "$DIST_DIR/$PACKAGE_NAME/luminous_nix/ui/"
    cp src/luminous_nix/ui/backend_connector.py "$DIST_DIR/$PACKAGE_NAME/luminous_nix/ui/"
    cp src/luminous_nix/ui/consciousness_orb.py "$DIST_DIR/$PACKAGE_NAME/luminous_nix/ui/"
fi

# Package files
cp src/luminous_nix/__init__.py "$DIST_DIR/$PACKAGE_NAME/luminous_nix/"
cp src/luminous_nix/types.py "$DIST_DIR/$PACKAGE_NAME/luminous_nix/" 2>/dev/null || true

# Create standalone launcher script
echo -e "${YELLOW}🔧 Creating standalone launcher...${NC}"
cat > "$DIST_DIR/$PACKAGE_NAME/luminous-nix" << 'EOF'
#!/usr/bin/env python3
"""
Luminous Nix v0.1.0-alpha - Standalone Launcher
Natural Language Interface for NixOS
"""

import sys
import os

# Add the package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run CLI
try:
    from luminous_nix.cli import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error: Missing dependency - {e}")
    print("\nPlease install required packages:")
    print("  pip install click rich requests")
    sys.exit(1)
EOF

chmod +x "$DIST_DIR/$PACKAGE_NAME/luminous-nix"

# Create requirements file for users
echo -e "${YELLOW}📝 Creating requirements.txt...${NC}"
cat > "$DIST_DIR/$PACKAGE_NAME/requirements.txt" << 'EOF'
# Core dependencies for Luminous Nix v0.1.0-alpha
click>=8.0.0
rich>=13.0.0
requests>=2.28.0
pydantic>=2.0.0

# Optional: For TUI support
textual>=0.40.0

# Optional: For AI features (if you have Ollama)
ollama>=0.1.0
EOF

# Create installation script
echo -e "${YELLOW}📜 Creating install script...${NC}"
cat > "$DIST_DIR/$PACKAGE_NAME/install.sh" << 'EOF'
#!/bin/bash
# Install Luminous Nix dependencies

echo "Installing Luminous Nix v0.1.0-alpha dependencies..."

# Check Python version
python3 --version

# Install dependencies
pip3 install --user -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "To run Luminous Nix:"
echo "  ./luminous-nix help"
echo "  ./luminous-nix 'search text editor'"
echo "  ./luminous-nix 'install firefox'"
EOF

chmod +x "$DIST_DIR/$PACKAGE_NAME/install.sh"

# Create README for standalone
echo -e "${YELLOW}📖 Creating README...${NC}"
cat > "$DIST_DIR/$PACKAGE_NAME/README.md" << 'EOF'
# Luminous Nix v0.1.0-alpha - Standalone Distribution

**Natural Language Interface for NixOS**

## Quick Start

1. **Install dependencies**:
   ```bash
   ./install.sh
   # or manually:
   pip3 install --user -r requirements.txt
   ```

2. **Run Luminous Nix**:
   ```bash
   ./luminous-nix help
   ./luminous-nix "search firefox"
   ./luminous-nix "install vim"
   ```

## What Works (v0.1.0-alpha)

✅ **Working Features**:
- Natural language commands
- Package search with typo correction
- Package installation
- List installed packages
- Help system
- Dry-run mode for safety

⚠️ **Alpha Limitations**:
- 2-3 second response times (standard Nix speed)
- Voice interface not yet functional
- Learning system not activated
- Basic AI features only

## Examples

```bash
# Search for packages
./luminous-nix "search text editor"
./luminous-nix "find markdown editor"

# Install packages (with confirmation)
./luminous-nix "install firefox"
./luminous-nix --dry-run "install vim"  # Preview only

# System operations
./luminous-nix "list installed"
./luminous-nix "what's installed?"
./luminous-nix "help"
```

## Requirements

- NixOS or Linux with Nix installed
- Python 3.9 or higher
- Internet connection for package operations

## Troubleshooting

If you get import errors:
1. Run `./install.sh` to install dependencies
2. Make sure Python 3.9+ is installed
3. Check that Nix is available: `which nix`

## About This Release

This is the first honest alpha release after extensive cleanup:
- Removed 70% of non-working code
- Fixed all import errors
- Integrated clean service architecture
- Set realistic expectations

## Roadmap

- v0.2.0 (Feb 2025): Voice interface, cache optimization
- v0.3.0 (Mar 2025): Learning system, personas
- v0.4.0 (Apr 2025): GUI preview
- v1.0.0 (Nov 2025): Production ready

## Support

Report issues: https://github.com/Luminous-Dynamics/luminous-nix/issues

## License

MIT

---
*"Making NixOS accessible through natural language"*
EOF

# Copy LICENSE if exists
if [ -f "LICENSE" ]; then
    cp LICENSE "$DIST_DIR/$PACKAGE_NAME/"
fi

# Copy CHANGELOG
if [ -f "CHANGELOG.md" ]; then
    cp CHANGELOG.md "$DIST_DIR/$PACKAGE_NAME/"
fi

# Clean up unnecessary files
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
find "$DIST_DIR/$PACKAGE_NAME" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$DIST_DIR/$PACKAGE_NAME" -name "*.pyc" -delete
find "$DIST_DIR/$PACKAGE_NAME" -name "test_*.py" -delete
find "$DIST_DIR/$PACKAGE_NAME" -name "*_test.py" -delete
find "$DIST_DIR/$PACKAGE_NAME" -name ".DS_Store" -delete 2>/dev/null || true

# Remove archived consciousness files if any leaked through
find "$DIST_DIR/$PACKAGE_NAME" -name "sacred_*.py" -delete 2>/dev/null || true
find "$DIST_DIR/$PACKAGE_NAME" -name "consciousness_*.py" ! -name "consciousness_orb.py" -delete 2>/dev/null || true

# Create archive
echo -e "${YELLOW}📦 Creating distribution archive...${NC}"
cd "$DIST_DIR"
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"
cd - > /dev/null

# Calculate sizes
ORIGINAL_SIZE=$(du -sh src/luminous_nix 2>/dev/null | cut -f1)
DIST_SIZE=$(du -sh "$DIST_DIR/$PACKAGE_NAME" 2>/dev/null | cut -f1)
ARCHIVE_SIZE=$(du -sh "$DIST_DIR/$PACKAGE_NAME.tar.gz" 2>/dev/null | cut -f1)

# Success message
echo ""
echo -e "${GREEN}✅ Standalone build successful!${NC}"
echo "================================================="
echo -e "📊 Size Statistics:"
echo -e "  Original source: ${YELLOW}$ORIGINAL_SIZE${NC}"
echo -e "  Distribution:    ${YELLOW}$DIST_SIZE${NC}"
echo -e "  Archive:         ${GREEN}$ARCHIVE_SIZE${NC}"
echo ""
echo -e "📦 Package: ${GREEN}$DIST_DIR/$PACKAGE_NAME.tar.gz${NC}"
echo ""
echo -e "${YELLOW}📋 Distribution contains:${NC}"
echo "  • Standalone Python executable"
echo "  • Core modules with integrated backend"
echo "  • Service architecture"
echo "  • AI orchestration framework"
echo "  • TUI components"
echo "  • Installation script"
echo "  • Documentation"
echo ""
echo -e "${GREEN}🚀 To test the standalone build:${NC}"
echo "  tar -xzf $DIST_DIR/$PACKAGE_NAME.tar.gz"
echo "  cd $PACKAGE_NAME"
echo "  ./install.sh"
echo "  ./luminous-nix help"
echo ""
echo -e "${GREEN}✨ Ready for v0.1.0-alpha release!${NC}"