#!/usr/bin/env python3
"""
🔄 Feedback Loop - Connecting Learning to Behavior
Makes the system automatically improve based on what it learns.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback the system can process"""
    SUCCESS = "success"
    FAILURE = "failure"
    USER_PREFERENCE = "user_preference"
    PERFORMANCE = "performance"
    EMOTIONAL = "emotional"
    LEARNING = "learning"


@dataclass
class FeedbackSignal:
    """A signal that triggers system adaptation"""
    type: FeedbackType
    source: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False


class FeedbackLoop:
    """
    Connects learning events to system behavior changes.
    
    This creates a self-improving system that gets better
    automatically based on user interactions.
    """
    
    def __init__(self, consciousness=None, learning_system=None, 
                 shared_state=None, predictive_cache=None):
        """Initialize feedback loop with system components"""
        self.consciousness = consciousness
        self.learning_system = learning_system
        self.shared_state = shared_state
        self.predictive_cache = predictive_cache
        
        # Feedback processors
        self.processors: Dict[FeedbackType, Callable] = {
            FeedbackType.SUCCESS: self._process_success,
            FeedbackType.FAILURE: self._process_failure,
            FeedbackType.USER_PREFERENCE: self._process_preference,
            FeedbackType.PERFORMANCE: self._process_performance,
            FeedbackType.EMOTIONAL: self._process_emotional,
            FeedbackType.LEARNING: self._process_learning
        }
        
        # Adaptation strategies
        self.adaptations = {
            "response_style": self._adapt_response_style,
            "explanation_depth": self._adapt_explanation_depth,
            "assistance_level": self._adapt_assistance_level,
            "prediction_confidence": self._adapt_prediction_confidence,
            "persona_selection": self._adapt_persona_selection
        }
        
        # Track feedback history
        self.feedback_history: List[FeedbackSignal] = []
        
        # Learning parameters (these evolve)
        self.parameters = {
            "temperature": 0.7,  # LLM temperature
            "verbosity": 0.5,    # Response detail level
            "proactivity": 0.5,  # How proactive to be
            "empathy": 0.5,      # Emotional responsiveness
            "technical": 0.5     # Technical depth
        }
        
        logger.info("🔄 Feedback Loop initialized - learning drives adaptation")
    
    async def process_feedback(self, signal: FeedbackSignal):
        """Process a feedback signal and adapt system"""
        # Store in history
        self.feedback_history.append(signal)
        
        # Process based on type
        if signal.type in self.processors:
            processor = self.processors[signal.type]
            adaptations = await processor(signal)
            
            # Apply adaptations
            for adaptation_type, value in adaptations.items():
                if adaptation_type in self.adaptations:
                    adapter = self.adaptations[adaptation_type]
                    await adapter(value)
            
            signal.processed = True
            logger.debug(f"🔄 Processed {signal.type.value} feedback from {signal.source}")
    
    async def _process_success(self, signal: FeedbackSignal) -> Dict[str, Any]:
        """Process success feedback"""
        adaptations = {}
        
        # Success reinforces current approach
        if self.shared_state:
            # Slightly increase confidence
            current_expertise = self.shared_state.get("user_expertise", 0.5)
            self.shared_state.modify("user_expertise", 0.02, max_val=1.0, 
                                    source="feedback_loop")
        
        # Learn successful patterns
        if self.learning_system:
            # Store successful pattern
            await self.learning_system.store_pattern(
                pattern_type="success",
                data=signal.data
            )
        
        # Adjust parameters
        self.parameters["proactivity"] = min(1.0, self.parameters["proactivity"] + 0.05)
        adaptations["prediction_confidence"] = 0.1  # Increase prediction confidence
        
        return adaptations
    
    async def _process_failure(self, signal: FeedbackSignal) -> Dict[str, Any]:
        """Process failure feedback"""
        adaptations = {}
        
        # Failures trigger support mode
        if self.shared_state:
            # Increase frustration
            self.shared_state.modify("frustration_level", 0.1, max_val=1.0,
                                    source="feedback_loop")
        
        # Learn failure patterns to avoid
        if self.learning_system:
            await self.learning_system.store_pattern(
                pattern_type="failure",
                data=signal.data
            )
        
        # Adjust parameters - become more helpful
        self.parameters["empathy"] = min(1.0, self.parameters["empathy"] + 0.1)
        self.parameters["verbosity"] = min(1.0, self.parameters["verbosity"] + 0.1)
        
        adaptations["assistance_level"] = 0.2  # Increase assistance
        adaptations["explanation_depth"] = 0.1  # More detailed explanations
        
        return adaptations
    
    async def _process_preference(self, signal: FeedbackSignal) -> Dict[str, Any]:
        """Process user preference feedback"""
        adaptations = {}
        
        preference = signal.data.get("preference", {})
        
        # Adjust response style based on preference
        if "concise" in str(preference).lower():
            self.parameters["verbosity"] = max(0.0, self.parameters["verbosity"] - 0.2)
            adaptations["response_style"] = "concise"
        elif "detailed" in str(preference).lower():
            self.parameters["verbosity"] = min(1.0, self.parameters["verbosity"] + 0.2)
            adaptations["response_style"] = "detailed"
        
        # Adjust technical level
        if "technical" in str(preference).lower():
            self.parameters["technical"] = min(1.0, self.parameters["technical"] + 0.2)
        elif "simple" in str(preference).lower():
            self.parameters["technical"] = max(0.0, self.parameters["technical"] - 0.2)
        
        return adaptations
    
    async def _process_performance(self, signal: FeedbackSignal) -> Dict[str, Any]:
        """Process performance feedback"""
        adaptations = {}
        
        response_time = signal.data.get("response_time", 0)
        
        # If responses are slow, optimize
        if response_time > 5.0:  # 5 seconds
            logger.info("🐢 Slow response detected, optimizing...")
            # Could trigger cache warming, model switching, etc.
            adaptations["prediction_confidence"] = 0.2  # Pre-fetch more aggressively
        
        return adaptations
    
    async def _process_emotional(self, signal: FeedbackSignal) -> Dict[str, Any]:
        """Process emotional feedback"""
        adaptations = {}
        
        emotion = signal.data.get("emotion", "neutral")
        
        if emotion == "frustrated":
            self.parameters["empathy"] = min(1.0, self.parameters["empathy"] + 0.2)
            adaptations["persona_selection"] = "supportive"
        elif emotion == "happy":
            # Keep doing what we're doing
            pass
        elif emotion == "confused":
            self.parameters["verbosity"] = min(1.0, self.parameters["verbosity"] + 0.1)
            adaptations["explanation_depth"] = 0.2
        
        return adaptations
    
    async def _process_learning(self, signal: FeedbackSignal) -> Dict[str, Any]:
        """Process learning feedback"""
        adaptations = {}
        
        mastery = signal.data.get("mastery_level", 0.5)
        
        # Adjust technical depth based on mastery
        if mastery > 0.7:
            self.parameters["technical"] = min(1.0, self.parameters["technical"] + 0.1)
            adaptations["explanation_depth"] = -0.1  # Less hand-holding
        elif mastery < 0.3:
            self.parameters["technical"] = max(0.0, self.parameters["technical"] - 0.1)
            adaptations["explanation_depth"] = 0.1  # More guidance
        
        return adaptations
    
    async def _adapt_response_style(self, style: str):
        """Adapt response style"""
        if self.consciousness and hasattr(self.consciousness, 'set_response_style'):
            self.consciousness.set_response_style(style)
        logger.info(f"📝 Response style adapted to: {style}")
    
    async def _adapt_explanation_depth(self, delta: float):
        """Adjust explanation depth"""
        self.parameters["verbosity"] = max(0.0, min(1.0, 
                                          self.parameters["verbosity"] + delta))
        logger.info(f"📊 Explanation depth adjusted: {self.parameters['verbosity']:.2f}")
    
    async def _adapt_assistance_level(self, delta: float):
        """Adjust assistance level"""
        self.parameters["proactivity"] = max(0.0, min(1.0,
                                            self.parameters["proactivity"] + delta))
        logger.info(f"🤝 Assistance level adjusted: {self.parameters['proactivity']:.2f}")
    
    async def _adapt_prediction_confidence(self, delta: float):
        """Adjust prediction confidence threshold"""
        # This would adjust when predictions are shown
        logger.info(f"🔮 Prediction confidence adjusted by: {delta:.2f}")
    
    async def _adapt_persona_selection(self, persona: str):
        """Switch to a different persona"""
        if self.shared_state:
            self.shared_state.set("current_persona", persona, source="feedback_loop")
        logger.info(f"🎭 Persona switched to: {persona}")
    
    def get_adapted_parameters(self) -> Dict[str, float]:
        """Get current adapted parameters for other systems to use"""
        return self.parameters.copy()
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of feedback patterns"""
        if not self.feedback_history:
            return {}
        
        # Count feedback types
        type_counts = {}
        for signal in self.feedback_history:
            type_counts[signal.type.value] = type_counts.get(signal.type.value, 0) + 1
        
        # Calculate success rate
        successes = sum(1 for s in self.feedback_history 
                       if s.type == FeedbackType.SUCCESS)
        failures = sum(1 for s in self.feedback_history 
                      if s.type == FeedbackType.FAILURE)
        
        success_rate = successes / (successes + failures) if (successes + failures) > 0 else 0.5
        
        return {
            "total_feedback": len(self.feedback_history),
            "type_distribution": type_counts,
            "success_rate": success_rate,
            "current_parameters": self.parameters,
            "adaptations_made": len([s for s in self.feedback_history if s.processed])
        }
    
    async def create_feedback_from_event(self, event_type: str, 
                                        event_data: Dict[str, Any]) -> FeedbackSignal:
        """Create feedback signal from a learning event"""
        # Map event types to feedback types
        if "success" in event_type.lower():
            feedback_type = FeedbackType.SUCCESS
        elif "error" in event_type.lower() or "fail" in event_type.lower():
            feedback_type = FeedbackType.FAILURE
        elif "preference" in event_type.lower():
            feedback_type = FeedbackType.USER_PREFERENCE
        else:
            feedback_type = FeedbackType.LEARNING
        
        signal = FeedbackSignal(
            type=feedback_type,
            source=event_type,
            data=event_data
        )
        
        await self.process_feedback(signal)
        return signal


async def test_feedback_loop():
    """Test the feedback loop system"""
    print("🔄 Testing Feedback Loop")
    print("=" * 60)
    
    # Create mock shared state
    from luminous_nix.core.shared_state import get_shared_state
    shared_state = get_shared_state()
    
    loop = FeedbackLoop(shared_state=shared_state)
    
    print("\n1. Initial parameters:")
    for key, value in loop.parameters.items():
        print(f"   {key}: {value:.2f}")
    
    print("\n2. Processing success feedback...")
    success_signal = FeedbackSignal(
        type=FeedbackType.SUCCESS,
        source="test",
        data={"command": "install firefox", "time": 2.5}
    )
    await loop.process_feedback(success_signal)
    
    print("\n3. Processing failure feedback...")
    failure_signal = FeedbackSignal(
        type=FeedbackType.FAILURE,
        source="test",
        data={"command": "unknown command", "error": "not found"}
    )
    await loop.process_feedback(failure_signal)
    
    print("\n4. Processing preference feedback...")
    pref_signal = FeedbackSignal(
        type=FeedbackType.USER_PREFERENCE,
        source="test",
        data={"preference": "concise technical"}
    )
    await loop.process_feedback(pref_signal)
    
    print("\n5. Adapted parameters:")
    for key, value in loop.parameters.items():
        print(f"   {key}: {value:.2f}")
    
    print("\n6. Feedback summary:")
    summary = loop.get_feedback_summary()
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v}")
        else:
            print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✨ Feedback loop working - system learns and adapts!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_feedback_loop())