#!/usr/bin/env bash
# Test script for AI Licensing Advisor functionality

echo "🤖 Testing AI Licensing Advisor Integration"
echo "=========================================="
echo

# Test basic model queries
echo "1️⃣ Testing model license queries:"
echo "--------------------------------"
./bin/ask-nix-ai-aware "What's the license for Llama 2?"
echo
./bin/ask-nix-ai-aware "Can I use Mistral-7B commercially?"
echo

# Test use case recommendations
echo "2️⃣ Testing use case recommendations:"
echo "-----------------------------------"
./bin/ask-nix-ai-aware "Which AI model should I use for a commercial SaaS?"
echo
./bin/ask-nix-ai-aware "What models are safe for my startup?"
echo

# Test license compatibility
echo "3️⃣ Testing license compatibility:"
echo "--------------------------------"
./bin/ask-nix-ai-aware "Is MIT compatible with GPL?"
echo

# Test problematic models
echo "4️⃣ Testing problematic model warnings:"
echo "--------------------------------------"
./bin/ask-nix-ai-aware "Tell me about YOLO v8 licensing"
echo
./bin/ask-nix-ai-aware "Can I use Stable Diffusion in a proprietary app?"
echo

# Test with different personalities
echo "5️⃣ Testing personality modes:"
echo "----------------------------"
echo "Minimal mode:"
./bin/ask-nix-ai-aware --minimal "What's the license for GPT-2?"
echo
echo "Technical mode:"
./bin/ask-nix-ai-aware --technical "Is AGPL safe for SaaS?"
echo

echo "✅ Test complete!"