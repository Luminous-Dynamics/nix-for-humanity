#!/bin/bash
# 🚀 Ship v0.2.0 - The Robust Architecture Release

set -e

echo "🚀 Shipping Luminous Nix v0.2.0 - The Robust Architecture Release"
echo "================================================================"
echo ""

# Check if we're on the right branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo "⚠️  You have uncommitted changes!"
    echo ""
    git status -s
    echo ""
    read -p "Do you want to commit them now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "🚀 Release v0.2.0 - The Robust Architecture Release

- Advanced Intent Recognition (25+ intents)
- Multi-turn Conversations with context
- Robust Command Execution with rollback
- Intelligent Error Recovery
- 10-100x Performance boost with caching
- Plugin Architecture for extensibility
- 3,500+ lines of new architecture code"
    else
        echo "Aborting release..."
        exit 1
    fi
fi

# Tag the release
echo "🏷️  Creating git tag v0.2.0..."
git tag -a v0.2.0 -m "Release v0.2.0 - The Robust Architecture Release

Major Features:
- Advanced Intent Recognition Pipeline
- Multi-turn Conversation Support
- Robust Command Execution Layer
- Intelligent Error Recovery System
- High-performance Search Caching
- Plugin Architecture

This release transforms Luminous Nix from a simple command wrapper into a sophisticated, context-aware assistant with professional-grade architecture."

echo "✅ Tag created!"

# Push changes and tags
read -p "Push to GitHub? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin $CURRENT_BRANCH
    git push origin v0.2.0
    echo "✅ Pushed to GitHub!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Go to: https://github.com/Luminous-Dynamics/luminous-nix/releases/new"
    echo "2. Select tag: v0.2.0"
    echo "3. Use RELEASE-v0.2.0.md for release notes"
    echo "4. Publish release!"
    echo ""
    echo "🎉 Ship it and iterate!"
else
    echo "Not pushing yet. You can push later with:"
    echo "  git push origin $CURRENT_BRANCH"
    echo "  git push origin v0.2.0"
fi

echo ""
echo "🌊 Remember: Ship fast, iterate faster, make NixOS accessible to all!"