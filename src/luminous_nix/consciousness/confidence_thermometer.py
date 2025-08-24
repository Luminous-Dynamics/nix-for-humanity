#!/usr/bin/env python3
"""
🌡️ Confidence Thermometer - Adaptive Intelligence for Human Confidence

This module tracks user confidence and adapts the entire system accordingly.
It integrates with POMLConsciousness to modify templates, personas, and responses
based on detected confidence levels.

Part of the Universal Consciousness Protocol.
"""

import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence levels that drive interface adaptation"""
    TERRIFIED = (0, 20, "Maximum safety mode")      # New user, very nervous
    NERVOUS = (20, 40, "Heavy guidance mode")       # Cautious, needs reassurance  
    LEARNING = (40, 60, "Balanced support mode")    # Growing confidence
    COMFORTABLE = (60, 80, "Light touch mode")      # Competent, occasional help
    CONFIDENT = (80, 100, "Flow mode")              # Expert, minimal friction
    
    def __init__(self, min_score: int, max_score: int, description: str):
        self.min_score = min_score
        self.max_score = max_score
        self.description = description
    
    @classmethod
    def from_score(cls, score: float) -> 'ConfidenceLevel':
        """Get confidence level from numeric score"""
        for level in cls:
            if level.min_score <= score < level.max_score:
                return level
        return cls.CONFIDENT if score >= 100 else cls.TERRIFIED


@dataclass
class ConfidenceSignal:
    """A single signal that affects confidence scoring"""
    signal_type: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    weight: float = 1.0
    
    # Signal categories
    POSITIVE_SIGNALS = {
        'command_success': 5,          # Successfully executed command
        'quick_action': 3,              # Fast decisive action
        'exploration': 2,               # Trying new features
        'helping_others': 10,           # Ultimate confidence sign
        'using_shortcuts': 4,           # Discovered and using shortcuts
        'dismissing_help': 2,           # Don't need hand-holding
    }
    
    NEGATIVE_SIGNALS = {
        'long_pause': -2,               # Hesitation before action
        'repeated_reading': -1,         # Re-reading same text
        'hover_without_click': -1,      # Mouse hovering, not clicking
        'backtrack': -3,                # Going back/canceling
        'panic_button': -5,             # Used panic button
        'error_repeated': -4,           # Same error multiple times
        'rage_click': -6,               # Frustration clicking
    }
    
    NEUTRAL_SIGNALS = {
        'steady_progress': 1,           # Consistent forward movement
        'reading_docs': 0,              # Learning (neither good nor bad)
        'asking_help': 0,               # Seeking help appropriately
    }


class ConfidenceThermometer:
    """
    The adaptive confidence tracking system that breathes with the user.
    
    This is the heart of making Linux accessible - we track confidence,
    not competence. Fear is the enemy, not complexity.
    """
    
    def __init__(self, initial_confidence: float = 30.0):
        """
        Initialize with slight confidence to avoid overwhelming new users.
        
        Args:
            initial_confidence: Starting confidence (0-100)
        """
        self.confidence_score = initial_confidence
        self.confidence_level = ConfidenceLevel.from_score(initial_confidence)
        self.signal_history: List[ConfidenceSignal] = []
        self.session_start = datetime.now()
        self.success_count = 0
        self.last_success = None
        self.panic_count = 0
        self.adaptation_callbacks = []
        
        # Confidence can only go up or stay same in short term
        # (but can gradually decrease if abandoned)
        self.ratchet_enabled = True
        self.last_interaction = datetime.now()
        
        # Micro-celebration tracking
        self.celebrations_triggered = 0
        self.last_celebration = None
        
        logger.info(f"🌡️ Confidence Thermometer initialized at {initial_confidence}% ({self.confidence_level.name})")
    
    def observe_interaction(self, interaction_type: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Observe a user interaction and update confidence accordingly.
        
        Args:
            interaction_type: Type of interaction observed
            metadata: Additional context about the interaction
            
        Returns:
            Dict with confidence update and recommended adaptations
        """
        metadata = metadata or {}
        
        # Create signal from interaction
        signal = self._create_signal(interaction_type, metadata)
        self.signal_history.append(signal)
        
        # Update confidence score
        old_score = self.confidence_score
        self._update_confidence(signal)
        
        # Check for level change
        old_level = self.confidence_level
        self.confidence_level = ConfidenceLevel.from_score(self.confidence_score)
        
        # Generate response
        response = {
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level.name,
            'score_change': self.confidence_score - old_score,
            'level_changed': old_level != self.confidence_level,
            'adaptations': self._get_adaptations(),
            'celebration': self._check_celebration(interaction_type, old_score)
        }
        
        # Update last interaction time
        self.last_interaction = datetime.now()
        
        # Trigger adaptation callbacks
        if response['level_changed']:
            self._trigger_adaptations(response)
        
        return response
    
    def _create_signal(self, interaction_type: str, metadata: Dict[str, Any]) -> ConfidenceSignal:
        """Create a confidence signal from an interaction"""
        # Determine weight based on signal type
        weight = 1.0
        if interaction_type in ConfidenceSignal.POSITIVE_SIGNALS:
            weight = ConfidenceSignal.POSITIVE_SIGNALS[interaction_type]
        elif interaction_type in ConfidenceSignal.NEGATIVE_SIGNALS:
            weight = ConfidenceSignal.NEGATIVE_SIGNALS[interaction_type]
        elif interaction_type in ConfidenceSignal.NEUTRAL_SIGNALS:
            weight = ConfidenceSignal.NEUTRAL_SIGNALS[interaction_type]
        
        # Adjust weight based on metadata
        if metadata.get('time_taken'):
            # Faster actions indicate more confidence
            if metadata['time_taken'] < 2:  # seconds
                weight *= 1.2
            elif metadata['time_taken'] > 10:
                weight *= 0.8
        
        return ConfidenceSignal(
            signal_type=interaction_type,
            value=metadata,
            weight=weight
        )
    
    def _update_confidence(self, signal: ConfidenceSignal):
        """Update confidence score based on signal"""
        # Calculate score change
        change = signal.weight
        
        # Apply ratchet (confidence doesn't decrease easily)
        if self.ratchet_enabled and change < 0:
            # Negative signals have reduced impact
            change *= 0.5
            
            # If user has been successful recently, ignore small negatives
            if self.last_success and (datetime.now() - self.last_success).seconds < 60:
                change *= 0.2
        
        # Apply change with bounds
        self.confidence_score = max(0, min(100, self.confidence_score + change))
        
        # Track successes
        if signal.weight > 0:
            self.success_count += 1
            self.last_success = datetime.now()
        
        # Track panic
        if signal.signal_type == 'panic_button':
            self.panic_count += 1
    
    def _get_adaptations(self) -> Dict[str, Any]:
        """Get recommended interface adaptations based on confidence level"""
        level = self.confidence_level
        
        adaptations = {
            'level': level.name,
            'description': level.description
        }
        
        if level == ConfidenceLevel.TERRIFIED:
            adaptations.update({
                'ui_mode': 'maximum_safety',
                'button_size': 'extra_large',
                'confirmations': 'every_action',
                'help_prominence': 'always_visible',
                'success_feedback': 'celebrate_everything',
                'error_handling': 'impossible_to_fail',
                'pace': 'very_slow',
                'options_shown': 1,  # One thing at a time
                'undo_availability': 'prominent',
                'encouragement': 'constant',
                'panic_button': 'extra_large_and_pulsing'
            })
        
        elif level == ConfidenceLevel.NERVOUS:
            adaptations.update({
                'ui_mode': 'guided',
                'button_size': 'large',
                'confirmations': 'important_actions',
                'help_prominence': 'readily_available',
                'success_feedback': 'celebrate_milestones',
                'error_handling': 'gentle_correction',
                'pace': 'slow',
                'options_shown': 3,
                'undo_availability': 'visible',
                'encouragement': 'frequent',
                'panic_button': 'always_visible'
            })
        
        elif level == ConfidenceLevel.LEARNING:
            adaptations.update({
                'ui_mode': 'balanced',
                'button_size': 'normal',
                'confirmations': 'dangerous_only',
                'help_prominence': 'on_hover',
                'success_feedback': 'subtle_acknowledgment',
                'error_handling': 'informative',
                'pace': 'moderate',
                'options_shown': 5,
                'undo_availability': 'menu',
                'encouragement': 'occasional',
                'panic_button': 'visible'
            })
        
        elif level == ConfidenceLevel.COMFORTABLE:
            adaptations.update({
                'ui_mode': 'efficient',
                'button_size': 'normal',
                'confirmations': 'minimal',
                'help_prominence': 'on_request',
                'success_feedback': 'brief',
                'error_handling': 'technical_details',
                'pace': 'fast',
                'options_shown': 10,
                'undo_availability': 'keyboard_shortcut',
                'encouragement': 'rare',
                'panic_button': 'hidden_but_available'
            })
        
        else:  # CONFIDENT
            adaptations.update({
                'ui_mode': 'expert',
                'button_size': 'compact',
                'confirmations': 'none',
                'help_prominence': 'hidden',
                'success_feedback': 'none',
                'error_handling': 'stack_trace',
                'pace': 'instant',
                'options_shown': 'all',
                'undo_availability': 'command_line',
                'encouragement': 'none',
                'panic_button': 'keyboard_shortcut_only',
                'advanced_features': 'all_enabled',
                'community_help': 'become_helper'
            })
        
        return adaptations
    
    def _check_celebration(self, interaction_type: str, old_score: float) -> Optional[Dict[str, Any]]:
        """Check if we should trigger a micro-celebration"""
        celebration = None
        
        # Celebrate specific achievements
        if interaction_type == 'command_success':
            if self.success_count == 1:
                celebration = {
                    'type': 'first_success',
                    'message': "Perfect! You're a natural at this!",
                    'emoji': '🎉',
                    'sound': 'success_major'
                }
            elif self.success_count % 5 == 0:
                celebration = {
                    'type': 'milestone',
                    'message': f"{self.success_count} successes! You're on fire!",
                    'emoji': '🔥',
                    'sound': 'success_milestone'
                }
            else:
                celebration = {
                    'type': 'micro',
                    'message': None,  # Just sound/visual
                    'emoji': '✓',
                    'sound': 'success_micro'
                }
        
        # Celebrate confidence breakthroughs
        if self.confidence_score >= 50 and old_score < 50:
            celebration = {
                'type': 'breakthrough',
                'message': "You're really getting the hang of this!",
                'emoji': '🚀',
                'sound': 'level_up'
            }
        
        # Celebrate helping others (ultimate confidence)
        if interaction_type == 'helping_others':
            celebration = {
                'type': 'master',
                'message': "You've become the teacher! Amazing progress!",
                'emoji': '🏆',
                'sound': 'achievement_ultimate'
            }
        
        if celebration:
            self.celebrations_triggered += 1
            self.last_celebration = datetime.now()
        
        return celebration
    
    def get_panic_button_config(self) -> Dict[str, Any]:
        """Get panic button configuration based on confidence"""
        if self.confidence_level == ConfidenceLevel.TERRIFIED:
            return {
                'visible': True,
                'size': 'extra_large',
                'position': 'center_prominent',
                'label': '😰 This is confusing - Help!',
                'animation': 'gentle_pulse',
                'color': 'warm_reassuring'
            }
        elif self.confidence_level in [ConfidenceLevel.NERVOUS, ConfidenceLevel.LEARNING]:
            return {
                'visible': True,
                'size': 'normal',
                'position': 'corner',
                'label': '❓ Need help',
                'animation': None,
                'color': 'soft_blue'
            }
        else:
            return {
                'visible': False,  # Still accessible via keyboard
                'shortcut': 'Ctrl+H',
                'position': 'hidden'
            }
    
    def handle_panic(self) -> Dict[str, Any]:
        """Handle panic button press with maximum compassion"""
        self.observe_interaction('panic_button')
        
        response = {
            'immediate_action': 'simplify_everything',
            'message': self._get_panic_response(),
            'ui_changes': {
                'reduce_to_essentials': True,
                'increase_text_size': True,
                'show_video_help': True,
                'offer_undo_recent': True,
                'breathing_prompt': self.panic_count > 2
            }
        }
        
        # After multiple panics, suggest a break
        if self.panic_count > 2:
            response['suggest_break'] = True
            response['break_message'] = "You're doing great. Sometimes a 5-minute break helps everything click."
        
        return response
    
    def _get_panic_response(self) -> str:
        """Get compassionate panic response based on history"""
        if self.panic_count == 1:
            return "No worries at all! Let's slow down and tackle this together. What were you trying to do?"
        elif self.panic_count == 2:
            return "It's okay! Linux can feel overwhelming. Let's take it one small step at a time."
        else:
            return "You're doing fine! Everyone feels this way sometimes. Let's reset and try a simpler approach."
    
    def integrate_with_poml(self, consciousness: 'POMLConsciousness') -> None:
        """
        Integrate with POMLConsciousness to modify templates based on confidence.
        
        This is where the magic happens - POML templates adapt to confidence level!
        """
        def adapt_template(template: str, context: Dict[str, Any]) -> str:
            """Modify POML template based on confidence"""
            context['confidence_level'] = self.confidence_level.name
            context['confidence_score'] = self.confidence_score
            context['ui_adaptations'] = self._get_adaptations()
            
            # Add confidence-specific template variables
            if self.confidence_level == ConfidenceLevel.TERRIFIED:
                context['response_style'] = 'maximum_reassurance'
                context['explanation_depth'] = 'eli5'  # Explain like I'm 5
                context['success_celebration'] = 'major'
            elif self.confidence_level == ConfidenceLevel.CONFIDENT:
                context['response_style'] = 'concise_technical'
                context['explanation_depth'] = 'expert'
                context['success_celebration'] = 'none'
            
            return template
        
        # Register adaptation callback with consciousness system
        consciousness.register_adapter('confidence', adapt_template)
        logger.info("🔗 Confidence Thermometer integrated with POMLConsciousness")
    
    def get_learning_velocity(self) -> str:
        """Determine how fast the user is learning"""
        if not self.signal_history:
            return "observing"
        
        recent_signals = self.signal_history[-10:]
        positive_ratio = sum(1 for s in recent_signals if s.weight > 0) / len(recent_signals)
        
        if positive_ratio > 0.8:
            return "accelerating"
        elif positive_ratio > 0.5:
            return "steady"
        else:
            return "struggling"
    
    def to_dict(self) -> Dict[str, Any]:
        """Export current state for persistence"""
        return {
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level.name,
            'success_count': self.success_count,
            'panic_count': self.panic_count,
            'session_duration': (datetime.now() - self.session_start).seconds,
            'celebrations_triggered': self.celebrations_triggered,
            'learning_velocity': self.get_learning_velocity()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfidenceThermometer':
        """Restore from persisted state"""
        thermometer = cls(initial_confidence=data.get('confidence_score', 30))
        thermometer.success_count = data.get('success_count', 0)
        thermometer.panic_count = data.get('panic_count', 0)
        thermometer.celebrations_triggered = data.get('celebrations_triggered', 0)
        return thermometer


# Global instance for easy access
_thermometer: Optional[ConfidenceThermometer] = None

def get_thermometer() -> ConfidenceThermometer:
    """Get or create the global confidence thermometer"""
    global _thermometer
    if _thermometer is None:
        _thermometer = ConfidenceThermometer()
    return _thermometer


def observe(interaction_type: str, **metadata) -> Dict[str, Any]:
    """Convenience function to observe interactions"""
    return get_thermometer().observe_interaction(interaction_type, metadata)