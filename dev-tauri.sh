#!/usr/bin/env bash
# Development script for Tauri app

set -e

echo "🚀 Starting Nix for Humanity development..."

# Check if we're in nix shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "⚠️  Not in nix shell. Running with nix develop..."
    exec nix develop --command "$0" "$@"
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm ci
fi

# Start Tauri dev
echo "🌟 Starting Tauri development server..."
npm run tauri:dev