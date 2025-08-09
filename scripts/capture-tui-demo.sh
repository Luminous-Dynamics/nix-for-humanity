#!/usr/bin/env bash
# Capture TUI demo using asciinema or script

set -e

echo "🎬 Preparing to capture Nix for Humanity TUI demo..."
echo "=================================================="

# Option 1: Try asciinema if available
if command -v asciinema &> /dev/null; then
    echo "✅ Found asciinema - recording demo..."
    echo ""
    echo "Instructions:"
    echo "1. The TUI will launch automatically"
    echo "2. Try these interactions:"
    echo "   - Type a natural language command"
    echo "   - Press Ctrl+Z to toggle Zen mode"
    echo "   - Watch the consciousness orb breathe"
    echo "3. Press Ctrl+C to stop recording"
    echo ""
    echo "Press Enter to start recording..."
    read
    
    asciinema rec -t "Nix for Humanity TUI Demo" tui-demo.cast \
        --command "python3 demo-tui.py"
    
    echo ""
    echo "✅ Recording saved to tui-demo.cast"
    echo "View with: asciinema play tui-demo.cast"
    echo "Upload with: asciinema upload tui-demo.cast"
    
# Option 2: Use script command for basic recording
elif command -v script &> /dev/null; then
    echo "📝 Using script command for recording..."
    echo ""
    echo "Instructions:"
    echo "1. The TUI will launch in recording mode"
    echo "2. Interact with the TUI"
    echo "3. Type 'exit' to stop recording"
    echo ""
    echo "Press Enter to start..."
    read
    
    script -q -c "python3 demo-tui.py" tui-demo.log
    
    echo ""
    echo "✅ Recording saved to tui-demo.log"
    echo "View with: cat tui-demo.log"
    
# Option 3: Just run the demo
else
    echo "📺 No recording tools found, running demo directly..."
    echo ""
    echo "Consider installing asciinema for recording:"
    echo "  pip install asciinema"
    echo ""
    echo "Press Enter to run the TUI..."
    read
    
    python3 demo-tui.py
fi