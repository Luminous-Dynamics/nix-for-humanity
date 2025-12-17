"""
Task Router

Analyzes queries, decomposes complex tasks, and routes to appropriate agents.
"""

from typing import Dict, List, Optional, Tuple
import re
import uuid

from .agent_protocol import SubTask, OrchestrationContext
from .agent_registry import AgentRegistry


class TaskRouter:
    """
    Routes queries to appropriate Sophia agents

    Responsibilities:
    - Analyze query complexity
    - Decompose complex queries into sub-tasks
    - Route tasks to best agents
    - Handle task dependencies
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

        # Define domain keywords for routing
        self.domain_keywords = {
            "nixos": [
                "install",
                "remove",
                "package",
                "nixos",
                "nix",
                "configuration",
                "rebuild",
                "flake",
                "derivation",
            ],
            "shell": [
                "script",
                "command",
                "bash",
                "execute",
                "run",
                "process",
                "pipe",
                "grep",
                "find",
            ],
            "security": [
                "security",
                "secure",
                "vulnerability",
                "firewall",
                "permission",
                "access",
                "ssl",
                "certificate",
                "encrypt",
            ],
        }

        # Define complexity patterns
        self.complexity_patterns = {
            "simple": [
                r"^install \w+$",  # Single package install
                r"^remove \w+$",  # Single package remove
                r"^search \w+$",  # Simple search
            ],
            "medium": [
                r"set up \w+",  # Setup tasks
                r"configure \w+",  # Configuration tasks
                r"create .+ environment",  # Environment creation
            ],
            "complex": [
                r"set up .+ with .+",  # Multi-component setup
                r"configure .+ and .+",  # Multiple configurations
                r"migrate .+ to .+",  # Migration tasks
            ],
        }

    def analyze_complexity(self, query: str) -> Tuple[str, float]:
        """
        Analyze query complexity

        Args:
            query: User query to analyze

        Returns:
            Tuple of (complexity_level, score)
            complexity_level: "simple", "medium", "complex"
            score: 0.0-1.0 complexity score
        """
        query_lower = query.lower()

        # Check simple patterns
        for pattern in self.complexity_patterns["simple"]:
            if re.match(pattern, query_lower):
                return ("simple", 0.2)

        # Check complex patterns
        for pattern in self.complexity_patterns["complex"]:
            if re.search(pattern, query_lower):
                return ("complex", 0.9)

        # Check medium patterns
        for pattern in self.complexity_patterns["medium"]:
            if re.search(pattern, query_lower):
                return ("medium", 0.5)

        # Default heuristics
        word_count = len(query.split())

        # Word count based complexity
        if word_count <= 3:
            return ("simple", 0.3)
        elif word_count <= 10:
            return ("medium", 0.6)
        else:
            return ("complex", 0.8)

    def identify_domains(self, query: str) -> List[str]:
        """
        Identify relevant domains for a query

        Args:
            query: User query

        Returns:
            List of domain names (e.g., ["nixos", "security"])
        """
        query_lower = query.lower()
        domains = []

        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    if domain not in domains:
                        domains.append(domain)
                    break

        # Default to nixos if no domain identified
        if not domains:
            domains.append("nixos")

        return domains

    def decompose(self, query: str, context: Dict) -> List[SubTask]:
        """
        Decompose complex query into sub-tasks

        Args:
            query: User query
            context: Query context

        Returns:
            List of SubTask objects
        """
        complexity, score = self.analyze_complexity(query)

        # Simple queries don't need decomposition
        if complexity == "simple":
            task = SubTask(
                task_id=str(uuid.uuid4()), query=query, context=context, priority=5
            )
            return [task]

        # Decompose complex queries
        sub_tasks = []

        # Identify domains involved
        domains = self.identify_domains(query)

        # Pattern-based decomposition
        query_lower = query.lower()

        # Example: "set up secure web server with SSL"
        if "set up" in query_lower and "secure" in query_lower:
            # 1. Package selection
            sub_tasks.append(
                SubTask(
                    task_id=str(uuid.uuid4()),
                    query=f"Select best packages for {query}",
                    context={**context, "domain": "nixos"},
                    priority=8,
                )
            )

            # 2. Security configuration
            sub_tasks.append(
                SubTask(
                    task_id=str(uuid.uuid4()),
                    query=f"Security recommendations for {query}",
                    context={**context, "domain": "security"},
                    priority=9,
                    dependencies=[sub_tasks[0].task_id] if sub_tasks else [],
                )
            )

            # 3. Configuration generation
            sub_tasks.append(
                SubTask(
                    task_id=str(uuid.uuid4()),
                    query=f"Generate configuration for {query}",
                    context={**context, "domain": "nixos"},
                    priority=7,
                    dependencies=[sub_tasks[0].task_id, sub_tasks[1].task_id]
                    if len(sub_tasks) >= 2
                    else [],
                )
            )

        # Example: "configure X and Y"
        elif " and " in query_lower:
            parts = query_lower.split(" and ")
            for i, part in enumerate(parts):
                sub_tasks.append(
                    SubTask(
                        task_id=str(uuid.uuid4()),
                        query=part.strip(),
                        context=context,
                        priority=5,
                    )
                )

        # Default decomposition - create task per domain
        if not sub_tasks:
            for domain in domains:
                sub_tasks.append(
                    SubTask(
                        task_id=str(uuid.uuid4()),
                        query=query,
                        context={**context, "domain": domain},
                        priority=5,
                    )
                )

        # If still no sub-tasks, create single task
        if not sub_tasks:
            sub_tasks.append(
                SubTask(
                    task_id=str(uuid.uuid4()), query=query, context=context, priority=5
                )
            )

        return sub_tasks

    def route(self, task: SubTask) -> Optional[str]:
        """
        Route a task to the best agent

        Args:
            task: SubTask to route

        Returns:
            Agent ID or None if no suitable agent
        """
        # Extract domain from task context
        domain = task.context.get("domain")

        # Get best agent for domain
        agent_id = self.registry.get_best_agent(domain=domain, prefer_low_load=True)

        if agent_id:
            task.assigned_agent = agent_id
            return agent_id

        # Fallback: Try without domain filter
        agent_id = self.registry.get_best_agent(prefer_low_load=True)

        if agent_id:
            task.assigned_agent = agent_id

        return agent_id

    def create_orchestration_context(
        self, query: str, user_id: str, session_id: str
    ) -> OrchestrationContext:
        """
        Create orchestration context for a query

        Args:
            query: User query
            user_id: User identifier
            session_id: Session identifier

        Returns:
            OrchestrationContext with decomposed tasks
        """
        # Analyze complexity
        complexity, score = self.analyze_complexity(query)

        # Decompose query
        sub_tasks = self.decompose(query, {"user_id": user_id, "session_id": session_id})

        # Route tasks to agents
        assigned_agents = {}
        for task in sub_tasks:
            agent_id = self.route(task)
            if agent_id:
                assigned_agents[task.task_id] = agent_id

        # Create context
        context = OrchestrationContext(
            query=query,
            user_id=user_id,
            session_id=session_id,
            sub_tasks=sub_tasks,
            assigned_agents=assigned_agents,
            complexity_score=score,
            requires_consensus=len(sub_tasks) > 1,
            confidence_threshold=0.85,
        )

        return context

    def rebalance(self):
        """Redistribute load across agents"""
        # Get network stats
        stats = self.registry.get_network_stats()

        if stats["total_agents"] == 0:
            return

        # Calculate average load
        avg_load = stats["total_load"] / stats["total_agents"]

        # TODO: Implement load rebalancing logic
        # This would involve:
        # 1. Identifying overloaded agents (load > avg_load * 1.5)
        # 2. Identifying underutilized agents (load < avg_load * 0.5)
        # 3. Moving pending tasks from overloaded to underutilized agents
        pass
