#!/usr/bin/env bash
# Quick demo creator - the easiest way to create demo materials

echo "🌟 Nix for Humanity - Quick Demo Creator"
echo "========================================"
echo ""
echo "This will create demo materials in the simplest way possible."
echo ""

# Create demo materials directory
mkdir -p demo-materials

# Option selection
echo "Choose demo type:"
echo "1. 📸 Screenshots only (fastest, no animation)"
echo "2. 🎬 Animated demo (requires screen recording)"
echo "3. 🤖 Automated demo mode (watch it run itself)"
echo "4. 📹 Full package (screenshots + instructions)"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📸 Generating screenshots..."
        python capture-tui-screenshots.py
        echo ""
        echo "✅ Screenshots created in ./screenshots/"
        echo ""
        echo "Next steps:"
        echo "  • Add to README: ![Demo](screenshots/01-idle-state.svg)"
        echo "  • Convert to PNG: convert screenshots/*.svg screenshots/*.png"
        ;;
        
    2)
        echo ""
        echo "🎬 Animated Demo Instructions"
        echo ""
        echo "1. Start your screen recorder now"
        echo "2. Press Enter to launch the TUI"
        echo "3. Follow these commands:"
        echo "   - help"
        echo "   - install firefox" 
        echo "   - voice on"
        echo "   - learn about nix"
        echo "   - (do 5+ commands for flow state)"
        echo "   - Ctrl+Z (zen mode)"
        echo "   - Ctrl+C (exit)"
        echo ""
        echo "Press Enter when recording is ready..."
        read
        
        ./run-enhanced-tui.sh
        
        echo ""
        echo "✅ Demo complete! Now:"
        echo "  • Stop your recording"
        echo "  • Trim to 60-90 seconds"
        echo "  • Convert to GIF if needed"
        ;;
        
    3)
        echo ""
        echo "🤖 Launching automated demo..."
        echo ""
        echo "The TUI will:"
        echo "  • Run through all features automatically"
        echo "  • Type commands with perfect timing"
        echo "  • Show all visualizations"
        echo ""
        echo "💡 TIP: Record your screen while this runs!"
        echo ""
        echo "Press Enter to start..."
        read
        
        # Create a simple launcher for demo mode
        cat > /tmp/demo-launcher.py << 'EOF'
import sys
sys.path.insert(0, '.')
from nix_humanity.ui.enhanced_main_app_with_demo import EnhancedNixForHumanityTUIWithDemo

app = EnhancedNixForHumanityTUIWithDemo()
# Auto-start demo after mount
app._demo_auto_start = True
app.run()
EOF
        
        python /tmp/demo-launcher.py
        ;;
        
    4)
        echo ""
        echo "📹 Creating full demo package..."
        echo ""
        
        # Generate screenshots
        echo "Step 1: Generating screenshots..."
        python capture-tui-screenshots.py
        
        # Create demo instructions
        echo ""
        echo "Step 2: Creating demo script..."
        
        cat > demo-materials/DEMO_SCRIPT.md << 'EOF'
# Demo Script - Nix for Humanity Enhanced TUI

## Setup
- Terminal: 120x40 characters
- Font: Fira Code 14pt
- Theme: Dracula or dark theme

## Script

1. **Launch** (0:00-0:05)
   ```
   ./run-enhanced-tui.sh
   ```
   Wait for orb to appear

2. **Basic Help** (0:05-0:10)
   ```
   help
   ```
   Show available commands

3. **Install Demo** (0:10-0:20)
   ```
   install firefox
   ```
   Watch thought particles

4. **Voice Mode** (0:20-0:30)
   ```
   voice on
   ```
   See waveform visualization

5. **Learning Mode** (0:30-0:40)
   ```
   learn about nix generations
   ```
   Watch progress bar grow

6. **Flow State** (0:40-0:55)
   Quick commands:
   ```
   search editor
   update system
   list packages
   check network
   clean cache
   ```
   Sacred geometry appears!

7. **Zen Mode** (0:55-1:00)
   ```
   Ctrl+Z
   ```
   Minimal UI
   ```
   Ctrl+Z
   ```
   Back to normal

8. **Exit** (1:00)
   ```
   Ctrl+C
   ```

## Key Features to Highlight
- ✨ Particle effects
- 🎤 Voice visualization
- 🌐 Network status
- 🧠 Learning progress
- 🌊 Flow state geometry
- 🧘 Zen mode
EOF
        
        echo "✅ Demo script created"
        echo ""
        echo "Step 3: Demo materials ready!"
        echo ""
        echo "📁 Created:"
        echo "  • screenshots/ - Static images"
        echo "  • demo-materials/DEMO_SCRIPT.md - Recording script"
        echo ""
        echo "Next: Record using the script or run automated demo"
        ;;
esac

echo ""
echo "🎯 Pro Tips:"
echo "  • Use consistent terminal size"
echo "  • Dark theme works best"
echo "  • Keep demos under 90 seconds"
echo "  • Focus on unique features"
echo ""
echo "Share your demos: #NixForHumanity"