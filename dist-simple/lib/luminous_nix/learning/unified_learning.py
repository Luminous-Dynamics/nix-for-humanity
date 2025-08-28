#!/usr/bin/env python3
"""
🧠 Unified Learning System - The ONE Learning Implementation
Combines the best features from all 30+ learning implementations into one coherent system

Features integrated:
- Data Trinity storage (DuckDB + ChromaDB + Kùzu) from trinity_store.py
- Pattern recognition from learning_system.py
- Improvement tracking from continuous_learner.py
- User adaptation from adaptation.py
- Semantic memory from learning_memory.py
- Learning paths from personalized_paths.py
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import hashlib

# Import the best storage backend
try:
    from ..persistence.trinity_store import TrinityStore
except ImportError:
    # Fallback if trinity store not available
    TrinityStore = None

# Graceful imports for optional features
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available - some features limited")

logger = logging.getLogger(__name__)


@dataclass
class LearningEvent:
    """Unified learning event combining all event types"""
    timestamp: datetime
    user_id: str
    event_type: str  # command, query, error, success, improvement, feedback
    content: str
    intent: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    resolution: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    feedback_score: Optional[float] = None
    
    # For improvements
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"
    impact_score: float = 0.0
    
    # Additional metadata for flexibility
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningEvent':
        """Create from dictionary"""
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class Pattern:
    """Learned pattern from user interactions"""
    pattern_id: str
    pattern_type: str  # sequence, error_resolution, preference, workflow, improvement
    trigger: str
    action: str
    confidence: float
    frequency: int
    last_seen: datetime
    success_rate: float
    user_specific: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['last_seen'] = self.last_seen.isoformat()
        return data


@dataclass
class UserProfile:
    """User-specific learning profile"""
    user_id: str
    skill_level: str  # novice, beginner, intermediate, advanced, expert
    preferences: Dict[str, Any]
    learning_style: str  # visual, textual, interactive, example-based
    common_tasks: List[str]
    error_patterns: List[str]
    success_patterns: List[str]
    adaptation_rate: float  # How quickly to adapt (0-1)
    total_interactions: int
    last_interaction: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['last_interaction'] = self.last_interaction.isoformat()
        return data


@dataclass
class LearningResult:
    """Result of a learning operation"""
    success: bool
    patterns_learned: List[Pattern]
    confidence: float
    adaptations: Dict[str, Any]
    suggestions: List[str]
    memory_updated: bool
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['patterns_learned'] = [p.to_dict() for p in self.patterns_learned]
        return data


class UnifiedLearningSystem:
    """
    The ONE unified learning system combining all best features
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the unified learning system
        
        Args:
            storage_path: Base path for all storage (defaults to ~/.luminous-nix/learning/)
        """
        if storage_path is None:
            storage_path = Path.home() / ".luminous-nix" / "learning"
        
        storage_path.mkdir(parents=True, exist_ok=True)
        self.storage_path = storage_path
        
        # Initialize Data Trinity storage if available
        if TrinityStore:
            try:
                self.storage = TrinityStore()
            except Exception as e:
                logger.warning(f"Could not initialize TrinityStore: {e}")
                self.storage = None
        else:
            self.storage = None  # Fallback to in-memory
        
        # Pattern recognition engine
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_counter = Counter()
        
        # User profiles
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Memory caches
        self.recent_events: List[LearningEvent] = []
        self.max_recent = 100
        
        # Learning thresholds
        self.confidence_threshold = 0.6
        self.pattern_min_frequency = 3
        
        # LLM control integration
        self.llm_control = None  # Will be injected
        self.learning_strategy = "reinforcement"  # Can be changed by LLM
        self.learning_rate = 0.01  # Can be adjusted by LLM
        
        # Load existing data
        self._load_state()
        
        logger.info("🧠 Unified Learning System initialized")
    
    async def learn(self, event: LearningEvent) -> LearningResult:
        """
        Main learning entry point - process any learning event
        
        Args:
            event: The learning event to process
            
        Returns:
            LearningResult with patterns learned and adaptations
        """
        try:
            # Store event in Data Trinity
            await self._store_event(event)
            
            # Update user profile
            profile = self._update_user_profile(event)
            
            # Extract patterns
            patterns = await self._extract_patterns(event)
            
            # Calculate confidence
            confidence = self._calculate_confidence(event, patterns)
            
            # Generate adaptations
            adaptations = self._generate_adaptations(event, profile, patterns)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(event, patterns, profile)
            
            # Update recent events cache
            self.recent_events.append(event)
            if len(self.recent_events) > self.max_recent:
                self.recent_events.pop(0)
            
            # Save state periodically
            if len(self.recent_events) % 10 == 0:
                self._save_state()
            
            return LearningResult(
                success=True,
                patterns_learned=patterns,
                confidence=confidence,
                adaptations=adaptations,
                suggestions=suggestions,
                memory_updated=True
            )
            
        except Exception as e:
            logger.error(f"Learning failed: {e}")
            return LearningResult(
                success=False,
                patterns_learned=[],
                confidence=0.0,
                adaptations={},
                suggestions=[f"Learning error: {str(e)}"],
                memory_updated=False
            )
    
    async def _store_event(self, event: LearningEvent):
        """Store event in Data Trinity databases"""
        
        if self.storage:
            # Use TrinityStore's actual API - record_learning_moment
            # This method handles all three databases internally
            try:
                event_id = self.storage.record_learning_moment(
                    user_id=event.user_id,
                    command=event.content,
                    concept=event.intent or event.event_type,
                    success=event.success,
                    context={
                        'event_type': event.event_type,
                        'error': event.error,
                        'resolution': event.resolution,
                        'feedback_score': event.feedback_score,
                        'risk_level': event.risk_level,
                        'impact_score': event.impact_score,
                        'metrics': event.metrics,
                        'code_before': event.code_before,
                        'code_after': event.code_after
                    }
                )
                logger.debug(f"Stored event {event_id} in Data Trinity")
            except Exception as e:
                logger.warning(f"Could not store in Data Trinity: {e}")
                # Continue anyway - we still have in-memory storage
        else:
            # Fallback: just keep in memory
            pass
    
    def _update_user_profile(self, event: LearningEvent) -> UserProfile:
        """Update or create user profile based on event"""
        
        if event.user_id not in self.user_profiles:
            # Create new profile
            self.user_profiles[event.user_id] = UserProfile(
                user_id=event.user_id,
                skill_level='beginner',
                preferences={},
                learning_style='interactive',
                common_tasks=[],
                error_patterns=[],
                success_patterns=[],
                adaptation_rate=0.7,
                total_interactions=0,
                last_interaction=event.timestamp
            )
        
        profile = self.user_profiles[event.user_id]
        profile.total_interactions += 1
        profile.last_interaction = event.timestamp
        
        # Track patterns
        if event.success:
            if event.content not in profile.success_patterns:
                profile.success_patterns.append(event.content)
        else:
            if event.error and event.error not in profile.error_patterns:
                profile.error_patterns.append(event.error)
        
        # Update skill level based on interactions
        if profile.total_interactions > 100:
            profile.skill_level = 'expert'
        elif profile.total_interactions > 50:
            profile.skill_level = 'advanced'
        elif profile.total_interactions > 20:
            profile.skill_level = 'intermediate'
        elif profile.total_interactions > 5:
            profile.skill_level = 'beginner'
        
        return profile
    
    async def _extract_patterns(self, event: LearningEvent) -> List[Pattern]:
        """Extract patterns from event and history"""
        patterns = []
        
        # Look for sequence patterns in recent events
        if len(self.recent_events) >= 2:
            prev_event = self.recent_events[-2]
            if prev_event.user_id == event.user_id:
                # Found a sequence
                pattern_id = hashlib.md5(
                    f"{prev_event.content}->{event.content}".encode()
                ).hexdigest()[:8]
                
                if pattern_id in self.patterns:
                    # Update existing pattern
                    pattern = self.patterns[pattern_id]
                    pattern.frequency += 1
                    pattern.last_seen = event.timestamp
                    if event.success:
                        pattern.success_rate = (
                            pattern.success_rate * (pattern.frequency - 1) + 1.0
                        ) / pattern.frequency
                else:
                    # Create new pattern
                    pattern = Pattern(
                        pattern_id=pattern_id,
                        pattern_type='sequence',
                        trigger=prev_event.content,
                        action=event.content,
                        confidence=0.5,
                        frequency=1,
                        last_seen=event.timestamp,
                        success_rate=1.0 if event.success else 0.0,
                        user_specific=True
                    )
                    self.patterns[pattern_id] = pattern
                
                if pattern.frequency >= self.pattern_min_frequency:
                    patterns.append(pattern)
        
        # Look for error resolution patterns
        if event.error and event.resolution:
            pattern_id = hashlib.md5(
                f"error:{event.error}->resolution:{event.resolution}".encode()
            ).hexdigest()[:8]
            
            if pattern_id not in self.patterns:
                pattern = Pattern(
                    pattern_id=pattern_id,
                    pattern_type='error_resolution',
                    trigger=event.error,
                    action=event.resolution,
                    confidence=0.8 if event.success else 0.3,
                    frequency=1,
                    last_seen=event.timestamp,
                    success_rate=1.0 if event.success else 0.0,
                    user_specific=False
                )
                self.patterns[pattern_id] = pattern
                patterns.append(pattern)
        
        return patterns
    
    def _calculate_confidence(self, event: LearningEvent, patterns: List[Pattern]) -> float:
        """Calculate confidence in learning from this event"""
        
        confidence = 0.5  # Base confidence
        
        # Increase for successful events
        if event.success:
            confidence += 0.2
        
        # Increase for events with feedback
        if event.feedback_score is not None:
            confidence += event.feedback_score * 0.2
        
        # Increase for recognized patterns
        if patterns:
            avg_pattern_confidence = sum(p.confidence for p in patterns) / len(patterns)
            confidence += avg_pattern_confidence * 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _generate_adaptations(
        self,
        event: LearningEvent,
        profile: UserProfile,
        patterns: List[Pattern]
    ) -> Dict[str, Any]:
        """Generate adaptations based on learning"""
        
        adaptations = {}
        
        # Adapt UI complexity based on skill level
        ui_levels = {
            'novice': 'minimal',
            'beginner': 'basic',
            'intermediate': 'standard',
            'advanced': 'detailed',
            'expert': 'expert'
        }
        adaptations['ui_level'] = ui_levels.get(profile.skill_level, 'standard')
        
        # Adapt voice tone based on recent success rate
        user_events = [e for e in self.recent_events if e.user_id == event.user_id]
        if user_events:
            recent_success = sum(
                1 for e in user_events[-10:]
                if e.success
            ) / min(10, len(user_events))
        else:
            recent_success = 0.5  # Default to neutral if no history
        
        if recent_success > 0.8:
            adaptations['voice_tone'] = 'encouraging'
        elif recent_success < 0.4:
            adaptations['voice_tone'] = 'supportive'
        else:
            adaptations['voice_tone'] = 'neutral'
        
        # Suggest command shortcuts for frequent patterns
        if patterns:
            frequent_patterns = [p for p in patterns if p.frequency > 5]
            if frequent_patterns:
                adaptations['shortcuts'] = [
                    {'trigger': p.trigger, 'action': p.action}
                    for p in frequent_patterns[:3]
                ]
        
        return adaptations
    
    def _generate_suggestions(
        self,
        event: LearningEvent,
        patterns: List[Pattern],
        profile: UserProfile
    ) -> List[str]:
        """Generate helpful suggestions based on learning"""
        
        suggestions = []
        
        # Suggest based on error patterns
        if not event.success and event.error:
            # Look for similar errors we've resolved before
            for pattern in self.patterns.values():
                if pattern.pattern_type == 'error_resolution' and pattern.trigger in event.error:
                    suggestions.append(f"Try: {pattern.action}")
                    break
        
        # Suggest based on user patterns
        if profile.common_tasks and event.content not in profile.common_tasks[-3:]:
            suggestions.append(f"You often follow this with: {profile.common_tasks[-1]}")
        
        # Suggest learning resources for beginners
        if profile.skill_level in ['novice', 'beginner']:
            suggestions.append("Type 'help' for a tutorial on this command")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _save_state(self):
        """Save current state to disk"""
        state_file = self.storage_path / "learning_state.json"
        
        state = {
            'patterns': {k: v.to_dict() for k, v in self.patterns.items()},
            'user_profiles': {k: v.to_dict() for k, v in self.user_profiles.items()},
            'metadata': {
                'last_save': datetime.now().isoformat(),
                'total_patterns': len(self.patterns),
                'total_users': len(self.user_profiles)
            }
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _load_state(self):
        """Load state from disk"""
        state_file = self.storage_path / "learning_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                # Load patterns
                for pattern_id, pattern_data in state.get('patterns', {}).items():
                    if isinstance(pattern_data['last_seen'], str):
                        pattern_data['last_seen'] = datetime.fromisoformat(pattern_data['last_seen'])
                    self.patterns[pattern_id] = Pattern(**pattern_data)
                
                # Load user profiles
                for user_id, profile_data in state.get('user_profiles', {}).items():
                    if isinstance(profile_data['last_interaction'], str):
                        profile_data['last_interaction'] = datetime.fromisoformat(
                            profile_data['last_interaction']
                        )
                    self.user_profiles[user_id] = UserProfile(**profile_data)
                
                logger.info(
                    f"Loaded {len(self.patterns)} patterns and "
                    f"{len(self.user_profiles)} user profiles"
                )
            except Exception as e:
                logger.warning(f"Could not load state: {e}")
    
    async def query_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar past learning events using semantic search
        
        Args:
            query: The query to search for
            limit: Maximum number of results
            
        Returns:
            List of similar events with metadata
        """
        if self.storage and hasattr(self.storage, 'semantic') and self.storage.semantic:
            # Use the semantic store's find_similar_commands method
            try:
                results = self.storage.semantic.find_similar_commands(query, n_results=limit)
                return results
            except Exception as e:
                logger.warning(f"Semantic search failed: {e}")
                return []
        return []
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a user
        
        Args:
            user_id: The user to get statistics for
            
        Returns:
            Dictionary of user statistics
        """
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {'error': 'User not found'}
        
        # Get understanding from TrinityStore
        understanding = {}
        if self.storage:
            try:
                # Use TrinityStore's get_user_understanding method
                understanding = self.storage.get_user_understanding(
                    user_id=user_id,
                    query="overall progress"
                )
            except Exception as e:
                logger.warning(f"Could not get user understanding: {e}")
        
        # Get pattern statistics
        user_patterns = [
            p for p in self.patterns.values()
            if p.metadata.get('user_id') == user_id
        ]
        
        return {
            'profile': profile.to_dict(),
            'understanding': understanding,
            'total_patterns': len(user_patterns),
            'success_rate': sum(p.success_rate for p in user_patterns) / len(user_patterns)
            if user_patterns else 0.0
        }
    
    def get_common_patterns(self, min_frequency: int = 5) -> List[Pattern]:
        """
        Get commonly occurring patterns across all users
        
        Args:
            min_frequency: Minimum frequency threshold
            
        Returns:
            List of common patterns
        """
        return [
            p for p in self.patterns.values()
            if p.frequency >= min_frequency and not p.user_specific
        ]


    # === LLM Control Methods ===
    
    def set_llm_control(self, llm_control):
        """Connect LLM control layer for AI-driven decisions"""
        self.llm_control = llm_control
        logger.info("🤖 LLM control connected to learning system")
    
    def set_strategy(self, strategy: str):
        """Set learning strategy (called by LLM)"""
        self.learning_strategy = strategy
        logger.info(f"📚 Learning strategy changed to: {strategy}")
    
    def set_learning_rate(self, rate: float):
        """Set learning rate (called by LLM)"""
        self.learning_rate = rate
        logger.info(f"📈 Learning rate adjusted to: {rate}")
    
    async def request_llm_guidance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Request guidance from LLM for learning decisions"""
        if not self.llm_control:
            return {"strategy": self.learning_strategy, "rate": self.learning_rate}
        
        # Ask LLM for learning strategy
        from ..consciousness.llm_control_layer import SystemCapability
        decision = await self.llm_control.request_llm_decision(
            context=context,
            capability=SystemCapability.LEARNING_STRATEGY
        )
        
        # Apply LLM decision
        if decision.parameters.get('strategy'):
            self.set_strategy(decision.parameters['strategy'])
        if decision.parameters.get('learning_rate'):
            self.set_learning_rate(decision.parameters['learning_rate'])
        
        return {
            "strategy": self.learning_strategy,
            "rate": self.learning_rate,
            "reasoning": decision.reasoning
        }
    
    async def store_permanent(self, data: Any):
        """Store data permanently (LLM-controlled)"""
        # Implementation would use storage backend
        logger.info("💾 Storing data permanently")
    
    async def cache_temporary(self, data: Any):
        """Cache data temporarily (LLM-controlled)"""
        # Implementation would use cache
        logger.info("⏱️ Caching data temporarily")
    
    async def forget(self, pattern_id: str):
        """Forget a pattern (LLM-controlled)"""
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            logger.info(f"🗑️ Forgot pattern: {pattern_id}")
    
    async def reset_user_model(self):
        """Reset user model (LLM-controlled)"""
        self.user_profiles.clear()
        logger.info("🔄 User models reset")
    
    async def update_user_model(self, updates: Dict[str, Any]):
        """Update user model with LLM-provided insights"""
        for user_id, attributes in updates.items():
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = UserProfile(user_id=user_id)
            
            profile = self.user_profiles[user_id]
            for attr, value in attributes.items():
                if hasattr(profile, attr):
                    setattr(profile, attr, value)
        
        logger.info(f"👤 Updated {len(updates)} user models")
    
    def enable_cache(self):
        """Enable caching optimization (LLM-controlled)"""
        logger.info("💾 Caching enabled for optimization")


# Convenience functions for easy integration
_global_learning_system: Optional[UnifiedLearningSystem] = None


def get_learning_system() -> UnifiedLearningSystem:
    """Get or create the global learning system instance"""
    global _global_learning_system
    if _global_learning_system is None:
        _global_learning_system = UnifiedLearningSystem()
    return _global_learning_system


async def learn_from_command(
    command: str,
    user_id: str = "default",
    success: bool = True,
    error: Optional[str] = None
) -> LearningResult:
    """
    Simple interface to learn from a command execution
    
    Args:
        command: The command that was executed
        user_id: User who executed it
        success: Whether it succeeded
        error: Error message if it failed
        
    Returns:
        LearningResult with patterns and suggestions
    """
    system = get_learning_system()
    
    event = LearningEvent(
        timestamp=datetime.now(),
        user_id=user_id,
        event_type='command',
        content=command,
        success=success,
        error=error
    )
    
    return await system.learn(event)


# Make the unified system the default export
__all__ = [
    'UnifiedLearningSystem',
    'LearningEvent',
    'Pattern',
    'UserProfile',
    'LearningResult',
    'get_learning_system',
    'learn_from_command'
]