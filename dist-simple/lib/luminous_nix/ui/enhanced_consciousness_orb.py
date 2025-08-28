"""
from typing import Tuple, List
🌟 Enhanced Consciousness Orb - Advanced Visual Features

This enhanced version includes:
- Voice activity visualization with waveforms
- Complex particle systems with physics
- Network status indicators
- Learning progress visualization
- Sacred geometry patterns
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
import random
from typing import Optional, Tuple, List, Dict
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
    FLOW = "flow"
    VOICE_ACTIVE = "voice_active"  # New state for voice activity


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
    SPEAKING = ("speaking", "#00BCD4", "◍")


@dataclass
class EnhancedParticle:
    """Enhanced particle with physics and types"""
    x: float
    y: float
    z: float  # 3D depth
    symbol: str
    velocity_x: float
    velocity_y: float
    velocity_z: float
    lifetime: float
    max_lifetime: float
    color: str
    size: float = 1.0
    gravity: float = 0.0
    particle_type: str = "thought"  # thought, voice, network, learning


@dataclass
class NetworkStatus:
    """Network connectivity status"""
    connected: bool
    latency_ms: float
    signal_strength: float  # 0.0 to 1.0
    packets_sent: int
    packets_received: int


@dataclass
class LearningProgress:
    """Learning system progress tracking"""
    total_interactions: int
    successful_commands: int
    learning_rate: float  # 0.0 to 1.0
    knowledge_nodes: int
    active_patterns: int
    confidence_level: float  # 0.0 to 1.0


class EnhancedConsciousnessOrb(Widget):
    """
    Enhanced consciousness orb with advanced visualizations:
    - Voice activity waveforms
    - Complex particle physics
    - Network status indicators
    - Learning progress visualization
    - Sacred geometry patterns
    """
    
    # Reactive properties
    ai_state = reactive(AIState.IDLE)
    emotional_state = reactive(EmotionalState.NEUTRAL)
    breathing_rate = reactive(2.0)
    attention_level = reactive(0.5)
    coherence = reactive(0.8)
    
    # Voice activity
    voice_amplitude = reactive(0.0)  # 0.0 to 1.0
    voice_frequency = reactive(440.0)  # Hz
    voice_active = reactive(False)
    
    # Network status
    network_connected = reactive(True)
    network_latency = reactive(20.0)  # ms
    network_strength = reactive(0.9)  # 0.0 to 1.0
    
    # Learning progress
    learning_progress = reactive(0.3)  # 0.0 to 1.0
    knowledge_growth = reactive(0.0)  # Rate of learning
    
    # Animation properties
    phase = reactive(0.0)
    pulse_intensity = reactive(0.5)
    
    # Visual configuration
    MIN_SIZE = 3
    MAX_SIZE = 9  # Larger for complex visualizations
    
    # Enhanced Unicode characters
    ORB_SYMBOLS = {
        AIState.IDLE: ["○", "◯", "◉", "◎"],
        AIState.LISTENING: ["◉", "◎", "◉", "◎"],
        AIState.THINKING: ["◐", "◓", "◑", "◒"],
        AIState.SPEAKING: ["◉", "◈", "◉", "◈"],
        AIState.LEARNING: ["◈", "◇", "◆", "◊"],
        AIState.ERROR: ["⊗", "⊕", "⊗", "⊕"],
        AIState.FLOW: ["✦", "✧", "⋆", "✶"],
        AIState.VOICE_ACTIVE: ["◍", "◌", "◍", "◌"]
    }
    
    # Complex particle systems
    PARTICLE_CONFIGS = {
        "thought": {
            "symbols": ["·", "∴", "∵", "‥", "⁘"],
            "colors": ["#7E57C2", "#9C27B0", "#673AB7"],
            "gravity": 0.1,
            "lifetime": 3.0
        },
        "voice": {
            "symbols": ["♪", "♫", "♬", "♩", "~"],
            "colors": ["#00BCD4", "#0097A7", "#00ACC1"],
            "gravity": -0.2,  # Floats up
            "lifetime": 2.0
        },
        "network": {
            "symbols": ["⟷", "↔", "⇄", "⟵", "⟶"],
            "colors": ["#4CAF50", "#43A047", "#388E3C"],
            "gravity": 0.0,
            "lifetime": 4.0
        },
        "learning": {
            "symbols": ["✨", "★", "✦", "✧", "⋆"],
            "colors": ["#FFD700", "#FFC107", "#FF9800"],
            "gravity": 0.05,
            "lifetime": 5.0
        }
    }
    
    # Sacred geometry patterns
    SACRED_PATTERNS = {
        "merkaba": [(0, 1), (1, -0.5), (-1, -0.5)],  # Triangle
        "flower": [(0, 0)] + [(math.cos(i*math.pi/3), math.sin(i*math.pi/3)) for i in range(6)],
        "spiral": [(math.cos(t/2)*t/4, math.sin(t/2)*t/4) for t in range(0, 20)]
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles: List[EnhancedParticle] = []
        self.memory_nodes: List[Tuple[float, float, float]] = []
        self.voice_waveform: List[float] = [0.0] * 40  # Voice visualization buffer
        self.network_history: List[float] = [1.0] * 20  # Network status history
        self.learning_history: List[float] = [0.0] * 30  # Learning progress history
        self.sacred_geometry_phase = 0.0
        self.start_time = time.time()
        
    def on_mount(self) -> None:
        """Start animations when mounted"""
        self.set_interval(1/60, self.animate)  # 60fps
        self.set_interval(0.1, self.update_voice_waveform)  # 10Hz voice updates
        self.set_interval(1.0, self.update_network_status)  # 1Hz network updates
        self.set_interval(2.0, self.update_learning_progress)  # 0.5Hz learning updates
        self.animate_breathing()
        
    def animate(self) -> None:
        """Main animation loop at 60fps"""
        current_time = time.time() - self.start_time
        
        # Update phase for smooth animations
        self.phase = current_time * self.breathing_rate
        self.sacred_geometry_phase = current_time * 0.5  # Slower rotation
        
        # Update all particle systems
        self._update_particle_physics(1/60)
        
        # Spawn particles based on state
        self._spawn_state_particles()
        
        # Update sacred geometry if in flow state
        if self.ai_state == AIState.FLOW:
            self._update_sacred_geometry()
            
        # Force refresh for smooth animation
        self.refresh()
        
    def _update_particle_physics(self, dt: float) -> None:
        """Advanced particle physics simulation"""
        new_particles = []
        
        for particle in self.particles:
            # Apply gravity
            particle.velocity_y += particle.gravity * dt * 10
            
            # Update position
            particle.x += particle.velocity_x * dt
            particle.y += particle.velocity_y * dt
            particle.z += particle.velocity_z * dt
            
            # Apply drag
            drag = 0.98
            particle.velocity_x *= drag
            particle.velocity_y *= drag
            particle.velocity_z *= drag
            
            # Orbital forces for learning particles
            if particle.particle_type == "learning":
                # Orbit around center
                angle_to_center = math.atan2(particle.y, particle.x)
                orbital_force = 0.5
                particle.velocity_x -= math.cos(angle_to_center) * orbital_force * dt
                particle.velocity_y -= math.sin(angle_to_center) * orbital_force * dt
            
            # Network particles form connections
            if particle.particle_type == "network" and self.network_connected:
                for other in self.particles[:5]:  # Connect to nearby particles
                    if other != particle and other.particle_type == "network":
                        dx = other.x - particle.x
                        dy = other.y - particle.y
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < 10 and dist > 0:
                            # Attraction force
                            force = 0.2 / dist
                            particle.velocity_x += dx * force * dt
                            particle.velocity_y += dy * force * dt
            
            # Update lifetime
            particle.lifetime -= dt
            
            # Fade out
            if particle.lifetime < 0.5:
                particle.size = particle.lifetime * 2
            
            # Keep if still alive
            if particle.lifetime > 0:
                new_particles.append(particle)
                
        self.particles = new_particles
        
    def _spawn_state_particles(self) -> None:
        """Spawn particles based on current state"""
        spawn_rate = {
            AIState.IDLE: 0.02,
            AIState.THINKING: 0.1,
            AIState.LEARNING: 0.15,
            AIState.VOICE_ACTIVE: 0.2,
            AIState.FLOW: 0.3
        }.get(self.ai_state, 0.05)
        
        if random.random() < spawn_rate and len(self.particles) < 50:
            # Determine particle type
            if self.voice_active:
                self._spawn_voice_particle()
            elif self.ai_state == AIState.LEARNING:
                self._spawn_learning_particle()
            elif not self.network_connected:
                self._spawn_network_particle()
            else:
                self._spawn_thought_particle()
                
    def _spawn_voice_particle(self) -> None:
        """Spawn voice visualization particles"""
        config = self.PARTICLE_CONFIGS["voice"]
        
        # Emit from sides based on voice amplitude
        side = random.choice([-1, 1])
        x = side * (self.MAX_SIZE + 2)
        y = random.uniform(-3, 3) * self.voice_amplitude
        
        particle = EnhancedParticle(
            x=x,
            y=y,
            z=random.uniform(-2, 2),
            symbol=random.choice(config["symbols"]),
            velocity_x=-side * random.uniform(10, 20) * self.voice_amplitude,
            velocity_y=random.uniform(-5, 5),
            velocity_z=0,
            lifetime=config["lifetime"],
            max_lifetime=config["lifetime"],
            color=random.choice(config["colors"]),
            gravity=config["gravity"],
            particle_type="voice"
        )
        self.particles.append(particle)
        
    def _spawn_learning_particle(self) -> None:
        """Spawn learning progress particles"""
        config = self.PARTICLE_CONFIGS["learning"]
        
        # Spiral emission pattern
        angle = self.phase * 2
        radius = 5 + self.learning_progress * 10
        
        particle = EnhancedParticle(
            x=math.cos(angle) * radius,
            y=math.sin(angle) * radius,
            z=random.uniform(-1, 1),
            symbol=random.choice(config["symbols"]),
            velocity_x=math.cos(angle) * 5,
            velocity_y=math.sin(angle) * 5,
            velocity_z=random.uniform(-1, 1),
            lifetime=config["lifetime"],
            max_lifetime=config["lifetime"],
            color=random.choice(config["colors"]),
            gravity=config["gravity"],
            particle_type="learning",
            size=0.5 + self.learning_progress * 0.5
        )
        self.particles.append(particle)
        
    def _spawn_network_particle(self) -> None:
        """Spawn network status particles"""
        config = self.PARTICLE_CONFIGS["network"]
        
        # Emit from random positions
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(8, 12)
        
        particle = EnhancedParticle(
            x=math.cos(angle) * dist,
            y=math.sin(angle) * dist,
            z=0,
            symbol=random.choice(config["symbols"]),
            velocity_x=random.uniform(-5, 5),
            velocity_y=random.uniform(-5, 5),
            velocity_z=0,
            lifetime=config["lifetime"],
            max_lifetime=config["lifetime"],
            color=config["colors"][0] if self.network_connected else "#F44336",
            gravity=config["gravity"],
            particle_type="network"
        )
        self.particles.append(particle)
        
    def _spawn_thought_particle(self) -> None:
        """Spawn standard thought particles"""
        config = self.PARTICLE_CONFIGS["thought"]
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(5, 15)
        
        particle = EnhancedParticle(
            x=0,
            y=0,
            z=0,
            symbol=random.choice(config["symbols"]),
            velocity_x=math.cos(angle) * speed,
            velocity_y=math.sin(angle) * speed,
            velocity_z=random.uniform(-2, 2),
            lifetime=config["lifetime"],
            max_lifetime=config["lifetime"],
            color=random.choice(config["colors"]),
            gravity=config["gravity"],
            particle_type="thought"
        )
        self.particles.append(particle)
        
    def update_voice_waveform(self) -> None:
        """Update voice activity waveform"""
        if self.voice_active:
            # Simulate voice waveform
            new_sample = math.sin(time.time() * self.voice_frequency) * self.voice_amplitude
            new_sample += random.uniform(-0.1, 0.1) * self.voice_amplitude  # Add noise
            
            self.voice_waveform = self.voice_waveform[1:] + [new_sample]
        else:
            # Decay to silence
            self.voice_waveform = [v * 0.9 for v in self.voice_waveform]
            
    def update_network_status(self) -> None:
        """Update network connectivity visualization"""
        # Simulate network fluctuations
        if self.network_connected:
            self.network_strength = min(1.0, max(0.3, 
                self.network_strength + random.uniform(-0.1, 0.1)))
            self.network_latency = max(5, min(200,
                self.network_latency + random.uniform(-10, 10)))
        
        # Update history
        self.network_history = self.network_history[1:] + [self.network_strength]
        
    def update_learning_progress(self) -> None:
        """Update learning system visualization"""
        # Simulate learning progress
        if self.ai_state == AIState.LEARNING:
            self.learning_progress = min(1.0, self.learning_progress + 0.02)
            self.knowledge_growth = 0.1
        else:
            self.knowledge_growth *= 0.9
            
        # Update history
        self.learning_history = self.learning_history[1:] + [self.learning_progress]
        
    def _update_sacred_geometry(self) -> None:
        """Update sacred geometry patterns in flow state"""
        # Create rotating sacred geometry
        pattern = self.SACRED_PATTERNS["flower"]
        
        for i, (x, y) in enumerate(pattern):
            if len(self.particles) < 100:  # Limit total particles
                # Rotate pattern
                angle = self.sacred_geometry_phase + i * math.pi / 3
                rx = x * math.cos(angle) - y * math.sin(angle)
                ry = x * math.sin(angle) + y * math.cos(angle)
                
                # Scale based on coherence
                scale = 10 * self.coherence
                
                particle = EnhancedParticle(
                    x=rx * scale,
                    y=ry * scale,
                    z=math.sin(angle) * 2,
                    symbol="✦",
                    velocity_x=0,
                    velocity_y=0,
                    velocity_z=0,
                    lifetime=0.5,
                    max_lifetime=0.5,
                    color="#26A69A",
                    gravity=0,
                    particle_type="sacred",
                    size=self.coherence
                )
                self.particles.append(particle)
                
    def render_enhanced_orb(self) -> List[str]:
        """Render the enhanced orb with all visualizations"""
        size = self.calculate_orb_size()
        lines = []
        
        # Calculate view bounds
        view_width = size * 4 + 20  # Extra space for indicators
        view_height = size * 2 + 10
        
        # Create empty canvas
        canvas = [[' ' for _ in range(view_width)] for _ in range(view_height)]
        
        # Center coordinates
        cx = view_width // 2
        cy = view_height // 2
        
        # Draw main orb
        orb_char = self.get_orb_character()
        for y in range(-size, size + 1):
            for x in range(-size * 2, size * 2 + 1):
                dist = math.sqrt((x/2)**2 + y**2)
                
                char = None
                if dist < size * 0.3:
                    char = orb_char
                elif dist < size * 0.6:
                    char = "◉" if self.ai_state == AIState.LISTENING else "◎"
                elif dist < size:
                    char = "·"
                    
                if char and 0 <= cy + y < view_height and 0 <= cx + x < view_width:
                    canvas[cy + y][cx + x] = char
        
        # Draw particles with 3D perspective
        for particle in self.particles:
            # Apply perspective based on z-coordinate
            perspective = 1.0 / (1.0 + particle.z * 0.1)
            px = int(cx + particle.x * perspective)
            py = int(cy + particle.y * perspective)
            
            if 0 <= px < view_width and 0 <= py < view_height:
                # Size based on z-depth
                if particle.size > 0.7 or particle.z > 0:
                    canvas[py][px] = particle.symbol
                    
        # Draw voice waveform on the left
        if self.voice_active or any(abs(v) > 0.01 for v in self.voice_waveform):
            waveform_x = 5
            for i, amplitude in enumerate(self.voice_waveform[-20:]):
                y = cy + int(amplitude * 5)
                if 0 <= y < view_height and waveform_x + i < view_width:
                    canvas[y][waveform_x + i] = "█" if abs(amplitude) > 0.5 else "▓"
                    
        # Draw network status indicator on the right
        net_x = view_width - 25
        if self.network_connected:
            signal_bars = int(self.network_strength * 5)
            for i in range(5):
                if i < signal_bars:
                    canvas[cy - 2 + i][net_x] = "▃▄▅▆█"[i]
            # Latency indicator
            lat_color = "🟢" if self.network_latency < 50 else "🟡" if self.network_latency < 100 else "🔴"
            if net_x + 2 < view_width:
                canvas[cy][net_x + 2] = lat_color[0] if len(lat_color) == 1 else "●"
        else:
            canvas[cy][net_x] = "❌"
            
        # Draw learning progress bar at the bottom
        if self.learning_progress > 0:
            bar_y = cy + size + 2
            bar_width = 30
            bar_start = cx - bar_width // 2
            
            if bar_y < view_height:
                filled = int(self.learning_progress * bar_width)
                for i in range(bar_width):
                    if bar_start + i < view_width:
                        if i < filled:
                            canvas[bar_y][bar_start + i] = "█"
                        else:
                            canvas[bar_y][bar_start + i] = "░"
                            
        # Convert canvas to strings
        for row in canvas:
            lines.append(''.join(row))
            
        return lines
        
    def calculate_orb_size(self) -> int:
        """Calculate orb size with enhanced states"""
        base_size = self.MIN_SIZE + (self.MAX_SIZE - self.MIN_SIZE) * self.attention_level
        
        # State modifiers
        if self.ai_state == AIState.FLOW:
            base_size *= 1.2
        elif self.ai_state == AIState.VOICE_ACTIVE:
            base_size *= 1.1
            
        # Breathing effect
        breath = math.sin(self.phase * math.pi) * 0.5 + 0.5
        size_mod = 1.0 + breath * self.pulse_intensity * 0.3
        
        return int(base_size * size_mod)
        
    def render(self) -> RenderResult:
        """Render the complete enhanced consciousness orb"""
        # Get enhanced ASCII representation
        orb_lines = self.render_enhanced_orb()
        
        # Create rich text with color
        orb_text = Text("\n".join(orb_lines), style=self.get_orb_color())
        
        # Add status indicators
        status_parts = []
        
        if self.voice_active:
            status_parts.append(Text("🎤 Voice Active", style="cyan"))
            
        if not self.network_connected:
            status_parts.append(Text("🔌 Offline", style="red"))
        elif self.network_latency > 100:
            status_parts.append(Text(f"⚡ {self.network_latency:.0f}ms", style="yellow"))
            
        if self.ai_state == AIState.LEARNING:
            progress_pct = self.learning_progress * 100
            status_parts.append(Text(f"🧠 Learning {progress_pct:.0f}%", style="blue"))
            
        if self.ai_state == AIState.FLOW:
            status_parts.append(Text("🌊 Flow State Active", style="green"))
            
        # Combine all elements
        combined = Text()
        combined.append(orb_text)
        
        if status_parts:
            combined.append("\n\n")
            combined.append(" | ".join(str(part) for part in status_parts))
            
        # Center everything
        centered = Align.center(combined, vertical="middle")
        
        # Add panel in special states
        if self.ai_state == AIState.FLOW:
            return Panel(
                centered,
                border_style="green",
                title="✨ Sacred Consciousness Field ✨",
                title_align="center"
            )
        elif self.voice_active:
            return Panel(
                centered,
                border_style="cyan",
                title="🎤 Voice Interaction Active 🎤",
                title_align="center"
            )
        else:
            return centered
            
    def set_voice_activity(self, active: bool, amplitude: float = 0.5, frequency: float = 440):
        """Update voice activity state"""
        self.voice_active = active
        self.voice_amplitude = amplitude
        self.voice_frequency = frequency
        
        if active:
            self.ai_state = AIState.VOICE_ACTIVE
            self.emotional_state = EmotionalState.SPEAKING
        else:
            self.ai_state = AIState.IDLE
            
    def set_network_status(self, connected: bool, latency: float = 20, strength: float = 0.9):
        """Update network connectivity status"""
        self.network_connected = connected
        self.network_latency = latency
        self.network_strength = strength
        
    def set_learning_progress(self, progress: float, growth_rate: float = 0.0):
        """Update learning system progress"""
        self.learning_progress = max(0.0, min(1.0, progress))
        self.knowledge_growth = growth_rate
        
        if growth_rate > 0:
            self.ai_state = AIState.LEARNING
            self.emotional_state = EmotionalState.LEARNING
            
    def get_orb_character(self) -> str:
        """Get current orb character based on animation phase"""
        symbols = self.ORB_SYMBOLS[self.ai_state]
        index = int(self.phase * 2) % len(symbols)
        return symbols[index]
        
    def get_orb_color(self) -> str:
        """Get current color based on emotional state"""
        _, color, _ = self.emotional_state.value
        return color