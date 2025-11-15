"""
Minimal consciousness orb replacement (archived features removed)
"""

from enum import Enum


class AIState(Enum):
    """AI system states"""

    IDLE = "idle"
    THINKING = "thinking"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"


class EmotionalState(Enum):
    """Emotional states for the orb"""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    CONCERNED = "concerned"
    CONFUSED = "confused"
    FLOW = "flow"


class ConsciousnessOrb:
    """Minimal orb for UI compatibility"""

    def __init__(self):
        self.state = AIState.IDLE
        self.emotion = EmotionalState.NEUTRAL

    def update(self, state: AIState, emotion: EmotionalState = None):
        """Update orb state"""
        self.state = state
        if emotion:
            self.emotion = emotion
