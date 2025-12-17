"""
Emergence Monitor

Detects and analyzes emergent patterns across the agent network.
Identifies novel insights that arise from agent collaboration.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re


@dataclass
class Pattern:
    """A detected pattern"""
    pattern_id: str
    pattern_type: str  # "query", "response", "collaboration", "temporal"
    description: str
    frequency: int
    first_seen: datetime
    last_seen: datetime
    agents_involved: Set[str] = field(default_factory=set)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    novelty_score: float = 0.0  # How novel/unexpected this pattern is


@dataclass
class EmergentInsight:
    """An emergent insight discovered from patterns"""
    insight_id: str
    content: str
    source_patterns: List[str]  # Pattern IDs that led to this insight
    confidence: float
    novelty: float
    discovered_at: datetime = field(default_factory=datetime.now)
    validation_count: int = 0  # How many times it's been validated


@dataclass
class CollaborationEvent:
    """Records agent collaboration"""
    event_id: str
    agents: List[str]
    query: str
    outcome_quality: float
    timestamp: datetime = field(default_factory=datetime.now)


class EmergenceMonitor:
    """
    Emergence Monitor

    Watches the agent network for emergent patterns and insights.
    Detects:
    - Query patterns (common problems, question types)
    - Response patterns (successful approaches, techniques)
    - Collaboration patterns (which agents work well together)
    - Temporal patterns (time-of-day effects, seasonal trends)
    - Novel insights (unexpected solutions, creative combinations)
    """

    def __init__(self):
        """Initialize emergence monitor"""
        # Pattern storage
        self.patterns: Dict[str, Pattern] = {}

        # Emergent insights
        self.insights: List[EmergentInsight] = []

        # Collaboration tracking
        self.collaborations: List[CollaborationEvent] = []

        # Query frequency tracking
        self.query_patterns: Counter = Counter()

        # Response pattern tracking
        self.response_patterns: Counter = Counter()

        # Agent synergy matrix (which agents work well together)
        self.agent_synergy: Dict[Tuple[str, str], float] = {}

        # Pattern ID counter
        self._next_pattern_id = 0
        self._next_insight_id = 0

    def observe_interaction(
        self,
        query: str,
        agents_involved: List[str],
        response: Dict[str, Any],
        quality_score: float,
    ):
        """
        Observe an interaction for pattern detection

        Args:
            query: The query
            agents_involved: List of agents that participated
            response: The response
            quality_score: Quality assessment (0.0-1.0)
        """
        # Record query pattern
        query_type = self._categorize_query(query)
        self.query_patterns[query_type] += 1

        # Record response pattern
        response_type = self._categorize_response(response)
        self.response_patterns[response_type] += 1

        # Record collaboration if multiple agents
        if len(agents_involved) > 1:
            self._record_collaboration(agents_involved, query, quality_score)

        # Update or create patterns
        self._update_patterns(query, agents_involved, response, quality_score)

        # Check for emergent insights
        self._detect_emergent_insights()

    def _categorize_query(self, query: str) -> str:
        """Categorize query type"""
        query_lower = query.lower()

        # Check for common patterns
        if any(word in query_lower for word in ["install", "add", "get"]):
            return "installation"
        elif any(word in query_lower for word in ["configure", "setup", "enable"]):
            return "configuration"
        elif any(word in query_lower for word in ["debug", "fix", "error", "problem"]):
            return "debugging"
        elif any(word in query_lower for word in ["secure", "protect", "harden"]):
            return "security"
        elif any(word in query_lower for word in ["how", "what", "why"]):
            return "information"
        else:
            return "other"

    def _categorize_response(self, response: Dict[str, Any]) -> str:
        """Categorize response type"""
        # Check what the response contains
        has_insights = len(response.get("insights", [])) > 0
        has_suggestions = len(response.get("suggestions", [])) > 0
        has_actions = len(response.get("actions", [])) > 0
        confidence = response.get("confidence", 0.0)

        if has_actions:
            return "actionable"
        elif has_suggestions and confidence > 0.8:
            return "confident_guidance"
        elif has_insights:
            return "educational"
        else:
            return "informational"

    def _record_collaboration(
        self,
        agents: List[str],
        query: str,
        quality_score: float,
    ):
        """Record collaboration event"""
        event_id = f"c{len(self.collaborations):06d}"

        event = CollaborationEvent(
            event_id=event_id,
            agents=sorted(agents),  # Sort for consistency
            query=query,
            outcome_quality=quality_score,
        )

        self.collaborations.append(event)

        # Update synergy matrix
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                key = tuple(sorted([agent1, agent2]))

                # Update synergy score (exponential moving average)
                current = self.agent_synergy.get(key, 0.5)
                alpha = 0.2
                self.agent_synergy[key] = (1 - alpha) * current + alpha * quality_score

    def _update_patterns(
        self,
        query: str,
        agents: List[str],
        response: Dict[str, Any],
        quality: float,
    ):
        """Update or create patterns"""
        query_type = self._categorize_query(query)
        response_type = self._categorize_response(response)

        # Pattern key
        pattern_key = f"{query_type}_{response_type}"

        if pattern_key in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_key]
            pattern.frequency += 1
            pattern.last_seen = datetime.now()
            pattern.agents_involved.update(agents)

            # Add example if high quality
            if quality > 0.8 and len(pattern.examples) < 5:
                pattern.examples.append({
                    "query": query,
                    "response_summary": response.get("message", "")[:100],
                    "quality": quality,
                })
        else:
            # Create new pattern
            pattern_id = f"p{self._next_pattern_id:06d}"
            self._next_pattern_id += 1

            pattern = Pattern(
                pattern_id=pattern_id,
                pattern_type="interaction",
                description=f"{query_type} → {response_type}",
                frequency=1,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                agents_involved=set(agents),
                examples=[{
                    "query": query,
                    "response_summary": response.get("message", "")[:100],
                    "quality": quality,
                }],
            )

            self.patterns[pattern_key] = pattern

    def _detect_emergent_insights(self):
        """Detect emergent insights from patterns"""
        # Look for novel combinations
        self._detect_novel_combinations()

        # Look for unexpected collaborations
        self._detect_unexpected_collaborations()

        # Look for emerging trends
        self._detect_emerging_trends()

    def _detect_novel_combinations(self):
        """Detect novel combinations of patterns"""
        # Look for patterns that frequently co-occur
        # This is a simplified version - could be much more sophisticated

        # Count co-occurrences (would need temporal windowing in real impl)
        recent_threshold = datetime.now() - timedelta(hours=1)
        recent_patterns = [
            p for p in self.patterns.values()
            if p.last_seen > recent_threshold
        ]

        # If we see multiple different patterns in short time, might be novel
        if len(recent_patterns) >= 3:
            # Check if this combination is new
            pattern_set = frozenset(p.pattern_id for p in recent_patterns)

            # Check if we've seen this before (simplified)
            is_novel = not any(
                frozenset(i.source_patterns) == pattern_set
                for i in self.insights
            )

            if is_novel:
                insight_id = f"i{self._next_insight_id:06d}"
                self._next_insight_id += 1

                insight = EmergentInsight(
                    insight_id=insight_id,
                    content=f"Novel pattern combination detected: {', '.join(p.description for p in recent_patterns[:3])}",
                    source_patterns=[p.pattern_id for p in recent_patterns],
                    confidence=0.7,
                    novelty=0.9,
                )

                self.insights.append(insight)

    def _detect_unexpected_collaborations(self):
        """Detect unexpected but successful collaborations"""
        # Look for agent pairs with surprisingly high synergy
        for (agent1, agent2), synergy in self.agent_synergy.items():
            # If synergy is high but collaboration count is low, it's interesting
            collab_count = sum(
                1 for c in self.collaborations
                if agent1 in c.agents and agent2 in c.agents
            )

            if synergy > 0.8 and collab_count < 5:
                # This is an unexpected successful collaboration!
                insight_id = f"i{self._next_insight_id:06d}"
                self._next_insight_id += 1

                insight = EmergentInsight(
                    insight_id=insight_id,
                    content=f"Unexpected synergy: {agent1} + {agent2} → {synergy:.2f} success rate",
                    source_patterns=[],
                    confidence=0.8,
                    novelty=0.85,
                )

                self.insights.append(insight)

    def _detect_emerging_trends(self):
        """Detect emerging trends in patterns"""
        # Look at pattern frequency changes over time
        # Simplified version - just check recent growth

        recent_threshold = datetime.now() - timedelta(hours=24)

        for pattern in self.patterns.values():
            if pattern.last_seen > recent_threshold and pattern.frequency > 10:
                # Calculate growth rate (simplified)
                # In real implementation, would track historical frequency

                # If pattern is both frequent and recent, it's trending
                if pattern.frequency > 20:
                    # Check if we've already reported this trend
                    already_reported = any(
                        pattern.pattern_id in i.source_patterns
                        for i in self.insights
                        if "trending" in i.content.lower()
                    )

                    if not already_reported:
                        insight_id = f"i{self._next_insight_id:06d}"
                        self._next_insight_id += 1

                        insight = EmergentInsight(
                            insight_id=insight_id,
                            content=f"Trending pattern: {pattern.description} ({pattern.frequency} occurrences)",
                            source_patterns=[pattern.pattern_id],
                            confidence=0.9,
                            novelty=0.6,
                        )

                        self.insights.append(insight)

    def get_top_patterns(self, n: int = 10) -> List[Pattern]:
        """
        Get top N most frequent patterns

        Args:
            n: Number of patterns to return

        Returns:
            List of top patterns
        """
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.frequency,
            reverse=True
        )
        return sorted_patterns[:n]

    def get_novel_insights(self, min_novelty: float = 0.7) -> List[EmergentInsight]:
        """
        Get novel insights

        Args:
            min_novelty: Minimum novelty threshold

        Returns:
            List of novel insights
        """
        return [
            i for i in self.insights
            if i.novelty >= min_novelty
        ]

    def get_agent_synergies(self) -> List[Tuple[str, str, float]]:
        """
        Get agent synergies

        Returns:
            List of (agent1, agent2, synergy_score) tuples
        """
        return [
            (a1, a2, score)
            for (a1, a2), score in sorted(
                self.agent_synergy.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get emergence statistics"""
        return {
            "total_patterns": len(self.patterns),
            "total_insights": len(self.insights),
            "total_collaborations": len(self.collaborations),
            "query_distribution": dict(self.query_patterns.most_common(5)),
            "response_distribution": dict(self.response_patterns.most_common(5)),
            "agent_pairs": len(self.agent_synergy),
            "novel_insights": len([i for i in self.insights if i.novelty > 0.7]),
        }
