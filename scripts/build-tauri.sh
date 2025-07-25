#!/usr/bin/env bash
# Build script for Tauri app

set -e

echo "🔨 Building Nix for Humanity..."

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

# Build frontend
echo "🎨 Building frontend..."
npm run build:frontend

# Build Rust backend
echo "🦀 Building Tauri app..."
cd src-tauri
cargo build --release
cd ..

echo "✅ Build complete! Run with: ./src-tauri/target/release/nix-for-humanity"