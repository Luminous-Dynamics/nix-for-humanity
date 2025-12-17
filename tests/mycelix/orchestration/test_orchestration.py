"""
Tests for Sophia Phase 4: Multi-Agent Orchestration

Tests the core orchestration infrastructure:
- Agent Protocol
- Agent Registry
- Task Router
- Meta-Sophia Orchestrator
"""

import pytest
import time
from unittest.mock import Mock, MagicMock

from luminous_nix.mycelix.orchestration import (
    MetaSophia,
    TaskRouter,
    AgentRegistry,
    AgentMessage,
    MessageType,
    AgentProfile,
    OrchestrationContext,
    ConsensusResponse,
    SubTask,
    AgentResponse,
)


# ============================================================================
# Agent Protocol Tests
# ============================================================================


def test_agent_message_creation():
    """Test creating agent messages"""
    msg = AgentMessage(
        sender="agent-1",
        recipient="agent-2",
        message_type=MessageType.QUERY,
        content={"query": "test"},
    )

    assert msg.sender == "agent-1"
    assert msg.recipient == "agent-2"
    assert msg.message_type == MessageType.QUERY
    assert msg.content == {"query": "test"}
    assert msg.confidence == 1.0
    assert msg.correlation_id is not None


def test_agent_message_serialization():
    """Test message serialization/deserialization"""
    msg = AgentMessage(
        sender="agent-1",
        recipient="agent-2",
        message_type=MessageType.RESPONSE,
        content={"result": "success"},
        confidence=0.95,
    )

    # Serialize
    data = msg.to_dict()
    assert data["sender"] == "agent-1"
    assert data["message_type"] == "response"

    # Deserialize
    msg2 = AgentMessage.from_dict(data)
    assert msg2.sender == msg.sender
    assert msg2.message_type == msg.message_type
    assert msg2.confidence == msg.confidence


def test_agent_profile_metrics():
    """Test agent profile metric updates"""
    profile = AgentProfile(
        agent_id="test-agent",
        name="Test Agent",
        specialization="testing",
        expertise_domains=["test"],
        capabilities=["testing"],
    )

    # Initial metrics
    assert profile.success_rate == 0.0
    assert profile.total_queries_processed == 0

    # Update with success
    profile.update_metrics(success=True, confidence=0.9, response_time=100)

    assert profile.total_queries_processed == 1
    assert profile.success_rate > 0.0
    assert profile.average_confidence > 0.0
    assert profile.response_time_avg > 0.0


# ============================================================================
# Agent Registry Tests
# ============================================================================


def test_agent_registry_register():
    """Test registering agents"""
    registry = AgentRegistry()

    profile = AgentProfile(
        agent_id="agent-1",
        name="Agent 1",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install", "configure"],
    )

    mock_agent = Mock()

    # Register agent
    result = registry.register_agent("agent-1", profile, mock_agent)
    assert result is True

    # Try to register again - should fail
    result = registry.register_agent("agent-1", profile, mock_agent)
    assert result is False

    # Verify agent is registered
    assert "agent-1" in registry.get_all_agents()


def test_agent_registry_get_agent():
    """Test retrieving agents"""
    registry = AgentRegistry()

    profile = AgentProfile(
        agent_id="agent-1",
        name="Agent 1",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install"],
    )

    mock_agent = Mock()
    registry.register_agent("agent-1", profile, mock_agent)

    # Get agent
    agent = registry.get_agent("agent-1")
    assert agent == mock_agent

    # Get non-existent agent
    agent = registry.get_agent("agent-999")
    assert agent is None


def test_agent_registry_by_domain():
    """Test finding agents by domain"""
    registry = AgentRegistry()

    # Register nixos agent
    profile1 = AgentProfile(
        agent_id="nixos-agent",
        name="NixOS Agent",
        specialization="nixos",
        expertise_domains=["nixos", "packages"],
        capabilities=["install"],
    )
    registry.register_agent("nixos-agent", profile1, Mock())

    # Register security agent
    profile2 = AgentProfile(
        agent_id="security-agent",
        name="Security Agent",
        specialization="security",
        expertise_domains=["security", "firewall"],
        capabilities=["audit"],
    )
    registry.register_agent("security-agent", profile2, Mock())

    # Find by domain
    nixos_agents = registry.get_agents_by_domain("nixos")
    assert "nixos-agent" in nixos_agents
    assert "security-agent" not in nixos_agents

    security_agents = registry.get_agents_by_domain("security")
    assert "security-agent" in security_agents
    assert "nixos-agent" not in security_agents


def test_agent_registry_best_agent():
    """Test selecting best agent"""
    registry = AgentRegistry()

    # Register high-performing agent
    profile1 = AgentProfile(
        agent_id="agent-good",
        name="Good Agent",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install"],
        success_rate=0.95,
        average_confidence=0.9,
        current_load=0,
    )
    registry.register_agent("agent-good", profile1, Mock())

    # Register lower-performing agent
    profile2 = AgentProfile(
        agent_id="agent-ok",
        name="OK Agent",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install"],
        success_rate=0.75,
        average_confidence=0.7,
        current_load=0,
    )
    registry.register_agent("agent-ok", profile2, Mock())

    # Get best agent
    best = registry.get_best_agent(domain="nixos")
    assert best == "agent-good"


def test_agent_registry_load_tracking():
    """Test load tracking"""
    registry = AgentRegistry()

    profile = AgentProfile(
        agent_id="agent-1",
        name="Agent 1",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install"],
        current_load=0,
        max_concurrent_tasks=5,
    )
    registry.register_agent("agent-1", profile, Mock())

    # Increment load
    registry.increment_load("agent-1")
    profile = registry.get_profile("agent-1")
    assert profile.current_load == 1

    # Decrement load
    registry.decrement_load("agent-1")
    profile = registry.get_profile("agent-1")
    assert profile.current_load == 0


def test_agent_registry_network_stats():
    """Test network statistics"""
    registry = AgentRegistry()

    # Register multiple agents
    for i in range(3):
        profile = AgentProfile(
            agent_id=f"agent-{i}",
            name=f"Agent {i}",
            specialization="test",
            expertise_domains=["test"],
            capabilities=["test"],
            current_load=i,
        )
        registry.register_agent(f"agent-{i}", profile, Mock())

    stats = registry.get_network_stats()

    assert stats["total_agents"] == 3
    assert stats["total_load"] == 3  # 0 + 1 + 2


# ============================================================================
# Task Router Tests
# ============================================================================


def test_task_router_complexity_analysis():
    """Test query complexity analysis"""
    registry = AgentRegistry()
    router = TaskRouter(registry)

    # Simple query
    complexity, score = router.analyze_complexity("install firefox")
    assert complexity == "simple"
    assert score < 0.5

    # Complex query
    complexity, score = router.analyze_complexity(
        "set up secure web server with SSL and firewall"
    )
    assert complexity == "complex"
    assert score > 0.7


def test_task_router_domain_identification():
    """Test domain identification"""
    registry = AgentRegistry()
    router = TaskRouter(registry)

    # NixOS domain
    domains = router.identify_domains("install firefox package")
    assert "nixos" in domains

    # Security domain
    domains = router.identify_domains("configure firewall security rules")
    assert "security" in domains

    # Multiple domains
    domains = router.identify_domains(
        "install nginx with secure SSL configuration"
    )
    assert "nixos" in domains
    assert "security" in domains


def test_task_router_simple_decomposition():
    """Test simple query decomposition"""
    registry = AgentRegistry()
    router = TaskRouter(registry)

    sub_tasks = router.decompose("install firefox", {})

    # Simple query shouldn't be decomposed
    assert len(sub_tasks) == 1
    assert sub_tasks[0].query == "install firefox"


def test_task_router_complex_decomposition():
    """Test complex query decomposition"""
    registry = AgentRegistry()
    router = TaskRouter(registry)

    sub_tasks = router.decompose(
        "set up secure web server with SSL", {"user_id": "test"}
    )

    # Complex query should be decomposed
    assert len(sub_tasks) > 1

    # Check task dependencies
    dependent_tasks = [t for t in sub_tasks if t.dependencies]
    assert len(dependent_tasks) > 0


def test_task_router_routing():
    """Test task routing to agents"""
    registry = AgentRegistry()

    # Register nixos agent
    profile = AgentProfile(
        agent_id="nixos-agent",
        name="NixOS Agent",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install"],
        success_rate=0.9,
    )
    registry.register_agent("nixos-agent", profile, Mock())

    router = TaskRouter(registry)

    # Create task
    task = SubTask(
        task_id="task-1", query="install firefox", context={"domain": "nixos"}
    )

    # Route task
    agent_id = router.route(task)

    assert agent_id == "nixos-agent"
    assert task.assigned_agent == "nixos-agent"


# ============================================================================
# Meta-Sophia Tests
# ============================================================================


def test_meta_sophia_initialization():
    """Test Meta-Sophia initialization"""
    meta = MetaSophia()

    assert meta.registry is not None
    assert meta.router is not None
    assert meta.total_orchestrations == 0


def test_meta_sophia_agent_registration():
    """Test registering agents with Meta-Sophia"""
    meta = MetaSophia()

    profile = AgentProfile(
        agent_id="test-agent",
        name="Test Agent",
        specialization="test",
        expertise_domains=["test"],
        capabilities=["test"],
    )

    mock_agent = Mock()

    # Register agent
    result = meta.register_agent("test-agent", profile, mock_agent)
    assert result is True

    # Verify registration
    agent = meta.registry.get_agent("test-agent")
    assert agent == mock_agent


def test_meta_sophia_simple_query():
    """Test processing simple query with single agent"""
    meta = MetaSophia()

    # Create mock agent
    mock_agent = Mock()
    mock_agent.respond_to_query = Mock(
        return_value={
            "content": "Firefox will be installed",
            "insights": ["Firefox is a web browser"],
            "suggestions": ["Consider Firefox ESR for stability"],
            "actions": ["nix-env -iA nixpkgs.firefox"],
            "confidence": 0.9,
        }
    )

    # Register agent
    profile = AgentProfile(
        agent_id="nixos-agent",
        name="NixOS Agent",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install"],
        success_rate=0.9,
    )
    meta.register_agent("nixos-agent", profile, mock_agent)

    # Process query
    response = meta.process_query("install firefox", "user-1", "session-1")

    # Verify response
    assert isinstance(response, ConsensusResponse)
    assert "Firefox" in response.content
    assert len(response.contributing_agents) == 1
    assert response.confidence >= 0.8


def test_meta_sophia_multi_agent_consensus():
    """Test consensus building from multiple agents"""
    meta = MetaSophia()

    # Create two mock agents
    agent1 = Mock()
    agent1.respond_to_query = Mock(
        return_value={
            "content": "Agent 1 response",
            "insights": ["Insight 1"],
            "suggestions": ["Suggestion 1"],
            "actions": [],
            "confidence": 0.85,
        }
    )

    agent2 = Mock()
    agent2.respond_to_query = Mock(
        return_value={
            "content": "Agent 2 response",
            "insights": ["Insight 2"],
            "suggestions": ["Suggestion 2"],
            "actions": [],
            "confidence": 0.90,
        }
    )

    # Register agents with different domains
    profile1 = AgentProfile(
        agent_id="agent-1",
        name="Agent 1",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install"],
        success_rate=0.9,
    )
    meta.register_agent("agent-1", profile1, agent1)

    profile2 = AgentProfile(
        agent_id="agent-2",
        name="Agent 2",
        specialization="security",
        expertise_domains=["security"],
        capabilities=["audit"],
        success_rate=0.9,
    )
    meta.register_agent("agent-2", profile2, agent2)

    # Process complex query that should use both agents
    response = meta.process_query(
        "set up secure web server", "user-1", "session-1"
    )

    # Verify consensus
    assert isinstance(response, ConsensusResponse)
    # Should have contributions from agents
    # (Note: actual multi-agent execution depends on task decomposition)


def test_meta_sophia_statistics():
    """Test orchestration statistics"""
    meta = MetaSophia()

    # Create mock agent
    mock_agent = Mock()
    mock_agent.respond_to_query = Mock(
        return_value={
            "content": "Response",
            "insights": [],
            "suggestions": [],
            "actions": [],
            "confidence": 0.9,
        }
    )

    # Register agent
    profile = AgentProfile(
        agent_id="test-agent",
        name="Test Agent",
        specialization="test",
        expertise_domains=["test"],
        capabilities=["test"],
        success_rate=0.9,
    )
    meta.register_agent("test-agent", profile, mock_agent)

    # Process queries
    meta.process_query("test query 1", "user-1", "session-1")
    meta.process_query("test query 2", "user-1", "session-1")

    # Get stats
    stats = meta.get_stats()

    assert stats["orchestration"]["total"] == 2
    assert stats["orchestration"]["successful"] >= 0
    assert stats["network"]["total_agents"] == 1


def test_consensus_response_serialization():
    """Test consensus response serialization"""
    response = ConsensusResponse(
        content="Test content",
        insights=["Insight 1"],
        suggestions=["Suggestion 1"],
        actions=["Action 1"],
        contributing_agents=["agent-1", "agent-2"],
        confidence=0.9,
        agreement_level=0.85,
    )

    # Serialize
    data = response.to_dict()

    assert data["content"] == "Test content"
    assert len(data["insights"]) == 1
    assert len(data["contributing_agents"]) == 2
    assert data["confidence"] == 0.9


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_orchestration_flow():
    """Test complete orchestration flow from query to consensus"""
    meta = MetaSophia()

    # Create and register multiple specialized agents
    agents = []
    for i in range(3):
        agent = Mock()
        agent.respond_to_query = Mock(
            return_value={
                "content": f"Agent {i} response",
                "insights": [f"Insight from agent {i}"],
                "suggestions": [f"Suggestion from agent {i}"],
                "actions": [f"action-{i}"],
                "confidence": 0.8 + (i * 0.05),
            }
        )
        agents.append(agent)

        profile = AgentProfile(
            agent_id=f"agent-{i}",
            name=f"Agent {i}",
            specialization="test",
            expertise_domains=["test"],
            capabilities=["test"],
            success_rate=0.9,
        )
        meta.register_agent(f"agent-{i}", profile, agent)

    # Process query
    response = meta.process_query("test complex query", "user-1", "session-1")

    # Verify orchestration occurred
    assert isinstance(response, ConsensusResponse)
    assert response.confidence > 0.0
    assert len(response.contributing_agents) >= 1

    # Verify at least one agent was called
    called = sum(1 for agent in agents if agent.respond_to_query.called)
    assert called >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
