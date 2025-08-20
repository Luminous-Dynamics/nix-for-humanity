#!/usr/bin/env bash
# Run the comprehensive Nix documentation training pipeline

set -e

echo "🚀 Starting Comprehensive Nix Expert Training"
echo "==========================================="
echo ""

# Check if we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required"
    exit 1
fi

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Error: Ollama is required. Please install it first:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

# Install Python dependencies if needed
echo "📦 Checking Python dependencies..."
pip install --quiet --user PyPDF2 beautifulsoup4 nltk requests || {
    echo "⚠️  Failed to install some dependencies. Trying with pip3..."
    pip3 install --quiet --user PyPDF2 beautifulsoup4 nltk requests
}

# Run the comprehensive training pipeline
echo ""
echo "🎓 Running comprehensive training pipeline..."
echo "This will:"
echo "  1. Download Nix documentation (including PhD thesis)"
echo "  2. Process theoretical and practical content"
echo "  3. Create training data in multiple formats"
echo "  4. Build an Ollama model"
echo ""
echo "This may take 30-60 minutes depending on your internet speed."
echo ""

# Ask for confirmation
read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Run the training
python3 train-comprehensive-nix-expert.py

echo ""
echo "✅ Training complete!"
echo ""
echo "🧪 Test your new model:"
echo "   ollama run nix-expert-comprehensive"
echo ""
echo "📚 Example questions to try:"
echo "   - What is a derivation?"
echo "   - How does Nix ensure reproducibility?"
echo "   - What's the difference between channels and flakes?"
echo "   - How do I create a development shell?"
echo ""