#!/usr/bin/env bash

# 🚀 Nix for Humanity - One Command Setup

set -e

echo "🌟 Setting up Nix for Humanity (Tauri Edition)"
echo "============================================="

# Check if we're in nix-shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "📦 Entering Nix shell with all dependencies..."
    exec nix-shell --run "$0"
fi

echo "✅ Nix shell active - all system dependencies ready!"

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
else
    echo "✅ npm dependencies already installed"
fi

# Check Rust
echo "🦀 Checking Rust installation..."
rustc --version
cargo --version

# Build Rust dependencies
echo "🔨 Building Rust dependencies..."
cd src-tauri
cargo check
cd ..

echo ""
echo "✨ Setup complete! You can now run:"
echo ""
echo "  npm run tauri:dev"
echo ""
echo "This will start the app with hot-reload for both"
echo "frontend (TypeScript) and backend (Rust)."
echo ""
echo "🎉 Happy coding!"