#!/bin/bash
# Quick test runner for persona feedback testing

echo "🎭 Nix for Humanity - Persona Feedback Testing"
echo "=============================================="
echo ""
echo "This script will test the system with all 10 personas."
echo "It will take approximately 5-10 minutes to complete."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

# Check if ask-nix exists
if ! command -v ask-nix &> /dev/null && [ ! -f "./bin/ask-nix" ]; then
    echo "❌ Error: ask-nix not found!"
    echo "Please ensure ask-nix is installed or available in ./bin/"
    exit 1
fi

# Create test results directory
mkdir -p test-results/persona-feedback

# Run the persona feedback test
echo ""
echo "🚀 Starting persona testing..."
python3 scripts/persona-feedback-test.py

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Testing complete!"
    echo ""
    echo "📊 Results saved in:"
    echo "   test-results/persona-feedback/"
    echo ""
    echo "📈 Next steps:"
    echo "1. Review the markdown report for human-readable insights"
    echo "2. Check the JSON report for detailed metrics"
    echo "3. Focus on personas with <70% success rate"
    echo "4. Implement the HIGH priority improvements first"
else
    echo ""
    echo "❌ Testing failed!"
    echo "Please check the error messages above."
    exit 1
fi