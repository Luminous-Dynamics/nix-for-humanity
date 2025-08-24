#!/usr/bin/env python3
"""
🧠 Adaptive Persona System - Dynamic Intelligence for Each User
Every user is unique and evolving. The system learns and adapts.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class EmotionalState(Enum):
    """Detected emotional states"""
    CURIOUS = "curious"          # Exploring, asking questions
    FOCUSED = "focused"          # In flow, productive
    FRUSTRATED = "frustrated"    # Errors, retries
    CONFUSED = "confused"        # Long pauses, unclear commands
    SATISFIED = "satisfied"      # Successful completions
    LEARNING = "learning"        # Trying new things
    RUSHED = "rushed"           # Quick commands, impatient


@dataclass
class Interaction:
    """Single interaction with the system"""
    timestamp: datetime
    command: str
    success: bool
    response_time_ms: int
    error_message: Optional[str] = None
    used_advanced_feature: bool = False
    reading_time_ms: Optional[int] = None
    retry_count: int = 0
    help_requested: bool = False
    

@dataclass
class DynamicPersona:
    """
    Evolving persona that learns from every interaction
    Each user gets their own unique, adaptive profile
    """
    # Identity
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    base_archetype: Optional[str] = None  # Starting template if any
    
    # Learned Characteristics (0.0 to 1.0, continuously adjusted)
    technical_proficiency: float = 0.5   # Novice ← → Expert
    preferred_verbosity: float = 0.5     # Minimal ← → Detailed
    patience_level: float = 0.5          # Impatient ← → Patient
    exploration_tendency: float = 0.5    # Conservative ← → Adventurous
    learning_speed: float = 0.5          # Slow ← → Fast learner
    
    # Adaptive Preferences (learned over time)
    preferred_examples: List[str] = field(default_factory=list)
    avoided_patterns: List[str] = field(default_factory=list)
    peak_hours: List[int] = field(default_factory=list)
    stress_indicators: List[str] = field(default_factory=list)
    success_patterns: List[str] = field(default_factory=list)
    
    # Current Session State
    current_mood: EmotionalState = EmotionalState.FOCUSED
    current_focus: str = "general"
    frustration_level: float = 0.0
    confidence_level: float = 0.5
    session_start: datetime = field(default_factory=datetime.now)
    
    # Learning History
    interaction_count: int = 0
    success_rate: float = 0.5
    avg_response_time: float = 1000.0  # milliseconds
    favorite_commands: Dict[str, int] = field(default_factory=dict)
    concept_mastery: Dict[str, float] = field(default_factory=dict)
    error_patterns: Dict[str, int] = field(default_factory=dict)
    
    # Behavioral Patterns
    prefers_voice: bool = False
    prefers_examples: bool = True
    prefers_shortcuts: bool = False
    learns_by_doing: bool = True
    needs_confirmation: bool = True
    
    # Meta-learning
    adaptation_rate: float = 0.1  # How fast to adjust (0.01 to 0.2)
    stability_threshold: int = 20  # Interactions before stabilizing


class PersonaLearningEngine:
    """
    Learns from every interaction to build understanding of the user
    Uses reinforcement learning principles for continuous improvement
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".luminous-nix" / "personas"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Learning parameters
        self.learning_rate = 0.05  # Base learning rate
        self.momentum = 0.9        # Smoothing factor
        self.decay_rate = 0.99     # Memory decay
        
        # State tracking
        self.personas: Dict[str, DynamicPersona] = {}
        self.interaction_buffer: Dict[str, List[Interaction]] = {}
        
    def learn_from_interaction(self, 
                              user_id: str,
                              interaction: Interaction) -> DynamicPersona:
        """
        Learn from a single interaction and update persona
        This is where the magic happens - continuous adaptation
        """
        # Get or create persona
        persona = self.get_or_create_persona(user_id)
        
        # Update interaction history
        persona.interaction_count += 1
        if user_id not in self.interaction_buffer:
            self.interaction_buffer[user_id] = []
        self.interaction_buffer[user_id].append(interaction)
        
        # Keep buffer manageable (last 100 interactions)
        if len(self.interaction_buffer[user_id]) > 100:
            self.interaction_buffer[user_id] = self.interaction_buffer[user_id][-100:]
        
        # Core learning updates
        persona = self._update_technical_proficiency(persona, interaction)
        persona = self._update_verbosity_preference(persona, interaction)
        persona = self._update_patience_level(persona, interaction)
        persona = self._update_exploration_tendency(persona, interaction)
        persona = self._detect_emotional_state(persona, interaction)
        persona = self._learn_patterns(persona, interaction)
        
        # Update success metrics
        persona.success_rate = (
            persona.success_rate * 0.95 + 
            (1.0 if interaction.success else 0.0) * 0.05
        )
        
        # Update response time average
        persona.avg_response_time = (
            persona.avg_response_time * 0.9 + 
            interaction.response_time_ms * 0.1
        )
        
        # Track favorite commands
        cmd_base = interaction.command.split()[0] if interaction.command else "unknown"
        persona.favorite_commands[cmd_base] = persona.favorite_commands.get(cmd_base, 0) + 1
        
        # Adjust adaptation rate based on stability
        if persona.interaction_count > persona.stability_threshold:
            persona.adaptation_rate = max(0.01, persona.adaptation_rate * 0.99)
        
        # Save updated persona
        self.save_persona(persona)
        
        logger.info(f"Learned from interaction for user {user_id}: "
                   f"tech={persona.technical_proficiency:.2f}, "
                   f"mood={persona.current_mood.value}")
        
        return persona
    
    def _update_technical_proficiency(self, 
                                     persona: DynamicPersona, 
                                     interaction: Interaction) -> DynamicPersona:
        """Update technical skill assessment"""
        # Advanced feature usage increases proficiency
        if interaction.used_advanced_feature:
            delta = persona.adaptation_rate * 0.5
            persona.technical_proficiency = min(1.0, persona.technical_proficiency + delta)
        
        # Errors on simple commands decrease proficiency
        simple_commands = ['install', 'search', 'list', 'help']
        if not interaction.success and any(cmd in interaction.command.lower() for cmd in simple_commands):
            delta = persona.adaptation_rate * 0.3
            persona.technical_proficiency = max(0.0, persona.technical_proficiency - delta)
        
        # Success on complex commands increases proficiency
        complex_indicators = ['flake', 'overlay', 'derivation', 'nixpkgs', 'home-manager']
        if interaction.success and any(term in interaction.command.lower() for term in complex_indicators):
            delta = persona.adaptation_rate * 0.7
            persona.technical_proficiency = min(1.0, persona.technical_proficiency + delta)
        
        return persona
    
    def _update_verbosity_preference(self,
                                    persona: DynamicPersona,
                                    interaction: Interaction) -> DynamicPersona:
        """Learn preferred response detail level"""
        if interaction.reading_time_ms:
            # Fast dismissal means too verbose
            if interaction.reading_time_ms < 500:
                persona.preferred_verbosity *= (1 - persona.adaptation_rate * 0.2)
            # Long reading means they want detail
            elif interaction.reading_time_ms > 3000:
                persona.preferred_verbosity *= (1 + persona.adaptation_rate * 0.1)
        
        # Help requests mean more detail needed
        if interaction.help_requested:
            persona.preferred_verbosity = min(1.0, persona.preferred_verbosity + persona.adaptation_rate)
        
        return persona
    
    def _update_patience_level(self,
                              persona: DynamicPersona,
                              interaction: Interaction) -> DynamicPersona:
        """Assess user patience from behavior"""
        # Multiple retries show patience
        if interaction.retry_count > 2:
            persona.patience_level = min(1.0, persona.patience_level + persona.adaptation_rate * 0.3)
        
        # Quick successive commands show impatience
        recent = self.interaction_buffer.get(persona.user_id, [])[-5:]
        if len(recent) >= 2:
            time_between = (recent[-1].timestamp - recent[-2].timestamp).seconds
            if time_between < 5:  # Rapid commands
                persona.patience_level = max(0.0, persona.patience_level - persona.adaptation_rate * 0.2)
        
        return persona
    
    def _update_exploration_tendency(self,
                                    persona: DynamicPersona,
                                    interaction: Interaction) -> DynamicPersona:
        """Track willingness to try new things"""
        # Track unique commands
        unique_commands = len(persona.favorite_commands)
        if unique_commands > 10:
            persona.exploration_tendency = min(1.0, 0.5 + unique_commands * 0.02)
        
        # Advanced features show exploration
        if interaction.used_advanced_feature:
            persona.exploration_tendency = min(1.0, 
                persona.exploration_tendency + persona.adaptation_rate * 0.5)
        
        return persona
    
    def _detect_emotional_state(self,
                               persona: DynamicPersona,
                               interaction: Interaction) -> DynamicPersona:
        """Detect current emotional state from patterns"""
        recent = self.interaction_buffer.get(persona.user_id, [])[-10:]
        
        if not recent:
            persona.current_mood = EmotionalState.FOCUSED
            return persona
        
        # Calculate indicators
        recent_errors = sum(1 for i in recent if not i.success)
        recent_retries = sum(i.retry_count for i in recent)
        avg_time = np.mean([i.response_time_ms for i in recent])
        
        # Determine mood
        if recent_errors > 3 or recent_retries > 5:
            persona.current_mood = EmotionalState.FRUSTRATED
            persona.frustration_level = min(1.0, persona.frustration_level + 0.1)
        elif interaction.help_requested:
            persona.current_mood = EmotionalState.CONFUSED
        elif recent_errors == 0 and len(recent) > 5:
            persona.current_mood = EmotionalState.SATISFIED
            persona.frustration_level = max(0.0, persona.frustration_level - 0.2)
        elif interaction.used_advanced_feature:
            persona.current_mood = EmotionalState.LEARNING
        elif avg_time < 500:
            persona.current_mood = EmotionalState.RUSHED
        else:
            persona.current_mood = EmotionalState.FOCUSED
        
        # Update confidence based on success
        if interaction.success:
            persona.confidence_level = min(1.0, persona.confidence_level + 0.05)
        else:
            persona.confidence_level = max(0.0, persona.confidence_level - 0.03)
        
        return persona
    
    def _learn_patterns(self,
                       persona: DynamicPersona,
                       interaction: Interaction) -> DynamicPersona:
        """Learn behavioral patterns"""
        # Track error patterns
        if not interaction.success and interaction.error_message:
            error_type = self._classify_error(interaction.error_message)
            persona.error_patterns[error_type] = persona.error_patterns.get(error_type, 0) + 1
        
        # Learn success patterns
        if interaction.success:
            pattern = self._extract_pattern(interaction.command)
            if pattern and pattern not in persona.success_patterns:
                persona.success_patterns.append(pattern)
                if len(persona.success_patterns) > 20:
                    persona.success_patterns = persona.success_patterns[-20:]
        
        # Detect peak hours
        hour = interaction.timestamp.hour
        if hour not in persona.peak_hours and interaction.success:
            persona.peak_hours.append(hour)
            persona.peak_hours = sorted(set(persona.peak_hours))
        
        return persona
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error types for pattern learning"""
        error_lower = error_message.lower()
        if 'not found' in error_lower:
            return 'not_found'
        elif 'permission' in error_lower:
            return 'permission'
        elif 'syntax' in error_lower or 'invalid' in error_lower:
            return 'syntax'
        elif 'network' in error_lower or 'connection' in error_lower:
            return 'network'
        else:
            return 'other'
    
    def _extract_pattern(self, command: str) -> Optional[str]:
        """Extract command pattern for learning"""
        parts = command.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"
        return parts[0] if parts else None
    
    def get_or_create_persona(self, user_id: str) -> DynamicPersona:
        """Get existing persona or create new one"""
        if user_id in self.personas:
            return self.personas[user_id]
        
        # Try to load from storage
        persona_file = self.storage_path / f"{user_id}.json"
        if persona_file.exists():
            try:
                with open(persona_file, 'r') as f:
                    data = json.load(f)
                    # Convert back to DynamicPersona
                    data['created_at'] = datetime.fromisoformat(data['created_at'])
                    data['session_start'] = datetime.fromisoformat(data['session_start'])
                    data['current_mood'] = EmotionalState(data['current_mood'])
                    persona = DynamicPersona(**data)
                    self.personas[user_id] = persona
                    logger.info(f"Loaded persona for user {user_id}")
                    return persona
            except Exception as e:
                logger.error(f"Failed to load persona: {e}")
        
        # Create new persona
        persona = DynamicPersona(user_id=user_id)
        self.personas[user_id] = persona
        logger.info(f"Created new persona for user {user_id}")
        return persona
    
    def save_persona(self, persona: DynamicPersona):
        """Save persona to persistent storage"""
        persona_file = self.storage_path / f"{persona.user_id}.json"
        
        # Convert to JSON-serializable format
        data = asdict(persona)
        data['created_at'] = persona.created_at.isoformat()
        data['session_start'] = persona.session_start.isoformat()
        data['current_mood'] = persona.current_mood.value
        
        try:
            with open(persona_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved persona for user {persona.user_id}")
        except Exception as e:
            logger.error(f"Failed to save persona: {e}")
    
    def predict_needs(self, user_id: str) -> List[str]:
        """Predict what the user might need next"""
        persona = self.get_or_create_persona(user_id)
        predictions = []
        
        # Based on current mood
        if persona.current_mood == EmotionalState.FRUSTRATED:
            predictions.append("Would you like me to explain that in more detail?")
        elif persona.current_mood == EmotionalState.LEARNING:
            predictions.append("Here are some advanced features you might enjoy...")
        elif persona.current_mood == EmotionalState.CONFUSED:
            predictions.append("Let me show you an example...")
        
        # Based on patterns
        if persona.error_patterns.get('not_found', 0) > 3:
            predictions.append("Tip: Use 'search' to find package names")
        
        # Based on time of day
        hour = datetime.now().hour
        if hour in persona.peak_hours:
            predictions.append("You're in your peak productivity time!")
        
        return predictions
    
    def get_adaptation_suggestions(self, user_id: str) -> Dict[str, Any]:
        """Get suggestions for how to adapt to this user"""
        persona = self.get_or_create_persona(user_id)
        
        return {
            'verbosity': 'minimal' if persona.preferred_verbosity < 0.3 else 
                        'detailed' if persona.preferred_verbosity > 0.7 else 'normal',
            'technical_level': 'expert' if persona.technical_proficiency > 0.7 else
                              'beginner' if persona.technical_proficiency < 0.3 else 'intermediate',
            'needs_encouragement': persona.frustration_level > 0.3,
            'prefers_examples': persona.prefers_examples,
            'current_mood': persona.current_mood.value,
            'confidence_level': persona.confidence_level,
            'suggested_responses': self.predict_needs(user_id)
        }