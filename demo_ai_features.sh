#!/usr/bin/env bash
# Demo AI-enhanced features in Luminous Nix

set -e

echo "🤖 Luminous Nix AI Features Demo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Ollama is running
if ! ollama list &>/dev/null; then
    echo "⚠️  Starting Ollama service..."
    nohup ollama serve > /dev/null 2>&1 &
    sleep 2
fi

# Enable AI for this session
export LUMINOUS_AI_ENABLED=true
export LUMINOUS_DRY_RUN=true
export LUMINOUS_SKIP_ONBOARDING=1
export LUMINOUS_SKIP_CONFIRM=true

echo "✅ AI Features Enabled"
echo ""
echo "═══════════════════════════════════════"
echo "1️⃣  Natural Language Understanding"
echo "═══════════════════════════════════════"
echo ""
echo "Command: luminous-nix 'what is NixOS and why should I use it?'"
echo ""
timeout 10 poetry run ask-nix "what is NixOS and why should I use it?" 2>/dev/null | head -20
echo ""

echo "═══════════════════════════════════════"
echo "2️⃣  Smart Package Suggestions"
echo "═══════════════════════════════════════"
echo ""
echo "Command: luminous-nix 'suggest packages for web development'"
echo ""
timeout 10 poetry run ask-nix "suggest packages for web development" 2>/dev/null | head -20
echo ""

echo "═══════════════════════════════════════"
echo "3️⃣  Error Explanations"
echo "═══════════════════════════════════════"
echo ""
echo "Command: luminous-nix 'why does nixos-rebuild fail with no space left?'"
echo ""
timeout 10 poetry run ask-nix "why does nixos-rebuild fail with no space left?" 2>/dev/null | head -20
echo ""

echo "═══════════════════════════════════════"
echo "4️⃣  Context-Aware Help"
echo "═══════════════════════════════════════"
echo ""
echo "Command: luminous-nix 'how do I set up a python development environment?'"
echo ""
timeout 10 poetry run ask-nix "how do I set up a python development environment?" 2>/dev/null | head -20
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 AI Features Demonstration Complete!"
echo ""
echo "💡 To enable AI permanently:"
echo "  1. Add to shell config: export LUMINOUS_AI_ENABLED=true"
echo "  2. Or run: ./scripts/enable-ai.sh"
echo ""
echo "📊 AI Models Used:"
echo "  • qwen:0.5b - Ultra-fast responses"
echo "  • mistral:7b - General knowledge"
echo "  • nix-quick - NixOS-specific help"
echo ""
echo "🔒 Privacy: All AI runs locally - no data leaves your machine!"