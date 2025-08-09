#!/usr/bin/env bash

# Dual Model Setup Script - Mistral-7B + CodeLlama-13B
# For Sacred Trinity power users with 32GB RAM

set -euo pipefail

echo "🌟 Sacred Trinity Dual Model Setup 🌟"
echo "====================================="
echo
echo "This script will configure both:"
echo "• Mistral-7B (6GB) - For rapid development"
echo "• CodeLlama-13B-Instruct (13GB) - For deep technical work"
echo
echo "Total RAM usage: ~20GB when both loaded"
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check system RAM
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
echo -e "${BLUE}System RAM: ${TOTAL_RAM}GB${NC}"

if [ "$TOTAL_RAM" -lt 20 ]; then
    echo -e "${YELLOW}⚠️  Warning: You have ${TOTAL_RAM}GB RAM. Recommended: 20GB+ for both models${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if in right directory
if [ ! -f "flake.nix" ]; then
    echo -e "${RED}❌ Error: Not in Nix for Humanity directory${NC}"
    echo "Please run from: /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
    exit 1
fi

# Enter Nix shell if not already
if [ -z "${IN_NIX_SHELL:-}" ]; then
    echo "Entering Nix development shell..."
    exec nix develop -c "$0" "$@"
fi

# Check Ollama service
echo -e "${YELLOW}🤖 Checking Ollama service...${NC}"
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 5
    
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo -e "${RED}❌ Failed to start Ollama${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Ollama is running${NC}"

# Download models
echo -e "${YELLOW}📥 Setting up models...${NC}"
echo

# Mistral-7B
echo "1. Mistral-7B (Default - Fast responses)"
if ollama list | grep -q "mistral:7b"; then
    echo -e "${GREEN}✅ Already installed${NC}"
else
    echo "Downloading Mistral-7B (~4GB)..."
    ollama pull mistral:7b || exit 1
    echo -e "${GREEN}✅ Mistral-7B ready${NC}"
fi

echo

# CodeLlama-13B-Instruct
echo "2. CodeLlama-13B-Instruct (Deep technical work)"
if ollama list | grep -q "codellama:13b-instruct"; then
    echo -e "${GREEN}✅ Already installed${NC}"
else
    echo "Downloading CodeLlama-13B-Instruct (~7GB)..."
    echo "This will take longer..."
    ollama pull codellama:13b-instruct || exit 1
    echo -e "${GREEN}✅ CodeLlama-13B ready${NC}"
fi

echo

# Test both models
echo -e "${YELLOW}🧪 Testing both models...${NC}"
echo

echo "Testing Mistral-7B (fast)..."
START_TIME=$(date +%s.%N)
MISTRAL_TEST=$(ask-nix-guru "What is NixOS?" 2>/dev/null | head -3)
END_TIME=$(date +%s.%N)
MISTRAL_TIME=$(echo "$END_TIME - $START_TIME" | bc)
echo -e "${GREEN}✅ Mistral responded in ${MISTRAL_TIME}s${NC}"

echo
echo "Testing CodeLlama-13B (detailed)..."
START_TIME=$(date +%s.%N)
CODELLAMA_TEST=$(NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru "What is NixOS?" 2>/dev/null | head -3)
END_TIME=$(date +%s.%N)
CODELLAMA_TIME=$(echo "$END_TIME - $START_TIME" | bc)
echo -e "${GREEN}✅ CodeLlama responded in ${CODELLAMA_TIME}s${NC}"

# Create enhanced shell configuration
echo
echo -e "${YELLOW}📝 Creating enhanced configuration...${NC}"

cat > ~/.nix-guru-dual << 'EOF'
# Dual Model Configuration for Sacred Trinity

# Quick aliases for model switching
alias guru='ask-nix-guru'                    # Default (Mistral-7B)
alias guru-fast='ask-nix-guru'               # Explicit fast mode
alias guru-detail='NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru'
alias guru-code='NIX_GURU_MODEL=deepseek-coder:6.7b ask-nix-guru'

# Function for easy model selection
nix-guru() {
    local model="${1}"
    if [[ "$model" == "fast" || "$model" == "mistral" ]]; then
        shift
        ask-nix-guru "$@"
    elif [[ "$model" == "detail" || "$model" == "code" || "$model" == "codellama" ]]; then
        shift
        NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru "$@"
    else
        # No model specified, use default
        ask-nix-guru "$@"
    fi
}

# Compare responses from both models
compare-models() {
    local question="$*"
    echo "🔄 Comparing model responses for: $question"
    echo
    
    echo "=== Mistral-7B (Fast) ==="
    time ask-nix-guru "$question" | head -15
    echo
    
    echo "=== CodeLlama-13B (Detailed) ==="
    time NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru "$question" | head -15
    echo
}

# Smart model selection based on question type
smart-guru() {
    local question="$*"
    
    # Keywords that suggest need for detailed response
    if echo "$question" | grep -qiE "(module|derivation|overlay|flake|explain|how does|why|debug|error|complex)"; then
        echo "🧠 Using CodeLlama for detailed response..."
        NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru "$question"
    else
        echo "🚀 Using Mistral for quick response..."
        ask-nix-guru "$question"
    fi
}

# Session management
export GURU_SESSION_MODEL="${GURU_SESSION_MODEL:-mistral:7b}"

# Set session to detailed mode
detail-mode() {
    export NIX_GURU_MODEL=codellama:13b-instruct
    export GURU_SESSION_MODEL=codellama:13b-instruct
    echo "📚 Switched to detailed mode (CodeLlama-13B)"
}

# Set session to fast mode (default)
fast-mode() {
    unset NIX_GURU_MODEL
    export GURU_SESSION_MODEL=mistral:7b
    echo "🚀 Switched to fast mode (Mistral-7B)"
}

# Show current mode
guru-mode() {
    echo "Current model: ${NIX_GURU_MODEL:-mistral:7b}"
    echo "Session default: $GURU_SESSION_MODEL"
}

# Preload both models for instant switching
preload-models() {
    echo "Preloading models for instant switching..."
    ask-nix-guru "test" >/dev/null 2>&1 &
    NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru "test" >/dev/null 2>&1 &
    wait
    echo "✅ Both models ready for instant use"
}
EOF

# Create workflow examples
cat > dual-model-workflows.md << 'EOF'
# Dual Model Workflows

## Quick Reference

```bash
# Default (Mistral - fast)
guru "How do I install Firefox?"

# Detailed (CodeLlama)
guru-detail "Explain Nix derivations with examples"

# Smart selection (auto-chooses based on question)
smart-guru "What is a package?"        # → Mistral
smart-guru "Debug this flake error"    # → CodeLlama

# Compare both
compare-models "What are Nix channels?"

# Session modes
detail-mode  # All queries use CodeLlama
fast-mode    # All queries use Mistral (default)
```

## Workflow Examples

### 1. Active Coding Session
```bash
# Quick syntax checks with Mistral
guru "systemd service syntax"
guru "How to add user to group"

# Complex implementation with CodeLlama
guru-detail "Create a NixOS module for a web service with nginx"
```

### 2. Learning Session
```bash
detail-mode  # Switch to CodeLlama for the session

guru "Explain Nix store and derivations"
guru "How do overlays modify packages"
guru "What's the difference between buildInputs and nativeBuildInputs"

fast-mode  # Back to normal
```

### 3. Debugging Session
```bash
# Quick check
guru "Common causes of infinite recursion"

# Detailed debugging
guru-detail "Debug: error: infinite recursion encountered at /etc/nixos/configuration.nix:45:10"

# Back to quick iterations
guru "Show me the fixed version"
```

### 4. Architecture Planning
```bash
# Use CodeLlama for comprehensive design
guru-detail "Design a multi-service NixOS configuration with microservices"

# Quick clarifications with Mistral
guru "Syntax for imports in configuration.nix"
```

## Performance Guide

| Task | Model | Time | Use When |
|------|-------|------|----------|
| Syntax check | Mistral | 2-3s | Coding actively |
| Quick how-to | Mistral | 3-5s | Need immediate answer |
| Error meaning | Mistral | 2-4s | Quick debugging |
| Full examples | CodeLlama | 5-8s | Learning something new |
| Module creation | CodeLlama | 6-10s | Building features |
| Architecture | CodeLlama | 8-12s | Planning phase |

## Tips

1. **Stay in flow**: Use Mistral by default
2. **Go deep when needed**: Switch to CodeLlama for complex work
3. **Preload for speed**: Run `preload-models` at session start
4. **Save good answers**: CodeLlama responses are worth keeping
5. **Know your RAM**: Monitor with `htop` if running heavy apps

## Resource Usage

- Mistral only: ~6GB RAM
- CodeLlama only: ~13GB RAM  
- Both loaded: ~20GB RAM
- With IDE + Browser: ~28GB total

Plenty of headroom with 32GB!
EOF

echo -e "${GREEN}✅ Created dual-model-workflows.md${NC}"

# Add to shell RC
echo
echo -e "${YELLOW}🔧 Updating shell configuration...${NC}"

# Detect shell
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.profile"
fi

# Add source line if not present
if ! grep -q "source ~/.nix-guru-dual" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Sacred Trinity Dual Model Configuration" >> "$SHELL_RC"
    echo "[ -f ~/.nix-guru-dual ] && source ~/.nix-guru-dual" >> "$SHELL_RC"
    echo -e "${GREEN}✅ Updated $SHELL_RC${NC}"
else
    echo "✅ Shell already configured"
fi

# Summary
echo
echo "========================================="
echo -e "${GREEN}🎉 Dual Model Setup Complete! 🎉${NC}"
echo "========================================="
echo
echo "You now have:"
echo "✅ Mistral-7B - Lightning fast responses (default)"
echo "✅ CodeLlama-13B - Deep technical knowledge"
echo "✅ Smart aliases and functions"
echo "✅ Workflow documentation"
echo
echo "Quick start:"
echo -e "${BLUE}source ~/.nix-guru-dual${NC}  # Load new commands"
echo -e "${BLUE}guru-mode${NC}               # Check current model"
echo -e "${BLUE}compare-models \"What is a flake?\"${NC}"
echo
echo "Aliases:"
echo "• guru          → Quick (Mistral)"
echo "• guru-detail   → Detailed (CodeLlama)"
echo "• smart-guru    → Auto-select based on question"
echo "• detail-mode   → Switch session to CodeLlama"
echo "• fast-mode     → Switch session to Mistral"
echo
echo -e "${GREEN}Two models, one workflow: Speed when you need it, depth when it matters! 🌊${NC}"

# Keep Ollama running if we started it
if [ ! -z "${OLLAMA_PID:-}" ]; then
    echo
    echo "Note: Ollama running in background (PID: $OLLAMA_PID)"
fi