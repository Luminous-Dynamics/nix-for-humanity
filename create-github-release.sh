#!/usr/bin/env bash
# Create GitHub release for v0.1.0-alpha

set -e

VERSION="v0.1.0-alpha"
RELEASE_TITLE="v0.1.0-alpha: First Real Working Release"

echo "🚀 Creating GitHub Release for $VERSION"
echo "========================================"

# Check if we have the gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found!"
    echo "Install with: nix-shell -p gh"
    exit 1
fi

# Check if release asset exists
if [ ! -f "dist-minimal/luminous-nix-v0.1.0-alpha-minimal.tar.gz" ]; then
    echo "❌ Release asset not found!"
    echo "Run: ./build-minimal.sh"
    exit 1
fi

# Check if release notes exist
if [ ! -f "RELEASE-v0.1.0-alpha.md" ]; then
    echo "❌ Release notes not found!"
    exit 1
fi

echo "📋 Pre-flight checks:"
echo "  ✅ GitHub CLI available"
echo "  ✅ Release asset found (2.0MB)"
echo "  ✅ Release notes ready"
echo

echo "📝 Release will include:"
echo "  - dist-minimal/luminous-nix-v0.1.0-alpha-minimal.tar.gz"
echo "  - Release notes from RELEASE-v0.1.0-alpha.md"
echo "  - Marked as pre-release (alpha)"
echo

read -p "🤔 Ready to create release? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Release cancelled"
    exit 1
fi

echo
echo "🏃 Pushing to GitHub..."

# Push main branch
echo "  📤 Pushing main branch..."
git push origin main || echo "  ⚠️  Main already up to date"

# Push tag
echo "  🏷️  Pushing tag..."
git push origin $VERSION || echo "  ⚠️  Tag already pushed"

echo
echo "📦 Creating GitHub release..."

# Create the release
gh release create $VERSION \
    dist-minimal/luminous-nix-v0.1.0-alpha-minimal.tar.gz \
    --title "$RELEASE_TITLE" \
    --notes-file RELEASE-v0.1.0-alpha.md \
    --prerelease

if [ $? -eq 0 ]; then
    echo
    echo "✅ Release created successfully!"
    echo
    echo "🎉 v0.1.0-alpha is now available!"
    echo
    echo "📊 What's next:"
    echo "  1. Check the release page on GitHub"
    echo "  2. Test the download link"
    echo "  3. Announce to NixOS community"
    echo "  4. Monitor for user feedback"
    echo
    echo "🔗 View release:"
    gh release view $VERSION --web
else
    echo
    echo "❌ Release creation failed!"
    echo "Check GitHub permissions and try again"
    exit 1
fi

echo
echo "🌟 First real release complete!"
echo "From mockup to reality - the journey continues..."