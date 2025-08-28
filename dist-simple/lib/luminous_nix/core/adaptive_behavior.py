"""
Adaptive behavior system - Learn from users, don't categorize them.

This replaces the static persona system with dynamic adaptation based on 
observed behavior patterns. Every user is unique.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path
from enum import Enum
import math


class ObservationType(Enum):
    """Types of user behavior we observe"""
    COMMAND_EXECUTED = "command_executed"
    PREVIEW_READ = "preview_read"
    HELP_REQUESTED = "help_requested"
    ERROR_ENCOUNTERED = "error_encountered"
    ERROR_RECOVERED = "error_recovered"
    CONFIRMATION_SPEED = "confirmation_speed"
    DOCUMENTATION_READ = "documentation_read"
    COMMAND_MODIFIED = "command_modified"
    EXPLORATION = "exploration"
    COMPLETION_USED = "completion_used"


@dataclass
class Observation:
    """A single observed user behavior"""
    type: ObservationType
    timestamp: datetime
    details: Dict = field(default_factory=dict)
    context: Dict = field(default_factory=dict)


@dataclass
class AdaptiveProfile:
    """Dynamic user profile that evolves with behavior"""
    
    # Core adaptation dimensions (0.0 to 1.0)
    technical_level: float = 0.5      # 0=beginner, 1=expert
    speed_preference: float = 0.5     # 0=deliberate, 1=fast
    detail_preference: float = 0.5    # 0=minimal, 1=comprehensive
    risk_tolerance: float = 0.2       # 0=cautious, 1=confident
    exploration_tendency: float = 0.5 # 0=focused, 1=exploratory
    
    # Learned patterns
    error_recovery_skill: float = 0.3
    command_complexity_comfort: float = 0.3
    documentation_engagement: float = 0.5
    
    # Behavioral velocity (how fast they're learning/changing)
    learning_rate: float = 0.5
    adaptation_speed: float = 0.5
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for persistence"""
        return {
            'technical_level': self.technical_level,
            'speed_preference': self.speed_preference,
            'detail_preference': self.detail_preference,
            'risk_tolerance': self.risk_tolerance,
            'exploration_tendency': self.exploration_tendency,
            'error_recovery_skill': self.error_recovery_skill,
            'command_complexity_comfort': self.command_complexity_comfort,
            'documentation_engagement': self.documentation_engagement,
            'learning_rate': self.learning_rate,
            'adaptation_speed': self.adaptation_speed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AdaptiveProfile':
        """Create from dictionary"""
        return cls(**data)


class AdaptiveBehaviorSystem:
    """
    Learn from user behavior instead of categorizing them.
    
    This system observes how users interact with the tool and continuously
    adapts the interface, safety levels, and assistance provided.
    
    Philosophy:
    - No two users are alike
    - Behavior reveals preference better than stated choice
    - Safety should match demonstrated competence
    - The interface should disappear as mastery grows
    """
    
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or "default"
        self.profile = AdaptiveProfile()
        self.observations: List[Observation] = []
        self.session_start = datetime.now()
        
        # Load existing profile if available
        self.profile_path = Path.home() / ".luminous-nix" / "adaptive" / f"{self.user_id}.json"
        self._load_profile()
        
        # Adaptation parameters
        self.min_observations_for_adaptation = 5
        self.adaptation_rate = 0.1  # How fast we adjust
        self.confidence_threshold = 0.7  # When we're confident in our model
        
    def observe(self, 
                action_type: ObservationType,
                details: Optional[Dict] = None,
                context: Optional[Dict] = None):
        """Record a user behavior observation"""
        
        observation = Observation(
            type=action_type,
            timestamp=datetime.now(),
            details=details or {},
            context=context or {}
        )
        
        self.observations.append(observation)
        
        # Adapt profile based on observation
        self._adapt_profile(observation)
        
        # Persist every N observations
        if len(self.observations) % 10 == 0:
            self._save_profile()
    
    def _adapt_profile(self, observation: Observation):
        """Adjust profile based on observed behavior"""
        
        # Learning rate decay - adapt slower as we learn more
        decay = 1.0 / (1.0 + len(self.observations) * 0.01)
        rate = self.adaptation_rate * decay
        
        if observation.type == ObservationType.COMMAND_EXECUTED:
            # Fast command execution suggests higher technical level
            if observation.details.get('time_to_execute', 999) < 5:
                self.profile.speed_preference = min(1.0, 
                    self.profile.speed_preference + rate)
                self.profile.technical_level = min(1.0,
                    self.profile.technical_level + rate * 0.5)
                
        elif observation.type == ObservationType.PREVIEW_READ:
            # Reading previews suggests caution
            read_time = observation.details.get('read_time', 0)
            if read_time > 3:
                self.profile.risk_tolerance = max(0.0,
                    self.profile.risk_tolerance - rate * 0.5)
                self.profile.detail_preference = min(1.0,
                    self.profile.detail_preference + rate)
                    
        elif observation.type == ObservationType.HELP_REQUESTED:
            # Asking for help adjusts technical level
            self.profile.technical_level = max(0.0,
                self.profile.technical_level - rate)
            self.profile.documentation_engagement = min(1.0,
                self.profile.documentation_engagement + rate)
                
        elif observation.type == ObservationType.ERROR_RECOVERED:
            # Successfully recovering from errors builds confidence
            self.profile.error_recovery_skill = min(1.0,
                self.profile.error_recovery_skill + rate)
            self.profile.technical_level = min(1.0,
                self.profile.technical_level + rate * 0.3)
                
        elif observation.type == ObservationType.EXPLORATION:
            # Exploring new commands shows curiosity
            self.profile.exploration_tendency = min(1.0,
                self.profile.exploration_tendency + rate)
                
        # Update learning velocity
        self._update_learning_velocity()
    
    def _update_learning_velocity(self):
        """Track how fast the user is learning/changing"""
        recent = self.observations[-20:] if len(self.observations) > 20 else self.observations
        
        if len(recent) > 5:
            # Calculate rate of successful actions
            successes = sum(1 for o in recent 
                          if o.type in [ObservationType.COMMAND_EXECUTED,
                                      ObservationType.ERROR_RECOVERED])
            self.profile.learning_rate = successes / len(recent)
    
    def should_show_preview(self, command: str) -> bool:
        """Determine if we should show preview based on profile"""
        
        # Always preview if low confidence in our model
        if len(self.observations) < self.min_observations_for_adaptation:
            return True
            
        # Always preview risky commands
        if self._is_risky_command(command):
            return True
            
        # Preview based on user's demonstrated caution
        return self.profile.risk_tolerance < 0.6
    
    def should_request_confirmation(self, command: str) -> bool:
        """Determine if confirmation is needed"""
        
        # Always confirm destructive operations
        if any(word in command for word in ['remove', 'delete', 'uninstall']):
            return True
            
        # Confirm based on user's risk tolerance and technical level
        confidence = (self.profile.technical_level + self.profile.risk_tolerance) / 2
        return confidence < self.confidence_threshold
    
    def get_explanation_level(self) -> str:
        """Determine appropriate explanation detail level"""
        
        if self.profile.technical_level < 0.3:
            return "simple"  # Plain language, no jargon
        elif self.profile.technical_level < 0.7:
            return "moderate"  # Some technical terms with explanation
        else:
            return "technical"  # Full technical details
    
    def get_interface_mode(self) -> Dict[str, any]:
        """Get current interface adaptation settings"""
        
        return {
            'show_tips': self.profile.technical_level < 0.5,
            'verbose_errors': self.profile.error_recovery_skill < 0.5,
            'auto_complete': self.profile.speed_preference > 0.6,
            'show_previews': self.should_show_preview("default"),
            'explanation_level': self.get_explanation_level(),
            'require_confirmation': self.profile.risk_tolerance < 0.5,
            'show_progress': self.profile.detail_preference > 0.3,
            'learning_mode': self.profile.learning_rate > 0.6,
        }
    
    def suggest_next_action(self) -> Optional[str]:
        """Suggest what the user might want to do next"""
        
        if not self.observations:
            return "Try 'ask-nix help' to see what I can do"
            
        last_action = self.observations[-1]
        
        if last_action.type == ObservationType.ERROR_ENCOUNTERED:
            return "Would you like help understanding that error?"
        elif last_action.type == ObservationType.HELP_REQUESTED:
            return "Try a simple command like 'ask-nix search firefox'"
        elif self.profile.exploration_tendency > 0.7:
            return "Explore available packages with 'ask-nix discover'"
            
        return None
    
    def _is_risky_command(self, command: str) -> bool:
        """Determine if a command is potentially risky"""
        risky_patterns = [
            'sudo', 'remove', 'delete', 'uninstall',
            'system', 'rebuild', 'switch', 'rollback',
            'format', 'partition', 'rm -rf'
        ]
        return any(pattern in command.lower() for pattern in risky_patterns)
    
    def _save_profile(self):
        """Persist profile to disk"""
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'user_id': self.user_id,
            'profile': self.profile.to_dict(),
            'observation_count': len(self.observations),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.profile_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_profile(self):
        """Load existing profile from disk"""
        if self.profile_path.exists():
            try:
                with open(self.profile_path, 'r') as f:
                    data = json.load(f)
                    self.profile = AdaptiveProfile.from_dict(data['profile'])
            except Exception:
                # If loading fails, start fresh
                pass
    
    def get_status(self) -> str:
        """Get human-readable status of adaptation"""
        
        observations = len(self.observations)
        
        if observations < 5:
            return "🌱 Just getting to know you..."
        elif observations < 20:
            return "🌿 Learning your preferences..."
        elif observations < 50:
            return "🌳 Adapting to your style..."
        else:
            return "🌲 Fully adapted to you!"
    
    def reset(self):
        """Reset profile to defaults"""
        self.profile = AdaptiveProfile()
        self.observations = []
        if self.profile_path.exists():
            self.profile_path.unlink()


class AdaptiveInterfaceWrapper:
    """
    Wrapper to replace PersonaManager in existing code.
    
    This provides a compatibility layer while we refactor.
    """
    
    def __init__(self):
        self.adaptive_system = AdaptiveBehaviorSystem()
        
    def format_response(self, response: str, context: Dict = None) -> str:
        """Format response based on adaptive profile"""
        
        level = self.adaptive_system.get_explanation_level()
        
        if level == "simple":
            # Remove technical jargon
            response = response.replace("nixpkgs#", "package ")
            response = response.replace("flake", "configuration")
            response = response.replace("derivation", "package")
            
        elif level == "technical":
            # Add more technical details if not present
            if context and context.get('command'):
                response += f"\n\nTechnical: {context['command']}"
                
        return response
    
    def set_persona(self, persona_name: str):
        """Legacy compatibility - convert persona to initial profile settings"""
        
        # Map old personas to behavioral patterns
        if persona_name == "grandma_rose":
            self.adaptive_system.profile.technical_level = 0.2
            self.adaptive_system.profile.risk_tolerance = 0.1
        elif persona_name == "maya_lightning":
            self.adaptive_system.profile.speed_preference = 0.9
            self.adaptive_system.profile.detail_preference = 0.2
        # But immediately start adapting from there!
        
        print(f"📊 Starting with '{persona_name}' preferences, but I'll adapt to you!")


# Example usage showing the difference
if __name__ == "__main__":
    # Create adaptive system
    adaptive = AdaptiveBehaviorSystem(user_id="demo")
    
    # Simulate user behavior
    print("Initial state:", adaptive.get_status())
    print("Interface mode:", adaptive.get_interface_mode())
    
    # User reads preview carefully
    adaptive.observe(
        ObservationType.PREVIEW_READ,
        details={'read_time': 5.2, 'scrolled': True}
    )
    
    # User executes command quickly
    adaptive.observe(
        ObservationType.COMMAND_EXECUTED,
        details={'time_to_execute': 2.1, 'command': 'install vim'}
    )
    
    # User recovers from error
    adaptive.observe(
        ObservationType.ERROR_RECOVERED,
        details={'error': 'package not found', 'recovery_time': 8.5}
    )
    
    print("\nAfter observations:", adaptive.get_status())
    print("Updated interface:", adaptive.get_interface_mode())
    print("Should confirm?", adaptive.should_request_confirmation("install firefox"))