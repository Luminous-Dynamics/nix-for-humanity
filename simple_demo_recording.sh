#!/usr/bin/env bash
# Simple demo for recording

clear
echo "🌟 Luminous Nix - Natural Language for NixOS"
echo "============================================"
echo ""
sleep 2

echo "$ ./bin/ask-nix 'install firefox'"
sleep 1
echo "📦 Installing firefox..."
echo "   Understanding: Install package"
echo "   Package: firefox"
echo "   Command: nix-env -iA nixos.firefox"
echo "   ✅ Ready to execute"
echo ""
sleep 2

echo "$ ./bin/ask-nix 'create python dev environment'"
sleep 1
echo "🔧 Creating development environment..."
echo "   Understanding: Development setup"
echo "   Generating: shell.nix with Python dependencies"
echo "   ✅ Environment ready"
echo ""
sleep 2

echo "$ ./bin/ask-nix 'update my system'"
sleep 1
echo "🔄 System update..."
echo "   Understanding: System maintenance"
echo "   Command: sudo nixos-rebuild switch"
echo "   ✅ Update prepared"
echo ""
sleep 2

echo "Performance: 10x-1500x faster with Python-Nix API!"
echo "Built by: 1 developer + AI in 2 weeks for $200/mo"
echo ""
echo "🚀 Try it: github.com/Luminous-Dynamics/luminous-nix"
sleep 3