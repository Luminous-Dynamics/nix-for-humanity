#!/usr/bin/env bash
# 🌟 Luminous Nix Installer
# Transform NixOS from complexity to conversation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check requirements
check_requirements() {
    print_header "Checking System Requirements"
    
    # Check for Nix
    if command -v nix &> /dev/null; then
        print_success "Nix package manager found"
    else
        print_error "Nix not found. Please install Nix first:"
        echo "  curl -L https://nixos.org/nix/install | sh"
        exit 1
    fi
    
    # Check for Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 not found. Installing..."
        nix-env -iA nixpkgs.python3
    fi
    
    # Check for Git
    if command -v git &> /dev/null; then
        print_success "Git found"
    else
        print_warning "Git not found. Installing..."
        nix-env -iA nixpkgs.git
    fi
    
    echo ""
}

# Install Poetry
install_poetry() {
    if command -v poetry &> /dev/null; then
        print_success "Poetry already installed"
    else
        print_info "Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
        print_success "Poetry installed"
    fi
}

# Clone repository
clone_repository() {
    print_header "Setting Up Luminous Nix"
    
    INSTALL_DIR="$HOME/luminous-nix"
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Installation directory already exists"
        read -p "Remove existing installation? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            cd "$INSTALL_DIR"
            git pull
            print_success "Updated existing installation"
            return
        fi
    fi
    
    print_info "Cloning repository..."
    git clone https://github.com/Luminous-Dynamics/luminous-nix.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    print_success "Repository cloned to $INSTALL_DIR"
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    print_info "Installing Python dependencies with Poetry..."
    poetry install --no-interaction
    print_success "Python dependencies installed"
    
    # Automatic voice dependency installation
    print_info "Checking for voice dependencies..."
    
    # Check if voice deps are already installed
    if poetry show SpeechRecognition &>/dev/null && poetry show pyttsx3 &>/dev/null; then
        print_success "Voice dependencies already installed"
    else
        print_info "Installing voice dependencies automatically..."
        
        # Install system dependencies first if on NixOS
        if [ -f /etc/nixos/configuration.nix ]; then
            print_info "Detected NixOS - installing system audio libraries..."
            nix-shell -p portaudio alsaLib --run "echo 'Audio libraries available'"
        fi
        
        # Install Python voice packages
        poetry add SpeechRecognition pyttsx3 pyaudio --quiet || {
            print_warning "Could not install pyaudio - trying without it"
            poetry add SpeechRecognition pyttsx3 --quiet
        }
        
        # Verify installation
        if poetry show SpeechRecognition &>/dev/null; then
            print_success "Voice dependencies installed successfully!"
            print_info "Voice interface is now available with --voice flag"
        else
            print_warning "Voice dependencies could not be installed automatically"
            print_info "You can manually install later with: poetry add SpeechRecognition pyttsx3 pyaudio"
        fi
    fi
    
    echo ""
}

# Setup AI (optional)
setup_ai() {
    print_header "AI Integration Setup (Optional)"
    
    read -p "Install AI integration (Ollama)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v ollama &> /dev/null; then
            print_success "Ollama already installed"
        else
            print_info "Installing Ollama..."
            curl -fsSL https://ollama.com/install.sh | sh
            print_success "Ollama installed"
        fi
        
        print_info "Starting Ollama service..."
        ollama serve &> /dev/null &
        sleep 2
        
        print_info "Downloading AI model (this may take 10-15 minutes)..."
        ollama pull mistral:7b
        print_success "AI model downloaded"
        
        echo "export LUMINOUS_AI_ENABLED=true" >> ~/.bashrc
        print_success "AI integration enabled"
    fi
    
    echo ""
}

# Create shortcuts
create_shortcuts() {
    print_header "Creating Command Shortcuts"
    
    # Create bin directory if it doesn't exist
    mkdir -p "$HOME/.local/bin"
    
    # Create ask-nix shortcut
    cat > "$HOME/.local/bin/ask-nix" << 'EOF'
#!/usr/bin/env bash
SCRIPT_DIR="$HOME/luminous-nix"
cd "$SCRIPT_DIR"
poetry run python bin/ask-nix "$@"
EOF
    
    chmod +x "$HOME/.local/bin/ask-nix"
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    print_success "Command 'ask-nix' available globally"
    echo ""
}

# Test installation
test_installation() {
    print_header "Testing Installation"
    
    print_info "Running functionality tests..."
    cd "$HOME/luminous-nix"
    
    # Basic test
    if poetry run python -c "from luminous_nix.interfaces.cli import UnifiedNixAssistant; print('✅ Core imports work')" 2>/dev/null; then
        print_success "Core modules working"
    else
        print_error "Core modules failed to import"
    fi
    
    # Test basic command
    if ask-nix "help" &> /dev/null; then
        print_success "Basic commands working"
    else
        print_warning "Basic commands may need configuration"
    fi
    
    # Run comprehensive test
    if [ -f "test_all_functionality.py" ]; then
        print_info "Running comprehensive tests..."
        poetry run python test_all_functionality.py
    fi
    
    echo ""
}

# Print usage instructions
print_usage() {
    print_header "🎉 Installation Complete!"
    
    echo "Luminous Nix is now installed and ready to use!"
    echo ""
    echo "Quick Start Commands:"
    echo "  ask-nix 'help'                    # Show available commands"
    echo "  ask-nix 'search text editor'      # Search for packages"
    echo "  ask-nix 'install firefox'         # Install a package"
    echo "  ask-nix 'list installed'          # Show installed packages"
    echo ""
    
    if [ -f "$HOME/.bashrc" ]; then
        echo "Please run: source ~/.bashrc"
        echo "Or start a new terminal for changes to take effect"
    fi
    
    echo ""
    echo "Documentation:"
    echo "  README: $HOME/luminous-nix/README.md"
    echo "  Voice Setup: $HOME/luminous-nix/VOICE_SETUP.md"
    echo "  AI Setup: $HOME/luminous-nix/AI_SETUP.md"
    echo ""
    echo "Thank you for installing Luminous Nix!"
    echo "Transform NixOS from complexity to conversation 🌟"
}

# Main installation flow
main() {
    clear
    print_header "🌟 Luminous Nix Installer v0.3.2"
    echo "Natural Language Interface for NixOS"
    echo ""
    
    check_requirements
    install_poetry
    clone_repository
    install_dependencies
    setup_ai
    create_shortcuts
    test_installation
    print_usage
}

# Run installer
main