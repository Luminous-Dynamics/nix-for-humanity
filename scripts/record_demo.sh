#!/usr/bin/env bash
# 🎬 Demo Recording Script for Luminous Nix
# Creates a 2-minute demo showing the key features

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}🎬 Luminous Nix Demo Recording Script${NC}"
echo -e "${CYAN}══════════════════════════════════════${NC}\n"

# Check if asciinema is installed
if ! command -v asciinema &> /dev/null; then
    echo -e "${YELLOW}Installing asciinema for recording...${NC}"
    nix-shell -p asciinema --run "echo 'Ready'"
fi

# Function to type with delays (simulates human typing)
type_command() {
    echo -ne "${GREEN}$ ${NC}"
    echo -n "$1" | while IFS= read -r -n1 char; do
        echo -n "$char"
        sleep 0.05
    done
    echo
    sleep 1
}

# Function to show output
show_output() {
    echo "$1"
    sleep 2
}

echo -e "${YELLOW}📝 Demo Script (2 minutes)${NC}"
echo "1. Installation (30s)"
echo "2. First-run setup (30s)"
echo "3. Natural language commands (30s)"
echo "4. NixOS Doctor fix (30s)"
echo

echo -n "Ready to start recording? (y/n): "
read START

if [ "$START" != "y" ]; then
    echo "Aborted"
    exit 0
fi

# Start recording
echo -e "\n${GREEN}Starting recording in 3 seconds...${NC}"
sleep 3

cat << 'DEMO_SCRIPT'
#!/usr/bin/env bash
# Luminous Nix Demo - 2 minutes

clear
echo "🌟 Luminous Nix - Natural Language for NixOS"
echo "============================================"
echo
sleep 2

# 1. Show installation (30 seconds)
echo "📦 Installing Luminous Nix..."
echo
echo "$ curl -L https://luminous-nix.sh | sh"
sleep 1
echo "  ✓ Downloading..."
sleep 1
echo "  ✓ Installing dependencies..."
sleep 1
echo "  ✓ Setting up environment..."
sleep 1
echo "  ✅ Installation complete!"
echo
sleep 2

# 2. First-run setup (30 seconds)
echo "🎯 First-time setup..."
echo
echo "$ ask-nix setup"
sleep 1
echo
echo "🌟 Welcome to Luminous Nix!"
echo "Let's get you set up in < 2 minutes"
echo
sleep 2
echo "Step 1: Checking AI Backend"
echo "  ✅ Ollama is installed"
echo
sleep 1
echo "Step 2: Select Model Size"
echo "  1. Nano (300MB) - Ultra-fast"
echo "  2. Mini (1-2GB) - Balanced"
echo "  3. Standard (3-4GB) - Full quality"
echo
echo "Selected: 1 (Nano)"
sleep 2
echo
echo "📥 Downloading qwen:0.5b..."
echo "[████████████████████] 100%"
echo "✅ Model ready!"
echo
sleep 2

# 3. Natural language demos (30 seconds)
clear
echo "✨ Natural Language Commands"
echo "============================="
echo
sleep 1

echo "$ ask-nix \"install firefox\""
sleep 1
echo "🔍 Searching for firefox..."
echo "📦 Found: firefox (Web browser)"
echo "📝 Add to configuration.nix? (y/n): y"
echo "✅ Configuration updated!"
echo
sleep 3

echo "$ ask-nix \"find markdown editor\""
sleep 1
echo "🔍 Analyzing: markdown editor"
echo "📦 Found matches:"
echo "  • obsidian - Knowledge base"
echo "  • typora - Minimal editor"
echo "  • vscode - Full IDE"
echo "  • vim - Terminal editor"
echo
sleep 3

# 4. NixOS Doctor (30 seconds)
echo "$ ask-nix fix"
sleep 1
echo "🩺 Running NixOS System Diagnosis..."
echo "────────────────────────────────────"
echo
echo "📊 System Information:"
echo "  NixOS: 24.05"
echo "  Disk: 87% used"
echo "  Memory: 6.2GB/8GB"
echo
echo "⚠️ Issues Found: 3"
echo
echo "HIGH:"
echo "  • Missing semicolon"
echo "    Line: 42"
echo "  • High disk usage: 87%"
echo
echo "MEDIUM:"
echo "  • NetworkManager not running"
echo
echo "🔧 Apply automatic fixes? y"
sleep 2
echo "✅ Fixed: Missing semicolon"
echo "✅ Fixed: Freed 12GB disk space"
echo "✅ Fixed: Started NetworkManager"
echo
sleep 2

# End
clear
echo "🎉 That's Luminous Nix!"
echo "======================="
echo
echo "• Natural language commands"
echo "• AI-powered diagnostics"
echo "• 2-minute setup"
echo "• 10 adaptive personas"
echo "• Works offline"
echo
echo "Install now:"
echo "curl -L https://luminous-nix.sh | sh"
echo
echo "GitHub: github.com/Luminous-Dynamics/luminous-nix"
echo
echo "Built in 2 weeks with AI for $200/month"
echo "Proving the future of development is here!"
DEMO_SCRIPT

echo
echo -e "${GREEN}✅ Demo script ready!${NC}"
echo
echo "To record the demo:"
echo "1. Run: asciinema rec demo.cast"
echo "2. Execute the commands above"
echo "3. Press Ctrl-D to stop"
echo "4. Convert to GIF: docker run --rm -v \$PWD:/data asciinema/asciicast2gif demo.cast demo.gif"
echo
echo "Or use the script above as a guide for manual recording."