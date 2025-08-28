#!/usr/bin/env bash
# Detect and setup Ollama for Luminous Nix

set -e

echo "🤖 Detecting Ollama Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if ollama is installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    
    # Check version
    OLLAMA_VERSION=$(ollama version 2>/dev/null || echo "unknown")
    echo "   Version: $OLLAMA_VERSION"
    
    # Check if ollama is running
    if ollama list &>/dev/null; then
        echo "✅ Ollama service is running"
        
        # List available models
        echo ""
        echo "📦 Available models:"
        ollama list | head -10
        
    else
        echo "⚠️  Ollama is installed but not running"
        echo ""
        echo "To start Ollama:"
        echo "  ollama serve"
        echo ""
        echo "Or in background:"
        echo "  nohup ollama serve > /dev/null 2>&1 &"
    fi
    
else
    echo "❌ Ollama is not installed"
    echo ""
    echo "📋 Installation Options:"
    echo ""
    echo "Option 1: Install on NixOS (recommended):"
    echo "  nix-env -iA nixpkgs.ollama"
    echo ""
    echo "Option 2: Official installer:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    echo "Option 3: Add to configuration.nix:"
    echo "  services.ollama.enable = true;"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for recommended models
echo ""
echo "🎯 Checking for NixOS-optimized models..."

RECOMMENDED_MODELS=(
    "mistral:7b"      # General purpose
    "qwen:0.5b"       # Ultra-fast tiny model
    "phi:2.7b"        # Good balance
)

if command -v ollama &> /dev/null && ollama list &>/dev/null; then
    INSTALLED_MODELS=$(ollama list | tail -n +2 | awk '{print $1}' | cut -d':' -f1)
    
    for model in "${RECOMMENDED_MODELS[@]}"; do
        MODEL_NAME=$(echo $model | cut -d':' -f1)
        if echo "$INSTALLED_MODELS" | grep -q "^$MODEL_NAME"; then
            echo "✅ $model - Installed"
        else
            echo "⚠️  $model - Not installed"
            echo "   Install with: ollama pull $model"
        fi
    done
else
    echo "⚠️  Cannot check models (Ollama not running)"
fi

echo ""
echo "💡 Quick Test:"
echo "  ollama run qwen:0.5b 'What is NixOS?'"
echo ""
echo "🎉 To enable AI features in Luminous Nix:"
echo "  export LUMINOUS_AI_ENABLED=true"
echo "  luminous-nix 'explain NixOS to me'"