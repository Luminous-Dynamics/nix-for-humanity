"""
from typing import Tuple, List, Optional
🌟 Consciousness Orb - The Living Visual Presence of AI

A beautiful, breathing terminal visualization that embodies the AI's presence
through smooth animations, emotional colors, and responsive behavior.
"""

from textual.widget import Widget
from textual.reactive import reactive
from textual.app import RenderResult
from rich.console import Console, ConsoleOptions, RenderResult as RichRenderResult
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.layout import Layout
from rich.style import Style
import math
import time
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum


class AIState(Enum):
    """AI consciousness states"""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    LEARNING = "learning"
    ERROR = "error"
    FLOW = "flow"  # Deep symbiotic connection


class EmotionalState(Enum):
    """Emotional states with associated colors"""
    NEUTRAL = ("neutral", "#E0E0E0", "○")
    ATTENTIVE = ("attentive", "#4FC3F7", "◉")
    THINKING = ("thinking", "#7E57C2", "◐")
    HAPPY = ("happy", "#66BB6A", "◉")
    CONCERNED = ("concerned", "#FFA726", "◎")
    CONFUSED = ("confused", "#9E9E9E", "◔")
    LEARNING = ("learning", "#5C6BC0", "◈")
    FLOW = ("flow", "#26A69A", "✦")


@dataclass
class ThoughtParticle:
    """Represents a thought particle around the orb"""
    x: float
    y: float
    symbol: str
    velocity_x: float
    velocity_y: float
    lifetime: float
    max_lifetime: float = 3.0


class ConsciousnessOrb(Widget):
    """
    The living, breathing consciousness orb that represents AI presence.
    
    Features:
    - Smooth breathing animations (60fps)
    - Emotional color transitions
    - Thought particles when processing
    - Adaptive size based on attention
    - Memory constellation visualization
    """
    
    # Reactive properties
    ai_state = reactive(AIState.IDLE)
    emotional_state = reactive(EmotionalState.NEUTRAL)
    breathing_rate = reactive(2.0)  # Breaths per second
    attention_level = reactive(0.5)  # 0.0 to 1.0
    coherence = reactive(0.8)  # Connection strength
    
    # Animation properties
    phase = reactive(0.0)
    pulse_intensity = reactive(0.5)
    
    # Visual configuration
    MIN_SIZE = 3
    MAX_SIZE = 7
    
    # Beautiful Unicode characters for different states
    ORB_SYMBOLS = {
        AIState.IDLE: ["○", "◯", "◉", "◎"],
        AIState.LISTENING: ["◉", "◎", "◉", "◎"],
        AIState.THINKING: ["◐", "◓", "◑", "◒"],
        AIState.SPEAKING: ["◉", "◈", "◉", "◈"],
        AIState.LEARNING: ["◈", "◇", "◆", "◊"],
        AIState.ERROR: ["⊗", "⊕", "⊗", "⊕"],
        AIState.FLOW: ["✦", "✧", "⋆", "✶"]
    }
    
    # Particle effects for different states
    PARTICLE_SYMBOLS = {
        AIState.THINKING: ["·", "∴", "∵", "‥", "⁘"],
        AIState.LEARNING: ["✨", "·", "∘", "∙", "⋅"],
        AIState.FLOW: ["≈", "～", "∼", "≋", "≈"]
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles: List[ThoughtParticle] = []
        self.memory_nodes: List[Tuple[float, float, float]] = []  # x, y, strength
        self.start_time = time.time()
        
    def on_mount(self) -> None:
        """Start the breathing animation when mounted"""
        self.set_interval(1/60, self.animate)  # 60fps animation
        # Start breathing animation after a short delay to ensure mount is complete
        self.set_timer(0.1, self.animate_breathing)
        
    def animate(self) -> None:
        """Main animation loop at 60fps"""
        current_time = time.time() - self.start_time
        
        # Update phase for smooth animations
        self.phase = current_time * self.breathing_rate
        
        # Update particles
        self._update_particles(1/60)
        
        # Generate new particles when thinking
        if self.ai_state in [AIState.THINKING, AIState.LEARNING]:
            if len(self.particles) < 12:
                self._spawn_particle()
                
        # Update memory constellation
        if self.ai_state == AIState.LEARNING:
            self._update_memory_constellation()
            
        # Force refresh for smooth animation
        self.refresh()
        
    def animate_breathing(self) -> None:
        """Smooth breathing animation"""
        # This creates a natural breathing rhythm
        # Note: In headless mode, we just update the value directly
        # In real TUI mode, this would use Textual's animation system
        self.pulse_intensity = 0.3 if self.ai_state == AIState.IDLE else 0.8
        
    def _update_particles(self, dt: float) -> None:
        """Update particle physics"""
        new_particles = []
        for particle in self.particles:
            # Update position
            particle.x += particle.velocity_x * dt
            particle.y += particle.velocity_y * dt
            
            # Update lifetime
            particle.lifetime -= dt
            
            # Keep if still alive
            if particle.lifetime > 0:
                new_particles.append(particle)
                
        self.particles = new_particles
        
    def _spawn_particle(self) -> None:
        """Create a new thought particle"""
        import random
        
        # Spawn from center with random velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(5, 15)
        
        symbols = self.PARTICLE_SYMBOLS.get(self.ai_state, ["·"])
        
        particle = ThoughtParticle(
            x=0,
            y=0,
            symbol=random.choice(symbols),
            velocity_x=math.cos(angle) * speed,
            velocity_y=math.sin(angle) * speed,
            lifetime=3.0
        )
        
        self.particles.append(particle)
        
    def _update_memory_constellation(self) -> None:
        """Update memory node positions"""
        # Add new memory nodes occasionally
        import random
        if random.random() < 0.02 and len(self.memory_nodes) < 8:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(10, 20)
            self.memory_nodes.append((
                math.cos(angle) * dist,
                math.sin(angle) * dist,
                random.uniform(0.3, 1.0)
            ))
            
    def get_orb_character(self) -> str:
        """Get the current orb character based on animation phase"""
        symbols = self.ORB_SYMBOLS[self.ai_state]
        index = int(self.phase * 2) % len(symbols)
        return symbols[index]
        
    def get_orb_color(self) -> str:
        """Get the current color based on emotional state"""
        _, color, _ = self.emotional_state.value
        return color
        
    def calculate_orb_size(self) -> int:
        """Calculate orb size based on attention and state"""
        base_size = self.MIN_SIZE + (self.MAX_SIZE - self.MIN_SIZE) * self.attention_level
        
        # Breathing effect
        breath = math.sin(self.phase * math.pi) * 0.5 + 0.5
        size_mod = 1.0 + breath * self.pulse_intensity * 0.3
        
        return int(base_size * size_mod)
        
    def render_orb_ascii(self) -> List[str]:
        """Render the orb as ASCII art"""
        size = self.calculate_orb_size()
        orb_char = self.get_orb_character()
        lines = []
        
        # Create circular orb
        for y in range(-size, size + 1):
            line = ""
            for x in range(-size * 2, size * 2 + 1):
                # Calculate distance from center (accounting for terminal aspect ratio)
                dist = math.sqrt((x/2)**2 + y**2)
                
                if dist < size * 0.3:
                    # Inner core
                    line += orb_char
                elif dist < size * 0.6:
                    # Middle layer
                    line += "◉" if self.ai_state == AIState.LISTENING else "◎"
                elif dist < size:
                    # Outer layer
                    line += "·"
                else:
                    # Check for particles
                    particle_found = False
                    for p in self.particles:
                        px = int(p.x)
                        py = int(p.y)
                        if abs(px - x/2) < 1 and abs(py - y) < 1:
                            line += p.symbol
                            particle_found = True
                            break
                    
                    if not particle_found:
                        line += " "
                        
            lines.append(line)
            
        return lines
        
    def render(self) -> RenderResult:
        """Render the complete consciousness orb"""
        # Get ASCII representation
        orb_lines = self.render_orb_ascii()
        
        # Create rich text with color
        orb_text = Text("\n".join(orb_lines), style=self.get_orb_color())
        
        # Add state indicator
        state_text = Text()
        if self.ai_state == AIState.LISTENING:
            state_text.append("\n\n👂 Listening...", style="cyan")
        elif self.ai_state == AIState.THINKING:
            state_text.append("\n\n🤔 Processing...", style="magenta")
        elif self.ai_state == AIState.LEARNING:
            state_text.append("\n\n🌱 Learning...", style="blue")
        elif self.ai_state == AIState.FLOW:
            state_text.append("\n\n🌊 In Flow...", style="green")
            
        # Combine orb and state
        combined = Text()
        combined.append(orb_text)
        combined.append(state_text)
        
        # Center everything
        centered = Align.center(combined, vertical="middle")
        
        # Optional: Add panel border in flow state
        if self.ai_state == AIState.FLOW:
            return Panel(
                centered,
                border_style="green",
                title="✨ Consciousness Field ✨",
                title_align="center"
            )
        else:
            return centered
            
    def set_state(self, ai_state: AIState, emotional_state: Optional[EmotionalState] = None):
        """Update the orb's state"""
        self.ai_state = ai_state
        
        if emotional_state:
            self.emotional_state = emotional_state
            
        # Adjust breathing rate based on state
        if ai_state == AIState.IDLE:
            self.breathing_rate = 0.5  # Slow, peaceful
        elif ai_state == AIState.THINKING:
            self.breathing_rate = 2.0  # Faster when processing
        elif ai_state == AIState.FLOW:
            self.breathing_rate = 1.0  # Perfect rhythm
        else:
            self.breathing_rate = 1.5  # Normal rate
            
        # Trigger breathing animation update
        self.animate_breathing()
        
    def pulse(self, intensity: float = 1.0):
        """Create a pulse effect"""
        # In headless mode, just set the intensity
        # In real TUI mode, this would animate
        self.pulse_intensity = intensity
        
    def enter_flow_state(self):
        """Special animation for entering flow state"""
        self.set_state(AIState.FLOW, EmotionalState.FLOW)
        self.pulse(1.0)
        
        # Clear particles and create flow waves
        self.particles.clear()
        for i in range(8):
            angle = i * math.pi / 4
            self.particles.append(ThoughtParticle(
                x=math.cos(angle) * 10,
                y=math.sin(angle) * 5,
                symbol="≈",
                velocity_x=0,
                velocity_y=0,
                lifetime=999  # Permanent in flow
            ))