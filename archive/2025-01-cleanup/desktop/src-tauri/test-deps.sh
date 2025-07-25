#!/usr/bin/env bash

echo "🔍 Testing Tauri dependencies..."
echo

echo "1. Testing pkg-config:"
pkg-config --version || echo "❌ pkg-config not found"
echo

echo "2. Testing critical libraries:"
pkg-config --exists webkit2gtk-4.1 && echo "✅ WebKit2GTK 4.1 found" || echo "❌ WebKit2GTK 4.1 missing"
pkg-config --exists gtk+-3.0 && echo "✅ GTK3 found" || echo "❌ GTK3 missing"
pkg-config --exists libsoup-3.0 && echo "✅ libsoup 3.0 found" || echo "❌ libsoup 3.0 missing"
pkg-config --exists openssl && echo "✅ OpenSSL found" || echo "❌ OpenSSL missing"
echo

echo "3. Checking Rust toolchain:"
rustc --version || echo "❌ rustc not found"
cargo --version || echo "❌ cargo not found"
echo

echo "4. Testing cargo build (backend only):"
cd /srv/luminous-dynamics/11-meta-consciousness/nixos-gui/src-tauri
echo "Building backend..."
cargo check 2>&1 | tail -20
echo

echo "✨ Dependency test complete!"