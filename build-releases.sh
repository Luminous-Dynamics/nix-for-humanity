#!/usr/bin/env bash
# Build standalone releases for v0.3.0 and v0.3.1

set -e

echo "🚀 Building Luminous Nix Releases..."
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create dist directory
mkdir -p dist-releases

# Function to build a release
build_release() {
    local version=$1
    echo -e "${BLUE}Building v${version}...${NC}"
    
    # Update version in pyproject.toml
    sed -i "s/version = \".*\"/version = \"${version}\"/" pyproject.toml
    
    # Build Python package
    poetry build
    
    # Create standalone directory
    mkdir -p dist-releases/luminous-nix-v${version}
    
    # Copy essential files
    cp -r bin dist-releases/luminous-nix-v${version}/
    cp -r src dist-releases/luminous-nix-v${version}/
    cp pyproject.toml dist-releases/luminous-nix-v${version}/
    cp README.md dist-releases/luminous-nix-v${version}/
    cp LICENSE dist-releases/luminous-nix-v${version}/
    
    # Create launcher script
    cat > dist-releases/luminous-nix-v${version}/luminous-nix << 'EOF'
#!/usr/bin/env bash
# Luminous Nix Launcher
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"
exec python3 "${SCRIPT_DIR}/bin/ask-nix" "$@"
EOF
    chmod +x dist-releases/luminous-nix-v${version}/luminous-nix
    
    # Create tarball
    cd dist-releases
    tar -czf luminous-nix-v${version}-standalone.tar.gz luminous-nix-v${version}
    cd ..
    
    # Create wheel package name for PyPI
    cp dist/luminous_nix-${version}-py3-none-any.whl dist-releases/
    
    echo -e "${GREEN}✅ Built v${version}${NC}"
    echo "  - Standalone: dist-releases/luminous-nix-v${version}-standalone.tar.gz"
    echo "  - Wheel: dist-releases/luminous_nix-${version}-py3-none-any.whl"
    echo ""
}

# Build v0.3.0
build_release "0.3.0"

# Build v0.3.1
build_release "0.3.1"

# Final summary
echo -e "${GREEN}🎉 All releases built successfully!${NC}"
echo ""
echo "Release artifacts:"
ls -lh dist-releases/*.tar.gz
echo ""
echo "PyPI wheels:"
ls -lh dist-releases/*.whl
echo ""
echo "Next steps:"
echo "1. Create GitHub releases with these files"
echo "2. Upload wheels to PyPI"
echo "3. Announce on HackerNews and Reddit"