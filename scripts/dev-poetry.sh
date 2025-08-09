#!/usr/bin/env bash
# Fast Python+Poetry development environment
# Combines Nix's reproducibility with Poetry's Python package management

set -e

echo "🐍✨ Starting Python+Poetry Development Environment"
echo "=================================================="
echo "This approach combines:"
echo "  • Nix: System dependencies & Python runtime"
echo "  • Poetry: Python package management & virtual envs"
echo "  • Result: Fast setup with proper dependency isolation"
echo

# Check if we're already in a Poetry environment
if [[ -n "$POETRY_ACTIVE" ]]; then
    echo "✅ Already in Poetry environment"
    exec bash
fi

# Use Nix to provide Python, Poetry, and system dependencies
exec nix-shell -p python313 poetry pkg-config gcc --run "
echo '🌟 Environment Ready!'
echo 'Python: $(python3 --version)'
echo 'Poetry: $(poetry --version)'
echo

# Ensure we're in the right directory
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Install dependencies if needed
if [ ! -d '.venv' ]; then
    echo '📦 Installing dependencies with Poetry...'
    poetry install --with dev --all-extras
    echo '✅ Dependencies installed!'
else
    echo '✅ Dependencies already installed'
fi

echo
echo '🚀 Available commands:'
echo '  poetry run pytest              - Run all tests'
echo '  poetry run pytest --cov       - Run tests with coverage'
echo '  poetry run ask-nix \"help\"      - Test CLI'
echo '  poetry shell                   - Enter Poetry virtual environment'
echo
echo '🧠 For AI Enhancement work:'
echo '  poetry run python -c \"import torch; print(torch.__version__)\"'
echo '  poetry run python -c \"import transformers; print(transformers.__version__)\"'
echo
echo 'Ready to work on AI Enhancement features! 🤖'

# Activate the Poetry environment
exec poetry shell
"