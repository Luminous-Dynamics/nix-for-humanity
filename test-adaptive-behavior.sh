#!/usr/bin/env bash
# Test the adaptive consciousness behavior

echo "🌊 Testing Adaptive Consciousness in Luminous Nix"
echo "=================================================="
echo
echo "This demonstrates how the system adapts to different users"
echo "without requiring explicit persona selection."
echo

# Test 1: Novice user
echo "📚 Test 1: First-time user asking basic question"
echo "Command: ask-nix 'how do I install a package?'"
poetry run ask-nix 'how do I install a package?' --dry-run
echo

# Test 2: Continuation (should detect dialogue mode)
echo "💬 Test 2: Continuing conversation"
echo "Command: ask-nix 'tell me more about that'"
poetry run ask-nix 'tell me more about that' --dry-run
echo

# Test 3: Error scenario (should offer learning if user is ready)
echo "🥋 Test 3: Error learning opportunity"
echo "Command: ask-nix 'error: attribute missing'"
poetry run ask-nix 'error: attribute missing' --dry-run
echo

# Test 4: Advanced user (after multiple interactions)
echo "🌟 Test 4: Advanced user seeking deep understanding"
echo "Command: ask-nix 'explain why NixOS uses symlinks for everything'"
poetry run ask-nix 'explain why NixOS uses symlinks for everything' --dry-run
echo

echo "✨ Notice how the responses adapt without selecting any persona!"
echo "The system learns from interaction patterns and adjusts naturally."