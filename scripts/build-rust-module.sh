#!/bin/bash
#
# Build the Rust module with PyO3 bindings
#

set -e

echo "🪨 Building Rust Module for Luminous Nix"
echo "=========================================="

# Navigate to rust directory
cd "$(dirname "$0")/../rust"

# Check for Rust installation
if ! command -v cargo &> /dev/null; then
    echo "❌ Cargo not found. Please install Rust:"
    echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.9" | bc) -eq 1 ]]; then
    echo "❌ Python 3.9+ required for PyO3 abi3"
    exit 1
fi

# Clean previous builds
echo -e "\n🧹 Cleaning previous builds..."
cargo clean

# Build in release mode
echo -e "\n🔨 Building Rust module (release mode)..."
cargo build --release

if [ $? -eq 0 ]; then
    echo -e "\n✅ Build successful!"

    # Find the built library
    LIB_PATH="target/release/libluminous_nix_core.so"
    if [ ! -f "$LIB_PATH" ]; then
        # Try dylib for macOS
        LIB_PATH="target/release/libluminous_nix_core.dylib"
    fi

    if [ -f "$LIB_PATH" ]; then
        # Copy to Python module location
        cp "$LIB_PATH" "luminous_nix_core.so" 2>/dev/null || \
        cp "$LIB_PATH" "luminous_nix_core.pyd" 2>/dev/null || \
        echo "Note: Manual copy may be needed for your platform"

        echo "📦 Library built at: $LIB_PATH"
        echo "📍 Size: $(du -h "$LIB_PATH" | cut -f1)"
    else
        echo "⚠️  Library file not found at expected location"
    fi

    # Run tests
    echo -e "\n🧪 Running Rust tests..."
    cargo test --release

    # Try Python integration test
    echo -e "\n🐍 Testing Python integration..."
    cd ..
    if python3 tests/test_rust_integration.py; then
        echo -e "\n🎉 Rust module integration successful!"
    else
        echo -e "\n⚠️  Python integration test failed (module may need installation)"
        echo "   Try: cd rust && maturin develop"
    fi

else
    echo -e "\n❌ Build failed. Check errors above."
    exit 1
fi

echo -e "\n📝 Next steps:"
echo "  1. Install with maturin: cd rust && maturin develop"
echo "  2. Or use pip: pip install ./rust"
echo "  3. Test: python3 tests/test_rust_integration.py"
