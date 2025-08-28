#!/usr/bin/env bash
# 🏗️ Build Standalone Executables for Luminous Nix v1.0
# Creates distribution-ready binaries that work without Poetry

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🏗️  Building Luminous Nix v1.0 Standalone Release          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo

# Check we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from luminous-nix root directory"
    exit 1
fi

# Install PyInstaller if not present
if ! poetry show pyinstaller > /dev/null 2>&1; then
    echo "📦 Installing PyInstaller..."
    poetry add --group dev pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Create a proper entry point script
echo "📝 Creating entry point..."
cat > build_entry.py << 'EOF'
#!/usr/bin/env python3
"""Entry point for standalone executable."""
import sys
import os

# Ensure we can find our modules
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_dir = sys._MEIPASS
else:
    # Running as script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Import and run CLI
from luminous_nix.cli import main

if __name__ == '__main__':
    main()
EOF

# Build the executable
echo "🏗️ Creating standalone executable..."
echo "   This may take 2-3 minutes..."

poetry run pyinstaller \
    --onefile \
    --name luminous-nix \
    --distpath ./dist \
    --workpath ./build \
    --specpath ./build \
    --hidden-import=click \
    --hidden-import=luminous_nix \
    --hidden-import=luminous_nix.core \
    --hidden-import=luminous_nix.core.intents \
    --hidden-import=luminous_nix.core.intent_pipeline \
    --hidden-import=luminous_nix.core.secure_intent_integration \
    --hidden-import=luminous_nix.frontends \
    --hidden-import=luminous_nix.frontends.cli \
    --hidden-import=luminous_nix.ai \
    --hidden-import=luminous_nix.ai.ollama_client \
    --hidden-import=luminous_nix.plugins \
    --hidden-import=luminous_nix.onboarding \
    --hidden-import=luminous_nix.onboarding.wizard \
    --collect-all=luminous_nix \
    --noconfirm \
    --clean \
    build_entry.py

# Clean up temp entry point
rm -f build_entry.py

# Check if build succeeded
if [ ! -f "./dist/luminous-nix" ]; then
    echo "❌ Build failed! Check errors above."
    exit 1
fi

# Get file size
SIZE=$(du -h ./dist/luminous-nix | cut -f1)
echo "📦 Executable size: $SIZE"

# Test the executable
echo ""
echo "🧪 Testing standalone executable..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test help command
echo "Testing: help command"
if ./dist/luminous-nix help > /dev/null 2>&1; then
    echo "✅ Help command works"
else
    echo "❌ Help command failed"
    exit 1
fi

# Test with dry run
echo "Testing: search command"
if LUMINOUS_DRY_RUN=true LUMINOUS_SKIP_CONFIRM=true timeout 5 ./dist/luminous-nix search editor > /dev/null 2>&1; then
    echo "✅ Search command works"
else
    echo "❌ Search command failed"
fi

echo ""
echo "🎉 Success! Standalone executable created!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Location: ./dist/luminous-nix ($SIZE)"
echo ""
echo "📋 Installation Options:"
echo ""
echo "  1. System-wide (recommended):"
echo "     sudo cp ./dist/luminous-nix /usr/local/bin/"
echo "     luminous-nix help"
echo ""
echo "  2. User-local:"
echo "     mkdir -p ~/.local/bin"
echo "     cp ./dist/luminous-nix ~/.local/bin/"
echo "     export PATH=\$HOME/.local/bin:\$PATH"
echo "     luminous-nix help"
echo ""
echo "  3. Test without installing:"
echo "     ./dist/luminous-nix help"
echo ""
echo "🚀 Ready to distribute!"