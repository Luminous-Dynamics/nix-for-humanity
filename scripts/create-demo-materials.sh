#!/usr/bin/env bash
# Create demo materials for Nix for Humanity Enhanced TUI

set -e

echo "🎬 Nix for Humanity Demo Materials Creator"
echo "========================================="
echo ""

# Check dependencies
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ $1 not found. Install with: $2"
        return 1
    else
        echo "✅ $1 found"
        return 0
    fi
}

echo "Checking dependencies..."
echo ""

# Check for various tools
TOOLS_OK=true

# Option 1: VHS (best for terminal GIFs)
if check_dependency "vhs" "brew install vhs OR nix-env -iA nixpkgs.vhs"; then
    VHS_AVAILABLE=true
else
    VHS_AVAILABLE=false
    TOOLS_OK=false
fi

# Option 2: Asciinema
if check_dependency "asciinema" "pip install asciinema OR nix-env -iA nixpkgs.asciinema"; then
    ASCIINEMA_AVAILABLE=true
else
    ASCIINEMA_AVAILABLE=false
fi

# Option 3: ttyrec + ttygif
if check_dependency "ttyrec" "sudo apt install ttyrec OR brew install ttyrec"; then
    TTYREC_AVAILABLE=true
else
    TTYREC_AVAILABLE=false
fi

# Option 4: terminalizer
if check_dependency "terminalizer" "npm install -g terminalizer"; then
    TERMINALIZER_AVAILABLE=true
else
    TERMINALIZER_AVAILABLE=false
fi

echo ""
echo "Available recording tools:"
[[ "$VHS_AVAILABLE" == true ]] && echo "  ✅ VHS (recommended)"
[[ "$ASCIINEMA_AVAILABLE" == true ]] && echo "  ✅ Asciinema"
[[ "$TTYREC_AVAILABLE" == true ]] && echo "  ✅ ttyrec"
[[ "$TERMINALIZER_AVAILABLE" == true ]] && echo "  ✅ terminalizer"

if [[ "$TOOLS_OK" == false ]]; then
    echo ""
    echo "⚠️  Installing VHS is recommended for best results"
    echo ""
fi

# Create output directory
OUTPUT_DIR="demo-materials"
mkdir -p "$OUTPUT_DIR"

echo ""
echo "Select demo creation method:"
echo "1. VHS - High-quality GIF (recommended)"
echo "2. Built-in Demo Mode - Automated showcase"
echo "3. Asciinema - Web-playable recording"
echo "4. Manual recording with instructions"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        if [[ "$VHS_AVAILABLE" == true ]]; then
            echo ""
            echo "🎬 Creating demo with VHS..."
            echo ""
            
            # Use the VHS tape file
            vhs demo-tui.tape
            
            echo "✅ Demo GIF created: enhanced-tui-demo.gif"
            mv enhanced-tui-demo.gif "$OUTPUT_DIR/"
            
            # Create additional formats
            echo ""
            echo "Creating additional demo formats..."
            
            # Quick demo
            cat > quick-demo.tape << 'EOF'
# Quick 30-second demo
Output quick-demo.gif
Set FontSize 16
Set Width 1000
Set Height 600
Set Theme "Dracula"

Type "./run-enhanced-tui.sh"
Enter
Sleep 3s

Type "install firefox"
Enter
Sleep 3s

Type "voice on"
Enter
Sleep 3s

Type "learn about nix"
Enter
Sleep 3s

Ctrl+C
EOF
            
            vhs quick-demo.tape
            mv quick-demo.gif "$OUTPUT_DIR/"
            
            echo "✅ Quick demo created: quick-demo.gif"
            
        else
            echo "❌ VHS not available. Please install it first."
        fi
        ;;
        
    2)
        echo ""
        echo "🎬 Launching built-in demo mode..."
        echo ""
        echo "This will:"
        echo "  • Clear the screen"
        echo "  • Run through all features automatically"
        echo "  • Perfect for screen recording"
        echo ""
        echo "Press Enter when ready to start..."
        read
        
        # Launch TUI with demo flag
        python3 -c "
import sys
sys.argv.append('--demo')
from nix_humanity.ui.enhanced_main_app_with_demo import EnhancedNixForHumanityTUIWithDemo
app = EnhancedNixForHumanityTUIWithDemo()
app.run()
"
        ;;
        
    3)
        if [[ "$ASCIINEMA_AVAILABLE" == true ]]; then
            echo ""
            echo "🎬 Recording with Asciinema..."
            echo ""
            echo "Instructions:"
            echo "  1. The recording will start after you press Enter"
            echo "  2. Run ./run-enhanced-tui.sh"
            echo "  3. Demonstrate all features"
            echo "  4. Exit with Ctrl+C then Ctrl+D to stop recording"
            echo ""
            echo "Press Enter to start recording..."
            read
            
            asciinema rec "$OUTPUT_DIR/demo.cast" -t "Nix for Humanity Enhanced TUI Demo"
            
            echo ""
            echo "✅ Recording saved to: $OUTPUT_DIR/demo.cast"
            echo ""
            echo "To share:"
            echo "  asciinema upload $OUTPUT_DIR/demo.cast"
            echo "Or convert to GIF:"
            echo "  docker run --rm -v \$PWD:/data asciinema/asciicast2gif -s 2 -t solarized-dark demo.cast demo.gif"
            
        else
            echo "❌ Asciinema not available. Please install it first."
        fi
        ;;
        
    4)
        echo ""
        echo "📹 Manual Recording Instructions"
        echo "================================"
        echo ""
        echo "1. Use your favorite screen recorder (OBS, SimpleScreenRecorder, etc.)"
        echo ""
        echo "2. Set recording area to terminal window"
        echo ""
        echo "3. Run this sequence:"
        echo "   ./run-enhanced-tui.sh"
        echo "   # Wait for load"
        echo "   help"
        echo "   install firefox"
        echo "   voice on"
        echo "   learn about nix"
        echo "   search editor"
        echo "   update system"
        echo "   # (Complete 5+ commands for flow state)"
        echo "   Ctrl+Z  # Zen mode"
        echo "   Ctrl+Z  # Back to normal"
        echo "   Ctrl+C  # Exit"
        echo ""
        echo "4. Edit video to ~60 seconds"
        echo ""
        echo "5. Convert to GIF using:"
        echo "   ffmpeg -i video.mp4 -vf 'fps=10,scale=1000:-1:flags=lanczos' -c:v gif output.gif"
        echo ""
        ;;
esac

echo ""
echo "📁 Demo materials will be in: $OUTPUT_DIR/"
echo ""
echo "🎯 Tips for great demos:"
echo "  • Clean terminal before recording"
echo "  • Use consistent terminal size (1200x800 recommended)"
echo "  • Pause between commands to show effects"
echo "  • Highlight unique features (particles, voice, flow state)"
echo "  • Keep total length under 90 seconds"
echo ""
echo "✨ Happy demo creating!"