#!/usr/bin/env bash

# Create GitHub Release for Luminous Nix v0.8.1
# This script creates the release with all artifacts

set -e

VERSION="0.8.1"
REPO="Tristan-Stoltz-ERC/luminous-nix"

echo "🚀 Creating GitHub Release for v$VERSION"
echo "======================================="

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is required but not installed."
    echo "   Install with: nix-shell -p gh"
    exit 1
fi

# Check if logged in
if ! gh auth status &>/dev/null; then
    echo "❌ Not logged into GitHub CLI"
    echo "   Run: gh auth login"
    exit 1
fi

# Check if release already exists
if gh release view v$VERSION --repo $REPO &>/dev/null; then
    echo "⚠️  Release v$VERSION already exists"
    echo "   Delete it first with: gh release delete v$VERSION --repo $REPO"
    exit 1
fi

# Verify artifacts exist
TARBALL="dist-v081/luminous-nix-v${VERSION}-standalone.tar.gz"
CHECKSUM="dist-v081/luminous-nix-v${VERSION}-standalone.tar.gz.sha256"

if [ ! -f "$TARBALL" ]; then
    echo "❌ Tarball not found: $TARBALL"
    echo "   Run: ./scripts/build-standalone-v0.8.1.sh"
    exit 1
fi

if [ ! -f "$CHECKSUM" ]; then
    echo "❌ Checksum not found: $CHECKSUM"
    exit 1
fi

echo "✅ Artifacts found"
echo "  - $(basename $TARBALL) ($(du -h $TARBALL | cut -f1))"
echo "  - $(basename $CHECKSUM)"

# Create the release
echo ""
echo "📦 Creating GitHub release..."
gh release create "v$VERSION" \
    "$TARBALL" \
    "$CHECKSUM" \
    --repo "$REPO" \
    --title "v${VERSION}: Real Neural HRM with 99.93% Accuracy! 🧠" \
    --notes-file "RELEASE_v${VERSION}.md" \
    --latest

echo ""
echo "✅ Release created successfully!"
echo ""
echo "📎 View at: https://github.com/$REPO/releases/tag/v$VERSION"
echo ""
echo "Next steps:"
echo "  1. ✅ GitHub release created"
echo "  2. 📝 Write blog post (see ANNOUNCEMENT_v0.8.1.md)"
echo "  3. 📦 Publish to PyPI with: poetry publish"
echo "  4. 📢 Share on forums"