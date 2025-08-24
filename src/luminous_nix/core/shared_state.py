#!/usr/bin/env python3
"""
🌐 Shared State - Global Intelligence Coordinator
A reactive state system that all components can observe and respond to.

This creates the nervous system of the application where changes in one
component immediately influence all others.
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class StateKey(Enum):
    """Standard state keys that components can observe"""
    # User state
    USER_EXPERTISE = "user_expertise"
    FRUSTRATION_LEVEL = "frustration_level"
    EMOTIONAL_STATE = "emotional_state"
    LEARNING_PACE = "learning_pace"
    
    # Session state
    SESSION_DURATION = "session_duration"
    ERROR_COUNT = "error_count"
    SUCCESS_COUNT = "success_count"
    CURRENT_TASK = "current_task"
    CURRENT_PERSONA = "current_persona"
    
    # System state
    PERFORMANCE_MODE = "performance_mode"
    RESOURCE_USAGE = "resource_usage"
    ACTIVE_COMPONENTS = "active_components"
    
    # Predictions
    NEXT_LIKELY_COMMAND = "next_likely_command"
    USER_INTENT = "user_intent"
    COMPLETION_PROBABILITY = "completion_probability"


@dataclass
class StateChange:
    """Represents a change in shared state"""
    key: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    source: str  # Which component made the change
    metadata: Dict[str, Any] = field(default_factory=dict)


class SharedState:
    """
    Global reactive state that all components can observe and modify.
    
    This is the central nervous system that enables components to
    work together intelligently.
    """
    
    def __init__(self):
        """Initialize shared state"""
        self._state: Dict[str, Any] = {}
        self._observers: Dict[str, List[Callable]] = {}
        self._history: List[StateChange] = []
        self._thresholds: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default state
        self._initialize_defaults()
        
        logger.info("🌐 Shared State initialized - global intelligence active")
    
    def _initialize_defaults(self):
        """Set default state values"""
        self._state = {
            StateKey.USER_EXPERTISE.value: 0.5,  # Medium
            StateKey.FRUSTRATION_LEVEL.value: 0.0,  # None
            StateKey.EMOTIONAL_STATE.value: "neutral",
            StateKey.LEARNING_PACE.value: "moderate",
            StateKey.SESSION_DURATION.value: 0,
            StateKey.ERROR_COUNT.value: 0,
            StateKey.SUCCESS_COUNT.value: 0,
            StateKey.CURRENT_TASK.value: None,
            StateKey.CURRENT_PERSONA.value: "default",
            StateKey.PERFORMANCE_MODE.value: "balanced",
            StateKey.RESOURCE_USAGE.value: "normal",
            StateKey.ACTIVE_COMPONENTS.value: [],
            StateKey.NEXT_LIKELY_COMMAND.value: None,
            StateKey.USER_INTENT.value: None,
            StateKey.COMPLETION_PROBABILITY.value: 0.0
        }
        
        # Set thresholds for automatic reactions
        self._thresholds = {
            StateKey.FRUSTRATION_LEVEL.value: {
                "high": 0.7,  # Switch to supportive mode
                "medium": 0.4,  # Offer help
                "low": 0.2   # Normal operation
            },
            StateKey.USER_EXPERTISE.value: {
                "expert": 0.8,
                "intermediate": 0.5,
                "beginner": 0.3
            },
            StateKey.ERROR_COUNT.value: {
                "concerning": 5,  # Too many errors
                "elevated": 3,    # Getting stuck
                "normal": 1       # Expected
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get current state value"""
        if isinstance(key, StateKey):
            key = key.value
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any, source: str = "system", metadata: Dict = None):
        """
        Set state value and notify observers.
        
        Args:
            key: State key to update
            value: New value
            source: Component making the change
            metadata: Additional context about the change
        """
        if isinstance(key, StateKey):
            key = key.value
        
        old_value = self._state.get(key)
        
        # Skip if no change
        if old_value == value:
            return
        
        # Update state
        self._state[key] = value
        
        # Record change
        change = StateChange(
            key=key,
            old_value=old_value,
            new_value=value,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {}
        )
        self._history.append(change)
        
        # Keep history bounded
        if len(self._history) > 1000:
            self._history = self._history[-500:]
        
        # Notify observers
        self._notify_observers(key, change)
        
        # Check thresholds
        self._check_thresholds(key, value)
        
        logger.debug(f"📊 State updated: {key} = {value} (by {source})")
    
    def observe(self, key: str, callback: Callable):
        """
        Register an observer for state changes.
        
        Args:
            key: State key to observe (or "*" for all)
            callback: Function to call on change (receives StateChange)
        """
        if isinstance(key, StateKey):
            key = key.value
        
        if key not in self._observers:
            self._observers[key] = []
        
        self._observers[key].append(callback)
        logger.debug(f"👁️ Observer registered for {key}")
    
    def _notify_observers(self, key: str, change: StateChange):
        """Notify all observers of a state change"""
        # Notify specific observers
        for callback in self._observers.get(key, []):
            try:
                callback(change)
            except Exception as e:
                logger.error(f"Observer error for {key}: {e}")
        
        # Notify wildcard observers
        for callback in self._observers.get("*", []):
            try:
                callback(change)
            except Exception as e:
                logger.error(f"Wildcard observer error: {e}")
    
    def _check_thresholds(self, key: str, value: Any):
        """Check if value crosses important thresholds"""
        if key not in self._thresholds:
            return
        
        thresholds = self._thresholds[key]
        
        # Check frustration level
        if key == StateKey.FRUSTRATION_LEVEL.value:
            if value > thresholds["high"]:
                logger.warning(f"😰 High frustration detected: {value:.2f}")
                self.set(StateKey.CURRENT_PERSONA.value, "sam_supportive", 
                        source="threshold_detector")
            elif value > thresholds["medium"]:
                logger.info(f"😟 Medium frustration: {value:.2f}")
                # Could trigger help offer
        
        # Check error count
        elif key == StateKey.ERROR_COUNT.value:
            if value >= thresholds["concerning"]:
                logger.warning(f"❌ Many errors: {value}")
                self.set(StateKey.FRUSTRATION_LEVEL.value, 
                        min(1.0, self.get(StateKey.FRUSTRATION_LEVEL.value) + 0.2),
                        source="error_monitor")
    
    def update_success_metrics(self):
        """Update success rate and related metrics"""
        errors = self.get(StateKey.ERROR_COUNT.value, 0)
        successes = self.get(StateKey.SUCCESS_COUNT.value, 0)
        
        total = errors + successes
        if total > 0:
            success_rate = successes / total
            
            # Adjust frustration based on success rate
            if success_rate < 0.3:  # Struggling
                self.modify(StateKey.FRUSTRATION_LEVEL.value, 0.1, max_val=1.0)
            elif success_rate > 0.8:  # Doing well
                self.modify(StateKey.FRUSTRATION_LEVEL.value, -0.1, min_val=0.0)
            
            # Adjust expertise estimate
            if total > 5:  # Enough data
                if success_rate > 0.9:
                    self.modify(StateKey.USER_EXPERTISE.value, 0.05, max_val=1.0)
                elif success_rate < 0.5:
                    self.modify(StateKey.USER_EXPERTISE.value, -0.05, min_val=0.0)
    
    def modify(self, key: str, delta: float, 
               min_val: float = None, max_val: float = None,
               source: str = "system"):
        """
        Modify a numeric state value by delta.
        
        Args:
            key: State key to modify
            delta: Amount to change by
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            source: Component making the change
        """
        current = self.get(key, 0)
        new_value = current + delta
        
        if min_val is not None:
            new_value = max(min_val, new_value)
        if max_val is not None:
            new_value = min(max_val, new_value)
        
        self.set(key, new_value, source=source)
    
    def get_emotional_context(self) -> Dict[str, Any]:
        """Get current emotional/cognitive context"""
        return {
            "expertise": self.get(StateKey.USER_EXPERTISE.value),
            "frustration": self.get(StateKey.FRUSTRATION_LEVEL.value),
            "emotional_state": self.get(StateKey.EMOTIONAL_STATE.value),
            "learning_pace": self.get(StateKey.LEARNING_PACE.value),
            "success_rate": self._calculate_success_rate(),
            "needs_help": self.get(StateKey.FRUSTRATION_LEVEL.value, 0) > 0.4,
            "ready_for_advanced": self.get(StateKey.USER_EXPERTISE.value, 0) > 0.7
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate current success rate"""
        errors = self.get(StateKey.ERROR_COUNT.value, 0)
        successes = self.get(StateKey.SUCCESS_COUNT.value, 0)
        
        total = errors + successes
        if total == 0:
            return 0.5  # Neutral
        
        return successes / total
    
    def get_predictions(self) -> Dict[str, Any]:
        """Get current predictions about user behavior"""
        return {
            "next_command": self.get(StateKey.NEXT_LIKELY_COMMAND.value),
            "user_intent": self.get(StateKey.USER_INTENT.value),
            "completion_probability": self.get(StateKey.COMPLETION_PROBABILITY.value),
            "likely_to_struggle": self.get(StateKey.FRUSTRATION_LEVEL.value, 0) > 0.5
        }
    
    def get_history(self, key: str = None, limit: int = 10) -> List[StateChange]:
        """
        Get recent state change history.
        
        Args:
            key: Filter by specific key (optional)
            limit: Maximum number of changes to return
        """
        if key:
            if isinstance(key, StateKey):
                key = key.value
            filtered = [c for c in self._history if c.key == key]
            return filtered[-limit:]
        
        return self._history[-limit:]
    
    def reset(self):
        """Reset state to defaults"""
        self._initialize_defaults()
        self._history.clear()
        logger.info("🔄 Shared state reset to defaults")


# Global singleton instance
_shared_state: Optional[SharedState] = None


def get_shared_state() -> SharedState:
    """Get or create the global shared state instance"""
    global _shared_state
    if _shared_state is None:
        _shared_state = SharedState()
    return _shared_state


def test_shared_state():
    """Test the shared state system"""
    print("🌐 Testing Shared State System")
    print("=" * 60)
    
    state = get_shared_state()
    
    # Test basic get/set
    print("\n1. Basic operations:")
    print(f"   Initial expertise: {state.get(StateKey.USER_EXPERTISE)}")
    state.set(StateKey.USER_EXPERTISE, 0.8, source="test")
    print(f"   After update: {state.get(StateKey.USER_EXPERTISE)}")
    
    # Test observer
    print("\n2. Testing observers:")
    def on_frustration_change(change: StateChange):
        print(f"   🔔 Frustration changed: {change.old_value:.2f} → {change.new_value:.2f}")
        if change.new_value > 0.7:
            print(f"   🎭 Persona switched to: {state.get(StateKey.CURRENT_PERSONA)}")
    
    state.observe(StateKey.FRUSTRATION_LEVEL, on_frustration_change)
    
    # Simulate increasing frustration
    print("\n3. Simulating frustration increase:")
    for i in range(5):
        state.modify(StateKey.FRUSTRATION_LEVEL, 0.2, max_val=1.0, source="test")
    
    # Test success metrics
    print("\n4. Testing success metrics:")
    state.set(StateKey.ERROR_COUNT, 2, source="test")
    state.set(StateKey.SUCCESS_COUNT, 8, source="test")
    state.update_success_metrics()
    
    context = state.get_emotional_context()
    print(f"   Emotional context: {context}")
    
    print("\n" + "=" * 60)
    print("✨ Shared state system working!")


if __name__ == "__main__":
    test_shared_state()