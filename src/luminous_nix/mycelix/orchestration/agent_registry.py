"""
Agent Registry

Manages the lifecycle and availability of Sophia agents in the network.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import threading
import time

from .agent_protocol import AgentProfile, AgentMessage, MessageType


@dataclass
class AgentInstance:
    """Runtime instance of a Sophia agent"""

    profile: AgentProfile
    agent: Any  # The actual agent instance
    status: str = "active"  # active, busy, idle, error
    last_heartbeat: float = 0.0
    created_at: float = 0.0

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.last_heartbeat == 0.0:
            self.last_heartbeat = time.time()


class AgentRegistry:
    """
    Manages Sophia agent instances in the network

    Responsibilities:
    - Register/unregister agents
    - Track agent availability and load
    - Select agents for tasks
    - Monitor agent health
    """

    def __init__(self):
        self.agents: Dict[str, AgentInstance] = {}
        self._lock = threading.RLock()
        self._heartbeat_timeout = 30.0  # seconds

    def register_agent(
        self, agent_id: str, profile: AgentProfile, agent_instance: Any
    ) -> bool:
        """
        Register a new agent in the network

        Args:
            agent_id: Unique identifier for agent
            profile: Agent's profile defining specialization
            agent_instance: The actual agent object

        Returns:
            True if registered successfully, False if already exists
        """
        with self._lock:
            if agent_id in self.agents:
                return False

            instance = AgentInstance(
                profile=profile,
                agent=agent_instance,
                status="active",
                last_heartbeat=time.time(),
                created_at=time.time(),
            )

            self.agents[agent_id] = instance
            return True

    def unregister_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the network

        Args:
            agent_id: ID of agent to remove

        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if agent_id not in self.agents:
                return False

            del self.agents[agent_id]
            return True

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """
        Get agent instance by ID

        Args:
            agent_id: ID of agent

        Returns:
            Agent instance or None if not found
        """
        with self._lock:
            instance = self.agents.get(agent_id)
            return instance.agent if instance else None

    def get_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get agent profile by ID"""
        with self._lock:
            instance = self.agents.get(agent_id)
            return instance.profile if instance else None

    def get_all_agents(self) -> List[str]:
        """Get list of all registered agent IDs"""
        with self._lock:
            return list(self.agents.keys())

    def get_agents_by_domain(self, domain: str) -> List[str]:
        """
        Get agents with expertise in a specific domain

        Args:
            domain: Expertise domain to search for

        Returns:
            List of agent IDs with that expertise
        """
        with self._lock:
            matching = []
            for agent_id, instance in self.agents.items():
                if domain in instance.profile.expertise_domains:
                    matching.append(agent_id)
            return matching

    def get_agents_by_capability(self, capability: str) -> List[str]:
        """
        Get agents with a specific capability

        Args:
            capability: Capability to search for

        Returns:
            List of agent IDs with that capability
        """
        with self._lock:
            matching = []
            for agent_id, instance in self.agents.items():
                if capability in instance.profile.capabilities:
                    matching.append(agent_id)
            return matching

    def get_available_agents(self, min_confidence: float = 0.0) -> List[str]:
        """
        Get agents that are available to process tasks

        Args:
            min_confidence: Minimum average confidence required

        Returns:
            List of available agent IDs
        """
        with self._lock:
            available = []
            for agent_id, instance in self.agents.items():
                # Check if agent is healthy
                if not self._is_agent_healthy(instance):
                    continue

                # Check if agent has capacity
                if instance.profile.current_load >= instance.profile.max_concurrent_tasks:
                    continue

                # Check confidence threshold
                if instance.profile.average_confidence < min_confidence:
                    continue

                available.append(agent_id)

            return available

    def get_best_agent(
        self,
        domain: Optional[str] = None,
        capability: Optional[str] = None,
        prefer_low_load: bool = True,
    ) -> Optional[str]:
        """
        Select the best agent for a task

        Args:
            domain: Required expertise domain (optional)
            capability: Required capability (optional)
            prefer_low_load: Prioritize agents with lower load

        Returns:
            Best agent ID or None if no suitable agent
        """
        with self._lock:
            # Get candidate agents
            candidates = self.get_available_agents()

            if not candidates:
                return None

            # Filter by domain if specified
            if domain:
                candidates = [
                    a for a in candidates if a in self.get_agents_by_domain(domain)
                ]

            # Filter by capability if specified
            if capability:
                candidates = [
                    a
                    for a in candidates
                    if a in self.get_agents_by_capability(capability)
                ]

            if not candidates:
                return None

            # Score agents
            scored = []
            for agent_id in candidates:
                instance = self.agents[agent_id]
                profile = instance.profile

                # Calculate score
                score = 0.0

                # Success rate (40% weight)
                score += profile.success_rate * 0.4

                # Confidence (30% weight)
                score += profile.average_confidence * 0.3

                # Load balance (20% weight)
                if prefer_low_load:
                    load_factor = 1.0 - (
                        profile.current_load / profile.max_concurrent_tasks
                    )
                    score += load_factor * 0.2

                # Response time (10% weight) - lower is better
                if profile.response_time_avg > 0:
                    time_score = min(1.0, 100.0 / profile.response_time_avg)
                    score += time_score * 0.1

                scored.append((agent_id, score))

            # Return best agent
            if not scored:
                return None

            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[0][0]

    def increment_load(self, agent_id: str) -> bool:
        """Increment agent's current load"""
        with self._lock:
            instance = self.agents.get(agent_id)
            if not instance:
                return False

            instance.profile.current_load += 1
            return True

    def decrement_load(self, agent_id: str) -> bool:
        """Decrement agent's current load"""
        with self._lock:
            instance = self.agents.get(agent_id)
            if not instance:
                return False

            instance.profile.current_load = max(0, instance.profile.current_load - 1)
            return True

    def update_heartbeat(self, agent_id: str) -> bool:
        """Update agent's last heartbeat timestamp"""
        with self._lock:
            instance = self.agents.get(agent_id)
            if not instance:
                return False

            instance.last_heartbeat = time.time()
            return True

    def update_metrics(
        self,
        agent_id: str,
        success: bool,
        confidence: float,
        response_time: float,
    ) -> bool:
        """
        Update agent's performance metrics

        Args:
            agent_id: Agent to update
            success: Whether task was successful
            confidence: Agent's confidence in result
            response_time: Time taken to respond (ms)

        Returns:
            True if updated, False if agent not found
        """
        with self._lock:
            instance = self.agents.get(agent_id)
            if not instance:
                return False

            instance.profile.update_metrics(success, confidence, response_time)
            return True

    def get_network_stats(self) -> Dict[str, any]:
        """Get statistics about the agent network"""
        with self._lock:
            total_agents = len(self.agents)
            active_agents = sum(
                1
                for i in self.agents.values()
                if self._is_agent_healthy(i) and i.profile.current_load > 0
            )
            total_load = sum(i.profile.current_load for i in self.agents.values())
            avg_success_rate = (
                sum(i.profile.success_rate for i in self.agents.values()) / total_agents
                if total_agents > 0
                else 0.0
            )

            return {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "idle_agents": total_agents - active_agents,
                "total_load": total_load,
                "average_success_rate": avg_success_rate,
                "healthy_agents": sum(
                    1 for i in self.agents.values() if self._is_agent_healthy(i)
                ),
            }

    def _is_agent_healthy(self, instance: AgentInstance) -> bool:
        """Check if agent is healthy based on heartbeat"""
        if instance.status == "error":
            return False

        # Check heartbeat timeout
        time_since_heartbeat = time.time() - instance.last_heartbeat
        if time_since_heartbeat > self._heartbeat_timeout:
            return False

        return True

    def cleanup_unhealthy_agents(self) -> List[str]:
        """
        Remove agents that haven't sent heartbeat recently

        Returns:
            List of removed agent IDs
        """
        with self._lock:
            to_remove = []

            for agent_id, instance in self.agents.items():
                if not self._is_agent_healthy(instance):
                    to_remove.append(agent_id)

            for agent_id in to_remove:
                del self.agents[agent_id]

            return to_remove
