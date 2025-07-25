#!/usr/bin/env bash

echo "🌟 NixOS GUI Build Script 🌟"
echo

# Check if we're in nix-shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "⚠️  Not in nix-shell. Entering now..."
    exec nix-shell --run "$0 $@"
fi

echo "✅ In nix-shell environment"
echo

# Check dependencies
echo "🔍 Checking dependencies..."
./test-deps.sh
echo

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf target/ 2>/dev/null
echo

# Install frontend dependencies if needed
if [ ! -d "../node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd .. && npm install && cd src-tauri
fi

# Build the application
echo "🏗️  Building NixOS GUI..."
echo

# First try a check to see if dependencies are OK
echo "Step 1: Checking backend compilation..."
cargo check
if [ $? -ne 0 ]; then
    echo "❌ Backend check failed. Please fix errors above."
    exit 1
fi
echo "✅ Backend check passed!"
echo

# Now try the full Tauri build
echo "Step 2: Building full Tauri application..."
cargo tauri build --debug
if [ $? -ne 0 ]; then
    echo "❌ Tauri build failed."
    echo
    echo "Common issues:"
    echo "- Missing GUI libraries (run in X11/Wayland session)"
    echo "- WebKit2GTK not found (check pkg-config)"
    echo "- Frontend build errors (check ../src/ directory)"
    exit 1
fi

echo
echo "✅ Build successful!"
echo "📍 Debug binary: target/debug/nixos-gui"
echo "📍 Bundle: target/debug/bundle/"
echo
echo "🚀 To run: cargo tauri dev"