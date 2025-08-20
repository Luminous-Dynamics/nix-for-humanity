#!/usr/bin/env bash
# Test if Tauri app can start

echo "🧪 Testing Tauri startup..."

# Enter nix shell if not already in it
if [ -z "$IN_NIX_SHELL" ]; then
    echo "⚠️  Entering nix shell..."
    exec nix develop --command "$0" "$@"
fi

# Check Rust
echo "Rust version: $(rustc --version)"

# Check Node
echo "Node version: $(node --version)"

# Check for Tauri dependencies
echo ""
echo "Checking Tauri dependencies..."
pkg-config --exists webkit2gtk-4.0 && echo "✅ WebKit2GTK found" || echo "❌ WebKit2GTK missing"
pkg-config --exists libsoup-2.4 && echo "✅ libsoup found" || echo "❌ libsoup missing"

# Try to build just the Rust part
echo ""
echo "Building Rust backend..."
cd src-tauri
cargo check
cd ..

echo ""
echo "✅ Basic checks complete!"