#!/usr/bin/env bash

# 🌟 Luminous Nix Quick Demo - Experience Natural Language NixOS in 60 Seconds
# =============================================================================

set -e

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Sacred greeting
echo -e "${PURPLE}${BOLD}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🌟 Luminous Nix - Natural Language NixOS Interface 🌟     ║"
echo "║         Experience the future of NixOS in 60 seconds          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if we're in the project directory
if [ ! -f "flake.nix" ]; then
    echo -e "${YELLOW}⚠️  Please run this script from the luminous-nix directory${NC}"
    exit 1
fi

# Quick dependency check
echo -e "${CYAN}📦 Checking environment...${NC}"
if ! command -v nix &> /dev/null; then
    echo -e "${RED}❌ Nix is not installed. Please install Nix first.${NC}"
    echo "   Visit: https://nixos.org/download"
    exit 1
fi

# Enter nix shell for dependencies
echo -e "${BLUE}🛠️  Loading Nix environment (one-time setup)...${NC}"
echo "   This provides all dependencies - no manual installs needed!"
echo

# Use nix develop for the demo
if command -v nix &> /dev/null && nix --version | grep -q "2\.[4-9]\|3\."; then
    # Nix 2.4+ with flakes
    echo -e "${GREEN}✅ Using Nix flakes (modern setup)${NC}"
    DEMO_CMD="nix develop --command"
else
    # Fallback to nix-shell
    echo -e "${YELLOW}📦 Using nix-shell (traditional setup)${NC}"
    DEMO_CMD="nix-shell --run"
fi

# Demo selection menu
echo
echo -e "${PURPLE}${BOLD}🎭 Choose Your Demo Experience:${NC}"
echo
echo -e "${GREEN}1)${NC} 🗣️  ${BOLD}Natural Language Commands${NC} - See how to install software with plain English"
echo -e "${GREEN}2)${NC} 👵 ${BOLD}Grandma Mode${NC} - Experience NixOS designed for non-technical users"
echo -e "${GREEN}3)${NC} 🎨 ${BOLD}Beautiful TUI${NC} - Explore the visual interface"
echo -e "${GREEN}4)${NC} 🧙 ${BOLD}AI Assistant${NC} - Ask the local LLM for NixOS help"
echo -e "${GREEN}5)${NC} ⚡ ${BOLD}Full Experience${NC} - Try everything!"
echo
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo
        echo -e "${CYAN}${BOLD}🗣️  Natural Language Demo${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo
        echo -e "${GREEN}Instead of memorizing commands like:${NC}"
        echo -e "${RED}  nix-env -iA nixpkgs.firefox${NC}"
        echo
        echo -e "${GREEN}Just say what you want:${NC}"
        echo -e "${CYAN}  'install firefox'${NC}"
        echo -e "${CYAN}  'find a markdown editor'${NC}"
        echo -e "${CYAN}  'create python development environment'${NC}"
        echo
        echo -e "${YELLOW}Let's try it! Type your request in plain English:${NC}"
        echo
        
        # Get user input
        read -p "What would you like to do? " user_request
        
        # Run the natural language command
        echo
        echo -e "${BLUE}🤖 Processing: \"$user_request\"${NC}"
        $DEMO_CMD "bash -c 'export NIX_HUMANITY_PYTHON_BACKEND=true; ./bin/ask-nix \"$user_request\"'"
        ;;
        
    2)
        echo
        echo -e "${CYAN}${BOLD}👵 Grandma Mode Demo${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo
        echo -e "${GREEN}NixOS for everyone, regardless of technical expertise!${NC}"
        echo
        echo "Features:"
        echo "  • Voice-first interaction (with typing fallback)"
        echo "  • Clear, jargon-free explanations"
        echo "  • Gentle error messages that teach"
        echo "  • Step-by-step guidance"
        echo
        echo -e "${YELLOW}Starting Grandma Mode...${NC}"
        echo
        
        $DEMO_CMD "./bin/grandma-nix help"
        echo
        echo -e "${GREEN}Try: ${CYAN}./bin/grandma-nix 'help me print photos'${NC}"
        ;;
        
    3)
        echo
        echo -e "${CYAN}${BOLD}🎨 Beautiful TUI Demo${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━"
        echo
        echo -e "${GREEN}A visual interface that adapts to your expertise level${NC}"
        echo
        echo "TUI Features:"
        echo "  • Real-time package search"
        echo "  • Visual configuration builder"
        echo "  • System health monitoring"
        echo "  • Generation management"
        echo
        echo -e "${YELLOW}Launching TUI (press 'q' to exit)...${NC}"
        echo
        sleep 2
        
        $DEMO_CMD "./bin/nix-tui"
        ;;
        
    4)
        echo
        echo -e "${CYAN}${BOLD}🧙 AI Assistant Demo${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━"
        echo
        echo -e "${GREEN}Local LLM providing NixOS expertise - no cloud needed!${NC}"
        echo
        echo "Sacred Trinity in action:"
        echo "  1. You provide the question"
        echo "  2. Local LLM provides NixOS expertise"
        echo "  3. System executes with safety checks"
        echo
        
        # Check if ollama is available
        if command -v ollama &> /dev/null || [ -f ~/.nix-profile/bin/ollama ]; then
            echo -e "${YELLOW}Let's ask a NixOS question:${NC}"
            read -p "Your question: " question
            $DEMO_CMD "ask-nix-guru \"$question\""
        else
            echo -e "${YELLOW}Note: Ollama not installed. Showing example:${NC}"
            echo
            echo "Example: ask-nix-guru 'How do I enable Docker in NixOS?'"
            echo
            echo "Would return:"
            echo "  To enable Docker in NixOS, add this to configuration.nix:"
            echo "    virtualisation.docker.enable = true;"
            echo "  Then rebuild: sudo nixos-rebuild switch"
        fi
        ;;
        
    5)
        echo
        echo -e "${CYAN}${BOLD}⚡ Full Experience Tour${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━"
        echo
        echo -e "${GREEN}Let's explore all the features!${NC}"
        echo
        
        # Natural language
        echo -e "${PURPLE}1. Natural Language:${NC}"
        echo -e "   ${CYAN}Searching for video editors...${NC}"
        $DEMO_CMD "bash -c 'export NIX_HUMANITY_PYTHON_BACKEND=true; ./bin/ask-nix \"find video editor\" | head -10'"
        echo
        sleep 2
        
        # Configuration generation
        echo -e "${PURPLE}2. Configuration Generation:${NC}"
        echo -e "   ${CYAN}Creating a web development environment...${NC}"
        $DEMO_CMD "bash -c 'export NIX_HUMANITY_PYTHON_BACKEND=true; ./bin/ask-nix \"create web development environment with nodejs and postgresql\" | head -20'"
        echo
        sleep 2
        
        # System health
        echo -e "${PURPLE}3. System Health Check:${NC}"
        echo -e "   ${CYAN}Checking your NixOS system...${NC}"
        $DEMO_CMD "bash -c 'export NIX_HUMANITY_PYTHON_BACKEND=true; ./bin/ask-nix \"check system health\" | head -15'"
        echo
        
        echo -e "${GREEN}${BOLD}✨ That's the power of Luminous Nix!${NC}"
        ;;
        
    *)
        echo -e "${RED}Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

# Closing message
echo
echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
echo
echo -e "${GREEN}${BOLD}🎉 Thanks for trying Luminous Nix!${NC}"
echo
echo -e "${CYAN}Quick Install (one command):${NC}"
echo -e "${YELLOW}  nix run github:Luminous-Dynamics/nix-for-humanity${NC}"
echo
echo -e "${CYAN}Learn more:${NC}"
echo "  • Documentation: ${BLUE}https://luminous-dynamics.github.io/nix-for-humanity${NC}"
echo "  • GitHub: ${BLUE}https://github.com/Luminous-Dynamics/nix-for-humanity${NC}"
echo "  • Sacred Trinity Workflow: ${BLUE}docs/SACRED_TRINITY_WORKFLOW.md${NC}"
echo
echo -e "${PURPLE}Built with love by a solo developer + AI for just \$200/month${NC}"
echo -e "${PURPLE}Proving that consciousness-first computing is accessible to all!${NC}"
echo
echo -e "${GREEN}${BOLD}🌊 We flow together toward a more accessible NixOS! 🌊${NC}"
echo