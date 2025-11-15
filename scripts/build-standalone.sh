#!/usr/bin/env bash
# Build standalone executable for Luminous Nix
# No Poetry or Python required for end users!

set -e

echo "🚀 Building Standalone Luminous Nix Executable"
echo "=============================================="

# Ensure we're in project root
cd "$(dirname "$0")/.."

# Use Nix shell for proper environment
echo "📦 Entering Nix shell for build environment..."
nix-shell --run "

# Check if we have PyInstaller
if ! python -c 'import PyInstaller' 2>/dev/null; then
    echo '📦 Installing PyInstaller...'
    pip install pyinstaller
fi"

# Get version
VERSION=$(cat VERSION || echo "0.4.0")
echo "📊 Version: $VERSION"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Create entry point for PyInstaller
echo "📝 Creating standalone entry point..."
cat > luminous_nix_main.py << 'EOF'
#!/usr/bin/env python3
"""Standalone entry point for Luminous Nix"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment for standalone
os.environ['LUMINOUS_STANDALONE'] = 'true'
os.environ['LUMINOUS_SKIP_UPDATES'] = 'true'

# Import and run CLI
from luminous_nix.cli import main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n✨ Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
EOF

# Build with PyInstaller
echo "🔨 Building executable with PyInstaller..."
poetry run pyinstaller \
    --name luminous-nix \
    --onefile \
    --console \
    --add-data "schemas:schemas" \
    --add-data "VERSION:." \
    --hidden-import "luminous_nix.core" \
    --hidden-import "luminous_nix.cli" \
    --hidden-import "luminous_nix.nix" \
    --hidden-import "luminous_nix.ai" \
    --hidden-import "luminous_nix.config" \
    --hidden-import "ollama" \
    --hidden-import "requests" \
    --hidden-import "rich" \
    --hidden-import "click" \
    --hidden-import "pyyaml" \
    --collect-all textual \
    --collect-all rich \
    luminous_nix_main.py

# Check if build succeeded
if [ -f "dist/luminous-nix" ]; then
    echo "✅ Build successful!"

    # Get file size
    SIZE=$(du -h dist/luminous-nix | cut -f1)
    echo "📊 Executable size: $SIZE"

    # Test the executable
    echo "🧪 Testing executable..."
    ./dist/luminous-nix --version || echo "Version check failed (might be normal)"
    ./dist/luminous-nix help | head -5

    echo ""
    echo "🎉 Standalone executable ready!"
    echo "================================"
    echo "📦 Location: dist/luminous-nix"
    echo "📊 Size: $SIZE"
    echo ""
    echo "🚀 To use:"
    echo "  ./dist/luminous-nix help"
    echo "  ./dist/luminous-nix search firefox"
    echo "  ./dist/luminous-nix install vim"
    echo ""
    echo "📤 To distribute:"
    echo "  Just share the single file: dist/luminous-nix"
    echo "  No Python, Poetry, or dependencies needed!"
else
    echo "❌ Build failed! Check errors above."
    exit 1
fi

# Clean up temp files
rm -f luminous_nix_main.py
