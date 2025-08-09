#!/usr/bin/env bash

# Fix Dependencies for Nix for Humanity Testing
# Happy Birthday Edition! 🎂

set -e

echo "🎉 Fixing dependencies for Nix for Humanity testing..."
echo "This will set up a proper Python environment with all dependencies."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in nix-for-humanity directory!"
    echo "Please run from: /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
    exit 1
fi

# Option 1: Use Poetry (if available)
if command -v poetry &> /dev/null; then
    echo "📦 Poetry found! Installing dependencies..."
    poetry install --with dev,test,tui,voice,web,ml,advanced
    echo "✅ Dependencies installed with Poetry!"
    echo ""
    echo "To run tests:"
    echo "  poetry run python run_tests.py"
    echo "  poetry run pytest tests/"
    exit 0
fi

# Option 2: Use pip with virtual environment
echo "📦 Poetry not found. Creating virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies from pyproject.toml
echo "📥 Installing core dependencies..."
pip install requests click colorama pyyaml

echo "📥 Installing TUI dependencies..."
pip install textual rich

echo "📥 Installing test dependencies..."
pip install pytest pytest-cov pytest-asyncio pytest-timeout

echo "📥 Installing ML dependencies..."
pip install sentence-transformers scikit-learn numpy

echo "📥 Installing voice dependencies (optional)..."
pip install SpeechRecognition pyaudio || echo "⚠️  Voice dependencies optional, skipping..."

echo "📥 Installing additional dependencies..."
pip install python-dateutil

# Create a simple test runner script
cat > test-with-deps.sh << 'EOF'
#!/usr/bin/env bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "🧪 Running tests with proper dependencies..."
python run_tests.py "$@"
EOF

chmod +x test-with-deps.sh

echo ""
echo "✅ Dependencies fixed! 🎉"
echo ""
echo "To run tests:"
echo "  ./test-with-deps.sh                    # Run all tests"
echo "  ./test-with-deps.sh test_knowledge     # Run specific test"
echo ""
echo "Or activate the environment manually:"
echo "  source venv/bin/activate"
echo "  python run_tests.py"
echo ""
echo "Happy Birthday! 🎂 May your tests pass and your code be bug-free!"