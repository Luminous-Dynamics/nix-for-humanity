#!/usr/bin/env bash
# Create demo materials on NixOS using proper Nix tools

set -e

echo "🎬 Nix for Humanity Demo Creator (NixOS Edition)"
echo "==============================================="
echo ""

# Check if we're in a Nix environment with VHS
if ! command -v vhs &> /dev/null; then
    echo "📦 VHS not found. Loading Nix environment..."
    echo ""
    echo "Choose setup method:"
    echo "1. Use nix-shell (temporary)"
    echo "2. Use nix shell (flakes, temporary)"
    echo "3. Add to system configuration (permanent)"
    echo ""
    
    read -p "Enter choice (1-3): " setup_choice
    
    case $setup_choice in
        1)
            echo "Starting nix-shell with VHS..."
            exec nix-shell shell-with-vhs.nix --run "$0 $@"
            ;;
            
        2)
            echo "Starting nix shell with VHS..."
            exec nix shell nixpkgs#vhs nixpkgs#imagemagick nixpkgs#ffmpeg -c "$0 $@"
            ;;
            
        3)
            echo ""
            echo "To install VHS permanently, add to /etc/nixos/configuration.nix:"
            echo ""
            echo "environment.systemPackages = with pkgs; ["
            echo "  vhs"
            echo "  asciinema"
            echo "  imagemagick"
            echo "  ffmpeg"
            echo "];"
            echo ""
            echo "Then run: sudo nixos-rebuild switch"
            exit 0
            ;;
    esac
fi

# VHS is available, proceed with demo creation
echo "✅ VHS is available!"
echo ""

# Create output directory
OUTPUT_DIR="demo-materials"
mkdir -p "$OUTPUT_DIR"

echo "Select demo type:"
echo "1. 📹 Full animated GIF (using VHS)"
echo "2. 🎬 Quick 30-second demo"
echo "3. 📸 Screenshots only"
echo "4. 🤖 Run automated demo mode"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Creating full demo with VHS..."
        
        # Check if tape file exists
        if [ ! -f "demo-tui.tape" ]; then
            echo "❌ demo-tui.tape not found!"
            echo "Creating one for you..."
            
            cat > demo-tui.tape << 'EOF'
# Nix for Humanity Enhanced TUI Demo
Output demo-materials/enhanced-tui-demo.gif

# Settings
Set FontSize 14
Set Width 1200
Set Height 800
Set Theme "Dracula"

# Setup
Type "cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
Enter
Sleep 1s

Type "./run-enhanced-tui.sh"
Enter
Sleep 3s

# Demo sequence
Type "help"
Enter
Sleep 3s

Type "install firefox"
Enter
Sleep 4s

Type "voice on"
Enter
Sleep 3s

Type "learn about nix"
Enter
Sleep 4s

# Exit
Ctrl+C
Sleep 1s
EOF
        fi
        
        vhs demo-tui.tape
        echo "✅ Demo created: $OUTPUT_DIR/enhanced-tui-demo.gif"
        
        # Optimize with gifsicle if available
        if command -v gifsicle &> /dev/null; then
            echo "Optimizing GIF..."
            gifsicle -O3 "$OUTPUT_DIR/enhanced-tui-demo.gif" -o "$OUTPUT_DIR/enhanced-tui-demo-optimized.gif"
            echo "✅ Optimized: $OUTPUT_DIR/enhanced-tui-demo-optimized.gif"
        fi
        ;;
        
    2)
        echo ""
        echo "Creating quick demo..."
        
        cat > quick-demo.tape << 'EOF'
Output demo-materials/quick-demo.gif
Set FontSize 16
Set Width 1000
Set Height 600
Set Theme "Dracula"

Type "./run-enhanced-tui.sh"
Enter
Sleep 2s

Type "install firefox"
Enter
Sleep 3s

Type "voice on"
Enter
Sleep 3s

Ctrl+C
EOF
        
        vhs quick-demo.tape
        rm quick-demo.tape
        echo "✅ Quick demo created: $OUTPUT_DIR/quick-demo.gif"
        ;;
        
    3)
        echo ""
        echo "Generating screenshots..."
        
        # Use Nix python if needed
        if ! command -v python3 &> /dev/null; then
            nix-shell -p python311 python311Packages.rich --run "python3 capture-tui-screenshots.py"
        else
            python3 capture-tui-screenshots.py
        fi
        
        # Convert SVG to PNG using ImageMagick
        if command -v convert &> /dev/null; then
            echo "Converting SVG to PNG..."
            for svg in screenshots/*.svg; do
                if [ -f "$svg" ]; then
                    png="${svg%.svg}.png"
                    convert -density 300 -background white "$svg" "$png"
                    echo "✅ Created: $png"
                fi
            done
        fi
        ;;
        
    4)
        echo ""
        echo "Launching automated demo mode..."
        echo ""
        echo "💡 TIP: Use another terminal to record with:"
        echo "  asciinema rec $OUTPUT_DIR/demo.cast"
        echo "  OR"
        echo "  vhs record > $OUTPUT_DIR/demo.tape"
        echo ""
        echo "Press Enter to start demo..."
        read
        
        ./run-enhanced-tui.sh
        ;;
esac

echo ""
echo "📁 Demo materials in: $OUTPUT_DIR/"
echo ""

# Show what tools are available
echo "🛠️ Available tools in this environment:"
command -v vhs &> /dev/null && echo "  ✅ vhs - Terminal GIF recorder"
command -v asciinema &> /dev/null && echo "  ✅ asciinema - Terminal session recorder"
command -v ffmpeg &> /dev/null && echo "  ✅ ffmpeg - Video processor"
command -v convert &> /dev/null && echo "  ✅ imagemagick - Image converter"
command -v gifsicle &> /dev/null && echo "  ✅ gifsicle - GIF optimizer"

echo ""
echo "✨ Happy demo creating!"