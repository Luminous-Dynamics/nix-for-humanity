#!/usr/bin/env bash
#
# 🚀 Nix for Humanity - XAI TUI Demo Launcher
# 
# This script launches the enhanced TUI with XAI features enabled
# Run this to experience the completed integration!

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to project directory
cd "$(dirname "${BASH_SOURCE[0]}")"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          ${GREEN}🌟 Nix for Humanity - XAI TUI Demo 🌟${BLUE}                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in development environment
if [ -z "$IN_NIX_SHELL" ]; then
    echo -e "${YELLOW}⚠️  Not in development environment. Starting dev shell...${NC}"
    echo ""
    exec ./dev.sh "$0" "$@"
fi

# Enable Python backend for best performance
export NIX_HUMANITY_PYTHON_BACKEND=true

# Menu
echo -e "${GREEN}Select demo mode:${NC}"
echo ""
echo "  1) 🖥️  Interactive TUI - Full terminal interface with XAI"
echo "  2) 🤖  Automated Demo - See XAI features in action"
echo "  3) 👵  Grandma Rose Demo - Gentle, accessible interface"
echo "  4) ⚡  Maya (ADHD) Demo - Fast, minimal responses"
echo "  5) 🔬  Dr. Sarah Demo - Technical, detailed explanations"
echo "  6) 👁️  Alex (Blind) Demo - Screen reader optimized"
echo ""
echo -n "Enter choice (1-6) [1]: "
read choice

# Default to interactive if no choice
choice=${choice:-1}

case $choice in
    1)
        echo -e "\n${GREEN}Launching interactive TUI...${NC}"
        echo -e "${YELLOW}Tips:${NC}"
        echo "  • Press Ctrl+X to toggle XAI explanations"
        echo "  • Press Ctrl+E to cycle explanation levels"
        echo "  • Try: 'install firefox' then ask 'why did you suggest that?'"
        echo ""
        sleep 2
        python3 demo_xai_tui.py
        ;;
    2)
        echo -e "\n${GREEN}Running automated demo...${NC}"
        python3 demo_xai_tui.py --auto
        ;;
    3)
        echo -e "\n${GREEN}Running Grandma Rose demo...${NC}"
        python3 demo_xai_tui.py --persona grandma_rose --auto
        ;;
    4)
        echo -e "\n${GREEN}Running Maya (ADHD) demo...${NC}"
        python3 demo_xai_tui.py --persona maya_adhd --auto
        ;;
    5)
        echo -e "\n${GREEN}Running Dr. Sarah demo...${NC}"
        python3 demo_xai_tui.py --persona dr_sarah --auto
        ;;
    6)
        echo -e "\n${GREEN}Running Alex (Blind) demo...${NC}"
        python3 demo_xai_tui.py --persona alex_blind --auto
        ;;
    *)
        echo -e "\n${YELLOW}Invalid choice. Launching interactive TUI...${NC}"
        sleep 1
        python3 demo_xai_tui.py
        ;;
esac

echo -e "\n${GREEN}✨ Demo completed!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "  • Try the TUI directly: ./bin/nix-tui"
echo "  • Read about XAI: cat docs/02-ARCHITECTURE/11-XAI-ARCHITECTURE.md"
echo "  • Test with CLI: ./bin/ask-nix --xai 'install firefox'"
echo ""