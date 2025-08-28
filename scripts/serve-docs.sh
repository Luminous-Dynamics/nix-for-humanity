#!/usr/bin/env bash
# Serve documentation locally with MkDocs

set -e

echo "🚀 Starting Luminous Nix Documentation Server"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Error: mkdocs.yml not found. Are you in the luminous-nix directory?"
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Error: Poetry is not installed"
    echo "Please install Poetry first: https://python-poetry.org/docs/"
    exit 1
fi

# Check if MkDocs is installed
if ! poetry run mkdocs --version &> /dev/null; then
    echo "📦 Installing MkDocs dependencies..."
    poetry install --with dev
fi

# Create necessary directories if they don't exist
mkdir -p docs/overrides
mkdir -p docs/stylesheets
mkdir -p docs/javascripts
mkdir -p docs/assets

# Start the documentation server
echo ""
echo "📚 Starting documentation server..."
echo "👉 Open your browser to: http://localhost:8000"
echo "📝 Docs will auto-reload when you make changes"
echo "Press Ctrl+C to stop the server"
echo ""

# Run MkDocs with Poetry
poetry run mkdocs serve --dev-addr=0.0.0.0:8000 --livereload