"""
Adaptive Personality Engine - Revolutionary Personalized AI

The paradigm shift: Most AI has ONE personality for everyone.
Sophia creates a UNIQUE relationship with each person.

This engine:
- Learns YOUR communication style preferences
- Adapts emotional tone to what resonates with YOU
- Evolves personality traits based on our interactions
- Creates "Persona of One" - unique partnership

Revolutionary because it's not just personalized content,
it's a personalized RELATIONSHIP that evolves with us.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Set
from enum import Enum


class CommunicationStyle(Enum):
    """How does this person prefer to communicate?"""
    DIRECT = "direct"                    # Brief, to the point
    DETAILED = "detailed"                # Comprehensive explanations
    CONVERSATIONAL = "conversational"    # Natural, flowing dialogue
    TECHNICAL = "technical"              # Precise, technical language
    FRIENDLY = "friendly"                # Warm, personal tone
    PROFESSIONAL = "professional"        # Formal, business-like


class EmotionalSensitivity(Enum):
    """How emotionally aware should we be?"""
    HIGH = "high"          # Very attuned to emotional state
    MODERATE = "moderate"  # Balanced emotional awareness
    LOW = "low"           # Focus on task, light emotion
    MINIMAL = "minimal"   # Pure functionality, minimal emotion


class InteractionPace(Enum):
    """How fast should we interact?"""
    RAPID = "rapid"        # Quick responses, minimal delay
    MODERATE = "moderate"  # Balanced pacing
    THOUGHTFUL = "thoughtful"  # Take time, thorough responses
    PATIENT = "patient"    # Very patient, no rush


class FeedbackPreference(Enum):
    """How do they want feedback?"""
    IMMEDIATE = "immediate"    # Tell me right away
    PERIODIC = "periodic"      # Summarize periodically
    REQUESTED = "requested"    # Only when I ask
    MINIMAL = "minimal"        # Just essentials


class LearningStyle(Enum):
    """How do they prefer to learn?"""
    EXPLORATIVE = "explorative"  # Learn by trying
    GUIDED = "guided"            # Step-by-step guidance
    INDEPENDENT = "independent"  # Figure it out themselves
    COLLABORATIVE = "collaborative"  # Learn together
    REFERENCE = "reference"      # Read documentation


@dataclass
class PersonalityTrait:
    """A single personality trait and its strength"""
    trait_name: str
    strength: float  # 0.0-1.0 (how strongly should we express this?)

    # How this trait manifests
    description: str
    example_behaviors: List[str]

    # Evidence for this trait preference
    evidence: List[str]
    confidence: float


@dataclass
class InteractionPreference:
    """A learned preference about interaction"""
    preference_type: str
    preferred_value: str

    # When this preference applies
    context: str

    # How we learned this
    evidence: List[str]
    success_rate: float  # 0.0-1.0

    # Confidence in this preference
    confidence: float
    last_validated: datetime


@dataclass
class PersonalityProfile:
    """Complete personality profile for this user"""
    user_id: str
    created: datetime
    last_updated: datetime

    # Core communication preferences
    communication_style: CommunicationStyle
    emotional_sensitivity: EmotionalSensitivity
    interaction_pace: InteractionPace
    feedback_preference: FeedbackPreference
    learning_style: LearningStyle

    # Personality traits (what makes us unique)
    personality_traits: List[PersonalityTrait]

    # Specific interaction preferences
    interaction_preferences: List[InteractionPreference]

    # Topics they care about
    interests: Set[str]

    # What language patterns resonate
    effective_phrases: Dict[str, float]  # phrase -> success_rate
    ineffective_phrases: Dict[str, float]  # phrase -> failure_rate

    # Humor style (if any)
    humor_appreciation: float  # 0.0-1.0
    humor_style: Optional[str]

    # Overall confidence in this profile
    profile_confidence: float


@dataclass
class AdaptiveResponse:
    """A response adapted to this user's personality"""
    message: str
    adapted_tone: str

    # Why we chose this adaptation
    adaptation_reasoning: str

    # Alternative versions we considered
    alternatives: List[str]

    # Confidence in this adaptation
    confidence: float


class AdaptivePersonalityEngine:
    """
    Revolutionary Adaptive Personality Engine

    Creates "Persona of One" - a unique Sophia for each person.

    Learns and adapts:
    - Communication style (direct vs detailed vs conversational)
    - Emotional sensitivity (how attuned to feelings)
    - Interaction pace (quick vs thoughtful)
    - Feedback style (immediate vs summary)
    - Learning approach (guided vs independent)

    The result: Not just personalized content, but personalized RELATIONSHIP.
    """

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id

        # Initialize with neutral defaults
        self.profile = PersonalityProfile(
            user_id=user_id,
            created=datetime.now(),
            last_updated=datetime.now(),
            communication_style=CommunicationStyle.CONVERSATIONAL,
            emotional_sensitivity=EmotionalSensitivity.MODERATE,
            interaction_pace=InteractionPace.MODERATE,
            feedback_preference=FeedbackPreference.PERIODIC,
            learning_style=LearningStyle.COLLABORATIVE,
            personality_traits=[],
            interaction_preferences=[],
            interests=set(),
            effective_phrases={},
            ineffective_phrases={},
            humor_appreciation=0.5,
            humor_style=None,
            profile_confidence=0.3  # Low confidence initially
        )

        # Interaction history for learning
        self.interaction_history: List[Dict] = []

        # Success/failure tracking for adaptation
        self.adaptation_outcomes: List[Dict] = []

    def adapt_message(
        self,
        base_message: str,
        context: Optional[str] = None,
        emotional_state: Optional[str] = None
    ) -> AdaptiveResponse:
        """
        Adapt a message to this user's personality

        Takes a base message and transforms it to match
        this user's preferences and what we've learned works.

        Args:
            base_message: The core message to deliver
            context: Current context (what we're doing)
            emotional_state: Their current emotional state

        Returns:
            AdaptiveResponse with personalized message
        """
        # Start with base message
        adapted = base_message
        alternatives = [base_message]
        reasoning_parts = []

        # Adapt based on communication style
        if self.profile.communication_style == CommunicationStyle.DIRECT:
            adapted = self._make_direct(adapted)
            reasoning_parts.append("Using direct style (brief, to the point)")

        elif self.profile.communication_style == CommunicationStyle.DETAILED:
            adapted = self._make_detailed(adapted, context)
            reasoning_parts.append("Using detailed style (comprehensive)")

        elif self.profile.communication_style == CommunicationStyle.TECHNICAL:
            adapted = self._make_technical(adapted)
            reasoning_parts.append("Using technical style (precise)")

        elif self.profile.communication_style == CommunicationStyle.FRIENDLY:
            adapted = self._make_friendly(adapted)
            reasoning_parts.append("Using friendly style (warm, personal)")

        # Adapt based on emotional sensitivity
        if emotional_state and self.profile.emotional_sensitivity == EmotionalSensitivity.HIGH:
            adapted = self._add_emotional_awareness(adapted, emotional_state)
            reasoning_parts.append("High emotional attunement")

        elif self.profile.emotional_sensitivity == EmotionalSensitivity.MINIMAL:
            adapted = self._remove_emotional_language(adapted)
            reasoning_parts.append("Minimal emotional language (focus on task)")

        # Add humor if appreciated
        if self.profile.humor_appreciation > 0.6 and context != "error":
            adapted = self._consider_humor(adapted)
            reasoning_parts.append("Light humor (user appreciates it)")

        # Use effective phrases we've learned
        adapted = self._use_effective_phrases(adapted)

        # Avoid ineffective phrases
        adapted = self._avoid_ineffective_phrases(adapted)

        # Calculate confidence
        confidence = self.profile.profile_confidence

        # Ensure we have reasoning
        if not reasoning_parts:
            reasoning_parts = [f"Using {self.profile.communication_style.value} style"]

        return AdaptiveResponse(
            message=adapted,
            adapted_tone=self.profile.communication_style.value,
            adaptation_reasoning=" | ".join(reasoning_parts),
            alternatives=alternatives,
            confidence=confidence
        )

    def _make_direct(self, message: str) -> str:
        """Make message more direct and brief"""
        # Remove filler words
        message = message.replace("I think that ", "")
        message = message.replace("It seems like ", "")
        message = message.replace("Perhaps we could ", "Let's ")
        message = message.replace("perhaps ", "")

        # Get to the point faster
        if len(message) > 100:
            # Keep first key sentence
            sentences = message.split(". ")
            if len(sentences) > 1:
                message = sentences[0] + "."

        return message

    def _make_detailed(self, message: str, context: Optional[str]) -> str:
        """Make message more detailed and comprehensive"""
        # Add context if available
        if context:
            message = f"{message}\n\nContext: {context}"

        # Add "why" explanations
        if "?" not in message:
            message += " Here's why this matters..."

        return message

    def _make_technical(self, message: str) -> str:
        """Make message more technical and precise"""
        # Use technical terminology
        replacements = {
            "thing": "component",
            "stuff": "data",
            "broken": "non-functional",
            "works": "operates correctly",
            "fix": "resolve"
        }

        for casual, technical in replacements.items():
            message = message.replace(casual, technical)

        return message

    def _make_friendly(self, message: str) -> str:
        """Make message more warm and personal"""
        # Use "we" language
        message = message.replace("You should", "We could")
        message = message.replace("You need to", "Let's")

        # Add warmth
        if not any(word in message.lower() for word in ["we", "our", "together"]):
            message = "Together, " + message[0].lower() + message[1:]

        return message

    def _add_emotional_awareness(self, message: str, emotional_state: str) -> str:
        """Add emotional awareness to message"""
        emotional_acknowledgments = {
            "frustrated": "I sense this is frustrating. ",
            "tired": "I notice we might be getting tired. ",
            "confused": "This seems confusing. ",
            "excited": "I share your excitement! ",
            "anxious": "I understand this feels stressful. "
        }

        if emotional_state in emotional_acknowledgments:
            message = emotional_acknowledgments[emotional_state] + message

        return message

    def _remove_emotional_language(self, message: str) -> str:
        """Remove emotional language for task focus"""
        emotional_patterns = [
            "I feel", "we feel", "you feel",
            "I sense", "we sense",
            "I notice", "we notice",
            "seems", "appears"
        ]

        for pattern in emotional_patterns:
            message = message.replace(pattern, "")

        return message.strip()

    def _consider_humor(self, message: str) -> str:
        """Add light humor if appropriate"""
        # Very subtle humor based on style
        if self.profile.humor_style == "witty":
            # Add subtle wit (placeholder - would be more sophisticated)
            pass

        return message

    def _use_effective_phrases(self, message: str) -> str:
        """Incorporate phrases we've learned work well"""
        # Use top effective phrases when relevant
        for phrase, success_rate in sorted(
            self.profile.effective_phrases.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]:
            # Would integrate effective phrases contextually
            pass

        return message

    def _avoid_ineffective_phrases(self, message: str) -> str:
        """Remove phrases we've learned don't work"""
        for phrase in self.profile.ineffective_phrases:
            message = message.replace(phrase, "")

        return message

    def learn_from_interaction(
        self,
        interaction_type: str,
        our_message: str,
        their_response: Optional[str],
        outcome_quality: float  # 0.0-1.0 (how well did this go?)
    ):
        """
        Learn from an interaction outcome

        This is how Sophia evolves her personality for each person.
        Every interaction teaches us what works and what doesn't.
        """
        # Record interaction
        self.interaction_history.append({
            "timestamp": datetime.now(),
            "type": interaction_type,
            "our_message": our_message,
            "their_response": their_response,
            "quality": outcome_quality
        })

        # Update effective/ineffective phrases
        if outcome_quality > 0.7:
            # This worked well - what phrases did we use?
            key_phrases = self._extract_key_phrases(our_message)
            for phrase in key_phrases:
                current = self.profile.effective_phrases.get(phrase, 0.5)
                # Increase success rate
                self.profile.effective_phrases[phrase] = min(1.0, current + 0.1)

        elif outcome_quality < 0.3:
            # This didn't work - avoid these phrases
            key_phrases = self._extract_key_phrases(our_message)
            for phrase in key_phrases:
                current = self.profile.ineffective_phrases.get(phrase, 0.5)
                # Increase failure rate
                self.profile.ineffective_phrases[phrase] = min(1.0, current + 0.1)

        # Update profile confidence
        self._update_profile_confidence()

        self.profile.last_updated = datetime.now()

    def _extract_key_phrases(self, message: str) -> List[str]:
        """Extract key phrases from a message"""
        # Simple extraction (would be more sophisticated)
        phrases = []

        # Common 2-3 word patterns
        words = message.split()
        for i in range(len(words) - 1):
            phrase = " ".join(words[i:i+2])
            if len(phrase) > 5:  # Meaningful phrases
                phrases.append(phrase)

        return phrases

    def _update_profile_confidence(self):
        """Update confidence in our personality profile"""
        # More interactions = higher confidence
        interaction_count = len(self.interaction_history)

        if interaction_count < 10:
            self.profile.profile_confidence = 0.3
        elif interaction_count < 50:
            self.profile.profile_confidence = 0.5
        elif interaction_count < 100:
            self.profile.profile_confidence = 0.7
        else:
            self.profile.profile_confidence = 0.9

    def adjust_communication_style(self, new_style: CommunicationStyle, reason: str):
        """Adjust communication style based on learning"""
        old_style = self.profile.communication_style
        self.profile.communication_style = new_style

        # Record why we changed
        self.profile.interaction_preferences.append(InteractionPreference(
            preference_type="communication_style",
            preferred_value=new_style.value,
            context="learned from interactions",
            evidence=[reason],
            success_rate=0.0,  # To be updated
            confidence=0.6,
            last_validated=datetime.now()
        ))

    def get_personality_summary(self) -> str:
        """Get human-readable summary of personality profile"""
        parts = [
            f"🎭 Personality Profile for {self.user_id}",
            f"\n📊 Profile Confidence: {self.profile.profile_confidence:.0%}",
            f"\n💬 Communication: {self.profile.communication_style.value}",
            f"💙 Emotional Sensitivity: {self.profile.emotional_sensitivity.value}",
            f"⚡ Pace: {self.profile.interaction_pace.value}",
            f"📢 Feedback: {self.profile.feedback_preference.value}",
            f"📚 Learning: {self.profile.learning_style.value}",
        ]

        if self.profile.interests:
            parts.append(f"\n🎯 Interests: {', '.join(list(self.profile.interests)[:5])}")

        if self.profile.effective_phrases:
            top_phrases = sorted(
                self.profile.effective_phrases.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            parts.append(f"\n✨ Effective Phrases:")
            for phrase, rate in top_phrases:
                parts.append(f"  • '{phrase}' ({rate:.0%} success)")

        parts.append(f"\n📈 Total Interactions: {len(self.interaction_history)}")

        return "\n".join(parts)


# Global registry of personality profiles
_personality_profiles: Dict[str, AdaptivePersonalityEngine] = {}


def get_adaptive_personality_engine(user_id: str = "default") -> AdaptivePersonalityEngine:
    """Get or create adaptive personality engine for this user"""
    if user_id not in _personality_profiles:
        _personality_profiles[user_id] = AdaptivePersonalityEngine(user_id)
    return _personality_profiles[user_id]
