"""
from typing import Tuple, List, Optional
🎉 Celebration Effects for Different Operation Types

Visual celebrations that match the operation's nature and speed.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional
import math
import random


class CelebrationStyle(Enum):
    """Different celebration styles for operations"""
    INSTANT = "instant"           # Lightning fast (<100ms)
    FAST = "fast"                # Quick operations (<1s)
    SUCCESSFUL = "successful"     # Normal success (1-5s)
    LEARNING = "learning"        # Knowledge gained
    BUILDING = "building"        # Building/compiling
    CLEANING = "cleaning"        # Garbage collection
    ROLLBACK = "rollback"        # System rollback
    ERROR_RECOVERY = "recovery"  # Recovered from error
    FLOW_ACHIEVED = "flow"       # Entered flow state
    MILESTONE = "milestone"      # Special achievement


@dataclass
class CelebrationConfig:
    """Configuration for a celebration effect"""
    style: CelebrationStyle
    duration: float
    particle_count: int
    particle_symbols: List[str]
    particle_colors: List[str]
    orb_pulse_intensity: float
    special_pattern: Optional[str] = None
    sound_effect: Optional[str] = None  # For future audio


class CelebrationEffects:
    """Manages celebration effects for different operation types"""
    
    CELEBRATIONS = {
        CelebrationStyle.INSTANT: CelebrationConfig(
            style=CelebrationStyle.INSTANT,
            duration=1.5,
            particle_count=20,
            particle_symbols=["⚡", "✦", "◉", "◎", "⋆"],
            particle_colors=["#00FFFF", "#00E5FF", "#00CED1", "#00BFFF"],
            orb_pulse_intensity=1.0,
            special_pattern="lightning_burst",
            sound_effect="electric_zap"
        ),
        
        CelebrationStyle.FAST: CelebrationConfig(
            style=CelebrationStyle.FAST,
            duration=1.0,
            particle_count=15,
            particle_symbols=["🚀", "↑", "▲", "△", "⬆"],
            particle_colors=["#32CD32", "#00FF00", "#7FFF00", "#ADFF2F"],
            orb_pulse_intensity=0.8,
            special_pattern="rocket_trail",
            sound_effect="whoosh"
        ),
        
        CelebrationStyle.SUCCESSFUL: CelebrationConfig(
            style=CelebrationStyle.SUCCESSFUL,
            duration=2.0,
            particle_count=10,
            particle_symbols=["✓", "✔", "✅", "●", "◆"],
            particle_colors=["#228B22", "#008000", "#006400", "#2E8B57"],
            orb_pulse_intensity=0.6,
            special_pattern="success_ripple",
            sound_effect="success_chime"
        ),
        
        CelebrationStyle.LEARNING: CelebrationConfig(
            style=CelebrationStyle.LEARNING,
            duration=3.0,
            particle_count=25,
            particle_symbols=["🧠", "💡", "📚", "✨", "★"],
            particle_colors=["#FFD700", "#FFA500", "#FF8C00", "#FF6347"],
            orb_pulse_intensity=0.7,
            special_pattern="knowledge_spiral",
            sound_effect="enlightenment"
        ),
        
        CelebrationStyle.BUILDING: CelebrationConfig(
            style=CelebrationStyle.BUILDING,
            duration=2.5,
            particle_count=30,
            particle_symbols=["🔨", "🔧", "⚙", "◧", "◨"],
            particle_colors=["#4682B4", "#4169E1", "#0000CD", "#191970"],
            orb_pulse_intensity=0.5,
            special_pattern="construction_grid",
            sound_effect="construction"
        ),
        
        CelebrationStyle.CLEANING: CelebrationConfig(
            style=CelebrationStyle.CLEANING,
            duration=2.0,
            particle_count=20,
            particle_symbols=["🧹", "✧", "◇", "◈", "⬡"],
            particle_colors=["#E6E6FA", "#D8BFD8", "#DDA0DD", "#EE82EE"],
            orb_pulse_intensity=0.6,
            special_pattern="cleanup_wave",
            sound_effect="sweep"
        ),
        
        CelebrationStyle.ROLLBACK: CelebrationConfig(
            style=CelebrationStyle.ROLLBACK,
            duration=2.0,
            particle_count=15,
            particle_symbols=["↺", "↻", "⟲", "⟳", "◐"],
            particle_colors=["#FF6B6B", "#FFA06B", "#FFD06B", "#FFEB6B"],
            orb_pulse_intensity=0.8,
            special_pattern="time_rewind",
            sound_effect="rewind"
        ),
        
        CelebrationStyle.ERROR_RECOVERY: CelebrationConfig(
            style=CelebrationStyle.ERROR_RECOVERY,
            duration=1.5,
            particle_count=12,
            particle_symbols=["🔄", "↻", "✓", "◎", "○"],
            particle_colors=["#FF4444", "#FF6666", "#FF8888", "#FFAAAA"],
            orb_pulse_intensity=0.7,
            special_pattern="phoenix_rise",
            sound_effect="recovery_bell"
        ),
        
        CelebrationStyle.FLOW_ACHIEVED: CelebrationConfig(
            style=CelebrationStyle.FLOW_ACHIEVED,
            duration=4.0,
            particle_count=50,
            particle_symbols=["🌊", "≈", "∼", "≋", "∿", "〜", "～"],
            particle_colors=["#00CED1", "#48D1CC", "#40E0D0", "#00FFFF"],
            orb_pulse_intensity=1.0,
            special_pattern="sacred_mandala",
            sound_effect="ocean_wave"
        ),
        
        CelebrationStyle.MILESTONE: CelebrationConfig(
            style=CelebrationStyle.MILESTONE,
            duration=5.0,
            particle_count=100,
            particle_symbols=["🌟", "⭐", "✨", "💫", "🎆", "🎇"],
            particle_colors=["#FFD700", "#FFC700", "#FFB700", "#FFA700"],
            orb_pulse_intensity=1.0,
            special_pattern="fireworks",
            sound_effect="achievement_fanfare"
        )
    }
    
    @classmethod
    def get_celebration_for_operation(cls, operation: str, duration_ms: float) -> CelebrationConfig:
        """Determine appropriate celebration based on operation and speed"""
        
        # Instant operations
        if duration_ms < 100:
            return cls.CELEBRATIONS[CelebrationStyle.INSTANT]
            
        # Fast operations
        elif duration_ms < 1000:
            return cls.CELEBRATIONS[CelebrationStyle.FAST]
            
        # Special operation types
        elif "learn" in operation.lower():
            return cls.CELEBRATIONS[CelebrationStyle.LEARNING]
        elif "build" in operation.lower() or "compile" in operation.lower():
            return cls.CELEBRATIONS[CelebrationStyle.BUILDING]
        elif "clean" in operation.lower() or "garbage" in operation.lower():
            return cls.CELEBRATIONS[CelebrationStyle.CLEANING]
        elif "rollback" in operation.lower():
            return cls.CELEBRATIONS[CelebrationStyle.ROLLBACK]
        elif "recover" in operation.lower():
            return cls.CELEBRATIONS[CelebrationStyle.ERROR_RECOVERY]
            
        # Default successful operation
        else:
            return cls.CELEBRATIONS[CelebrationStyle.SUCCESSFUL]
            
    @classmethod
    def get_milestone_celebration(cls, milestone_type: str) -> CelebrationConfig:
        """Get special milestone celebrations"""
        milestone_map = {
            "first_instant": CelebrationStyle.MILESTONE,
            "10_commands": CelebrationStyle.MILESTONE,
            "flow_state": CelebrationStyle.FLOW_ACHIEVED,
            "learning_complete": CelebrationStyle.LEARNING,
            "100_operations": CelebrationStyle.MILESTONE
        }
        
        style = milestone_map.get(milestone_type, CelebrationStyle.SUCCESSFUL)
        return cls.CELEBRATIONS[style]
        
    @staticmethod
    def create_special_pattern(pattern_name: str, center_x: int, center_y: int) -> List[Tuple[int, int, str]]:
        """Create special particle patterns"""
        particles = []
        
        if pattern_name == "lightning_burst":
            # Lightning bolt pattern
            for i in range(8):
                angle = i * math.pi / 4
                for j in range(1, 4):
                    x = center_x + int(math.cos(angle) * j * 10)
                    y = center_y + int(math.sin(angle) * j * 5)
                    particles.append((x, y, "⚡"))
                    
        elif pattern_name == "rocket_trail":
            # Upward rocket trail
            for i in range(10):
                x = center_x + random.randint(-2, 2)
                y = center_y + i * 2
                particles.append((x, y, "🚀" if i == 0 else "▲"))
                
        elif pattern_name == "success_ripple":
            # Expanding ripples
            for radius in [5, 10, 15]:
                for i in range(12):
                    angle = i * math.pi / 6
                    x = center_x + int(math.cos(angle) * radius)
                    y = center_y + int(math.sin(angle) * radius / 2)
                    particles.append((x, y, "✓"))
                    
        elif pattern_name == "knowledge_spiral":
            # Spiral pattern
            for i in range(20):
                angle = i * math.pi / 4
                radius = i * 2
                x = center_x + int(math.cos(angle) * radius)
                y = center_y + int(math.sin(angle) * radius / 2)
                particles.append((x, y, "✨"))
                
        elif pattern_name == "construction_grid":
            # Grid pattern
            for dx in [-10, -5, 0, 5, 10]:
                for dy in [-5, 0, 5]:
                    x = center_x + dx
                    y = center_y + dy
                    particles.append((x, y, "⚙"))
                    
        elif pattern_name == "cleanup_wave":
            # Wave pattern
            for i in range(15):
                x = center_x - 20 + i * 3
                y = center_y + int(math.sin(i * 0.5) * 5)
                particles.append((x, y, "✧"))
                
        elif pattern_name == "time_rewind":
            # Counterclockwise spiral
            for i in range(15):
                angle = -i * math.pi / 4
                radius = 15 - i
                x = center_x + int(math.cos(angle) * radius)
                y = center_y + int(math.sin(angle) * radius / 2)
                particles.append((x, y, "↺"))
                
        elif pattern_name == "phoenix_rise":
            # Rising phoenix shape
            for i in range(10):
                x1 = center_x - i
                x2 = center_x + i
                y = center_y - i * 2
                particles.append((x1, y, "🔄"))
                particles.append((x2, y, "🔄"))
                
        elif pattern_name == "sacred_mandala":
            # Mandala pattern
            for ring in range(3):
                radius = (ring + 1) * 10
                points = (ring + 1) * 6
                for i in range(points):
                    angle = i * 2 * math.pi / points
                    x = center_x + int(math.cos(angle) * radius)
                    y = center_y + int(math.sin(angle) * radius / 2)
                    particles.append((x, y, "≈"))
                    
        elif pattern_name == "fireworks":
            # Fireworks explosion
            for burst in range(3):
                cx = center_x + random.randint(-20, 20)
                cy = center_y + random.randint(-10, 10)
                for i in range(20):
                    angle = random.uniform(0, 2 * math.pi)
                    radius = random.uniform(5, 20)
                    x = cx + int(math.cos(angle) * radius)
                    y = cy + int(math.sin(angle) * radius / 2)
                    particles.append((x, y, random.choice(["🌟", "✨", "💫"])))
                    
        return particles


class MilestoneTracker:
    """Tracks user milestones for special celebrations"""
    
    def __init__(self):
        self.stats = {
            "total_commands": 0,
            "instant_operations": 0,
            "successful_operations": 0,
            "flow_states_achieved": 0,
            "learning_sessions": 0,
            "errors_recovered": 0
        }
        self.achieved_milestones = set()
        
    def record_operation(self, operation: str, duration_ms: float, success: bool) -> Optional[str]:
        """Record an operation and check for milestones"""
        self.stats["total_commands"] += 1
        
        if success:
            self.stats["successful_operations"] += 1
            
            if duration_ms < 100:
                self.stats["instant_operations"] += 1
                
                # First instant operation milestone
                if self.stats["instant_operations"] == 1 and "first_instant" not in self.achieved_milestones:
                    self.achieved_milestones.add("first_instant")
                    return "first_instant"
                    
        # Check other milestones
        if self.stats["total_commands"] == 10 and "10_commands" not in self.achieved_milestones:
            self.achieved_milestones.add("10_commands")
            return "10_commands"
            
        if self.stats["total_commands"] == 100 and "100_operations" not in self.achieved_milestones:
            self.achieved_milestones.add("100_operations")
            return "100_operations"
            
        return None
        
    def record_flow_state(self):
        """Record achievement of flow state"""
        self.stats["flow_states_achieved"] += 1
        
    def record_learning(self):
        """Record a learning session"""
        self.stats["learning_sessions"] += 1