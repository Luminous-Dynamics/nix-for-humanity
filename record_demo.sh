#!/bin/bash
# Record demo for Hacker News launch

echo "🎬 Recording Luminous Nix Demo for Hacker News"
echo "=============================================="
echo ""
echo "This will record a demo showing:"
echo "1. Natural language package installation"
echo "2. Creating development environments"
echo "3. System management commands"
echo ""
echo "Press Enter to start recording..."
read

# Start recording
poetry run asciinema rec --title="Luminous Nix: Natural Language for NixOS" \
                        --idle-time-limit=2 \
                        luminous_nix_demo.cast

echo ""
echo "✅ Recording saved to luminous_nix_demo.cast"
echo ""
echo "To upload and share:"
echo "  poetry run asciinema upload luminous_nix_demo.cast"
echo ""
echo "To play locally:"
echo "  poetry run asciinema play luminous_nix_demo.cast"