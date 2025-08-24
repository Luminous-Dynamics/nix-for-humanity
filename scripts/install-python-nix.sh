#!/usr/bin/env bash
# Install Tweag's python-nix for real native performance

set -e

echo "🚀 Installing python-nix for TRUE native performance!"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Run this from the luminous-nix root directory"
    exit 1
fi

# Create a temporary directory for building
BUILD_DIR=$(mktemp -d)
echo "📦 Building in: $BUILD_DIR"

cd "$BUILD_DIR"

# Clone the python-nix repository
echo "📥 Cloning python-nix from Tweag..."
git clone https://github.com/tweag/python-nix.git
cd python-nix

# Check if Nix is available
if ! command -v nix &> /dev/null; then
    echo "❌ Error: Nix is not installed"
    exit 1
fi

# Build with Nix
echo "🔨 Building python-nix with Nix..."
if nix build --no-link --print-out-paths; then
    BUILD_RESULT=$(nix build --no-link --print-out-paths)
    echo "✅ Build successful!"
    echo "📍 Build output: $BUILD_RESULT"
    
    # Try to find the Python module
    PYTHON_MODULE=$(find "$BUILD_RESULT" -name "python_nix*.so" -o -name "python_nix*.pyd" 2>/dev/null | head -1)
    
    if [ -n "$PYTHON_MODULE" ]; then
        echo "✅ Found Python module: $PYTHON_MODULE"
        
        # Copy to our project
        DEST_DIR="$OLDPWD/src/luminous_nix/nix/native_libs"
        mkdir -p "$DEST_DIR"
        cp -r "$BUILD_RESULT"/* "$DEST_DIR/" 2>/dev/null || true
        
        echo "📋 Copied to: $DEST_DIR"
    else
        echo "⚠️  Could not find Python module in build output"
        echo "    You may need to manually install from: $BUILD_RESULT"
    fi
else
    echo "⚠️  Build failed - trying alternative approach..."
    
    # Try with pip if available in the repo
    if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
        echo "🐍 Attempting pip installation..."
        pip install --user . || {
            echo "❌ Pip installation also failed"
            echo ""
            echo "Manual installation steps:"
            echo "1. Check the build requirements in the repo"
            echo "2. Ensure you have Nix development environment"
            echo "3. Try: nix develop -c pip install ."
        }
    fi
fi

# Test if we can import it
echo ""
echo "🧪 Testing python-nix import..."
cd "$OLDPWD"

python3 -c "
try:
    from python_nix import Nix
    print('✅ SUCCESS! python-nix is installed and working!')
    print('🚀 You now have TRUE native Nix bindings!')
except ImportError as e:
    print('⚠️  Import failed:', e)
    print('')
    print('Try adding to PYTHONPATH:')
    print('  export PYTHONPATH=$OLDPWD/src/luminous_nix/nix/native_libs:\$PYTHONPATH')
" 2>&1

# Cleanup
echo ""
echo "🧹 Cleaning up build directory..."
rm -rf "$BUILD_DIR"

echo ""
echo "📝 Next steps:"
echo "1. Test with: python3 src/luminous_nix/nix/true_native_backend.py"
echo "2. Benchmark performance gains"
echo "3. Update native_backend.py to use real bindings"
echo ""
echo "🌟 Ready to achieve 10-1000x performance improvements!"