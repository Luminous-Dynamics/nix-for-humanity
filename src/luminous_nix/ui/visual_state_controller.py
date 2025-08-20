"""
from typing import Tuple, Dict, List
🔗 Visual State Controller - Bridge between Core Engine and Visual Presence

Manages the visual representation of AI state, translating internal engine
states into beautiful visual expressions through the consciousness orb.
"""

from enum import Enum
from typing import Dict, Optional, Callable, List, Any, Tuple
from dataclasses import dataclass, field
import asyncio
from datetime import datetime


class AIState(Enum):
    """AI operational states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    LEARNING = "learning"
    ERROR = "error"


class UserFlowState(Enum):
    """User cognitive flow states"""
    NORMAL = "normal"
    FOCUSED = "focused"
    DEEP_FOCUS = "deep_focus"
    STRUGGLING = "struggling"
    EXPLORING = "exploring"


@dataclass
class VisualState:
    """Complete visual state representation"""
    ai_state: str = "idle"
    ai_emotion: str = "neutral"
    emotion_intensity: float = 0.5
    user_flow: UserFlowState = UserFlowState.NORMAL
    complexity_level: str = "focused"
    thought_particles: List[Dict] = field(default_factory=list)
    memory_nodes: List[Dict] = field(default_factory=list)
    coherence_level: float = 0.8
    breathing_rate: float = 1.0


class VisualStateController:
    """
    Manages visual state based on core engine events.
    
    This controller:
    - Listens to engine events
    - Translates them to visual states
    - Manages state transitions
    - Notifies UI components
    """
    
    def __init__(self, core_engine):
        self.engine = core_engine
        self.current_state = VisualState()
        self.subscribers: List[Callable] = []
        self.state_history: List[VisualState] = []
        self.emotion_memory = EmotionMemory()
        
        # Register for engine events if available
        if hasattr(self.engine, 'on'):
            self._register_engine_events()
            
    def _register_engine_events(self):
        """Register for all relevant engine events"""
        event_handlers = {
            'nlp_processing': self._on_nlp_processing,
            'command_executing': self._on_command_executing,
            'learning_moment': self._on_learning_moment,
            'error_occurred': self._on_error,
            'user_input_received': self._on_user_input,
            'response_generated': self._on_response_generated,
            'confidence_changed': self._on_confidence_changed,
            'pattern_detected': self._on_pattern_detected
        }
        
        for event, handler in event_handlers.items():
            if hasattr(self.engine, 'on'):
                self.engine.on(event, handler)
                
    def subscribe(self, callback: Callable) -> None:
        """Subscribe to visual state changes"""
        self.subscribers.append(callback)
        # Immediately notify with current state
        callback(self.current_state)
        
    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from visual state changes"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            
    def _notify_subscribers(self) -> None:
        """Notify all subscribers of state change"""
        for callback in self.subscribers:
            try:
                callback(self.current_state)
            except Exception as e:
                # Log error but don't crash
                print(f"Error notifying subscriber: {e}")
                
    def update_state(self, **kwargs) -> None:
        """Update visual state with new values"""
        # Store previous state
        self.state_history.append(self.current_state)
        if len(self.state_history) > 100:
            self.state_history.pop(0)
            
        # Update current state
        for key, value in kwargs.items():
            if hasattr(self.current_state, key):
                setattr(self.current_state, key, value)
                
        # Notify subscribers
        self._notify_subscribers()
        
    def _on_nlp_processing(self, event: Dict[str, Any]) -> None:
        """Handle NLP processing events"""
        self.update_state(
            ai_state="processing",
            ai_emotion="thinking",
            emotion_intensity=0.7
        )
        
        # Extract concepts for thought particles
        concepts = event.get('concepts', [])[:5]
        self.current_state.thought_particles = [
            {"id": i, "concept": c, "relevance": event.get('relevance', [0.5] * 5)[i]}
            for i, c in enumerate(concepts)
        ]
        
        self._notify_subscribers()
        
    def _on_command_executing(self, event: Dict[str, Any]) -> None:
        """Handle command execution events"""
        self.update_state(
            ai_state="processing",
            ai_emotion="focused",
            emotion_intensity=0.8
        )
        
    def _on_learning_moment(self, event: Dict[str, Any]) -> None:
        """Handle learning events"""
        self.update_state(
            ai_state="learning",
            ai_emotion="curious",
            emotion_intensity=0.9
        )
        
        # Add to memory constellation
        self.current_state.memory_nodes.append({
            "id": event.get('concept_id', datetime.now().timestamp()),
            "concept": event.get('concept', 'new learning'),
            "strength": event.get('confidence', 0.5),
            "timestamp": datetime.now()
        })
        
        # Keep memory nodes limited
        if len(self.current_state.memory_nodes) > 20:
            self.current_state.memory_nodes.pop(0)
            
        self._notify_subscribers()
        
    def _on_error(self, event: Dict[str, Any]) -> None:
        """Handle error events"""
        self.update_state(
            ai_state="error",
            ai_emotion="concerned",
            emotion_intensity=0.6
        )
        
    def _on_user_input(self, event: Dict[str, Any]) -> None:
        """Handle user input received"""
        self.update_state(
            ai_state="listening",
            ai_emotion="attentive",
            emotion_intensity=0.7
        )
        
    def _on_response_generated(self, event: Dict[str, Any]) -> None:
        """Handle response generation"""
        self.update_state(
            ai_state="responding",
            ai_emotion="helpful",
            emotion_intensity=0.6
        )
        
    def _on_confidence_changed(self, event: Dict[str, Any]) -> None:
        """Handle confidence level changes"""
        confidence = event.get('confidence', 0.5)
        
        # Map confidence to emotion
        if confidence > 0.9:
            emotion = "confident"
            intensity = 0.9
        elif confidence > 0.7:
            emotion = "neutral"
            intensity = 0.6
        elif confidence > 0.5:
            emotion = "uncertain"
            intensity = 0.5
        else:
            emotion = "confused"
            intensity = 0.4
            
        self.update_state(
            ai_emotion=emotion,
            emotion_intensity=intensity
        )
        
    def _on_pattern_detected(self, event: Dict[str, Any]) -> None:
        """Handle pattern detection events"""
        # This indicates flow state potential
        pattern_strength = event.get('strength', 0.5)
        
        if pattern_strength > 0.8:
            self.update_state(
                ai_emotion="flow",
                emotion_intensity=1.0,
                coherence_level=pattern_strength
            )
            
    def update_from_engine(self, engine_state: Any) -> None:
        """Update visual state from engine state object"""
        if not engine_state:
            return
            
        # Map engine state to visual state
        updates = {}
        
        if hasattr(engine_state, 'processing'):
            if engine_state.processing:
                updates['ai_state'] = 'processing'
            else:
                updates['ai_state'] = 'idle'
                
        if hasattr(engine_state, 'confidence'):
            self._on_confidence_changed({'confidence': engine_state.confidence})
            
        if hasattr(engine_state, 'user_state'):
            updates['user_flow'] = self._map_user_state(engine_state.user_state)
            
        if updates:
            self.update_state(**updates)
            
    def _map_user_state(self, user_state: Any) -> UserFlowState:
        """Map engine user state to visual flow state"""
        if not user_state:
            return UserFlowState.NORMAL
            
        # Simple mapping logic
        if hasattr(user_state, 'flow_level'):
            if user_state.flow_level > 0.8:
                return UserFlowState.DEEP_FOCUS
            elif user_state.flow_level > 0.6:
                return UserFlowState.FOCUSED
            elif user_state.flow_level < 0.3:
                return UserFlowState.STRUGGLING
                
        return UserFlowState.NORMAL
        
    def get_animation_params(self) -> Dict[str, Any]:
        """Get current animation parameters"""
        return {
            'breathing_rate': self.current_state.breathing_rate,
            'particle_count': len(self.current_state.thought_particles),
            'glow_intensity': self.current_state.emotion_intensity,
            'coherence': self.current_state.coherence_level
        }


class EmotionMemory:
    """Tracks emotional patterns over time"""
    
    def __init__(self, window_size: int = 50):
        self.history: List[Tuple[datetime, str, float]] = []
        self.window_size = window_size
        
    def add(self, emotion: str, intensity: float) -> None:
        """Add an emotion to history"""
        self.history.append((datetime.now(), emotion, intensity))
        
        # Keep history bounded
        if len(self.history) > self.window_size:
            self.history.pop(0)
            
    def get_dominant_emotion(self) -> Tuple[str, float]:
        """Get the most common recent emotion"""
        if not self.history:
            return "neutral", 0.5
            
        # Count emotions in recent history
        emotion_counts = {}
        for _, emotion, intensity in self.history[-20:]:
            if emotion not in emotion_counts:
                emotion_counts[emotion] = []
            emotion_counts[emotion].append(intensity)
            
        # Find dominant emotion
        dominant = max(emotion_counts.items(), 
                      key=lambda x: len(x[1]))
        
        avg_intensity = sum(dominant[1]) / len(dominant[1])
        return dominant[0], avg_intensity
        
    def get_emotional_trajectory(self) -> str:
        """Determine if emotions are improving or declining"""
        if len(self.history) < 10:
            return "stable"
            
        # Compare recent to older emotions
        recent = self.history[-5:]
        older = self.history[-10:-5]
        
        recent_avg = sum(x[2] for x in recent) / len(recent)
        older_avg = sum(x[2] for x in older) / len(older)
        
        if recent_avg > older_avg + 0.1:
            return "improving"
        elif recent_avg < older_avg - 0.1:
            return "declining"
        else:
            return "stable"