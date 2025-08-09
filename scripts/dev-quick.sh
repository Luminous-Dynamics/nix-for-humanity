#!/usr/bin/env bash
# 🚀 Quick Development Entry for Nix for Humanity
# Handles Claude Code timeout issues gracefully

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🌟 Nix for Humanity - Quick Development Setup${NC}"
echo "============================================"
echo ""

# Check if we're in Claude Code
if [ -n "${CLAUDE_CODE:-}" ]; then
    echo -e "${YELLOW}⚠️  Claude Code detected - using timeout-friendly approach${NC}"
fi

# Check if dependencies are already cached
if [ -f ".nix-deps-status" ]; then
    echo -e "${GREEN}✅ Found dependency status file${NC}"
    cat .nix-deps-status
    echo ""
fi

# Offer choices
echo "Choose your development path:"
echo ""
echo "1) Full environment (nix develop) - Best if pre-fetched"
echo "2) Minimal voice shell - Quick start (~50MB)"
echo "3) Progress indicator - See what's happening"
echo "4) Mock mode - Instant, no dependencies"
echo "5) Pre-fetch dependencies - Run outside Claude Code"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo -e "\n${BLUE}Starting full Nix development environment...${NC}"
        echo -e "${YELLOW}This may timeout in Claude Code if not pre-fetched!${NC}"
        nix develop
        ;;
    2)
        echo -e "\n${BLUE}Starting minimal voice shell...${NC}"
        nix-shell shell-voice-minimal.nix
        ;;
    3)
        echo -e "\n${BLUE}Starting with progress indicator...${NC}"
        ./scripts/nix-with-progress.sh develop
        ;;
    4)
        echo -e "\n${GREEN}Starting in mock mode - no dependencies needed!${NC}"
        export NIX_VOICE_MOCK=true
        export NIX_HUMANITY_MOCK=true
        echo ""
        echo "Mock mode activated! You can now run:"
        echo "  ./bin/ask-nix 'help'"
        echo "  ./bin/nix-voice"
        echo "  ./bin/nix-tui"
        echo ""
        echo "Note: Actual NixOS operations won't work in mock mode"
        /bin/bash
        ;;
    5)
        echo -e "\n${YELLOW}Pre-fetch instructions:${NC}"
        echo ""
        echo "Run this command OUTSIDE of Claude Code:"
        echo -e "${GREEN}./scripts/prefetch-dependencies.sh${NC}"
        echo ""
        echo "This will download all dependencies in the background."
        echo "Once complete, option 1 will work instantly!"
        ;;
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac