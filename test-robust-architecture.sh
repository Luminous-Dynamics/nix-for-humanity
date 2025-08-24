#!/bin/bash

# Test script for the robust architecture (CommandExecutor, ErrorRecovery, ConversationState)

echo "🚀 Testing Robust Architecture Components"
echo "========================================="
echo

# Set up environment
export LUMINOUS_VERBOSE=1
export LUMINOUS_DRY_RUN=true  # Test in dry-run mode
export SKIP_FIRST_RUN=1

# Test 1: Command Execution with Preview
echo "📋 Test 1: Command Execution with Preview"
echo "-----------------------------------------"
./bin/ask-nix "install firefox"
echo

# Test 2: Error Recovery
echo "🔧 Test 2: Error Recovery (intentionally broken package)"
echo "-------------------------------------------------------"
./bin/ask-nix "install nonexistent-package-12345"
echo

# Test 3: Conversation State - Pronoun Resolution
echo "💬 Test 3: Conversation State - Pronoun Resolution"
echo "--------------------------------------------------"
echo "First command: search for browser"
./bin/ask-nix "search browser"
echo
echo "Second command: install it (should resolve 'it' to browser)"
./bin/ask-nix "install it"
echo

# Test 4: Multi-turn Conversation
echo "🔄 Test 4: Multi-turn Conversation"
echo "---------------------------------"
./bin/ask-nix "what packages are installed?"
echo
./bin/ask-nix "search text editor"
echo
./bin/ask-nix "install that"
echo

# Test 5: Rollback Functionality
echo "⏪ Test 5: Rollback Functionality"
echo "---------------------------------"
./bin/ask-nix "rollback to previous"
echo

# Test 6: Command History
echo "📜 Test 6: Command History"
echo "-------------------------"
echo "Checking command history..."
ls -la ~/.local/state/luminous-nix/command_history.json 2>/dev/null && echo "✅ Command history file exists"
echo

# Test 7: Error Classification
echo "🏷️ Test 7: Error Classification"
echo "-------------------------------"
./bin/ask-nix "install package-that-needs-sudo"
echo

# Test 8: Search Cache Performance
echo "⚡ Test 8: Search Cache Performance"
echo "----------------------------------"
echo "First search (may be slow):"
time ./bin/ask-nix "search python"
echo
echo "Second search (should be cached):"
time ./bin/ask-nix "search python"
echo

# Test 9: AI Integration with Architecture
echo "🤖 Test 9: AI Integration (if enabled)"
echo "-------------------------------------"
export LUMINOUS_AI_ENABLED=true
./bin/ask-nix "install a web browser"
echo

# Test 10: Socratic Mode
echo "🤔 Test 10: Socratic Mode"
echo "------------------------"
export LUMINOUS_ASK_MODE=true
./bin/ask-nix "search editor"
echo

echo "✅ Robust Architecture Tests Complete!"
echo
echo "Summary:"
echo "- CommandExecutor: Preview, execute, rollback capabilities"
echo "- ErrorRecovery: Intelligent error handling and suggestions"
echo "- ConversationState: Multi-turn context and pronoun resolution"
echo "- SearchCache: Performance optimization"
echo "- AI Integration: Natural language understanding"
echo
echo "Check ~/.local/state/luminous-nix/ for:"
echo "- command_history.json (command history)"
echo "- conversations/ (conversation sessions)"
echo "- snapshots/ (system snapshots)"
echo "- search_cache.json (cached searches)"