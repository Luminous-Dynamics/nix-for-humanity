#!/usr/bin/env bash
# Enable AI features in Luminous Nix

set -e

echo "🤖 Enabling AI Features for Luminous Nix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Ollama is available
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed!"
    echo ""
    echo "Please install Ollama first:"
    echo "  nix-env -iA nixpkgs.ollama"
    echo "  ollama serve  # Start the service"
    exit 1
fi

# Check if Ollama is running
if ! ollama list &>/dev/null; then
    echo "⚠️  Ollama is installed but not running"
    echo ""
    echo "Starting Ollama service..."
    nohup ollama serve > /dev/null 2>&1 &
    sleep 2
fi

# Check for at least one model
MODELS=$(ollama list | tail -n +2 | wc -l)
if [ "$MODELS" -eq 0 ]; then
    echo "📦 No models installed. Installing lightweight model..."
    ollama pull qwen:0.5b
    echo "✅ Lightweight model installed"
fi

# Update shell configuration
SHELL_CONFIG=""
if [ -f ~/.bashrc ]; then
    SHELL_CONFIG=~/.bashrc
elif [ -f ~/.zshrc ]; then
    SHELL_CONFIG=~/.zshrc
fi

if [ -n "$SHELL_CONFIG" ]; then
    # Check if already configured
    if ! grep -q "LUMINOUS_AI_ENABLED" "$SHELL_CONFIG"; then
        echo "" >> "$SHELL_CONFIG"
        echo "# Luminous Nix AI Features" >> "$SHELL_CONFIG"
        echo "export LUMINOUS_AI_ENABLED=true" >> "$SHELL_CONFIG"
        echo "✅ Added to $SHELL_CONFIG"
    else
        echo "✅ Already configured in $SHELL_CONFIG"
    fi
fi

# Set for current session
export LUMINOUS_AI_ENABLED=true

echo ""
echo "🎉 AI Features Enabled!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ What's now available:"
echo "  • Natural language understanding"
echo "  • Smart package suggestions"
echo "  • Error explanations"
echo "  • Context-aware help"
echo ""
echo "🚀 Try these AI-powered commands:"
echo ""
echo '  luminous-nix "explain what NixOS is"'
echo '  luminous-nix "suggest packages for web development"'
echo '  luminous-nix "why is my wifi not working?"'
echo ""
echo "💡 Tips:"
echo "  • AI responses adapt to your skill level"
echo "  • Works offline with local models"
echo "  • Privacy-first: Everything stays on your machine"
echo ""
echo "For current session, AI is already enabled."
echo "For permanent: source $SHELL_CONFIG"