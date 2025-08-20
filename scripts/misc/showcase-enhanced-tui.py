#!/usr/bin/env python3
"""
🌟 Enhanced Nix for Humanity TUI Showcase

Demonstrates advanced features:
- Voice activity visualization
- Complex particle systems
- Network status monitoring
- Learning progress tracking
- Sacred geometry in flow state
"""

import sys
import os
import time
from datetime import datetime

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("🌟 Enhanced Nix for Humanity TUI Feature Showcase")
print("=" * 60)
print("\n✨ NEW Advanced Features in this Demo:\n")

new_features = [
    ("🎤 Voice Activity Visualization", "See voice waveforms when speaking"),
    ("🌐 Network Status Monitoring", "Real-time connection and latency display"),
    ("🧠 Learning Progress Tracking", "Watch the AI learn from interactions"),
    ("✨ Complex Particle Systems", "Physics-based particles with types"),
    ("🔮 Sacred Geometry", "Flow state activates sacred patterns"),
    ("📊 Sacred Metrics Dashboard", "Flow score, coherence, attention levels"),
    ("⚡ Quick Action Buttons", "One-click common commands"),
    ("🌊 Enhanced Flow States", "Deeper visual feedback for peak performance")
]

for i, (feature, description) in enumerate(new_features, 1):
    print(f"{i}. {feature}")
    print(f"   {description}")
    time.sleep(0.5)

print("\n" + "=" * 60)
print("\n🎮 Enhanced Interactive Commands:\n")

commands = [
    "install firefox    - Watch thought particles spawn",
    "help              - See all available commands",
    "search editor     - See network particles",
    "voice on          - Activate voice visualization",
    "learn about nix   - Trigger learning mode with progress",
    "Ctrl+V            - Toggle voice mode on/off",
    "Ctrl+Z            - Enter Zen Mode (minimal UI)",
    "Ctrl+D            - Show debug information",
    "F1                - Get keyboard help",
    "Ctrl+C            - Exit gracefully"
]

for cmd in commands:
    print(f"  • {cmd}")
    time.sleep(0.3)

print("\n" + "=" * 60)
print("\n🌊 Flow State Activation:")
print("  Complete several successful commands to enter flow state")
print("  Watch for sacred geometry patterns and enhanced coherence")

print("\n" + "=" * 60)
print("\n🚀 Press Enter to launch the ENHANCED TUI showcase...")

try:
    input()
    
    print("\n🔮 Launching enhanced consciousness-first interface...\n")
    
    # Try to import and run the enhanced version
    try:
        from luminous_nix.ui.enhanced_main_app import EnhancedNixForHumanityTUI
        from luminous_nix.core.engine import NixForHumanityBackend
        
        # Create mock backend if needed
        class EnhancedMockBackend:
            def __init__(self):
                self.state = "ready"
                self.learning_data = []
                
            async def process_query(self, query):
                # Enhanced mock responses
                self.learning_data.append({
                    "query": query,
                    "timestamp": datetime.now(),
                    "success": True
                })
                
                if "install" in query.lower():
                    return {
                        "success": True,
                        "message": f"✅ Installing {query.split()[-1]}... Done!",
                        "command": f"nix-env -iA nixpkgs.{query.split()[-1]}",
                        "learning": "I've learned your package preferences"
                    }
                elif "voice" in query.lower():
                    return {
                        "success": True,
                        "message": "🎤 Voice mode activated! Try speaking naturally.",
                        "voice_enabled": True
                    }
                elif "learn" in query.lower():
                    return {
                        "success": True,
                        "message": "🧠 Learning mode active! I'm analyzing patterns in NixOS...",
                        "learning_active": True
                    }
                elif "help" in query.lower():
                    return {
                        "success": True,
                        "message": """🌟 Enhanced Commands:
• Voice control: "voice on/off"
• Learning mode: "learn about [topic]"
• Network test: "check network"
• Flow state: Complete 5+ commands
• Sacred mode: "activate sacred geometry"

Try the quick action buttons on the right!"""
                    }
                elif "network" in query.lower():
                    return {
                        "success": True,
                        "message": "🌐 Network status: Connected, 25ms latency, 95% strength"
                    }
                else:
                    return {
                        "success": True,
                        "message": f"✨ Processing: {query} (Learning from this interaction)"
                    }
        
        # Try real backend first, fall back to enhanced mock
        try:
            backend = NixForHumanityBackend()
            print("✅ Using real backend with enhancements")
        except Exception:
            backend = EnhancedMockBackend()
            print("📝 Using enhanced mock backend for demo")
        
        # Create and run enhanced app
        app = EnhancedNixForHumanityTUI(engine=backend)
        
        print("\n💡 Tips for the best experience:")
        print("  1. Try 'voice on' to see voice visualization")
        print("  2. Complete several commands to activate flow state")
        print("  3. Watch the learning progress bar grow")
        print("  4. Notice network status indicators")
        print("  5. Use Ctrl+Z for zen mode\n")
        
        app.run()
        
    except ImportError as e:
        print(f"❌ Error importing enhanced TUI components: {e}")
        print("\nMake sure you have textual installed:")
        print("  pip install textual rich")
        
except KeyboardInterrupt:
    print("\n\n✨ Thank you for exploring enhanced consciousness-first computing!")
    print("🌊 We flow with gratitude.")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("📚 Learn more about the enhanced features:")
print("  • ENHANCED_CONSCIOUSNESS_ORB.md")
print("  • SYMBIOTIC_PARTNER_ARCHITECTURE.md")
print("  • EMBODIMENT_ROADMAP.md")
print("\n🌟 The future of human-AI partnership is here! 🌟")