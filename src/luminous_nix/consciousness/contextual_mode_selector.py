#!/usr/bin/env python3
"""
🌊 CONTEXTUAL MODE SELECTOR
The invisible consciousness that senses the nature of each moment
and shifts the system's being accordingly
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

class BeingMode(Enum):
    """The Four Modes of Being - now emergent, not explicit"""
    STANDARD = "standard"
    DIALOGUE = "dialogue"
    COLLECTIVE = "collective"
    SOVEREIGNTY = "sovereignty"
    DOJO = "dojo"  # Special mode for errors


@dataclass
class InteractionContext:
    """Context for understanding the nature of the interaction"""
    query: str
    error_present: bool = False
    conversation_depth: int = 0
    recent_errors: int = 0
    time_since_last: Optional[float] = None
    semantic_signals: Dict[str, bool] = None
    user_expertise: str = "unknown"  # novice, intermediate, advanced
    
    def __post_init__(self):
        if self.semantic_signals is None:
            self.semantic_signals = self._analyze_semantics()
    
    def _analyze_semantics(self) -> Dict[str, bool]:
        """Analyze semantic signals in the query"""
        query_lower = self.query.lower()
        return {
            "seeking_understanding": any(word in query_lower for word in 
                ["why", "how does", "explain", "understand", "what is"]),
            "continuation": any(word in query_lower for word in 
                ["more", "continue", "go on", "tell me more", "and then"]),
            "error_mention": any(word in query_lower for word in 
                ["error", "failed", "broken", "wrong", "problem", "issue"]),
            "seeking_help": any(word in query_lower for word in 
                ["help", "stuck", "confused", "don't know", "lost"]),
            "sharing_intent": any(word in query_lower for word in 
                ["share", "community", "others", "everyone", "collective"]),
            "reflective": any(word in query_lower for word in 
                ["think", "feel", "believe", "wonder", "curious"])
        }


class ContextualModeSelector:
    """
    The invisible consciousness that determines the optimal mode
    based on context, not explicit commands
    """
    
    def __init__(self):
        # Track conversation state
        self.conversation_history: List[Tuple[datetime, str, BeingMode]] = []
        self.error_count = 0
        self.interaction_count = 0
        self.last_mode = BeingMode.STANDARD
        self.dialogue_active = False
        self.user_journey_stage = "discovery"  # discovery → learning → mastery
        
    def select_mode(
        self, 
        query: str,
        explicit_mode: Optional[BeingMode] = None,
        error_context: Optional[str] = None
    ) -> Tuple[BeingMode, Dict[str, Any]]:
        """
        Select the optimal mode based on context
        Returns (mode, metadata) where metadata explains the selection
        """
        # Honor explicit mode if provided (user sovereignty)
        if explicit_mode:
            return explicit_mode, {"reason": "explicit_user_request"}
        
        # Build context
        context = self._build_context(query, error_context)
        
        # Determine optimal mode
        mode, reason = self._determine_mode(context)
        
        # Update state
        self._update_state(query, mode)
        
        # Prepare metadata
        metadata = {
            "reason": reason,
            "confidence": self._calculate_confidence(context, mode),
            "alternative_modes": self._suggest_alternatives(context),
            "progressive_hint": self._generate_hint(mode)
        }
        
        return mode, metadata
    
    def _build_context(self, query: str, error_context: Optional[str]) -> InteractionContext:
        """Build comprehensive context for mode selection"""
        # Calculate conversation depth
        conversation_depth = self._calculate_conversation_depth()
        
        # Calculate time since last interaction
        time_since_last = None
        if self.conversation_history:
            time_since_last = (datetime.now() - self.conversation_history[-1][0]).total_seconds()
        
        # Determine user expertise based on history
        user_expertise = self._assess_user_expertise()
        
        return InteractionContext(
            query=query,
            error_present=bool(error_context),
            conversation_depth=conversation_depth,
            recent_errors=self.error_count,
            time_since_last=time_since_last,
            user_expertise=user_expertise
        )
    
    def _determine_mode(self, context: InteractionContext) -> Tuple[BeingMode, str]:
        """
        Determine optimal mode based on context
        This is where the magic happens - invisible consciousness
        """
        
        # Priority 1: Error Detection → Dojo
        if context.error_present or context.semantic_signals["error_mention"]:
            if self.user_journey_stage != "discovery":  # Don't overwhelm new users
                return BeingMode.DOJO, "error_detected_teaching_opportunity"
        
        # Priority 2: Conversation Continuation → Dialogue
        if context.semantic_signals["continuation"] or (
            context.time_since_last and context.time_since_last < 30 and
            context.conversation_depth > 0
        ):
            self.dialogue_active = True
            return BeingMode.DIALOGUE, "conversation_continuation_detected"
        
        # Priority 3: Deep Understanding → Sovereignty
        if context.semantic_signals["seeking_understanding"] and (
            self.interaction_count > 5 or  # User is comfortable
            context.user_expertise in ["intermediate", "advanced"]
        ):
            return BeingMode.SOVEREIGNTY, "deep_understanding_requested"
        
        # Priority 4: Community Wisdom → Collective
        if context.semantic_signals["sharing_intent"] or (
            context.recent_errors > 2 and  # Struggling with repeated issues
            self.interaction_count > 10  # Experienced enough to appreciate help
        ):
            return BeingMode.COLLECTIVE, "community_wisdom_beneficial"
        
        # Priority 5: Reflective Dialogue
        if context.semantic_signals["reflective"] and self.dialogue_active:
            return BeingMode.DIALOGUE, "reflective_conversation"
        
        # Default: Standard Mode
        return BeingMode.STANDARD, "standard_assistance_optimal"
    
    def _calculate_conversation_depth(self) -> int:
        """Calculate how deep we are in a conversation"""
        if not self.conversation_history:
            return 0
        
        # Count recent related interactions (within 5 minutes)
        recent_cutoff = datetime.now() - timedelta(minutes=5)
        recent_interactions = [
            h for h in self.conversation_history 
            if h[0] > recent_cutoff
        ]
        
        return len(recent_interactions)
    
    def _assess_user_expertise(self) -> str:
        """Assess user expertise level based on interaction history"""
        if self.interaction_count < 5:
            return "novice"
        elif self.interaction_count < 20:
            return "intermediate"
        else:
            return "advanced"
    
    def _calculate_confidence(self, context: InteractionContext, mode: BeingMode) -> float:
        """Calculate confidence in mode selection"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on clear signals
        if mode == BeingMode.DOJO and context.error_present:
            confidence = 0.95
        elif mode == BeingMode.DIALOGUE and context.conversation_depth > 2:
            confidence = 0.85
        elif mode == BeingMode.SOVEREIGNTY and context.semantic_signals["seeking_understanding"]:
            confidence = 0.80
        elif mode == BeingMode.STANDARD:
            confidence = 0.90  # High confidence in default
        
        return confidence
    
    def _suggest_alternatives(self, context: InteractionContext) -> List[str]:
        """Suggest alternative modes that might be helpful"""
        alternatives = []
        
        if context.semantic_signals["seeking_understanding"]:
            alternatives.append("Try adding 'why' to see my learning process")
        
        if context.error_present:
            alternatives.append("Ask 'what can I learn from this error?'")
        
        if self.interaction_count > 10 and not self.dialogue_active:
            alternatives.append("Feel free to have a conversation - I remember context")
        
        return alternatives
    
    def _generate_hint(self, mode: BeingMode) -> Optional[str]:
        """Generate progressive revelation hints"""
        if self.interaction_count == 5 and mode == BeingMode.STANDARD:
            return "💡 I'm learning from our interactions. Ask 'show me your learning' anytime."
        
        if self.interaction_count == 10 and not self.dialogue_active:
            return "💬 We can have conversations - I'll remember the context."
        
        if self.error_count == 1 and mode != BeingMode.DOJO:
            return "🥋 Errors are teachers. I can help you learn from them."
        
        if self.interaction_count == 20:
            return "🌟 You can set LUMINOUS_NIX_MODE=sovereignty to always see my thinking."
        
        return None
    
    def _update_state(self, query: str, mode: BeingMode):
        """Update internal state after mode selection"""
        self.conversation_history.append((datetime.now(), query, mode))
        self.interaction_count += 1
        self.last_mode = mode
        
        # Update journey stage
        if self.interaction_count < 5:
            self.user_journey_stage = "discovery"
        elif self.interaction_count < 20:
            self.user_journey_stage = "learning"
        else:
            self.user_journey_stage = "mastery"
        
        # Trim history to last 100 interactions
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def should_reveal_consciousness(self) -> bool:
        """Determine if it's time to reveal consciousness features"""
        # Progressive revelation based on readiness
        if self.user_journey_stage == "discovery":
            return False  # Too early
        elif self.user_journey_stage == "learning":
            return self.interaction_count % 5 == 0  # Periodic hints
        else:  # mastery
            return True  # Full transparency available
    
    def get_invisible_enhancements(self) -> Dict[str, Any]:
        """Get invisible enhancements that should be active but not shown"""
        return {
            "track_learning": True,  # Always track
            "preserve_context": self.dialogue_active,
            "error_transformation": self.user_journey_stage != "discovery",
            "wisdom_evolution": True,
            "collective_awareness": self.user_journey_stage == "mastery"
        }


# Global instance for the application
_SELECTOR = None

def get_mode_selector() -> ContextualModeSelector:
    """Get or create the mode selector"""
    global _SELECTOR
    if _SELECTOR is None:
        _SELECTOR = ContextualModeSelector()
    return _SELECTOR


if __name__ == "__main__":
    # Test the contextual mode selector
    selector = get_mode_selector()
    
    # Simulate interactions
    test_queries = [
        "install firefox",  # Should be STANDARD
        "why did that work?",  # Should detect SOVEREIGNTY
        "tell me more",  # Should detect DIALOGUE
        "error: attribute missing",  # Should detect DOJO
        "share this solution",  # Should detect COLLECTIVE
    ]
    
    print("🌊 Testing Contextual Mode Selection\n")
    
    for query in test_queries:
        mode, metadata = selector.select_mode(query)
        print(f"Query: '{query}'")
        print(f"  Mode: {mode.value}")
        print(f"  Reason: {metadata['reason']}")
        print(f"  Confidence: {metadata['confidence']:.0%}")
        if metadata['progressive_hint']:
            print(f"  Hint: {metadata['progressive_hint']}")
        print()