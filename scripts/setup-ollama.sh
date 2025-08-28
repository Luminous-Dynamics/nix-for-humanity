#!/usr/bin/env bash
# Setup Ollama integration for enhanced AI features

set -e

echo "🤖 Setting up Ollama LLM Integration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📦 Ollama not found. Would you like to install it?"
    echo "   Run: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🚀 Starting Ollama service..."
    ollama serve &
    sleep 3
fi

# Check for suitable models
echo "🔍 Checking available models..."
MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')

if [ -z "$MODELS" ]; then
    echo "📥 No models found. Installing recommended model..."
    echo "   This will download ~4GB. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ollama pull mistral:7b-instruct
    else
        echo "⚠️ Skipping model download. You can run later:"
        echo "   ollama pull mistral:7b-instruct"
    fi
else
    echo "✅ Found models:"
    echo "$MODELS" | sed 's/^/   - /'
fi

# Test the integration
echo ""
echo "🧪 Testing Ollama integration..."
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from luminous_nix.ai.ollama_client import OllamaClient
    client = OllamaClient()
    if client.is_available():
        print('✅ Ollama integration working!')
        response = client.complete('What is NixOS in one sentence?')
        print(f'🤖 Test response: {response[:100]}...')
    else:
        print('⚠️ Ollama not available')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "📝 To enable Ollama in Luminous Nix:"
echo "   export LUMINOUS_AI_ENABLED=true"
echo "   export LUMINOUS_AI_MODEL=mistral:7b-instruct"
echo ""
echo "✨ Ollama integration ready!"