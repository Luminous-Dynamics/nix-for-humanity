"""
User Modeler - Personalized AI Partnership

Revolutionary feature: The AI learns YOUR preferences and adapts to YOU.

This is not generic AI assistance. This is a personalized AI partner that:
- Learns your communication style
- Remembers your preferences
- Adapts explanations to your expertise level
- Anticipates your needs
- Respects your boundaries

Every user gets a unique, personalized experience.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter


class ExpertiseLevel(Enum):
    """User's expertise level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CommunicationStyle(Enum):
    """Preferred communication style"""
    CONCISE = "concise"  # Brief, to-the-point
    DETAILED = "detailed"  # Comprehensive explanations
    CONVERSATIONAL = "conversational"  # Friendly, casual
    TECHNICAL = "technical"  # Precise, formal


@dataclass
class Preference:
    """A learned user preference"""
    preference_type: str
    value: Any
    confidence: float  # How sure we are (0-1)
    evidence_count: int  # How many observations support this
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Adaptation:
    """An adaptation made for a user"""
    what_changed: str
    why_changed: str
    before: Any
    after: Any
    user_response: Optional[str] = None  # Did they like it?
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UserProfile:
    """Complete user profile"""
    user_id: str
    expertise_level: ExpertiseLevel
    communication_style: CommunicationStyle
    preferences: Dict[str, Preference]
    interaction_count: int
    successful_interactions: int
    topics_of_interest: List[str]
    common_tasks: List[str]
    time_preferences: Dict[str, Any]  # When they use the system
    created_at: datetime = field(default_factory=datetime.now)
    last_interaction: datetime = field(default_factory=datetime.now)


class UserModeler:
    """
    Learns and adapts to individual users

    Philosophy:
    - Every user is unique
    - Preferences emerge from behavior, not surveys
    - Adaptation should be invisible but felt
    - Privacy first - nothing leaves the local system
    """

    def __init__(self):
        """Initialize user modeler"""
        # User profiles
        self.profiles: Dict[str, UserProfile] = {}

        # Adaptation history
        self.adaptations: Dict[str, List[Adaptation]] = defaultdict(list)

        # Interaction tracking
        self.interaction_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get existing profile or create new one"""
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(
                user_id=user_id,
                expertise_level=ExpertiseLevel.INTERMEDIATE,  # Default assumption
                communication_style=CommunicationStyle.CONVERSATIONAL,  # Default
                preferences={},
                interaction_count=0,
                successful_interactions=0,
                topics_of_interest=[],
                common_tasks=[],
                time_preferences={},
            )

        return self.profiles[user_id]

    def observe_interaction(
        self,
        user_id: str,
        query: str,
        response: Dict[str, Any],
        user_feedback: Optional[str] = None,
        successful: bool = True,
    ):
        """
        Observe a user interaction and learn from it

        Args:
            user_id: User identifier
            query: What they asked
            response: What we responded
            user_feedback: Their feedback (if any)
            successful: Was it successful?
        """
        profile = self.get_or_create_profile(user_id)

        # Update interaction counts
        profile.interaction_count += 1
        if successful:
            profile.successful_interactions += 1
        profile.last_interaction = datetime.now()

        # Record interaction
        self.interaction_history[user_id].append({
            "timestamp": datetime.now(),
            "query": query,
            "response_length": len(response.get("content", "")),
            "confidence": response.get("confidence", 0.5),
            "successful": successful,
            "feedback": user_feedback,
        })

        # Learn from this interaction
        self._learn_expertise_level(user_id, query, response)
        self._learn_communication_style(user_id, query, response, user_feedback)
        self._learn_topic_interests(user_id, query)
        self._learn_task_patterns(user_id, query)
        self._learn_time_preferences(user_id)

    def _learn_expertise_level(
        self,
        user_id: str,
        query: str,
        response: Dict[str, Any]
    ):
        """Infer expertise level from query and responses"""
        profile = self.profiles[user_id]
        query_lower = query.lower()

        # Indicators of expertise
        beginner_indicators = [
            "what is", "how do i", "help me", "tutorial",
            "beginner", "new to", "first time"
        ]

        intermediate_indicators = [
            "configure", "setup", "install", "how to"
        ]

        advanced_indicators = [
            "optimize", "debug", "customize", "integrate",
            "performance", "architecture"
        ]

        expert_indicators = [
            "kernel", "low-level", "compile", "patch",
            "internals", "implementation"
        ]

        # Count indicators
        beginner_count = sum(1 for ind in beginner_indicators if ind in query_lower)
        intermediate_count = sum(1 for ind in intermediate_indicators if ind in query_lower)
        advanced_count = sum(1 for ind in advanced_indicators if ind in query_lower)
        expert_count = sum(1 for ind in expert_indicators if ind in query_lower)

        # Determine implied level
        if expert_count > 0:
            implied_level = ExpertiseLevel.EXPERT
        elif advanced_count > 0:
            implied_level = ExpertiseLevel.ADVANCED
        elif intermediate_count > 0:
            implied_level = ExpertiseLevel.INTERMEDIATE
        elif beginner_count > 0:
            implied_level = ExpertiseLevel.BEGINNER
        else:
            implied_level = None

        # Update profile if we have evidence
        if implied_level and profile.interaction_count > 3:
            # Need multiple interactions before updating
            if implied_level.value != profile.expertise_level.value:
                self._record_adaptation(
                    user_id,
                    "expertise_level",
                    f"Updated expertise level based on query patterns",
                    profile.expertise_level.value,
                    implied_level.value
                )
                profile.expertise_level = implied_level

    def _learn_communication_style(
        self,
        user_id: str,
        query: str,
        response: Dict[str, Any],
        feedback: Optional[str]
    ):
        """Learn preferred communication style"""
        profile = self.profiles[user_id]

        # Check feedback for style preferences
        if feedback:
            feedback_lower = feedback.lower()

            if any(word in feedback_lower for word in ["too long", "verbose", "tldr", "brief"]):
                # User wants more concise responses
                if profile.communication_style != CommunicationStyle.CONCISE:
                    self._record_adaptation(
                        user_id,
                        "communication_style",
                        "User indicated preference for concise communication",
                        profile.communication_style.value,
                        CommunicationStyle.CONCISE.value
                    )
                    profile.communication_style = CommunicationStyle.CONCISE

            elif any(word in feedback_lower for word in ["more detail", "explain more", "elaborate"]):
                # User wants more detail
                if profile.communication_style != CommunicationStyle.DETAILED:
                    self._record_adaptation(
                        user_id,
                        "communication_style",
                        "User indicated preference for detailed explanations",
                        profile.communication_style.value,
                        CommunicationStyle.DETAILED.value
                    )
                    profile.communication_style = CommunicationStyle.DETAILED

            elif any(word in feedback_lower for word in ["too technical", "simpler", "easier"]):
                # User wants conversational style
                if profile.communication_style != CommunicationStyle.CONVERSATIONAL:
                    self._record_adaptation(
                        user_id,
                        "communication_style",
                        "User indicated preference for conversational style",
                        profile.communication_style.value,
                        CommunicationStyle.CONVERSATIONAL.value
                    )
                    profile.communication_style = CommunicationStyle.CONVERSATIONAL

    def _learn_topic_interests(self, user_id: str, query: str):
        """Learn what topics the user is interested in"""
        profile = self.profiles[user_id]

        # Extract topics (simplified - could use NLP)
        topics = []
        query_lower = query.lower()

        topic_keywords = {
            "packages": ["install", "package", "download"],
            "configuration": ["configure", "config", "setup", "settings"],
            "security": ["secure", "firewall", "ssl", "tls", "encrypt"],
            "development": ["develop", "code", "program", "build"],
            "networking": ["network", "connection", "port", "ip"],
            "system": ["system", "kernel", "boot", "startup"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in query_lower for kw in keywords):
                topics.append(topic)

        # Update profile
        for topic in topics:
            if topic not in profile.topics_of_interest:
                profile.topics_of_interest.append(topic)

        # Limit to top 10 topics
        if len(profile.topics_of_interest) > 10:
            profile.topics_of_interest = profile.topics_of_interest[-10:]

    def _learn_task_patterns(self, user_id: str, query: str):
        """Learn common tasks the user performs"""
        profile = self.profiles[user_id]

        # Extract task type (simplified)
        task = None
        query_lower = query.lower()

        if "install" in query_lower:
            task = "install_packages"
        elif "configure" in query_lower or "setup" in query_lower:
            task = "configuration"
        elif "debug" in query_lower or "error" in query_lower:
            task = "debugging"
        elif "search" in query_lower or "find" in query_lower:
            task = "search"

        if task:
            if task not in profile.common_tasks:
                profile.common_tasks.append(task)

            # Limit to most recent 10 tasks
            if len(profile.common_tasks) > 10:
                profile.common_tasks = profile.common_tasks[-10:]

    def _learn_time_preferences(self, user_id: str):
        """Learn when user prefers to interact"""
        profile = self.profiles[user_id]
        now = datetime.now()

        # Track hour of day
        if "hours" not in profile.time_preferences:
            profile.time_preferences["hours"] = Counter()

        profile.time_preferences["hours"][now.hour] += 1

        # Track day of week
        if "days" not in profile.time_preferences:
            profile.time_preferences["days"] = Counter()

        profile.time_preferences["days"][now.weekday()] += 1

    def _record_adaptation(
        self,
        user_id: str,
        what: str,
        why: str,
        before: Any,
        after: Any
    ):
        """Record an adaptation made for a user"""
        adaptation = Adaptation(
            what_changed=what,
            why_changed=why,
            before=before,
            after=after
        )

        self.adaptations[user_id].append(adaptation)

    def adapt_response(
        self,
        user_id: str,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapt a response to user preferences

        Args:
            user_id: User identifier
            response: Response to adapt

        Returns:
            Adapted response
        """
        profile = self.get_or_create_profile(user_id)

        # Create adapted copy
        adapted = response.copy()

        # Adapt based on communication style
        if profile.communication_style == CommunicationStyle.CONCISE:
            # Shorten content, keep only key points
            adapted["content"] = self._make_concise(response.get("content", ""))
            # Limit suggestions to top 3
            if len(adapted.get("suggestions", [])) > 3:
                adapted["suggestions"] = adapted["suggestions"][:3]

        elif profile.communication_style == CommunicationStyle.DETAILED:
            # Add more explanation
            adapted["insights"] = response.get("insights", []) + self._add_context(
                response.get("content", "")
            )

        elif profile.communication_style == CommunicationStyle.TECHNICAL:
            # Use technical terminology
            adapted["content"] = self._make_technical(response.get("content", ""))

        # Adapt based on expertise level
        if profile.expertise_level == ExpertiseLevel.BEGINNER:
            # Add explanations of terms
            adapted["insights"] = response.get("insights", []) + self._explain_terms(
                response.get("content", "")
            )

        elif profile.expertise_level == ExpertiseLevel.EXPERT:
            # Remove basic explanations, add advanced details
            adapted["content"] = self._add_advanced_info(response.get("content", ""))

        return adapted

    def _make_concise(self, content: str) -> str:
        """Make content more concise"""
        # Very simplified - just take first sentence
        sentences = content.split(".")
        if len(sentences) > 2:
            return ". ".join(sentences[:2]) + "."
        return content

    def _make_technical(self, content: str) -> str:
        """Make content more technical"""
        # In real implementation, would use technical synonyms
        return content  # Placeholder

    def _add_context(self, content: str) -> List[str]:
        """Add contextual information"""
        # In real implementation, would add relevant background
        return ["Consider the broader implications", "Related concepts may be helpful"]

    def _explain_terms(self, content: str) -> List[str]:
        """Explain technical terms"""
        # In real implementation, would detect and explain technical terms
        return []  # Placeholder

    def _add_advanced_info(self, content: str) -> str:
        """Add advanced information"""
        # In real implementation, would add technical details
        return content  # Placeholder

    def get_recommendations(self, user_id: str) -> List[str]:
        """Get recommendations for this user"""
        profile = self.get_or_create_profile(user_id)

        recommendations = []

        # Based on common tasks
        if "install_packages" in profile.common_tasks:
            recommendations.append("You frequently install packages - consider learning about nix flakes")

        if "debugging" in profile.common_tasks:
            recommendations.append("You often debug issues - check out the system logs tool")

        # Based on expertise level
        if profile.expertise_level == ExpertiseLevel.BEGINNER:
            recommendations.append("Explore the tutorial section to learn more")

        elif profile.expertise_level == ExpertiseLevel.EXPERT:
            recommendations.append("Try advanced features like custom derivations")

        return recommendations

    def get_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user modeling statistics"""
        if user_id:
            profile = self.get_or_create_profile(user_id)
            return {
                "user_id": user_id,
                "interaction_count": profile.interaction_count,
                "success_rate": (
                    profile.successful_interactions / profile.interaction_count
                    if profile.interaction_count > 0
                    else 0.0
                ),
                "expertise_level": profile.expertise_level.value,
                "communication_style": profile.communication_style.value,
                "topics_of_interest": profile.topics_of_interest,
                "adaptations_made": len(self.adaptations.get(user_id, [])),
            }
        else:
            # Overall stats
            return {
                "total_users": len(self.profiles),
                "total_interactions": sum(p.interaction_count for p in self.profiles.values()),
                "total_adaptations": sum(len(a) for a in self.adaptations.values()),
            }
