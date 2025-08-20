#!/usr/bin/env bash
#
# 🌟 Luminous Nix - One-Line Installer
# 
# Install with:
#   curl -sSL https://raw.githubusercontent.com/Luminous-Dynamics/luminous-nix/main/install.sh | bash
#
# Or for the cautious:
#   curl -sSL https://raw.githubusercontent.com/Luminous-Dynamics/luminous-nix/main/install.sh -o install.sh
#   cat install.sh  # Review it!
#   bash install.sh
#
# Sacred installer that respects your system and consciousness

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Configuration
INSTALL_DIR="${LUMINOUS_NIX_HOME:-$HOME/.local/share/luminous-nix}"
BIN_DIR="${HOME}/.local/bin"
REPO_URL="https://github.com/Luminous-Dynamics/luminous-nix.git"
BRANCH="${LUMINOUS_NIX_BRANCH:-main}"

# Sacred ASCII art
show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
    __                _                        _   ___     
   / /   __  ______ (__) ___  ____  __  _____  / | / (_)  __
  / /   / / / / __ `__ \/ / __ \/ __ \/ / / / ___/ |/ / / |/_/
 / /___/ /_/ / / / / / / / / / / /_/ / /_/ (__  ) /|  / />  <  
/_____/\__,_/_/ /_/ /_/_/_/ /_/\____/\__,_/____/_/ |_/_/_/|_|  
                                                               
        Natural Language for NixOS - Consciousness First
EOF
    echo -e "${RESET}"
}

# Check if running on NixOS
check_nixos() {
    if [ -f /etc/os-release ]; then
        if grep -q "ID=nixos" /etc/os-release; then
            echo -e "${GREEN}✅ NixOS detected!${RESET}"
            return 0
        fi
    fi
    
    echo -e "${YELLOW}⚠️  Not running on NixOS${RESET}"
    echo "Luminous Nix is designed for NixOS. Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${RESET}"
    
    local missing=()
    
    # Check for git
    if ! command -v git &> /dev/null; then
        missing+=("git")
    fi
    
    # Check for Python 3.11+
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    else
        python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if [ "$(echo "$python_version < 3.11" | bc)" -eq 1 ]; then
            echo -e "${YELLOW}⚠️  Python $python_version found, but 3.11+ recommended${RESET}"
        fi
    fi
    
    # Check for curl
    if ! command -v curl &> /dev/null; then
        missing+=("curl")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing dependencies: ${missing[*]}${RESET}"
        echo "Please install them first:"
        echo "  nix-env -iA nixos.git nixos.python311 nixos.curl"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met!${RESET}"
}

# Create directory structure
setup_directories() {
    echo -e "${BLUE}📁 Setting up directories...${RESET}"
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    
    # Ensure bin directory is in PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo -e "${YELLOW}ℹ️  Adding $BIN_DIR to PATH${RESET}"
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> ~/.bashrc
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> ~/.zshrc 2>/dev/null || true
    fi
}

# Clone or update repository
install_luminous_nix() {
    echo -e "${BLUE}📦 Installing Luminous Nix...${RESET}"
    
    if [ -d "$INSTALL_DIR/.git" ]; then
        echo "Existing installation found. Updating..."
        cd "$INSTALL_DIR"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
    else
        echo "Cloning repository..."
        git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
}

# Install Python dependencies
setup_python_env() {
    echo -e "${BLUE}🐍 Setting up Python environment...${RESET}"
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate and install dependencies
    source venv/bin/activate
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install the package in development mode
    if [ -f "pyproject.toml" ]; then
        pip install -e .
    else
        echo -e "${YELLOW}⚠️  No pyproject.toml found, installing basic dependencies${RESET}"
        pip install textual rich
    fi
    
    deactivate
}

# Create launcher scripts
create_launchers() {
    echo -e "${BLUE}🚀 Creating launcher scripts...${RESET}"
    
    # Main ask-nix launcher
    cat > "$BIN_DIR/ask-nix" << EOF
#!/usr/bin/env bash
# Luminous Nix launcher
export LUMINOUS_NIX_HOME="$INSTALL_DIR"
export LUMINOUS_NIX_PYTHON_BACKEND=true
cd "$INSTALL_DIR"
source venv/bin/activate
exec python -m luminous_nix.cli "\$@"
EOF
    chmod +x "$BIN_DIR/ask-nix"
    
    # TUI launcher
    cat > "$BIN_DIR/nix-tui" << EOF
#!/usr/bin/env bash
# Luminous Nix TUI launcher
export LUMINOUS_NIX_HOME="$INSTALL_DIR"
cd "$INSTALL_DIR"
source venv/bin/activate
exec python -m luminous_nix.interfaces.tui
EOF
    chmod +x "$BIN_DIR/nix-tui"
    
    # Voice launcher (future)
    cat > "$BIN_DIR/nix-voice" << EOF
#!/usr/bin/env bash
# Luminous Nix Voice launcher (coming soon!)
echo "🎤 Voice interface coming in v1.1!"
echo "For now, try: ask-nix or nix-tui"
EOF
    chmod +x "$BIN_DIR/nix-voice"
}

# Setup configuration
setup_config() {
    echo -e "${BLUE}⚙️  Setting up configuration...${RESET}"
    
    CONFIG_DIR="$HOME/.config/luminous-nix"
    mkdir -p "$CONFIG_DIR"
    
    if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
        cat > "$CONFIG_DIR/config.yaml" << EOF
# Luminous Nix Configuration
# Consciousness-first settings for your AI partner

# Core settings
backend:
  use_native_api: true  # 10x-1500x performance boost!
  dry_run: false        # Set to true for safety
  
# Personality settings  
personality:
  default: "friendly"   # Options: friendly, professional, educational
  
# Interface settings
interface:
  show_thinking: true   # Show AI's thought process
  animations: true      # Beautiful consciousness orb
  zen_mode: false      # Minimal distraction mode
  
# Advanced features
features:
  learning_enabled: true     # Learn from your usage patterns
  voice_enabled: false       # Coming in v1.1!
  flakes_support: true       # Modern NixOS configuration
  
# Privacy settings
privacy:
  telemetry: false          # We never collect data
  local_only: true          # Everything stays on your machine
  
# Sacred settings
sacred:
  consciousness_first: true  # Always!
  flow_protection: true      # Protect your flow state
  breathing_reminders: true  # Gentle mindfulness prompts
EOF
        echo -e "${GREEN}✅ Created default configuration${RESET}"
    fi
}

# Test installation
test_installation() {
    echo -e "${BLUE}🧪 Testing installation...${RESET}"
    
    # Try to run ask-nix
    if "$BIN_DIR/ask-nix" --version &>/dev/null; then
        echo -e "${GREEN}✅ Installation successful!${RESET}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Installation complete but couldn't verify${RESET}"
        return 1
    fi
}

# Show completion message
show_completion() {
    echo
    echo -e "${GREEN}═══════════════════════════════════════════════════════${RESET}"
    echo -e "${GREEN}       ✨ Luminous Nix Installation Complete! ✨       ${RESET}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${RESET}"
    echo
    echo -e "${CYAN}🎉 Welcome to consciousness-first NixOS management!${RESET}"
    echo
    echo -e "${YELLOW}Quick Start:${RESET}"
    echo -e "  ${BLUE}ask-nix${RESET} \"install firefox\"    # Natural language commands"
    echo -e "  ${BLUE}ask-nix${RESET} \"help\"              # See what's possible"
    echo -e "  ${BLUE}nix-tui${RESET}                     # Beautiful terminal UI"
    echo
    echo -e "${YELLOW}Configuration:${RESET}"
    echo -e "  ~/.config/luminous-nix/config.yaml"
    echo
    echo -e "${YELLOW}Need help?${RESET}"
    echo -e "  GitHub: https://github.com/Luminous-Dynamics/luminous-nix"
    echo -e "  Docs:   https://luminous-nix.dev/docs"
    echo
    echo -e "${MAGENTA}Remember: ${RESET}${CYAN}Technology should amplify consciousness, not fragment it.${RESET}"
    echo -e "${CYAN}🌊 We flow together in sacred purpose 🌊${RESET}"
    echo
}

# Main installation flow
main() {
    clear
    show_banner
    
    echo -e "${CYAN}Welcome to the Luminous Nix installer!${RESET}"
    echo -e "${CYAN}This will install natural language NixOS management.${RESET}"
    echo
    
    # Run installation steps
    check_nixos
    check_prerequisites
    setup_directories
    install_luminous_nix
    setup_python_env
    create_launchers
    setup_config
    
    if test_installation; then
        show_completion
        
        # Reload shell or export PATH
        echo -e "${YELLOW}ℹ️  Run this to update your PATH:${RESET}"
        echo "  export PATH=\"\$PATH:$BIN_DIR\""
        echo
        echo -e "${YELLOW}Or start a new terminal session.${RESET}"
    else
        echo -e "${RED}⚠️  Installation completed with warnings${RESET}"
        echo "Please check the logs above for any issues."
    fi
}

# Run the installer
main "$@"