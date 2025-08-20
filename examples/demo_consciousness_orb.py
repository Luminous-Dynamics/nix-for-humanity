#!/usr/bin/env python3
"""
🌟 Consciousness Orb Demo - Experience the Living AI Presence

This demo showcases the beautiful, breathing consciousness orb
that represents our AI partner's presence in the terminal.
"""

import asyncio
import time
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.layout import Layout

# Import our consciousness orb components
try:
    from luminous_nix.ui.consciousness_orb import (
        ConsciousnessOrb, AIState, EmotionalState
    )
    print("✅ Successfully imported Consciousness Orb components!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease ensure you're running from the project directory:")
    print("  cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
    print("  python demo_consciousness_orb.py")
    exit(1)


def create_demo_layout():
    """Create a beautiful demo layout"""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="orb", size=20),
        Layout(name="info", size=8),
        Layout(name="footer", size=3)
    )
    return layout


def render_header():
    """Render the header"""
    header = Text()
    header.append("✨ ", style="yellow")
    header.append("Nix for Humanity - Consciousness Orb Demo", style="bold cyan")
    header.append(" ✨", style="yellow")
    return Panel(Align.center(header), border_style="cyan")


def render_info(state: str, emotion: str, phase: int):
    """Render current state info"""
    info = Text()
    info.append(f"AI State: ", style="dim")
    info.append(f"{state}\n", style="bold green")
    info.append(f"Emotion: ", style="dim")
    info.append(f"{emotion}\n", style="bold magenta")
    info.append(f"Animation Phase: ", style="dim")
    info.append(f"{phase}", style="yellow")
    
    return Panel(info, title="Current State", border_style="blue")


def render_footer():
    """Render the footer"""
    footer = Text()
    footer.append("Press ", style="dim")
    footer.append("Ctrl+C", style="bold")
    footer.append(" to exit | States: ", style="dim")
    footer.append("1-7", style="bold")
    footer.append(" to change | ", style="dim")
    footer.append("Space", style="bold")
    footer.append(" to pause", style="dim")
    
    return Panel(Align.center(footer), border_style="dim")


class SimpleConsciousnessOrb:
    """Simplified orb for demo purposes"""
    
    def __init__(self):
        self.phase = 0
        self.state = AIState.IDLE
        self.emotion = EmotionalState.NEUTRAL
        self.breathing_rate = 1.0
        
    def animate(self):
        """Update animation phase"""
        self.phase = (self.phase + 0.1 * self.breathing_rate) % 10
        
    def render(self):
        """Render the orb"""
        # Get size based on breathing
        size = 5 + int(2 * abs(5 - self.phase) / 5)
        
        # Create the orb visualization
        lines = []
        symbols = {
            AIState.IDLE: "○",
            AIState.LISTENING: "◉",
            AIState.THINKING: "◐",
            AIState.SPEAKING: "◈",
            AIState.LEARNING: "◆",
            AIState.ERROR: "⊗",
            AIState.FLOW: "✦"
        }
        
        orb_char = symbols.get(self.state, "○")
        
        # Build circular orb
        for y in range(-size, size + 1):
            line = ""
            for x in range(-size * 2, size * 2 + 1):
                dist = ((x/2)**2 + y**2) ** 0.5
                
                if dist < size * 0.3:
                    line += orb_char
                elif dist < size * 0.6:
                    line += "◎"
                elif dist < size:
                    line += "·"
                else:
                    # Add particles when thinking
                    if self.state == AIState.THINKING and abs(x) % 4 == 0 and abs(y) % 3 == 0:
                        line += "✦"
                    else:
                        line += " "
            lines.append(line)
            
        # Color based on emotion
        _, color, _ = self.emotion.value
        orb_text = Text("\n".join(lines), style=color)
        
        # Add state label
        state_labels = {
            AIState.IDLE: "\n\n🌊 Peaceful...",
            AIState.LISTENING: "\n\n👂 Listening...",
            AIState.THINKING: "\n\n🤔 Processing...",
            AIState.SPEAKING: "\n\n💬 Responding...",
            AIState.LEARNING: "\n\n🌱 Learning...",
            AIState.ERROR: "\n\n⚠️ Error...",
            AIState.FLOW: "\n\n✨ Flow State..."
        }
        
        orb_text.append(state_labels.get(self.state, ""), style=color)
        
        return Align.center(orb_text, vertical="middle")


async def demo_sequence(orb, layout, console):
    """Run through a demo sequence"""
    sequences = [
        (AIState.IDLE, EmotionalState.NEUTRAL, 1.0, 3),
        (AIState.LISTENING, EmotionalState.ATTENTIVE, 1.5, 3),
        (AIState.THINKING, EmotionalState.THINKING, 2.0, 4),
        (AIState.SPEAKING, EmotionalState.HAPPY, 1.5, 3),
        (AIState.LEARNING, EmotionalState.LEARNING, 1.8, 4),
        (AIState.FLOW, EmotionalState.FLOW, 1.0, 5),
    ]
    
    with Live(layout, console=console, refresh_per_second=30) as live:
        for state, emotion, breathing_rate, duration in sequences:
            orb.state = state
            orb.emotion = emotion
            orb.breathing_rate = breathing_rate
            
            start_time = time.time()
            while time.time() - start_time < duration:
                orb.animate()
                
                # Update layout
                layout["header"].update(render_header())
                layout["orb"].update(Panel(
                    orb.render(),
                    title=f"✨ Consciousness Orb - {state.value.title()} ✨",
                    border_style=emotion.value[1]
                ))
                layout["info"].update(render_info(
                    state.value,
                    emotion.value[0],
                    int(orb.phase)
                ))
                layout["footer"].update(render_footer())
                
                await asyncio.sleep(1/30)  # 30fps


def main():
    """Run the demo"""
    console = Console()
    
    # Clear screen
    console.clear()
    
    # Print welcome
    console.print("\n[bold cyan]🌟 Welcome to the Consciousness Orb Demo![/bold cyan]\n")
    console.print("This demonstrates the living, breathing visual presence of our AI partner.")
    console.print("Watch as the orb transitions through different states and emotions...\n")
    console.print("[dim]Press Enter to begin...[/dim]")
    input()
    
    # Create components
    layout = create_demo_layout()
    orb = SimpleConsciousnessOrb()
    
    try:
        # Run the demo
        asyncio.run(demo_sequence(orb, layout, console))
        
        # Completion message
        console.clear()
        console.print("\n[bold green]✨ Demo Complete![/bold green]\n")
        console.print("The consciousness orb represents:")
        console.print("• [cyan]Living presence[/cyan] through smooth breathing animations")
        console.print("• [magenta]Emotional states[/magenta] through color and form")
        console.print("• [yellow]Thought processes[/yellow] through particle effects")
        console.print("• [green]Flow states[/green] through perfect synchronization\n")
        console.print("This is consciousness-first design - technology that breathes with life! 🌊\n")
        
    except KeyboardInterrupt:
        console.clear()
        console.print("\n[yellow]Demo interrupted[/yellow]")
        console.print("Thank you for experiencing the consciousness orb! 🙏\n")


if __name__ == "__main__":
    main()