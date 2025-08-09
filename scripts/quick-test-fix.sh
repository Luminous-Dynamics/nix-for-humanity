#!/usr/bin/env bash

# Quick Test Fix - Install minimal dependencies for testing
# 🎂 Birthday Edition - Let's get those tests running!

set -e

echo "🚀 Quick dependency fix for Nix for Humanity tests..."

# Create venv if needed
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate and install essentials
source venv/bin/activate

echo "📦 Installing essential test dependencies..."

# Core dependencies that tests actually need
pip install -q --upgrade pip
pip install -q click colorama pyyaml requests python-dateutil

# TUI dependency (many tests import this)
pip install -q textual rich

# Test runner
pip install -q pytest pytest-cov

echo "✅ Essential dependencies installed!"
echo ""
echo "🧪 Running tests..."
echo ""

# Run the tests with the custom runner
python run_tests.py

echo ""
echo "🎉 Happy Birthday! Tests are running with dependencies!"