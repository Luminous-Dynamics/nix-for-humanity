#!/bin/bash
# Install Luminous Nix Intelligence System

echo "Installing Luminous Nix..."

# Check Python version
python3 --version >/dev/null 2>&1 || {
    echo "Error: Python 3 is required"
    exit 1
}

# Install with pip
if [ -f "luminous_nix-*.whl" ]; then
    pip3 install --user luminous_nix-*.whl
    echo "✅ Installed via wheel"
elif [ -f "luminous_nix-*.tar.gz" ]; then
    pip3 install --user luminous_nix-*.tar.gz
    echo "✅ Installed via source distribution"
else
    echo "Error: No installation package found"
    exit 1
fi

# Copy standalone script
mkdir -p ~/.local/bin
cp luminous-nix ~/.local/bin/
chmod +x ~/.local/bin/luminous-nix

echo "✅ Installation complete!"
echo ""
echo "Add ~/.local/bin to your PATH if not already done:"
echo "  export PATH=\$HOME/.local/bin:\$PATH"
echo ""
echo "Run 'luminous-nix --help' to get started"
