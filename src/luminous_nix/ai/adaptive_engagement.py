"""
Adaptive Engagement Engine - Layer 5: User Experience Intelligence

Revolutionary capability: Adapt EVERY interaction to the user's archetype,
goals, and preferences. Same query, different users = different experiences.

This engine transforms:
- HOW we respond (tone, verbosity, depth)
- WHAT we include (explanations, alternatives, options)
- WHEN we act (immediately vs asking permission)

This ensures that EVERY user gets the experience THEY need.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from .user_profiler import (
    UserProfile, UserArchetype, EngagementMode,
    TechnicalLevel
)


@dataclass
class EngagementStrategy:
    """Strategy for how to engage with user for a specific interaction"""
    # Response characteristics
    verbosity: str  # "minimal", "moderate", "detailed"
    include_explanation: bool  # Explain why/how?
    include_learning: bool  # Add educational content?
    include_alternatives: bool  # Suggest other options?

    # Action characteristics
    auto_execute: bool  # Execute without asking?
    preview_before_action: bool  # Show what will happen first?
    ask_for_confirmation: bool  # Require explicit yes?

    # Teaching characteristics (if include_learning=True)
    teaching_depth: str  # "surface", "intermediate", "deep"
    use_analogies: bool  # Use metaphors and analogies?
    show_examples: bool  # Show code examples?

    # Tone
    tone: str  # "friendly", "professional", "technical", "encouraging"


class AdaptiveEngagementEngine:
    """
    Adapts AI interaction style to each unique user.

    Philosophy: One size fits nobody. Everyone deserves an experience
    tailored to their goals, skills, and preferences.
    """

    def __init__(self):
        """Initialize engagement engine"""
        pass

    def select_strategy(
        self,
        profile: UserProfile,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> EngagementStrategy:
        """
        Select optimal engagement strategy for this user and query.

        Args:
            profile: User's profile with preferences
            query: What user is trying to do
            context: Additional context (error state, system state, etc.)

        Returns:
            EngagementStrategy defining how to interact
        """
        # Start with archetype-based defaults
        if profile.archetype == UserArchetype.LEARNER:
            return self._learner_strategy(profile, query, context)
        elif profile.archetype == UserArchetype.PRAGMATIST:
            return self._pragmatist_strategy(profile, query, context)
        elif profile.archetype == UserArchetype.EXPLORER:
            return self._explorer_strategy(profile, query, context)
        elif profile.archetype == UserArchetype.CREATOR:
            return self._creator_strategy(profile, query, context)
        else:
            # Unknown - use balanced approach
            return self._balanced_strategy(profile, query, context)

    def _learner_strategy(
        self,
        profile: UserProfile,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> EngagementStrategy:
        """
        Strategy for LEARNER archetype.

        Learners want to understand deeply. Give them:
        - Detailed explanations
        - Teaching moments
        - Analogies and examples
        - Understanding before action
        """
        return EngagementStrategy(
            # Response
            verbosity="detailed",
            include_explanation=True,
            include_learning=True,
            include_alternatives=True,  # Show them options to learn

            # Action
            auto_execute=False,  # Always ask first - they want to understand
            preview_before_action=True,  # Show what will happen
            ask_for_confirmation=True,  # Explicit control

            # Teaching
            teaching_depth="deep",
            use_analogies=True,  # Help connect to known concepts
            show_examples=True,  # Concrete examples aid learning

            # Tone
            tone="encouraging"  # Supportive learning environment
        )

    def _pragmatist_strategy(
        self,
        profile: UserProfile,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> EngagementStrategy:
        """
        Strategy for PRAGMATIST archetype.

        Pragmatists want results, not lessons. Give them:
        - Minimal talk, maximum action
        - Just do what they asked
        - Brief confirmation of what happened
        - No unsolicited teaching
        """
        # Check if they've explicitly set automation preferences
        auto_execute = profile.prefers_automation

        return EngagementStrategy(
            # Response
            verbosity="minimal",  # Get to the point
            include_explanation=False,  # Unless they ask
            include_learning=False,  # No unsolicited teaching
            include_alternatives=False,  # They know what they want

            # Action
            auto_execute=auto_execute,  # Respect their automation preference
            preview_before_action=not auto_execute,  # If not auto, show first
            ask_for_confirmation=not auto_execute,  # If not auto, ask

            # Teaching (rarely used)
            teaching_depth="surface",
            use_analogies=False,
            show_examples=False,

            # Tone
            tone="professional"  # Direct and efficient
        )

    def _explorer_strategy(
        self,
        profile: UserProfile,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> EngagementStrategy:
        """
        Strategy for EXPLORER archetype.

        Explorers want to see what's possible. Give them:
        - Multiple options and alternatives
        - "Did you know?" moments
        - Examples of what others have done
        - Encouragement to experiment
        """
        return EngagementStrategy(
            # Response
            verbosity="moderate",
            include_explanation=True,  # But focus on "what's possible"
            include_learning=True,  # Moderate educational content
            include_alternatives=True,  # CRITICAL: Show many options!

            # Action
            auto_execute=False,  # Let them choose
            preview_before_action=True,  # Show options
            ask_for_confirmation=True,  # Give them choice

            # Teaching
            teaching_depth="intermediate",
            use_analogies=True,  # Help them see connections
            show_examples=True,  # Concrete possibilities inspire

            # Tone
            tone="friendly"  # Welcoming exploration
        )

    def _creator_strategy(
        self,
        profile: UserProfile,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> EngagementStrategy:
        """
        Strategy for CREATOR archetype.

        Creators want to build custom solutions. Give them:
        - Technical details and options
        - Code examples and templates
        - Collaborative problem-solving
        - Tools and building blocks
        """
        return EngagementStrategy(
            # Response
            verbosity="detailed",  # Technical details matter
            include_explanation=True,  # Explain the how and why
            include_learning=True,  # Technical learning welcome
            include_alternatives=True,  # Show different approaches

            # Action
            auto_execute=False,  # They want control
            preview_before_action=True,  # Show the plan
            ask_for_confirmation=False,  # Trust their expertise

            # Teaching
            teaching_depth="deep",  # Technical depth
            use_analogies=False,  # Prefer technical precision
            show_examples=True,  # Code examples are gold

            # Tone
            tone="technical"  # Peer-to-peer collaboration
        )

    def _balanced_strategy(
        self,
        profile: UserProfile,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> EngagementStrategy:
        """
        Balanced strategy for unknown archetype or adaptive mode.

        Use moderate approach and learn from feedback.
        """
        return EngagementStrategy(
            # Response
            verbosity="moderate",
            include_explanation=True,
            include_learning=profile.wants_learning,  # Respect preference
            include_alternatives=profile.interested_in_alternatives,

            # Action
            auto_execute=profile.prefers_automation,
            preview_before_action=True,
            ask_for_confirmation=not profile.prefers_automation,

            # Teaching
            teaching_depth="intermediate",
            use_analogies=True,
            show_examples=True,

            # Tone
            tone="friendly"
        )

    def format_response(
        self,
        content: str,
        strategy: EngagementStrategy,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format response according to engagement strategy.

        Args:
            content: The core response content
            strategy: How to format it
            metadata: Additional info (alternatives, explanations, etc.)

        Returns:
            Formatted response string
        """
        response_parts = []

        # Core content (always included)
        response_parts.append(content)

        # Add explanation if strategy calls for it
        if strategy.include_explanation and metadata and "explanation" in metadata:
            if strategy.verbosity != "minimal":
                response_parts.append(f"\n\n**Why this works:**\n{metadata['explanation']}")

        # Add alternatives if strategy calls for it
        if strategy.include_alternatives and metadata and "alternatives" in metadata:
            alternatives = metadata["alternatives"]
            if alternatives:
                response_parts.append("\n\n**Other options you might consider:**")
                for alt in alternatives:
                    response_parts.append(f"- {alt}")

        # Add learning content if strategy calls for it
        if strategy.include_learning and metadata and "learning_content" in metadata:
            if strategy.teaching_depth != "surface":
                response_parts.append(f"\n\n**Learn more:**\n{metadata['learning_content']}")

        # Add examples if strategy calls for it
        if strategy.show_examples and metadata and "examples" in metadata:
            response_parts.append(f"\n\n**Example:**\n```\n{metadata['examples']}\n```")

        return "\n".join(response_parts)

    def should_teach_now(
        self,
        profile: UserProfile,
        concept_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Determine if NOW is a good time to teach a concept.

        This respects:
        - User's archetype (Pragmatists rarely want teaching)
        - User's explicit preferences
        - Context (error state = not good time to teach)

        Args:
            profile: User profile
            concept_id: What concept we might teach
            context: Current context

        Returns:
            True if teaching moment is appropriate
        """
        # Pragmatists only want teaching if they explicitly ask
        if profile.archetype == UserArchetype.PRAGMATIST:
            # Check if they asked a "why" or "how" question
            if context and "query" in context:
                query = context["query"].lower()
                if any(word in query for word in ["why", "how", "explain", "teach"]):
                    return True
            return False

        # Never teach if user doesn't want learning (but after checking explicit asks)
        if not profile.wants_learning:
            return False

        # Learners almost always want teaching
        if profile.archetype == UserArchetype.LEARNER:
            return True

        # Explorers want teaching about possibilities
        if profile.archetype == UserArchetype.EXPLORER:
            return True

        # Creators want technical teaching
        if profile.archetype == UserArchetype.CREATOR:
            return True

        # Default: teach if user wants learning
        return profile.wants_learning

    def should_suggest_alternatives(
        self,
        profile: UserProfile,
        current_choice: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Determine if we should suggest alternatives to user's choice.

        Explorers love alternatives. Pragmatists don't want unsolicited suggestions.

        Args:
            profile: User profile
            current_choice: What they're currently choosing
            context: Additional context

        Returns:
            True if we should suggest alternatives
        """
        # Respect explicit preference
        if not profile.interested_in_alternatives:
            return False

        # Pragmatists don't want suggestions unless they ask
        if profile.archetype == UserArchetype.PRAGMATIST:
            return False

        # Explorers LOVE alternatives
        if profile.archetype == UserArchetype.EXPLORER:
            return True

        # Learners appreciate seeing options
        if profile.archetype == UserArchetype.LEARNER:
            return True

        # Creators want to know all the tools available
        if profile.archetype == UserArchetype.CREATOR:
            return True

        return False


def get_adaptive_engagement_engine() -> AdaptiveEngagementEngine:
    """Get singleton instance of adaptive engagement engine"""
    global _adaptive_engagement_engine

    if _adaptive_engagement_engine is None:
        _adaptive_engagement_engine = AdaptiveEngagementEngine()

    return _adaptive_engagement_engine


# Singleton
_adaptive_engagement_engine: Optional[AdaptiveEngagementEngine] = None
