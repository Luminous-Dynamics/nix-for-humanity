#!/usr/bin/env bash
# 🚀 Quick Nix Setup for Nix for Humanity
# Handles the download timeout issue gracefully

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌟 Nix for Humanity - Quick Setup${NC}"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "flake.nix" ]; then
    echo -e "${RED}❌ Error: flake.nix not found. Please run from the project root.${NC}"
    exit 1
fi

# Function to check if nix store has our deps
check_deps_cached() {
    # Check for a few key dependencies
    if nix-store -q --references /nix/store/*-python3.11-openai-whisper* 2>/dev/null | grep -q whisper; then
        return 0
    fi
    return 1
}

# Main menu
echo "Choose your approach:"
echo ""
echo "1) 🚀 Quick start with minimal shell (50MB download)"
echo "2) 📦 Check if dependencies are cached"
echo "3) 🎭 Mock mode (no downloads needed)"
echo "4) 📥 Full environment (run outside Claude Code)"
echo "5) 📚 Show help"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo -e "\n${GREEN}Starting minimal voice environment...${NC}"
        echo "This downloads only essential packages (~50MB)"
        echo ""
        if [ -f "shell-voice-minimal.nix" ]; then
            nix-shell shell-voice-minimal.nix --command "echo '✅ Minimal environment ready!'"
        else
            echo -e "${YELLOW}Creating minimal shell...${NC}"
            cat > shell-voice-minimal.nix << 'EOF'
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-humanity-minimal";
  
  buildInputs = with pkgs; [
    python311
    portaudio
    espeak-ng
    sox
    ffmpeg
  ];
  
  shellHook = ''
    echo "🎤 Minimal voice environment loaded"
    echo "Use python venv for additional packages if needed"
    echo ""
    export PYTHONPATH="${toString ./.}:$PYTHONPATH"
  '';
}
EOF
            nix-shell shell-voice-minimal.nix
        fi
        ;;
        
    2)
        echo -e "\n${BLUE}Checking dependency cache...${NC}"
        if check_deps_cached; then
            echo -e "${GREEN}✅ Dependencies are cached! You can use 'nix develop'${NC}"
        else
            echo -e "${YELLOW}⚠️  Dependencies not cached. Run option 4 outside Claude Code.${NC}"
        fi
        ;;
        
    3)
        echo -e "\n${GREEN}Starting in mock mode...${NC}"
        echo "No downloads needed - using mock implementations"
        echo ""
        export NIX_VOICE_MOCK=true
        export NIX_HUMANITY_PYTHON_BACKEND=true
        echo "Environment variables set:"
        echo "  NIX_VOICE_MOCK=true"
        echo "  NIX_HUMANITY_PYTHON_BACKEND=true"
        echo ""
        echo "Now run: ./bin/nix-voice"
        ;;
        
    4)
        echo -e "\n${YELLOW}Full environment setup${NC}"
        echo "This needs to run OUTSIDE Claude Code due to download size."
        echo ""
        echo "Steps:"
        echo "1. Open a regular terminal"
        echo "2. Navigate to: $(pwd)"
        echo "3. Run: nix develop"
        echo "4. Wait for downloads (5-10 minutes first time)"
        echo "5. Return to Claude Code - deps will be cached"
        echo ""
        echo "Alternative: ./scripts/prefetch-dependencies.sh"
        ;;
        
    5)
        echo -e "\n${BLUE}Help: Managing Nix Downloads${NC}"
        echo ""
        echo "The issue: 'nix develop' downloads ~2.8GB which times out in Claude Code."
        echo ""
        echo "Solutions:"
        echo "• Use minimal shell (option 1) for quick testing"
        echo "• Run full downloads outside Claude Code (option 4)"
        echo "• Use mock mode (option 3) for development"
        echo "• Configure binary caches for faster downloads"
        echo ""
        echo "Once downloaded, Nix caches everything - subsequent runs are instant!"
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✨ Ready to develop! Remember: NO PIP! Everything through Nix!${NC}"