#!/usr/bin/env bash
# Test that development environment provides all dependencies

set -euo pipefail

echo "🧪 Testing development environment..."

# Function to test import
test_import() {
    local module=$1
    local name=${2:-$module}
    
    echo -n "  Testing $name... "
    if python -c "import $module" 2>/dev/null; then
        echo "✅"
        return 0
    else
        echo "❌"
        return 1
    fi
}

# Test Python is available
echo -n "Python version: "
python --version

# Test core dependencies
echo -e "\nCore dependencies:"
test_import click
test_import rich
test_import blessed
test_import textual
test_import pytest

# Test optional dependencies
echo -e "\nOptional dependencies:"
test_import whisper "OpenAI Whisper" || true
test_import piper "Piper TTS" || true
test_import torch "PyTorch" || true

# Test development tools
echo -e "\nDevelopment tools:"
which black >/dev/null 2>&1 && echo "  Black... ✅" || echo "  Black... ❌"
which mypy >/dev/null 2>&1 && echo "  Mypy... ✅" || echo "  Mypy... ❌"
which pytest >/dev/null 2>&1 && echo "  Pytest... ✅" || echo "  Pytest... ❌"

# Test Nix for Humanity imports
echo -e "\nProject imports:"
test_import nix_humanity "Nix for Humanity" || echo "    (Expected if not installed)"

echo -e "\n📋 Environment test complete"
