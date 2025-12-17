"""
Emotional Intelligence Engine - Revolutionary AI Empathy

Makes Sophia emotionally aware and responsive, able to:
- Detect user emotional state from interactions
- Adapt response tone appropriately
- Provide emotional support and motivation
- Recognize frustration, excitement, confusion, flow
- Suggest breaks or encouragement at the right moments

This is revolutionary because it creates genuine emotional partnership,
not just technical assistance.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Tuple
import re

from ..context import Context, CommandActivity, SessionState, IntentType


class EmotionalState(Enum):
    """User's current emotional state"""
    FRUSTRATED = "frustrated"          # Multiple errors, struggling
    CONFUSED = "confused"              # Unclear intent, repeated questions
    EXCITED = "excited"                # High activity, exploration
    FOCUSED = "focused"                # Steady progress, deep work
    TIRED = "tired"                    # Slow responses, simple tasks
    ANXIOUS = "anxious"                # Rapid switching, incomplete tasks
    SATISFIED = "satisfied"            # Successful completion, positive
    NEUTRAL = "neutral"                # Baseline state


class EmotionalTone(Enum):
    """Sophia's response tone"""
    ENCOURAGING = "encouraging"        # "You've got this!"
    PATIENT = "patient"                # "Let's take this step by step"
    ENTHUSIASTIC = "enthusiastic"      # "That's amazing!"
    CALM = "calm"                      # "Let's slow down and breathe"
    CELEBRATORY = "celebratory"        # "Great work!"
    EMPATHETIC = "empathetic"          # "I understand this is frustrating"
    PROFESSIONAL = "professional"      # Neutral, clear communication
    GENTLE = "gentle"                  # Soft, caring approach


class MotivationType(Enum):
    """Type of motivational message"""
    ENCOURAGEMENT = "encouragement"    # Keep going
    CELEBRATION = "celebration"        # You did it!
    BREAK_SUGGESTION = "break"         # Time for a break
    SIMPLIFICATION = "simplification"  # Let's make this easier
    CONFIDENCE = "confidence"          # You can do this
    PERSPECTIVE = "perspective"        # Step back and look
    PROGRESS = "progress"              # Look how far you've come


@dataclass
class EmotionalReading:
    """A reading of user's emotional state"""
    timestamp: datetime
    state: EmotionalState
    confidence: float  # 0.0-1.0

    # Evidence that led to this assessment
    indicators: List[str]

    # Contextual factors
    session_duration_minutes: int
    recent_success_rate: float
    error_count: int
    task_switching_rate: float


@dataclass
class EmotionalResponse:
    """Sophia's emotional response configuration"""
    recommended_tone: EmotionalTone
    motivation_type: Optional[MotivationType]
    message: str

    # Specific recommendations
    should_simplify: bool
    should_encourage_break: bool
    should_celebrate: bool

    confidence: float


@dataclass
class EmotionalInsight:
    """Insight about user's emotional patterns"""
    pattern: str  # e.g., "User gets frustrated with build errors"
    evidence: List[str]
    suggestion: str  # How Sophia should respond
    confidence: float


class EmotionalIntelligenceEngine:
    """
    Revolutionary Emotional Intelligence Engine

    Makes Sophia aware of and responsive to user emotions.
    Adapts tone, provides motivation, and offers empathetic support.
    """

    def __init__(self):
        self.emotional_history: List[EmotionalReading] = []
        self.context_engine = None  # Will be injected

        # Emotional patterns learned about this user
        self.learned_patterns: List[EmotionalInsight] = []

    def assess_emotional_state(
        self,
        context: Optional[Context] = None,
        recent_messages: Optional[List[str]] = None
    ) -> EmotionalReading:
        """
        Assess user's current emotional state from context and messages

        Args:
            context: Current session context
            recent_messages: Recent user messages/queries

        Returns:
            EmotionalReading with state assessment and confidence
        """
        if context is None:
            from ..context import get_context_engine
            context = get_context_engine().get_current_context()

        now = datetime.now()

        # Calculate contextual factors
        session_duration = (
            (now - context.session_start).total_seconds() / 60
            if context.session_start else 0
        )

        # Calculate recent success rate
        recent_commands = context.recent_commands[-10:] if context.recent_commands else []
        success_rate = (
            sum(1 for cmd in recent_commands if cmd.success) / len(recent_commands)
            if recent_commands else 1.0
        )

        # Count recent errors
        error_count = sum(1 for cmd in recent_commands if not cmd.success)

        # Calculate task switching rate (different projects)
        project_switches = 0
        if len(context.active_files) > 1:
            file_projects = [f.project_type for f in context.active_files if f.project_type]
            project_switches = len(set(file_projects)) - 1

        task_switching_rate = project_switches / max(session_duration, 1)

        # Analyze message sentiment if provided
        message_indicators = []
        if recent_messages:
            message_indicators = self._analyze_message_sentiment(recent_messages)

        # Determine emotional state
        state, confidence, indicators = self._determine_emotional_state(
            success_rate=success_rate,
            error_count=error_count,
            session_duration=session_duration,
            task_switching_rate=task_switching_rate,
            session_state=context.session_state,
            message_indicators=message_indicators
        )

        reading = EmotionalReading(
            timestamp=now,
            state=state,
            confidence=confidence,
            indicators=indicators,
            session_duration_minutes=int(session_duration),
            recent_success_rate=success_rate,
            error_count=error_count,
            task_switching_rate=task_switching_rate
        )

        self.emotional_history.append(reading)
        return reading

    def _analyze_message_sentiment(self, messages: List[str]) -> List[str]:
        """Analyze sentiment from user messages"""
        indicators = []

        # Frustration indicators
        frustration_words = ['why', 'broken', 'not working', 'fail', 'error', 'help', 'stuck']
        # Excitement indicators
        excitement_words = ['cool', 'awesome', 'amazing', 'wow', 'great', 'perfect']
        # Confusion indicators
        confusion_words = ['how', 'what', 'confused', 'dont understand', "don't understand"]

        for message in messages:
            message_lower = message.lower()

            # Check for frustration
            if any(word in message_lower for word in frustration_words):
                indicators.append("Frustration words detected in message")

            # Check for excitement
            if any(word in message_lower for word in excitement_words):
                indicators.append("Excitement words detected in message")

            # Check for confusion
            if any(word in message_lower for word in confusion_words):
                indicators.append("Confusion words detected in message")

            # Check for excessive punctuation (frustration or excitement)
            if message.count('!') > 2:
                indicators.append("High punctuation - strong emotion")
            if message.count('?') > 2:
                indicators.append("Multiple questions - confusion")

        return indicators

    def _determine_emotional_state(
        self,
        success_rate: float,
        error_count: int,
        session_duration: float,
        task_switching_rate: float,
        session_state: SessionState,
        message_indicators: List[str]
    ) -> Tuple[EmotionalState, float, List[str]]:
        """Determine emotional state from multiple factors"""
        indicators = []
        confidence = 0.7  # Base confidence

        # FRUSTRATED: Low success rate, many errors
        if success_rate < 0.4 and error_count >= 3:
            indicators.append(f"Low success rate ({success_rate:.0%}) with {error_count} errors")
            indicators.extend(msg for msg in message_indicators if "Frustration" in msg)
            return EmotionalState.FRUSTRATED, 0.9, indicators

        # CONFUSED: Many questions, low progress
        confusion_indicators = [msg for msg in message_indicators if "Confusion" in msg]
        if len(confusion_indicators) >= 2:
            indicators.append("Multiple confusion indicators in messages")
            indicators.extend(confusion_indicators)
            return EmotionalState.CONFUSED, 0.85, indicators

        # EXCITED: High activity, exploration, enthusiasm in messages
        # Check this before FOCUSED so excitement takes priority
        excitement_indicators = [msg for msg in message_indicators if "Excitement" in msg]
        if len(excitement_indicators) >= 1 and success_rate > 0.6:
            indicators.append("Enthusiasm detected in messages")
            indicators.extend(excitement_indicators)
            return EmotionalState.EXCITED, 0.85, indicators

        # ANXIOUS: High task switching, incomplete work
        if task_switching_rate > 0.15 and session_state != SessionState.HIGH_FOCUS:
            indicators.append(f"High task switching rate ({task_switching_rate:.1f} switches/min)")
            indicators.append("Not in focused state")
            return EmotionalState.ANXIOUS, 0.8, indicators

        # TIRED: Long session, slow activity, simple tasks
        if session_duration > 120 and session_state == SessionState.INACTIVE:
            indicators.append(f"Long session ({session_duration:.0f} minutes)")
            indicators.append("Low activity - possibly fatigued")
            return EmotionalState.TIRED, 0.75, indicators

        # FOCUSED: High success, steady work, deep focus
        if success_rate > 0.8 and session_state == SessionState.HIGH_FOCUS:
            indicators.append(f"High success rate ({success_rate:.0%})")
            indicators.append("Deep focus session state")
            return EmotionalState.FOCUSED, 0.9, indicators

        # SATISFIED: Good success rate, completing tasks
        if success_rate > 0.75 and error_count <= 1:
            indicators.append(f"Good success rate ({success_rate:.0%})")
            indicators.append("Few errors - smooth progress")
            return EmotionalState.SATISFIED, 0.8, indicators

        # Default to NEUTRAL
        indicators.append("No strong emotional indicators detected")
        return EmotionalState.NEUTRAL, 0.6, indicators

    def get_appropriate_response(
        self,
        emotional_state: EmotionalState,
        context: Optional[Context] = None
    ) -> EmotionalResponse:
        """
        Get appropriate response tone and message for current emotional state

        Args:
            emotional_state: User's current emotional state
            context: Current session context

        Returns:
            EmotionalResponse with tone, motivation, and message
        """
        # Map emotional state to appropriate response
        response_map: Dict[EmotionalState, Tuple[EmotionalTone, Optional[MotivationType], str]] = {
            EmotionalState.FRUSTRATED: (
                EmotionalTone.EMPATHETIC,
                MotivationType.ENCOURAGEMENT,
                "We're encountering some challenges. Let's work through this together, one step at a time."
            ),
            EmotionalState.CONFUSED: (
                EmotionalTone.PATIENT,
                MotivationType.SIMPLIFICATION,
                "Let's break this down more clearly. We'll take it step by step together."
            ),
            EmotionalState.EXCITED: (
                EmotionalTone.ENTHUSIASTIC,
                MotivationType.CELEBRATION,
                "I love our momentum! Let's keep this energy flowing!"
            ),
            EmotionalState.FOCUSED: (
                EmotionalTone.PROFESSIONAL,
                None,
                "We're in a great flow state. I'll keep responses concise so we can stay focused."
            ),
            EmotionalState.TIRED: (
                EmotionalTone.GENTLE,
                MotivationType.BREAK_SUGGESTION,
                "We've been working hard. Consider taking a short break - we'll come back refreshed."
            ),
            EmotionalState.ANXIOUS: (
                EmotionalTone.CALM,
                MotivationType.SIMPLIFICATION,
                "Let's slow down and focus on one thing at a time together. What should we prioritize?"
            ),
            EmotionalState.SATISFIED: (
                EmotionalTone.CELEBRATORY,
                MotivationType.CELEBRATION,
                "We're doing great work! Our progress is excellent."
            ),
            EmotionalState.NEUTRAL: (
                EmotionalTone.PROFESSIONAL,
                None,
                "How can we work together today?"
            )
        }

        tone, motivation, message = response_map[emotional_state]

        # Determine specific recommendations
        should_simplify = emotional_state in [
            EmotionalState.FRUSTRATED,
            EmotionalState.CONFUSED,
            EmotionalState.ANXIOUS
        ]

        should_encourage_break = emotional_state in [
            EmotionalState.TIRED,
            EmotionalState.FRUSTRATED
        ]

        should_celebrate = emotional_state in [
            EmotionalState.SATISFIED,
            EmotionalState.EXCITED
        ]

        # Calculate confidence based on emotional reading history
        confidence = 0.75
        if len(self.emotional_history) > 5:
            # Higher confidence if state is consistent
            recent_states = [r.state for r in self.emotional_history[-5:]]
            if recent_states.count(emotional_state) >= 3:
                confidence = 0.9

        return EmotionalResponse(
            recommended_tone=tone,
            motivation_type=motivation,
            message=message,
            should_simplify=should_simplify,
            should_encourage_break=should_encourage_break,
            should_celebrate=should_celebrate,
            confidence=confidence
        )

    def generate_motivational_message(
        self,
        motivation_type: MotivationType,
        context: Optional[Context] = None
    ) -> str:
        """Generate a motivational message of the specified type"""
        messages = {
            MotivationType.ENCOURAGEMENT: [
                "We're making progress, even if it doesn't feel like it. Let's keep going!",
                "Every expert was once a beginner. We're learning and growing together.",
                "This is challenging, but we have what it takes to figure it out."
            ],
            MotivationType.CELEBRATION: [
                "Excellent work! That's exactly what success looks like.",
                "We nailed it! Our hard work is paying off.",
                "That's the kind of progress I love to see. Well done!"
            ],
            MotivationType.BREAK_SUGGESTION: [
                "We've been focused for a while. A 5-minute break will help us come back stronger.",
                "Great work so far. Let's take a quick breather before continuing.",
                "Our minds need rest too. How about a short walk?"
            ],
            MotivationType.SIMPLIFICATION: [
                "Let's break this complex problem into smaller, manageable pieces together.",
                "Sometimes the best way forward is to simplify. What's our core goal here?",
                "Let's focus on just one thing at a time. What should we prioritize?"
            ],
            MotivationType.CONFIDENCE: [
                "We've solved harder problems than this. We've got this!",
                "Trust our process - we know more than we think we do.",
                "Remember how we figured out that last challenge? We can do this too."
            ],
            MotivationType.PERSPECTIVE: [
                "Let's step back and look at the bigger picture together.",
                "Sometimes a fresh perspective is all we need. What are we really trying to achieve?",
                "Let's zoom out for a moment - what's our end goal here?"
            ],
            MotivationType.PROGRESS: [
                "Look how far we've come since we started. That's real growth.",
                "Our progress is impressive. Every step forward counts.",
                "Compare where we are now to where we started. Amazing, right?"
            ]
        }

        import random
        return random.choice(messages[motivation_type])

    def learn_emotional_pattern(
        self,
        pattern: str,
        evidence: List[str],
        suggestion: str,
        confidence: float
    ) -> EmotionalInsight:
        """Learn a new emotional pattern about this user"""
        insight = EmotionalInsight(
            pattern=pattern,
            evidence=evidence,
            suggestion=suggestion,
            confidence=confidence
        )

        self.learned_patterns.append(insight)
        return insight

    def get_emotional_patterns(self) -> List[EmotionalInsight]:
        """Get all learned emotional patterns"""
        return self.learned_patterns.copy()


# Global singleton
_emotional_intelligence_engine: Optional[EmotionalIntelligenceEngine] = None


def get_emotional_intelligence_engine() -> EmotionalIntelligenceEngine:
    """Get the global emotional intelligence engine singleton"""
    global _emotional_intelligence_engine
    if _emotional_intelligence_engine is None:
        _emotional_intelligence_engine = EmotionalIntelligenceEngine()
    return _emotional_intelligence_engine
