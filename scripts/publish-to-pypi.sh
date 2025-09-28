#!/usr/bin/env bash

# Publish Luminous Nix v0.8.1 to PyPI
# Requires: poetry, PyPI account with API token

set -e

VERSION="0.8.1"

echo "📦 Publishing Luminous Nix v$VERSION to PyPI"
echo "==========================================="

# Check version in pyproject.toml
CURRENT_VERSION=$(grep "^version" pyproject.toml | cut -d'"' -f2)
if [ "$CURRENT_VERSION" != "$VERSION" ]; then
    echo "❌ Version mismatch!"
    echo "   pyproject.toml has: $CURRENT_VERSION"
    echo "   Expected: $VERSION"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/

# Build the package
echo "🔨 Building package..."
poetry build

# Check build artifacts
if [ ! -f "dist/luminous_nix-${VERSION}-py3-none-any.whl" ]; then
    echo "❌ Wheel not found!"
    exit 1
fi

if [ ! -f "dist/luminous_nix-${VERSION}.tar.gz" ]; then
    echo "❌ Source distribution not found!"
    exit 1
fi

echo "✅ Build successful:"
ls -lh dist/

# Check if we have PyPI credentials
echo ""
echo "📝 PyPI Authentication"
echo "----------------------"
echo "You need a PyPI API token. If you don't have one:"
echo "  1. Go to https://pypi.org/manage/account/token/"
echo "  2. Create a token with upload permissions"
echo "  3. Save it securely"
echo ""
echo "Configure poetry with your token:"
echo "  poetry config pypi-token.pypi YOUR_TOKEN"
echo ""
read -p "Do you have PyPI configured? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⏸️  Configure PyPI first, then run this script again"
    exit 0
fi

# Publish to PyPI
echo ""
echo "🚀 Publishing to PyPI..."
poetry publish

echo ""
echo "✅ Successfully published to PyPI!"
echo ""
echo "📦 Package available at:"
echo "   https://pypi.org/project/luminous-nix/$VERSION/"
echo ""
echo "🎉 Users can now install with:"
echo "   pip install luminous-nix==$VERSION"
echo ""
echo "Next steps:"
echo "  1. ✅ GitHub release created"
echo "  2. ✅ Blog post written"
echo "  3. ✅ Published to PyPI"
echo "  4. 📢 Share on forums (NixOS Discourse, Reddit, HN)"
