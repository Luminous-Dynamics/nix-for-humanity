#!/usr/bin/env bash

# 🌟 Luminous Nix - One-Line Installer
# =====================================
# Run with: curl -L https://luminous.sh | sh
# Or: wget -qO- https://luminous.sh | sh

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${BLUE}${BOLD}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🌟 Installing Luminous Nix - Natural Language NixOS 🌟    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}⚠️  macOS detected. Luminous Nix is designed for NixOS/Linux.${NC}"
    echo "   You can still use it with nix-darwin or in a VM."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    OS="darwin"
else
    echo -e "${RED}❌ Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

# Check for Nix
if ! command -v nix &> /dev/null; then
    echo -e "${YELLOW}📦 Nix is not installed.${NC}"
    echo "Would you like to install Nix now? (recommended)"
    read -p "(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Installing Nix...${NC}"
        if [[ "$OS" == "linux" ]]; then
            sh <(curl -L https://nixos.org/nix/install) --daemon
        else
            sh <(curl -L https://nixos.org/nix/install)
        fi
        
        # Source nix
        if [ -e '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' ]; then
            . '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'
        fi
    else
        echo -e "${RED}❌ Nix is required. Please install it first.${NC}"
        echo "   Visit: https://nixos.org/download"
        exit 1
    fi
fi

# Check Nix version for flakes support
NIX_VERSION=$(nix --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
NIX_MAJOR=$(echo $NIX_VERSION | cut -d. -f1)
NIX_MINOR=$(echo $NIX_VERSION | cut -d. -f2)

FLAKES_ENABLED=false
if [ "$NIX_MAJOR" -gt 2 ] || ([ "$NIX_MAJOR" -eq 2 ] && [ "$NIX_MINOR" -ge 4 ]); then
    # Check if flakes are enabled
    if nix flake --help &>/dev/null; then
        FLAKES_ENABLED=true
    fi
fi

if [ "$FLAKES_ENABLED" = false ]; then
    echo -e "${YELLOW}📋 Enabling Nix flakes...${NC}"
    mkdir -p ~/.config/nix
    echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
    
    # For NixOS systems
    if [ -f /etc/nixos/configuration.nix ]; then
        echo -e "${YELLOW}Note: You may need to add this to your configuration.nix:${NC}"
        echo "  nix.settings.experimental-features = [ \"nix-command\" \"flakes\" ];"
    fi
fi

# Installation method selection
echo
echo -e "${BLUE}Choose installation method:${NC}"
echo "1) Quick Try (no installation, run directly)"
echo "2) User Install (install to ~/.nix-profile)"
echo "3) System Install (NixOS only, adds to configuration.nix)"
echo "4) Development Mode (clone repository for contributing)"
echo
read -p "Select (1-4): " install_method

case $install_method in
    1)
        # Quick try with nix run
        echo -e "${GREEN}🚀 Running Luminous Nix directly...${NC}"
        echo -e "${YELLOW}This will download and run without installing.${NC}"
        echo
        
        if [ "$FLAKES_ENABLED" = true ]; then
            echo -e "${BLUE}Starting Grandma Mode (easiest interface)...${NC}"
            nix run github:Luminous-Dynamics/nix-for-humanity#grandma-nix -- help
            
            echo
            echo -e "${GREEN}✅ Quick try complete!${NC}"
            echo -e "${YELLOW}To install permanently, run this script again and choose option 2 or 3.${NC}"
        else
            echo -e "${RED}❌ Flakes must be enabled for quick try.${NC}"
            echo "Please run the installer again after enabling flakes."
            exit 1
        fi
        ;;
        
    2)
        # User installation
        echo -e "${GREEN}📦 Installing to user profile...${NC}"
        
        if [ "$FLAKES_ENABLED" = true ]; then
            nix profile install github:Luminous-Dynamics/nix-for-humanity
        else
            # Fallback to traditional nix-env
            nix-env -if https://github.com/Luminous-Dynamics/nix-for-humanity/tarball/main
        fi
        
        echo -e "${GREEN}✅ Installation complete!${NC}"
        echo
        echo -e "${BLUE}Available commands:${NC}"
        echo "  ask-nix         - Natural language NixOS interface"
        echo "  grandma-nix     - Simplified interface for beginners"
        echo "  nix-tui         - Beautiful terminal UI"
        echo "  ask-nix-guru    - Local AI assistant"
        echo
        echo -e "${YELLOW}Try: ask-nix 'install firefox'${NC}"
        ;;
        
    3)
        # System installation (NixOS)
        if [ ! -f /etc/nixos/configuration.nix ]; then
            echo -e "${RED}❌ This option is only for NixOS systems.${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}📝 Adding to NixOS configuration...${NC}"
        echo
        echo "Add this to your configuration.nix:"
        echo
        echo -e "${YELLOW}  # Luminous Nix - Natural Language Interface"
        echo "  programs.luminous-nix = {"
        echo "    enable = true;"
        echo "  };"
        echo
        echo "  # Also add the flake input:"
        echo "  inputs.nix-for-humanity.url = \"github:Luminous-Dynamics/nix-for-humanity\";"
        echo -e "${NC}"
        echo
        echo "Then rebuild with: sudo nixos-rebuild switch"
        echo
        read -p "Would you like to open configuration.nix now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} /etc/nixos/configuration.nix
        fi
        ;;
        
    4)
        # Development installation
        echo -e "${GREEN}🔧 Setting up development environment...${NC}"
        
        # Clone repository
        if [ -d "nix-for-humanity" ]; then
            echo -e "${YELLOW}Directory 'nix-for-humanity' already exists.${NC}"
            read -p "Remove and re-clone? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf nix-for-humanity
            else
                cd nix-for-humanity
                git pull
            fi
        fi
        
        if [ ! -d "nix-for-humanity" ]; then
            echo -e "${BLUE}Cloning repository...${NC}"
            git clone https://github.com/Luminous-Dynamics/nix-for-humanity.git
            cd nix-for-humanity
        fi
        
        echo -e "${BLUE}Entering development shell...${NC}"
        if [ "$FLAKES_ENABLED" = true ]; then
            nix develop -c bash -c "
                echo -e '${GREEN}✅ Development environment ready!${NC}'
                echo
                echo 'Available commands:'
                echo '  ./quick-demo.sh  - Run the interactive demo'
                echo '  ask-nix         - Test natural language interface'
                echo '  grandma-nix     - Test beginner-friendly mode'
                echo '  nix-tui         - Test the TUI'
                echo
                echo 'Development commands:'
                echo '  npm test        - Run tests'
                echo '  npm run build   - Build project'
                echo
                echo -e '${YELLOW}You are now in the development shell.${NC}'
                exec bash
            "
        else
            nix-shell --run "
                echo -e '${GREEN}✅ Development environment ready!${NC}'
                exec bash
            "
        fi
        ;;
        
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

# Success message
if [ "$install_method" != "4" ]; then
    echo
    echo -e "${GREEN}${BOLD}🎉 Luminous Nix is ready!${NC}"
    echo
    echo -e "${BLUE}Quick Start:${NC}"
    echo "  ask-nix 'help'              - See what you can do"
    echo "  ask-nix 'install firefox'   - Install software naturally"
    echo "  grandma-nix help            - Beginner-friendly mode"
    echo
    echo -e "${BLUE}Learn More:${NC}"
    echo "  Website: https://luminous-dynamics.github.io/nix-for-humanity"
    echo "  GitHub:  https://github.com/Luminous-Dynamics/nix-for-humanity"
    echo
    echo -e "${GREEN}Welcome to natural language NixOS! 🌊${NC}"
fi