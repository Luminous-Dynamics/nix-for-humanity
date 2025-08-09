#!/bin/bash
# Launch the advanced features TUI for Nix for Humanity

echo "🌟 Launching Nix for Humanity - Advanced Features TUI"
echo "=================================================="
echo ""
echo "This beautiful interface showcases:"
echo "  📦 Flake Management - Modern NixOS configuration"
echo "  👤 Profile Management - Switch environments easily"
echo "  💬 Interactive REPL - Explore Nix interactively"
echo "  🌐 Remote Deployment - Build and deploy anywhere"
echo "  💿 Image Building - Create ISOs, VMs, and more"
echo ""
echo "All powered by native Python-Nix API for instant operations!"
echo ""

# Check if we're in the right directory
if [ ! -f "tui/advanced_features_ui.py" ]; then
    echo "❌ Error: Please run this from the nix-for-humanity directory"
    exit 1
fi

# Launch the TUI
python3 tui/advanced_features_ui.py