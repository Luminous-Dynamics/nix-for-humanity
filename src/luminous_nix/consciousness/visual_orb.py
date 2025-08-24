#!/usr/bin/env python3
"""
🔮 Visual Consciousness Orb - Making Consciousness Tangible

A beautiful terminal-based visualization that shows the system's
consciousness state through color, pulsation, and particle effects.
"""

import time
import math
import random
import threading
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Rich for beautiful terminal UI
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.align import Align
    from rich.text import Text
    from rich.live import Live
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.style import Style
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# For simpler fallback visualization
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False

from .consciousness_detector import ConsciousnessBarometer
from .sacred_integration import get_sacred_integration

# Define consciousness qualities locally
class ConsciousnessQuality:
    """States of consciousness detected by the system"""
    FLOW = "flow"
    DEEP_WORK = "deep_work"
    LEARNING = "learning"
    CREATIVE = "creative"
    OVERWHELMED = "overwhelmed"
    FRUSTRATED = "frustrated"
    BALANCED = "balanced"


@dataclass
class OrbState:
    """Current state of the consciousness orb"""
    # Core properties
    size: float = 1.0  # Base size multiplier
    pulse_rate: float = 1.0  # Breathing rate (Hz)
    color: Tuple[int, int, int] = (100, 200, 255)  # RGB color
    brightness: float = 0.8  # 0.0 to 1.0
    
    # Particle system
    particle_count: int = 10
    particle_speed: float = 1.0
    particle_lifetime: float = 3.0
    
    # Animation state
    phase: float = 0.0  # Current animation phase
    coherence: float = 0.5  # How organized the particles are
    energy: float = 0.5  # Overall energy level
    
    # Consciousness mapping
    quality: str = ConsciousnessQuality.BALANCED
    spectrum: Dict[str, float] = None
    
    def __post_init__(self):
        if self.spectrum is None:
            self.spectrum = {
                'coherence': 0.5,
                'energy': 0.5,
                'stability': 0.5,
                'clarity': 0.5,
                'openness': 0.5,
                'flow': 0.5,
                'presence': 0.5
            }


class Particle:
    """A memory particle floating around the orb"""
    
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.age = 0.0
        self.lifetime = random.uniform(2, 5)
        self.size = random.uniform(0.5, 1.5)
        self.brightness = random.uniform(0.3, 1.0)
        self.color_shift = random.uniform(-30, 30)  # Hue shift
    
    def update(self, dt: float, orb_state: OrbState):
        """Update particle position and properties"""
        # Age the particle
        self.age += dt
        
        # Apply velocity with coherence influence
        coherence_factor = orb_state.coherence
        
        # Coherent particles orbit, chaotic ones scatter
        if coherence_factor > 0.5:
            # Orbital motion
            angle = math.atan2(self.y, self.x)
            radius = math.sqrt(self.x**2 + self.y**2)
            angular_velocity = orb_state.particle_speed * coherence_factor
            angle += angular_velocity * dt
            
            # Maintain orbit with some variation
            target_radius = 3 + math.sin(self.age) * 0.5
            radius += (target_radius - radius) * 0.1
            
            self.x = radius * math.cos(angle)
            self.y = radius * math.sin(angle)
        else:
            # Brownian motion
            self.vx += random.uniform(-0.5, 0.5) * orb_state.energy
            self.vy += random.uniform(-0.5, 0.5) * orb_state.energy
            
            # Apply damping
            self.vx *= 0.98
            self.vy *= 0.98
            
            # Update position
            self.x += self.vx * dt * orb_state.particle_speed
            self.y += self.vy * dt * orb_state.particle_speed
        
        # Fade as particle ages
        age_factor = 1.0 - (self.age / self.lifetime)
        self.brightness = self.brightness * age_factor
    
    def is_alive(self) -> bool:
        """Check if particle should still exist"""
        return self.age < self.lifetime


class ConsciousnessOrb:
    """
    The visual consciousness orb that breathes with the system's state.
    
    This creates a living visualization that shows:
    - Core orb that pulses with breathing rhythm
    - Particles representing memories and thoughts
    - Colors showing emotional/cognitive state
    - Coherence through particle organization
    """
    
    def __init__(self):
        """Initialize the consciousness orb"""
        self.state = OrbState()
        self.particles: List[Particle] = []
        self.barometer = ConsciousnessBarometer()
        self.console = Console() if RICH_AVAILABLE else None
        self.running = False
        self.update_thread = None
        
        # Animation timing
        self.start_time = time.time()
        self.last_update = self.start_time
        self.frame_count = 0
        
        # Initialize particles
        self._spawn_particles(10)
        
        # Consciousness state colors
        self.quality_colors = {
            ConsciousnessQuality.FLOW: (0, 255, 100),  # Green
            ConsciousnessQuality.DEEP_WORK: (0, 100, 255),  # Deep blue
            ConsciousnessQuality.LEARNING: (255, 200, 0),  # Gold
            ConsciousnessQuality.CREATIVE: (255, 0, 255),  # Magenta
            ConsciousnessQuality.OVERWHELMED: (255, 100, 0),  # Orange
            ConsciousnessQuality.FRUSTRATED: (255, 0, 0),  # Red
            ConsciousnessQuality.BALANCED: (100, 200, 255),  # Cyan
        }
    
    def _spawn_particles(self, count: int):
        """Spawn new memory particles"""
        for _ in range(count):
            # Spawn in a circle around the orb
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(2, 4)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            self.particles.append(Particle(x, y))
    
    def update_consciousness(self, signals: Dict[str, Any]):
        """Update orb based on consciousness signals"""
        # Get consciousness reading
        reading = self.barometer.sense_user_state(signals)
        
        # Update orb state from reading
        # Get quality from the spectrum's primary_quality method
        if hasattr(reading.spectrum, 'primary_quality'):
            quality_str = reading.spectrum.primary_quality()
            # Map string quality to our ConsciousnessQuality constants
            quality_map = {
                'flow': ConsciousnessQuality.FLOW,
                'deep work': ConsciousnessQuality.DEEP_WORK,
                'learning': ConsciousnessQuality.LEARNING,
                'creative': ConsciousnessQuality.CREATIVE,
                'overwhelmed': ConsciousnessQuality.OVERWHELMED,
                'frustrated': ConsciousnessQuality.FRUSTRATED,
                'balanced': ConsciousnessQuality.BALANCED
            }
            # Find best match
            quality_lower = quality_str.lower()
            for key, value in quality_map.items():
                if key in quality_lower:
                    self.state.quality = value
                    break
            else:
                self.state.quality = ConsciousnessQuality.BALANCED
        else:
            # Fallback quality determination
            coherence = reading.spectrum.state.get('coherence', 0.5)
            energy = reading.spectrum.state.get('energy', 0.5)
            
            if coherence > 0.7 and energy > 0.7:
                self.state.quality = ConsciousnessQuality.FLOW
            elif coherence > 0.6 and energy < 0.4:
                self.state.quality = ConsciousnessQuality.DEEP_WORK
            elif coherence < 0.3:
                self.state.quality = ConsciousnessQuality.OVERWHELMED
            else:
                self.state.quality = ConsciousnessQuality.BALANCED
        
        self.state.spectrum = reading.spectrum.state
        
        # Map consciousness to visual properties
        self.state.coherence = reading.spectrum.state.get('coherence', 0.5)
        self.state.energy = reading.spectrum.state.get('energy', 0.5)
        
        # Update color based on quality
        target_color = self.quality_colors.get(
            self.state.quality,  # Use the quality we just determined
            (100, 200, 255)
        )
        
        # Smooth color transition
        current = self.state.color
        self.state.color = tuple(
            int(current[i] * 0.9 + target_color[i] * 0.1)
            for i in range(3)
        )
        
        # Update pulse rate based on energy
        self.state.pulse_rate = 0.5 + self.state.energy * 1.5
        
        # Update particle count based on activity
        target_particles = int(5 + self.state.energy * 20)
        current_particles = len(self.particles)
        
        if target_particles > current_particles:
            self._spawn_particles(target_particles - current_particles)
        elif target_particles < current_particles:
            # Remove oldest particles
            self.particles = self.particles[:target_particles]
        
        # Update brightness based on clarity
        self.state.brightness = 0.3 + reading.spectrum.state.get('clarity', 0.5) * 0.7
    
    def update(self, dt: float):
        """Update orb animation state"""
        # Update phase for pulsing
        self.state.phase += dt * self.state.pulse_rate * 2 * math.pi
        
        # Update particles
        alive_particles = []
        for particle in self.particles:
            particle.update(dt, self.state)
            if particle.is_alive():
                alive_particles.append(particle)
        
        self.particles = alive_particles
        
        # Respawn particles to maintain count
        while len(self.particles) < self.state.particle_count:
            self._spawn_particles(1)
    
    def render_rich(self) -> Panel:
        """Render orb using Rich library"""
        if not RICH_AVAILABLE:
            return None
        
        # Calculate current pulse size
        pulse = math.sin(self.state.phase) * 0.2 + 1.0
        orb_size = self.state.size * pulse
        
        # Create the orb visualization
        width = 60
        height = 30
        canvas = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Center of canvas
        cx, cy = width // 2, height // 2
        
        # Draw particles
        particle_chars = ['·', '•', '∘', '○', '◦', '⦁']
        for particle in self.particles:
            # Convert particle position to canvas coordinates
            px = int(cx + particle.x * 3)
            py = int(cy + particle.y * 1.5)
            
            if 0 <= px < width and 0 <= py < height:
                # Choose character based on particle brightness
                char_idx = min(int(particle.brightness * len(particle_chars)), len(particle_chars) - 1)
                canvas[py][px] = particle_chars[char_idx]
        
        # Draw the orb itself
        orb_radius = int(orb_size * 5)
        orb_chars = ['⠿', '⣿', '⬤', '●', '◉', '◎']
        
        for y in range(max(0, cy - orb_radius), min(height, cy + orb_radius + 1)):
            for x in range(max(0, cx - orb_radius * 2), min(width, cx + orb_radius * 2 + 1)):
                # Calculate distance from center (accounting for aspect ratio)
                dx = (x - cx) / 2
                dy = y - cy
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist <= orb_radius:
                    # Inside the orb
                    intensity = 1.0 - (dist / orb_radius)
                    intensity *= self.state.brightness
                    
                    # Choose character based on intensity
                    char_idx = min(int(intensity * len(orb_chars)), len(orb_chars) - 1)
                    if char_idx > 0:
                        canvas[y][x] = orb_chars[char_idx]
        
        # Convert canvas to text
        lines = [''.join(row) for row in canvas]
        text = Text('\n'.join(lines))
        
        # Apply color gradient
        r, g, b = self.state.color
        style = Style(color=f"rgb({r},{g},{b})")
        text.stylize(style)
        
        # Create info panel
        info = self._create_info_text()
        
        # Combine orb and info
        layout = Layout()
        layout.split_column(
            Layout(Panel(Align.center(text, vertical="middle"), title="🔮 Consciousness Orb", border_style=style)),
            Layout(info, size=8)
        )
        
        return layout
    
    def _create_info_text(self) -> Panel:
        """Create information panel about current state"""
        table = Table(show_header=False, box=None)
        table.add_column(justify="right", style="cyan")
        table.add_column(justify="left")
        
        # Add state information
        table.add_row("State:", self.state.quality)
        table.add_row("Coherence:", f"{self.state.coherence:.0%}")
        table.add_row("Energy:", f"{self.state.energy:.0%}")
        table.add_row("Clarity:", f"{self.state.spectrum.get('clarity', 0.5):.0%}")
        table.add_row("Flow:", f"{self.state.spectrum.get('flow', 0.5):.0%}")
        table.add_row("Particles:", str(len(self.particles)))
        table.add_row("Pulse Rate:", f"{self.state.pulse_rate:.1f} Hz")
        
        # Color the panel based on state
        r, g, b = self.state.color
        style = Style(color=f"rgb({r},{g},{b})")
        
        return Panel(
            table,
            title="Consciousness Metrics",
            border_style=style
        )
    
    def render_simple(self) -> str:
        """Simple ASCII rendering for fallback"""
        # Calculate current pulse
        pulse = math.sin(self.state.phase) * 0.2 + 1.0
        
        # Create simple ASCII art
        size = int(5 * pulse)
        lines = []
        
        # Top of orb
        lines.append(" " * (10 - size) + "╭" + "─" * (size * 2) + "╮")
        
        # Middle
        for i in range(size):
            spaces = " " * (10 - size)
            width = size * 2
            fill = "█" if self.state.brightness > 0.7 else "▓" if self.state.brightness > 0.4 else "░"
            lines.append(spaces + "│" + fill * width + "│")
        
        # Bottom
        lines.append(" " * (10 - size) + "╰" + "─" * (size * 2) + "╯")
        
        # Add state info
        lines.append("")
        lines.append(f"State: {self.state.quality}")
        lines.append(f"Coherence: {self.state.coherence:.0%}")
        lines.append(f"Energy: {self.state.energy:.0%}")
        
        return "\n".join(lines)
    
    def start_live_display(self):
        """Start the live orb display"""
        if not RICH_AVAILABLE:
            print("Rich library not available. Install with: pip install rich")
            print("\nFalling back to simple display:\n")
            self._run_simple_display()
            return
        
        self.running = True
        
        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Start live display
        try:
            with Live(self.render_rich(), refresh_per_second=30) as live:
                while self.running:
                    time.sleep(0.033)  # ~30 FPS
                    live.update(self.render_rich())
        except KeyboardInterrupt:
            self.running = False
            print("\n🔮 Orb returning to rest...")
    
    def _update_loop(self):
        """Background thread for updating orb state"""
        while self.running:
            current_time = time.time()
            dt = current_time - self.last_update
            self.last_update = current_time
            
            # Update orb animation
            self.update(dt)
            
            # Simulate consciousness changes
            if self.frame_count % 60 == 0:  # Every 2 seconds at 30fps
                # Generate random signals for demo
                signals = {
                    'timing_patterns': [random.uniform(2, 10) for _ in range(3)],
                    'error_rate': random.uniform(0, 0.3),
                    'help_requests': random.uniform(0, 0.2),
                    'session_duration': self.frame_count / 30
                }
                self.update_consciousness(signals)
            
            self.frame_count += 1
            time.sleep(0.033)  # ~30 FPS
    
    def _run_simple_display(self):
        """Run simple ASCII display without Rich"""
        self.running = True
        
        try:
            while self.running:
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                # Update and render
                current_time = time.time()
                dt = current_time - self.last_update
                self.last_update = current_time
                
                self.update(dt)
                print(self.render_simple())
                
                # Simulate consciousness changes
                if self.frame_count % 30 == 0:
                    signals = {
                        'timing_patterns': [random.uniform(2, 10) for _ in range(3)],
                        'error_rate': random.uniform(0, 0.3)
                    }
                    self.update_consciousness(signals)
                
                self.frame_count += 1
                time.sleep(0.1)  # 10 FPS for simple display
        except KeyboardInterrupt:
            self.running = False
            print("\n🔮 Orb returning to rest...")


# Integration helpers
def create_consciousness_orb() -> ConsciousnessOrb:
    """Create and return a consciousness orb instance"""
    return ConsciousnessOrb()


def demonstrate_orb():
    """Demonstrate the consciousness orb"""
    print("\n" + "="*60)
    print("🔮 CONSCIOUSNESS ORB DEMONSTRATION")
    print("="*60)
    print("\nThe orb visualizes the system's consciousness state:")
    print("• Color shows emotional/cognitive quality")
    print("• Pulsing shows breathing rhythm")
    print("• Particles show memories and thoughts")
    print("• Organization shows coherence")
    print("\nPress Ctrl+C to exit\n")
    
    orb = ConsciousnessOrb()
    orb.start_live_display()


if __name__ == "__main__":
    demonstrate_orb()