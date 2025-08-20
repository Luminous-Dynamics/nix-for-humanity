#!/bin/bash
# Simple push script using gh CLI

echo "🚀 Pushing Nix for Humanity to GitHub"
echo "===================================="

# Change to repository directory
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository!"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  You have uncommitted changes:"
    git status --short
    echo ""
    read -p "Do you want to commit them first? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " COMMIT_MSG
        git add .
        git commit -m "$COMMIT_MSG"
    fi
fi

# Push using gh CLI
echo ""
echo "🔐 Authenticating with GitHub..."

# Use the existing gh auth
if gh auth status &>/dev/null; then
    echo "✅ Already authenticated with GitHub"
else
    echo "❌ Not authenticated. Please run: gh auth login"
    exit 1
fi

# Configure git to use gh for authentication
git config credential.helper ""
git config credential.helper "!gh auth git-credential"

# Set remote URL to use HTTPS (gh CLI works better with HTTPS)
git remote set-url origin https://github.com/Luminous-Dynamics/nix-for-humanity.git

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
if git push origin "$CURRENT_BRANCH"; then
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🌐 View your repository at:"
    echo "   https://github.com/Luminous-Dynamics/nix-for-humanity"
else
    echo "❌ Push failed. Please check the error message above."
    exit 1
fi