"""
Knowledge Broker

Manages shared knowledge and learning across the agent network.
Enables agents to learn from each other's experiences and build
collective intelligence.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class KnowledgeEntry:
    """A piece of shared knowledge"""
    knowledge_id: str
    domain: str  # Which domain this knowledge applies to
    content: str  # The actual knowledge
    source_agent: str  # Which agent contributed this
    confidence: float  # How confident we are in this knowledge
    usage_count: int = 0  # How many times it's been used
    success_rate: float = 1.0  # How often it led to good outcomes
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    related_queries: List[str] = field(default_factory=list)


@dataclass
class LearningEvent:
    """Records a learning event"""
    event_id: str
    agent_id: str
    query: str
    response: Dict[str, Any]
    success: bool
    user_feedback: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    extracted_knowledge: List[str] = field(default_factory=list)


class KnowledgeBroker:
    """
    Knowledge Broker

    Central hub for shared knowledge and learning across the agent network.
    Enables:
    - Knowledge sharing between agents
    - Learning from successful interactions
    - Building collective intelligence
    - Cross-domain knowledge transfer
    """

    def __init__(self):
        """Initialize knowledge broker"""
        # Knowledge storage by domain
        self.knowledge_base: Dict[str, List[KnowledgeEntry]] = defaultdict(list)

        # Learning history
        self.learning_events: List[LearningEvent] = []

        # Agent contributions tracker
        self.agent_contributions: Dict[str, int] = defaultdict(int)

        # Cross-domain connections
        self.domain_connections: Dict[str, Set[str]] = defaultdict(set)

        # Knowledge ID counter
        self._next_id = 0

    def contribute_knowledge(
        self,
        agent_id: str,
        domain: str,
        content: str,
        confidence: float = 0.8,
        tags: Optional[List[str]] = None,
        related_queries: Optional[List[str]] = None,
    ) -> str:
        """
        Agent contributes knowledge to the shared pool

        Args:
            agent_id: Contributing agent
            domain: Knowledge domain
            content: The knowledge content
            confidence: How confident the agent is
            tags: Optional tags for categorization
            related_queries: Queries this knowledge applies to

        Returns:
            Knowledge ID
        """
        # Generate knowledge ID
        knowledge_id = f"k{self._next_id:06d}"
        self._next_id += 1

        # Create knowledge entry
        entry = KnowledgeEntry(
            knowledge_id=knowledge_id,
            domain=domain,
            content=content,
            source_agent=agent_id,
            confidence=confidence,
            tags=tags or [],
            related_queries=related_queries or [],
        )

        # Store in knowledge base
        self.knowledge_base[domain].append(entry)

        # Track contribution
        self.agent_contributions[agent_id] += 1

        return knowledge_id

    def query_knowledge(
        self,
        domain: str,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_confidence: float = 0.5,
    ) -> List[KnowledgeEntry]:
        """
        Query knowledge from the shared pool

        Args:
            domain: Knowledge domain to query
            query: Optional query string for relevance matching
            tags: Optional tags to filter by
            min_confidence: Minimum confidence threshold

        Returns:
            List of relevant knowledge entries
        """
        # Get all knowledge for domain
        domain_knowledge = self.knowledge_base.get(domain, [])

        # Filter by confidence
        results = [k for k in domain_knowledge if k.confidence >= min_confidence]

        # Filter by tags if provided
        if tags:
            results = [
                k for k in results
                if any(tag in k.tags for tag in tags)
            ]

        # Filter by query relevance if provided
        if query:
            query_lower = query.lower()
            results = [
                k for k in results
                if (query_lower in k.content.lower() or
                    any(query_lower in q.lower() for q in k.related_queries))
            ]

        # Sort by usage and success rate
        results.sort(
            key=lambda k: (k.success_rate * k.usage_count, k.confidence),
            reverse=True
        )

        return results

    def record_learning_event(
        self,
        agent_id: str,
        query: str,
        response: Dict[str, Any],
        success: bool,
        user_feedback: Optional[str] = None,
    ) -> str:
        """
        Record a learning event

        Args:
            agent_id: Agent that handled the query
            query: The query
            response: Agent's response
            success: Whether it was successful
            user_feedback: Optional user feedback

        Returns:
            Event ID
        """
        # Generate event ID
        event_id = f"e{len(self.learning_events):06d}"

        # Create learning event
        event = LearningEvent(
            event_id=event_id,
            agent_id=agent_id,
            query=query,
            response=response,
            success=success,
            user_feedback=user_feedback,
        )

        # Store event
        self.learning_events.append(event)

        # Extract knowledge if successful
        if success:
            self._extract_knowledge_from_event(event)

        return event_id

    def _extract_knowledge_from_event(self, event: LearningEvent):
        """
        Extract reusable knowledge from a successful interaction

        Args:
            event: The learning event
        """
        # Extract insights as knowledge
        insights = event.response.get("insights", [])
        for insight in insights:
            # Determine domain from agent
            domain = self._infer_domain(event.agent_id)

            # Create knowledge entry
            knowledge_id = self.contribute_knowledge(
                agent_id=event.agent_id,
                domain=domain,
                content=insight,
                confidence=0.7,  # Medium confidence for extracted knowledge
                related_queries=[event.query],
            )

            event.extracted_knowledge.append(knowledge_id)

    def update_knowledge_performance(
        self,
        knowledge_id: str,
        success: bool,
    ):
        """
        Update knowledge performance based on usage

        Args:
            knowledge_id: Knowledge to update
            success: Whether using this knowledge led to success
        """
        # Find knowledge entry
        for domain_knowledge in self.knowledge_base.values():
            for entry in domain_knowledge:
                if entry.knowledge_id == knowledge_id:
                    # Update usage count
                    entry.usage_count += 1
                    entry.last_used = datetime.now()

                    # Update success rate (exponential moving average)
                    alpha = 0.2  # Learning rate
                    new_rate = 1.0 if success else 0.0
                    entry.success_rate = (
                        (1 - alpha) * entry.success_rate + alpha * new_rate
                    )
                    return

    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get statistics for an agent's contributions

        Args:
            agent_id: Agent to get stats for

        Returns:
            Statistics dictionary
        """
        # Count contributions
        contributions = self.agent_contributions.get(agent_id, 0)

        # Count learning events
        events = [e for e in self.learning_events if e.agent_id == agent_id]
        total_events = len(events)
        successful_events = sum(1 for e in events if e.success)
        success_rate = successful_events / total_events if total_events > 0 else 0.0

        return {
            "agent_id": agent_id,
            "contributions": contributions,
            "total_events": total_events,
            "successful_events": successful_events,
            "success_rate": success_rate,
        }

    def get_domain_stats(self, domain: str) -> Dict[str, Any]:
        """
        Get statistics for a knowledge domain

        Args:
            domain: Domain to get stats for

        Returns:
            Statistics dictionary
        """
        knowledge = self.knowledge_base.get(domain, [])

        total_knowledge = len(knowledge)
        total_usage = sum(k.usage_count for k in knowledge)
        avg_confidence = (
            sum(k.confidence for k in knowledge) / total_knowledge
            if total_knowledge > 0 else 0.0
        )
        avg_success_rate = (
            sum(k.success_rate for k in knowledge) / total_knowledge
            if total_knowledge > 0 else 0.0
        )

        # Count contributors
        contributors = set(k.source_agent for k in knowledge)

        return {
            "domain": domain,
            "total_knowledge": total_knowledge,
            "total_usage": total_usage,
            "avg_confidence": avg_confidence,
            "avg_success_rate": avg_success_rate,
            "contributors": len(contributors),
        }

    def discover_cross_domain_connections(self):
        """
        Analyze knowledge to discover cross-domain connections
        """
        # Analyze all knowledge entries
        for domain1, knowledge1 in self.knowledge_base.items():
            for domain2, knowledge2 in self.knowledge_base.items():
                if domain1 >= domain2:  # Skip self and duplicates
                    continue

                # Look for common tags or related queries
                for k1 in knowledge1:
                    for k2 in knowledge2:
                        # Check for overlap
                        common_tags = set(k1.tags) & set(k2.tags)
                        common_queries = set(k1.related_queries) & set(k2.related_queries)

                        if common_tags or common_queries:
                            # Found connection!
                            self.domain_connections[domain1].add(domain2)
                            self.domain_connections[domain2].add(domain1)

    def get_connected_domains(self, domain: str) -> List[str]:
        """
        Get domains connected to the given domain

        Args:
            domain: Domain to check

        Returns:
            List of connected domains
        """
        return list(self.domain_connections.get(domain, set()))

    def export_knowledge(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Export knowledge base for persistence

        Args:
            domain: Optional domain to export (None = all)

        Returns:
            Exportable knowledge dictionary
        """
        if domain:
            domains_to_export = {domain: self.knowledge_base[domain]}
        else:
            domains_to_export = self.knowledge_base

        export = {
            "domains": {},
            "stats": {
                "total_contributions": sum(self.agent_contributions.values()),
                "total_events": len(self.learning_events),
            }
        }

        for dom, knowledge in domains_to_export.items():
            export["domains"][dom] = [
                {
                    "id": k.knowledge_id,
                    "content": k.content,
                    "source": k.source_agent,
                    "confidence": k.confidence,
                    "usage": k.usage_count,
                    "success_rate": k.success_rate,
                }
                for k in knowledge
            ]

        return export

    def _infer_domain(self, agent_id: str) -> str:
        """Infer domain from agent ID"""
        if "nixos" in agent_id.lower():
            return "nixos"
        elif "shell" in agent_id.lower():
            return "shell"
        elif "security" in agent_id.lower():
            return "security"
        else:
            return "general"
