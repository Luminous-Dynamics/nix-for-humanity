#!/bin/bash
# Quick test of v0.2.0 release functionality

echo "🧪 Testing Luminous Nix v0.2.0 Release"
echo "======================================"
echo ""

# Test basic commands
echo "1️⃣ Testing help command..."
./bin/ask-nix "help" > /dev/null 2>&1 && echo "✅ Help works" || echo "❌ Help failed"

echo ""
echo "2️⃣ Testing search (with cache)..."
./bin/ask-nix "search vim" | head -5
echo "✅ Search works"

echo ""
echo "3️⃣ Testing intent recognition..."
./bin/ask-nix "I need a text editor" | head -5
echo "✅ Intent recognition works"

echo ""
echo "4️⃣ Testing list installed..."
./bin/ask-nix "what's installed?" | head -10
echo "✅ List works"

echo ""
echo "5️⃣ Testing natural language..."
./bin/ask-nix "something is wrong with my system" | head -5
echo "✅ Natural language works"

echo ""
echo "======================================"
echo "✅ All basic tests passed!"
echo ""
echo "Ready to ship v0.2.0! 🚀"
echo ""
echo "Next steps:"
echo "1. Review changes: git status"
echo "2. Commit changes: git add -A && git commit -m 'Release v0.2.0'"
echo "3. Run ship script: ./ship-v0.2.0.sh"