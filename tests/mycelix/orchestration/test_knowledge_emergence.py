"""
Tests for Knowledge & Emergence (Phase 4C)

Tests the KnowledgeBroker and EmergenceMonitor systems.
"""

import pytest
from luminous_nix.mycelix.orchestration import (
    KnowledgeBroker,
    EmergenceMonitor,
    MetaSophia,
    AgentProfile,
)
from luminous_nix.mycelix.agents import SophiaNixOS, SophiaShell, SophiaSecurity


# ============================================================================
# Knowledge Broker Tests
# ============================================================================


def test_knowledge_broker_initialization():
    """Test knowledge broker initializes correctly"""
    kb = KnowledgeBroker()

    assert kb is not None
    assert len(kb.knowledge_base) == 0
    assert len(kb.learning_events) == 0
    assert len(kb.agent_contributions) == 0


def test_contribute_knowledge():
    """Test contributing knowledge to the broker"""
    kb = KnowledgeBroker()

    knowledge_id = kb.contribute_knowledge(
        agent_id="sophia-nixos",
        domain="nixos",
        content="Use 'nix-env -iA' for better package installation",
        confidence=0.9,
        tags=["installation", "best-practice"],
        related_queries=["install package", "how to install"],
    )

    assert knowledge_id.startswith("k")
    assert "nixos" in kb.knowledge_base
    assert len(kb.knowledge_base["nixos"]) == 1
    assert kb.agent_contributions["sophia-nixos"] == 1


def test_query_knowledge():
    """Test querying knowledge from the broker"""
    kb = KnowledgeBroker()

    # Add some knowledge
    kb.contribute_knowledge(
        agent_id="sophia-nixos",
        domain="nixos",
        content="Use flakes for reproducible environments",
        confidence=0.95,
        tags=["flakes", "reproducibility"],
    )

    kb.contribute_knowledge(
        agent_id="sophia-nixos",
        domain="nixos",
        content="Use home-manager for user configuration",
        confidence=0.85,
        tags=["home-manager", "configuration"],
    )

    # Query all nixos knowledge
    results = kb.query_knowledge(domain="nixos")
    assert len(results) == 2

    # Query with tag filter
    results = kb.query_knowledge(domain="nixos", tags=["flakes"])
    assert len(results) == 1
    assert "flakes" in results[0].content.lower()

    # Query with confidence threshold
    results = kb.query_knowledge(domain="nixos", min_confidence=0.9)
    assert len(results) == 1
    assert results[0].confidence >= 0.9


def test_record_learning_event():
    """Test recording learning events"""
    kb = KnowledgeBroker()

    event_id = kb.record_learning_event(
        agent_id="sophia-nixos",
        query="install vim",
        response={"insights": ["Vim is a powerful editor"], "confidence": 0.9},
        success=True,
    )

    assert event_id.startswith("e")
    assert len(kb.learning_events) == 1
    assert kb.learning_events[0].agent_id == "sophia-nixos"
    assert kb.learning_events[0].success is True


def test_knowledge_extraction_from_success():
    """Test automatic knowledge extraction from successful interactions"""
    kb = KnowledgeBroker()

    # Record successful event with insights
    kb.record_learning_event(
        agent_id="sophia-nixos",
        query="configure firewall",
        response={
            "insights": [
                "Enable firewall in configuration.nix",
                "Only open necessary ports",
            ],
            "confidence": 0.9,
        },
        success=True,
    )

    # Should have extracted knowledge
    event = kb.learning_events[0]
    assert len(event.extracted_knowledge) == 2

    # Should have knowledge entries
    assert "nixos" in kb.knowledge_base
    assert len(kb.knowledge_base["nixos"]) == 2


def test_knowledge_performance_update():
    """Test updating knowledge performance based on usage"""
    kb = KnowledgeBroker()

    # Add knowledge
    knowledge_id = kb.contribute_knowledge(
        agent_id="sophia-nixos",
        domain="nixos",
        content="Test knowledge",
        confidence=0.8,
    )

    # Get initial state
    knowledge = kb.knowledge_base["nixos"][0]
    initial_usage = knowledge.usage_count
    initial_success_rate = knowledge.success_rate

    # Update performance (success)
    kb.update_knowledge_performance(knowledge_id, success=True)

    assert knowledge.usage_count == initial_usage + 1
    assert knowledge.success_rate >= initial_success_rate

    # Update performance (failure)
    kb.update_knowledge_performance(knowledge_id, success=False)

    assert knowledge.usage_count == initial_usage + 2
    # Success rate should decrease after failure
    assert knowledge.success_rate < 1.0


def test_agent_stats():
    """Test agent contribution statistics"""
    kb = KnowledgeBroker()

    # Add contributions
    kb.contribute_knowledge("sophia-nixos", "nixos", "Knowledge 1", 0.9)
    kb.contribute_knowledge("sophia-nixos", "nixos", "Knowledge 2", 0.8)

    # Record events
    kb.record_learning_event("sophia-nixos", "query1", {}, success=True)
    kb.record_learning_event("sophia-nixos", "query2", {}, success=True)
    kb.record_learning_event("sophia-nixos", "query3", {}, success=False)

    # Get stats
    stats = kb.get_agent_stats("sophia-nixos")

    assert stats["contributions"] == 2
    assert stats["total_events"] == 3
    assert stats["successful_events"] == 2
    assert stats["success_rate"] == pytest.approx(2 / 3, rel=0.01)


def test_domain_stats():
    """Test domain statistics"""
    kb = KnowledgeBroker()

    # Add knowledge to domain
    kb.contribute_knowledge("agent1", "nixos", "Knowledge 1", 0.9)
    kb.contribute_knowledge("agent2", "nixos", "Knowledge 2", 0.8)

    # Mark one as used
    knowledge = kb.knowledge_base["nixos"][0]
    knowledge.usage_count = 5

    # Get stats
    stats = kb.get_domain_stats("nixos")

    assert stats["total_knowledge"] == 2
    assert stats["total_usage"] == 5
    assert stats["contributors"] == 2
    assert 0.8 <= stats["avg_confidence"] <= 0.9


# ============================================================================
# Emergence Monitor Tests
# ============================================================================


def test_emergence_monitor_initialization():
    """Test emergence monitor initializes correctly"""
    em = EmergenceMonitor()

    assert em is not None
    assert len(em.patterns) == 0
    assert len(em.insights) == 0
    assert len(em.collaborations) == 0


def test_observe_interaction():
    """Test observing interactions"""
    em = EmergenceMonitor()

    em.observe_interaction(
        query="install firefox",
        agents_involved=["sophia-nixos"],
        response={"message": "Installing...", "confidence": 0.9},
        quality_score=0.9,
    )

    # Should have recorded patterns
    assert len(em.patterns) > 0
    assert em.query_patterns["installation"] == 1


def test_collaboration_recording():
    """Test recording collaborations"""
    em = EmergenceMonitor()

    em.observe_interaction(
        query="secure web server",
        agents_involved=["sophia-nixos", "sophia-security"],
        response={"message": "...", "confidence": 0.95},
        quality_score=0.95,
    )

    # Should have recorded collaboration
    assert len(em.collaborations) == 1
    collab = em.collaborations[0]
    assert len(collab.agents) == 2
    assert collab.outcome_quality == 0.95

    # Should have synergy score
    key = tuple(sorted(["sophia-nixos", "sophia-security"]))
    assert key in em.agent_synergy


def test_pattern_detection():
    """Test pattern detection"""
    em = EmergenceMonitor()

    # Simulate multiple similar interactions
    for i in range(5):
        em.observe_interaction(
            query=f"install package {i}",
            agents_involved=["sophia-nixos"],
            response={"message": "...", "confidence": 0.9},
            quality_score=0.9,
        )

    # Should have detected pattern
    patterns = em.get_top_patterns(n=5)
    assert len(patterns) > 0
    assert patterns[0].frequency >= 5


def test_agent_synergy_calculation():
    """Test agent synergy calculation"""
    em = EmergenceMonitor()

    # Multiple successful collaborations
    for i in range(3):
        em.observe_interaction(
            query=f"query {i}",
            agents_involved=["agent1", "agent2"],
            response={"confidence": 0.9},
            quality_score=0.9,
        )

    synergies = em.get_agent_synergies()
    assert len(synergies) > 0
    agent1, agent2, score = synergies[0]
    # Synergy builds up through exponential moving average (starts at 0.5)
    assert score > 0.65  # Good synergy from successful collaborations


def test_emergence_statistics():
    """Test getting emergence statistics"""
    em = EmergenceMonitor()

    # Add some data
    em.observe_interaction("query1", ["agent1"], {"confidence": 0.9}, 0.9)
    em.observe_interaction("query2", ["agent1", "agent2"], {"confidence": 0.85}, 0.85)

    stats = em.get_statistics()

    assert "total_patterns" in stats
    assert "total_collaborations" in stats
    assert "query_distribution" in stats
    assert stats["total_collaborations"] == 1  # Only the multi-agent one


# ============================================================================
# Integration Tests with Meta-Sophia
# ============================================================================


def test_meta_sophia_with_knowledge_emergence():
    """Test Meta-Sophia with knowledge and emergence systems"""
    meta = MetaSophia()

    # Verify systems are initialized
    assert meta.knowledge is not None
    assert meta.emergence is not None

    # Register agents
    nixos_agent = SophiaNixOS()
    profile = AgentProfile(
        agent_id="sophia-nixos",
        name="Sophia NixOS",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install"],
    )
    meta.register_agent("sophia-nixos", profile, nixos_agent)

    # Process query
    response = meta.process_query(
        "install vim", user_id="test", session_id="test"
    )

    # Can access knowledge and emergence
    assert hasattr(meta, "knowledge")
    assert hasattr(meta, "emergence")


def test_observe_interaction_integration():
    """Test observing interactions through Meta-Sophia"""
    meta = MetaSophia()

    # Observe interaction
    meta.observe_interaction(
        query="install firefox",
        agents_involved=["sophia-nixos"],
        response={"confidence": 0.9, "insights": ["Great browser"]},
        success=True,
    )

    # Should be recorded in both systems
    assert len(meta.knowledge.learning_events) == 1
    assert len(meta.emergence.patterns) > 0


def test_query_shared_knowledge_integration():
    """Test querying shared knowledge through Meta-Sophia"""
    meta = MetaSophia()

    # Contribute knowledge
    knowledge_id = meta.contribute_knowledge(
        agent_id="sophia-nixos",
        domain="nixos",
        content="Use flakes for reproducibility",
        confidence=0.95,
        tags=["flakes"],
    )

    # Query it back
    results = meta.query_shared_knowledge(domain="nixos", tags=["flakes"])

    assert len(results) == 1
    assert results[0].knowledge_id == knowledge_id


def test_stats_include_knowledge_emergence():
    """Test that stats include knowledge and emergence data"""
    meta = MetaSophia()

    # Add some data
    meta.contribute_knowledge("agent1", "domain1", "content", 0.9)
    meta.observe_interaction("query", ["agent1"], {"confidence": 0.9}, True)

    # Get stats
    stats = meta.get_stats()

    assert "knowledge" in stats
    assert "emergence" in stats
    assert stats["knowledge"]["total_knowledge"] == 1
    assert stats["emergence"]["total_patterns"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
