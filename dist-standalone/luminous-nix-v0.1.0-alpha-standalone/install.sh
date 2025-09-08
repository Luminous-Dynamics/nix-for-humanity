#!/bin/bash
# Install Luminous Nix dependencies

echo "Installing Luminous Nix v0.1.0-alpha dependencies..."

# Check Python version
python3 --version

# Install dependencies
pip3 install --user -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "To run Luminous Nix:"
echo "  ./luminous-nix help"
echo "  ./luminous-nix 'search text editor'"
echo "  ./luminous-nix 'install firefox'"
