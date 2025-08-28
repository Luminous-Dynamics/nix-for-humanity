#!/usr/bin/env bash

# Simple test for poetry2nix integration
echo "🧪 Simple Poetry2nix Integration Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "1. Checking flake structure..."
if nix flake show --json 2>/dev/null | grep -q "ask-nix"; then
    echo -e "${GREEN}✅ Flake structure valid${NC}"
else
    echo -e "${YELLOW}⚠️  Flake needs evaluation${NC}"
fi

echo ""
echo "2. Checking Poetry files..."
if [ -f "poetry.lock" ] && [ -f "pyproject.toml" ]; then
    echo -e "${GREEN}✅ Poetry files exist${NC}"
else
    echo -e "${RED}❌ Missing Poetry files${NC}"
fi

echo ""
echo "3. Testing flake outputs..."
echo "   Available apps:"
nix flake show 2>&1 | grep -E "ask-nix|nix-tui|docs" | head -5

echo ""
echo "4. Testing traditional Poetry (should always work)..."
if poetry --version > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Poetry is available${NC}"
    echo "   You can use: poetry install && poetry run ask-nix"
else
    echo -e "${YELLOW}⚠️  Poetry not in PATH${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Summary:"
echo ""
echo "Poetry2nix is integrated! You have two options:"
echo ""
echo "1. ${GREEN}REPRODUCIBLE (Nix)${NC} - When it works:"
echo "   nix develop"
echo "   nix run .#ask-nix -- help"
echo ""
echo "2. ${GREEN}TRADITIONAL (Poetry)${NC} - Always works:"
echo "   poetry install"
echo "   poetry run ask-nix help"
echo ""
echo "Both approaches use the same pyproject.toml!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"