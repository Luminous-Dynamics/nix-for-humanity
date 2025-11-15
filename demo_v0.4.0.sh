#!/bin/bash
# Demo script for Luminous Nix v0.4.0 - AI-Powered Features

echo "🚀 Luminous Nix v0.4.0 - AI-Powered System Intelligence Demo"
echo "============================================================"
echo

# Check version
echo "📌 Version Check:"
poetry run ask-nix --version
echo

# Demo 1: Rollback Intelligence
echo "🔄 Demo 1: Rollback Intelligence"
echo "---------------------------------"
echo "Finding safe rollback point for boot failure..."
poetry run ask-nix rollback analyze "system won't boot" | head -15
echo
echo "Press Enter to continue..."
read

# Demo 2: Storage Optimization
echo "💾 Demo 2: Storage Optimization"
echo "-------------------------------"
echo "Analyzing storage for cleanup opportunities..."
poetry run ask-nix storage analyze | head -20
echo
echo "Press Enter to continue..."
read

# Demo 3: Security Auditing
echo "🔐 Demo 3: Security Auditing"
echo "----------------------------"
echo "Running security audit..."
poetry run ask-nix security audit | head -20
echo
echo "Press Enter to continue..."
read

# Demo 4: JSON Output
echo "📊 Demo 4: JSON Output for Scripting"
echo "------------------------------------"
echo "Getting rollback analysis in JSON format..."
poetry run ask-nix rollback analyze --json | python3 -m json.tool | head -15
echo

echo "✅ Demo Complete!"
echo
echo "Try these commands yourself:"
echo "  poetry run ask-nix rollback --help"
echo "  poetry run ask-nix storage --help"
echo "  poetry run ask-nix security --help"
echo
echo "Full documentation: docs/ADVANCED_FEATURES.md"
