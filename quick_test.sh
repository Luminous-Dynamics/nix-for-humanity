#!/bin/bash
# Quick test script to verify Luminous Nix is working

echo "🧪 Testing Luminous Nix Core Commands..."
echo "========================================="

cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix

# Test 1: Help command
echo -e "\n1️⃣ Testing help command..."
poetry run python -m luminous_nix.cli --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Help works"
else
    echo "❌ Help failed"
fi

# Test 2: Version check
echo -e "\n2️⃣ Testing version..."
poetry run python -m luminous_nix.cli --version 2>&1 | grep -q "0.8.3"
if [ $? -eq 0 ]; then
    echo "✅ Version check works (0.8.3)"
else
    echo "❌ Version check failed"
fi

# Test 3: Actual command (dry run)
echo -e "\n3️⃣ Testing 'install firefox' command (dry run)..."
poetry run python -c "
import sys
import os
os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
sys.path.insert(0, 'src')

from luminous_nix.core.engine import NixForHumanityCore
from luminous_nix.core.types import Query

core = NixForHumanityCore()
query = Query(raw_text='install firefox', context={})
response = core.process_query(query)
print(f'✅ Command processed: {response.explanation[:50]}...')
" 2>/dev/null || echo "❌ Command processing failed"

# Test 4: Check if models are available
echo -e "\n4️⃣ Checking AI models..."
if command -v ollama > /dev/null 2>&1; then
    MODEL_COUNT=$(ollama list 2>/dev/null | wc -l)
    if [ $MODEL_COUNT -gt 1 ]; then
        echo "✅ Ollama installed with $((MODEL_COUNT-1)) models"
    else
        echo "⚠️ Ollama installed but no models found"
    fi
else
    echo "⚠️ Ollama not installed (AI features limited)"
fi

# Test 5: Simple Python import test
echo -e "\n5️⃣ Testing core imports..."
poetry run python -c "
from luminous_nix.core import NixForHumanityCore
from luminous_nix.nlp import EnhancedIntentRecognizer
from luminous_nix.executor import NixCommandExecutor
print('✅ All core modules import successfully')
" 2>/dev/null || echo "❌ Import errors found"

echo -e "\n========================================="
echo "📊 Test Summary"
echo "If you see mostly ✅, Luminous Nix is ready!"
echo "If you see ❌, we need to fix those issues first."
echo ""
echo "Next step: Fix any ❌ issues, then launch on HN!"