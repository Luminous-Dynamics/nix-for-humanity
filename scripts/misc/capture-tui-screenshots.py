#!/usr/bin/env python3
"""
Capture screenshots of the TUI in various states for documentation
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from luminous_nix.ui.enhanced_consciousness_orb import EnhancedConsciousnessOrb, AIState, EmotionalState
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.columns import Columns


def create_screenshot(state: AIState, emotion: EmotionalState, filename: str, 
                     voice_active: bool = False, network_connected: bool = True,
                     learning_progress: float = 0.3):
    """Create a screenshot of the orb in a specific state"""
    
    console = Console(record=True, width=120, height=40)
    
    # Create orb
    orb = EnhancedConsciousnessOrb()
    orb.ai_state = state
    orb.emotional_state = emotion
    orb.voice_active = voice_active
    orb.network_connected = network_connected
    orb.learning_progress = learning_progress
    
    # Simulate some particles
    if state == AIState.THINKING:
        for _ in range(5):
            orb._spawn_thought_particle()
    elif state == AIState.LEARNING:
        for _ in range(8):
            orb._spawn_learning_particle()
    elif voice_active:
        for _ in range(6):
            orb._spawn_voice_particle()
            
    # Update orb animation phase
    orb.phase = 1.5  # Mid-animation
    
    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", size=25),
        Layout(name="status", size=8),
        Layout(name="footer", size=3)
    )
    
    # Header
    header_text = Text("🌟 Nix for Humanity - Enhanced Consciousness TUI", style="bold cyan")
    layout["header"].update(Align.center(header_text, vertical="middle"))
    
    # Main orb display
    orb_render = orb.render()
    layout["main"].update(orb_render)
    
    # Status panel
    status_text = Text()
    status_text.append("🌐 Network: ", style="bold")
    status_text.append("Connected\n" if network_connected else "Disconnected\n", 
                      style="green" if network_connected else "red")
    
    status_text.append("🎤 Voice: ", style="bold")
    status_text.append("Active\n" if voice_active else "Inactive\n",
                      style="cyan" if voice_active else "dim")
    
    status_text.append("🧠 Learning: ", style="bold")
    status_text.append(f"{learning_progress:.0%} Complete\n", style="blue")
    
    status_text.append("🌊 State: ", style="bold")
    status_text.append(f"{state.value.title()}", style="yellow")
    
    status_panel = Panel(status_text, title="System Status", border_style="green")
    layout["status"].update(status_panel)
    
    # Footer
    footer_text = Text(f"Screenshot: {filename}", style="dim")
    layout["footer"].update(Align.center(footer_text, vertical="middle"))
    
    # Print to console (which is recording)
    console.print(layout)
    
    # Save as SVG
    console.save_svg(f"screenshots/{filename}.svg", title=filename)
    
    # Also save as text
    console.save_text(f"screenshots/{filename}.txt")
    
    print(f"✅ Created screenshot: {filename}")


def main():
    """Generate a series of screenshots showing different states"""
    
    # Create output directory
    Path("screenshots").mkdir(exist_ok=True)
    
    print("📸 Generating TUI Screenshots")
    print("============================")
    print("")
    
    # Define screenshots to capture
    screenshots = [
        # (AIState, EmotionalState, filename, voice_active, network_connected, learning_progress)
        (AIState.IDLE, EmotionalState.NEUTRAL, "01-idle-state", False, True, 0.1),
        (AIState.LISTENING, EmotionalState.ATTENTIVE, "02-listening", False, True, 0.1),
        (AIState.THINKING, EmotionalState.THINKING, "03-thinking-particles", False, True, 0.2),
        (AIState.VOICE_ACTIVE, EmotionalState.SPEAKING, "04-voice-active", True, True, 0.3),
        (AIState.LEARNING, EmotionalState.LEARNING, "05-learning-mode", False, True, 0.5),
        (AIState.FLOW, EmotionalState.FLOW, "06-flow-state", False, True, 0.8),
        (AIState.ERROR, EmotionalState.CONCERNED, "07-error-state", False, False, 0.3),
    ]
    
    for state, emotion, filename, voice, network, learning in screenshots:
        create_screenshot(state, emotion, filename, voice, network, learning)
        
    print("")
    print("🎉 All screenshots generated!")
    print("")
    print("📁 Screenshots saved in: ./screenshots/")
    print("")
    print("You can:")
    print("  • Convert SVG to PNG: convert screenshots/*.svg screenshots/*.png")
    print("  • Use in documentation: ![TUI](screenshots/01-idle-state.svg)")
    print("  • Create a montage: montage screenshots/*.png -geometry +2+2 montage.png")
    

if __name__ == "__main__":
    main()