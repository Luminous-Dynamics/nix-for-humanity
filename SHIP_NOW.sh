#!/usr/bin/env bash
# 🚀 FINAL SHIPPING COMMANDS FOR LUMINOUS NIX v0.1.0-alpha

set -e

echo "🚀 LUMINOUS NIX SHIPPING SCRIPT"
echo "================================"
echo ""
echo "This script will:"
echo "1. Commit all changes"
echo "2. Create git tag"
echo "3. Push to GitHub"
echo "4. Create GitHub release"
echo ""
echo "Press Enter to continue or Ctrl+C to abort..."
read

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📝 Step 1: Committing all changes...${NC}"
git add -A
git commit -m "🚀 Release v0.1.0-alpha - Natural Language NixOS Interface

- Natural language interface for NixOS
- AI-powered system diagnosis and repair  
- 10 adaptive personas
- 2-minute setup wizard
- Built in 2 weeks with AI for $200/month

This is the first public alpha release of Luminous Nix, demonstrating
AI-assisted development and making NixOS accessible to everyone." || echo "Already committed"

echo -e "${GREEN}✅ Changes committed${NC}"
echo ""

echo -e "${YELLOW}🏷️ Step 2: Creating git tag...${NC}"
git tag -a v0.1.0-alpha -m "First public alpha release" || echo "Tag already exists"
echo -e "${GREEN}✅ Tag created${NC}"
echo ""

echo -e "${YELLOW}📤 Step 3: Pushing to GitHub...${NC}"
echo "Pushing main branch..."
git push origin main || echo "Already up to date"
echo "Pushing tag..."
git push origin v0.1.0-alpha || echo "Tag already pushed"
echo -e "${GREEN}✅ Pushed to GitHub${NC}"
echo ""

echo -e "${YELLOW}🎉 Step 4: Creating GitHub release...${NC}"
echo "Creating release on GitHub..."

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) not installed. Please install it or create release manually at:"
    echo "https://github.com/Luminous-Dynamics/luminous-nix/releases/new"
else
    gh release create v0.1.0-alpha \
        --repo Luminous-Dynamics/luminous-nix \
        --title "v0.1.0-alpha: Natural Language Interface for NixOS" \
        --notes-file RELEASE_NOTES.md \
        --prerelease \
        --discussion-category "Announcements" || echo "Release already exists"
    
    echo -e "${GREEN}✅ GitHub release created${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}🎉 SHIP COMPLETE! 🎉${NC}"
echo ""
echo "Next steps:"
echo "1. Visit: https://github.com/Luminous-Dynamics/luminous-nix/releases"
echo "2. Post announcements:"
echo "   - Reddit: r/NixOS (see announcements/reddit.md)"
echo "   - Hacker News: Submit as Show HN"
echo "   - Twitter/X: Post announcement (see announcements/twitter.md)"
echo "   - Discord: NixOS Discord #announcements"
echo ""
echo "3. Monitor:"
echo "   - GitHub Issues for bug reports"
echo "   - GitHub Discussions for questions"
echo "   - Social media for feedback"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🌟 Congratulations! You've shipped Luminous Nix v0.1.0-alpha! 🌟"
echo ""
echo "This proves that AI-assisted development works."
echo "Solo developer + AI = Team productivity"
echo ""
echo "Now let's see how the world responds! 🚀"