#!/bin/bash
# Convert asciinema recording to GIF for GitHub README

echo "🎬 Converting asciinema recording to GIF"
echo "========================================"
echo ""
echo "This will create a GIF from the demo recording."
echo ""

# Method 1: Using asciinema upload (simplest)
echo "Method 1: Upload to asciinema.org for embedding"
echo "------------------------------------------------"
echo "Run: poetry run asciinema upload luminous_nix_demo.cast"
echo "This will give you a URL to embed in your README"
echo ""

# Method 2: Using asciicast2gif (requires Docker)
echo "Method 2: Convert to GIF using Docker"
echo "--------------------------------------"
cat << 'EOF'
docker run --rm -v $PWD:/data asciinema/asciicast2gif \
    -w 80 -h 24 \
    luminous_nix_demo.cast luminous_nix_demo.gif
EOF
echo ""

# Method 3: Using svg-term (requires npm)
echo "Method 3: Convert to SVG (animated)"
echo "------------------------------------"
cat << 'EOF'
npx svg-term --cast=luminous_nix_demo.cast --out=luminous_nix_demo.svg \
    --window --width=80 --height=24
EOF
echo ""

# Method 4: Play and screen record
echo "Method 4: Play and manually screen record"
echo "------------------------------------------"
echo "poetry run asciinema play luminous_nix_demo.cast"
echo "Use any screen recording tool to capture as GIF"
echo ""

echo "Choose the method that works best for your setup!"