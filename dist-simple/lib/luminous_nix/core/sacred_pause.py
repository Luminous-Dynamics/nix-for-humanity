"""
Sacred Pause - Mindful interaction with system changes
A practical implementation of consciousness-first principles
"""

import time
import sys
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class SacredPauseConfig:
    """Configuration for sacred pause behavior"""
    enabled: bool = True
    duration: float = 3.0  # seconds
    show_breathing_guide: bool = True
    progressive_reduction: bool = True  # Reduce pause as user gains expertise
    
    
class SacredPause:
    """
    Implements mindful pauses before significant operations.
    
    Philosophy meets practice:
    - Prevents accidental destructive operations
    - Creates space for intention-setting
    - Reduces anxiety around system changes
    - Gradually disappears as user gains confidence
    """
    
    def __init__(self, config: Optional[SacredPauseConfig] = None):
        self.config = config or SacredPauseConfig()
        self.operation_count = 0
        self.user_expertise_level = 0
        
    def before_operation(self, operation: str, impact: str = "medium") -> None:
        """
        Sacred pause before an operation.
        
        Args:
            operation: Description of what's about to happen
            impact: "low", "medium", "high" - determines pause behavior
        """
        if not self.config.enabled:
            return
            
        # Calculate pause duration based on impact and user expertise
        base_duration = {
            "low": 1.0,
            "medium": 3.0,
            "high": 5.0
        }.get(impact, 3.0)
        
        # Progressive reduction: reduce by 10% for every 10 operations
        if self.config.progressive_reduction:
            reduction = min(0.5, self.operation_count / 100.0)
            actual_duration = base_duration * (1 - reduction)
        else:
            actual_duration = base_duration
            
        # Skip very short pauses (user is expert)
        if actual_duration < 0.5:
            return
            
        # Display the pause
        self._show_pause(operation, actual_duration)
        
        # Increment operation count
        self.operation_count += 1
        
    def _show_pause(self, operation: str, duration: float) -> None:
        """Display the sacred pause with optional breathing guide"""
        
        print(f"\n🌟 Preparing to: {operation}")
        
        if self.config.show_breathing_guide and duration >= 3.0:
            # Three breaths for significant operations
            breaths = int(duration / 3)
            for i in range(breaths):
                print(f"   {'🫁' if i == 0 else '  '} Breath {i+1}: ", end="")
                
                # Inhale phase
                for _ in range(3):
                    print("·", end="", flush=True)
                    time.sleep(0.5)
                print(" in ", end="")
                
                # Exhale phase
                for _ in range(3):
                    print("·", end="", flush=True)
                    time.sleep(0.5)
                print(" out")
        else:
            # Simple progress dots for shorter pauses
            steps = int(duration * 2)
            print("   ", end="")
            for _ in range(steps):
                print("·", end="", flush=True)
                time.sleep(0.5)
            print()
            
        print("   ✨ Ready\n")
        
    def reflection_moment(self, result: str, success: bool) -> None:
        """
        Brief moment of reflection after an operation completes.
        
        This is where "Chamber of Reflection" becomes practical:
        - Acknowledge what happened
        - Learn from success or failure
        - Build user confidence
        """
        if not self.config.enabled:
            return
            
        if success:
            # Positive reinforcement builds confidence
            messages = [
                "✅ Operation completed successfully",
                "🌱 Your system grows with intention",
                "💫 Change applied mindfully",
            ]
            print(messages[self.operation_count % len(messages)])
        else:
            # Failures are teachers
            print("🔍 The system teaches through this moment")
            print(f"   Learning: {result}")
            
    def set_user_expertise(self, level: int) -> None:
        """
        Adjust behavior based on user expertise.
        Part of the "Disappearing Path" philosophy.
        
        Args:
            level: 0 (beginner) to 100 (expert)
        """
        self.user_expertise_level = level
        
        # Experts barely see pauses
        if level > 80:
            self.config.duration = 0.5
            self.config.show_breathing_guide = False
        # Intermediate users get shorter pauses
        elif level > 50:
            self.config.duration = 1.5
        # Beginners get full mindful experience
        else:
            self.config.duration = 3.0
            self.config.show_breathing_guide = True


# Global instance for easy use
sacred_pause = SacredPause()


def with_sacred_pause(operation: str, impact: str = "medium"):
    """
    Decorator for adding sacred pause to functions.
    
    Example:
        @with_sacred_pause("Installing Firefox", impact="low")
        def install_firefox():
            # ... installation code ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            sacred_pause.before_operation(operation, impact)
            result = func(*args, **kwargs)
            success = result.get('success', False) if isinstance(result, dict) else True
            sacred_pause.reflection_moment(str(result), success)
            return result
        return wrapper
    return decorator