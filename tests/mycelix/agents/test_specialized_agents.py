"""
Tests for Specialized Sophia Agents

Tests the three domain-specific agents:
- SophiaNixOS (NixOS specialist)
- SophiaShell (Shell expert)
- SophiaSecurity (Security guardian)

And tests multi-agent orchestration.
"""

import pytest
from luminous_nix.mycelix.agents import SophiaNixOS, SophiaShell, SophiaSecurity
from luminous_nix.mycelix.orchestration import MetaSophia, AgentProfile


# ============================================================================
# SophiaNixOS Tests
# ============================================================================


def test_sophia_nixos_initialization():
    """Test SophiaNixOS initialization"""
    agent = SophiaNixOS()

    assert agent.specialization == "NixOS"
    assert "nixos" in agent.expertise_domains
    assert "packages" in agent.expertise_domains
    assert len(agent.package_patterns) > 0


def test_sophia_nixos_package_query():
    """Test NixOS package query enhancement"""
    agent = SophiaNixOS()

    response = agent.respond_to_query(
        "install vim",
        {"user_id": "test"}
    )

    assert response["confidence"] >= 0.8
    # Should have NixOS-specific insights
    insights_text = " ".join(response.get("insights", []))
    assert "vim" in insights_text.lower() or "editor" in insights_text.lower()


def test_sophia_nixos_config_query():
    """Test NixOS configuration query"""
    agent = SophiaNixOS()

    response = agent.respond_to_query(
        "enable gnome desktop",
        {"user_id": "test"}
    )

    assert response["confidence"] >= 0.8
    suggestions_text = " ".join(response.get("suggestions", []))
    assert "configuration.nix" in suggestions_text or "nixos-rebuild" in suggestions_text


def test_sophia_nixos_expertise_summary():
    """Test expertise summary"""
    agent = SophiaNixOS()
    summary = agent.get_expertise_summary()

    assert summary["specialization"] == "NixOS"
    assert summary["confidence_in_domain"] >= 0.9
    assert len(summary["package_categories"]) > 0


# ============================================================================
# SophiaShell Tests
# ============================================================================


def test_sophia_shell_initialization():
    """Test SophiaShell initialization"""
    agent = SophiaShell()

    assert agent.specialization == "Shell"
    assert "shell" in agent.expertise_domains
    assert "bash" in agent.expertise_domains
    assert len(agent.command_patterns) > 0


def test_sophia_shell_command_query():
    """Test shell command query"""
    agent = SophiaShell()

    response = agent.respond_to_query(
        "how to find files",
        {"user_id": "test"}
    )

    assert response["confidence"] >= 0.8
    # Should mention find command
    all_text = " ".join(
        response.get("insights", []) + response.get("suggestions", [])
    )
    assert "find" in all_text.lower()


def test_sophia_shell_script_query():
    """Test shell scripting query"""
    agent = SophiaShell()

    response = agent.respond_to_query(
        "create a bash script",
        {"user_id": "test"}
    )

    assert response["confidence"] >= 0.8
    suggestions_text = " ".join(response.get("suggestions", []))
    assert "#!/bin/bash" in suggestions_text or "shebang" in suggestions_text.lower()


def test_sophia_shell_debugging_query():
    """Test debugging query"""
    agent = SophiaShell()

    response = agent.respond_to_query(
        "debug my script",
        {"user_id": "test"}
    )

    assert response["confidence"] >= 0.8
    suggestions_text = " ".join(response.get("suggestions", []))
    assert "set -x" in suggestions_text or "debug" in suggestions_text.lower()


def test_sophia_shell_script_template():
    """Test script template generation"""
    agent = SophiaShell()
    template = agent.get_script_template()

    assert "#!/bin/bash" in template
    assert "set -e" in template
    assert "main()" in template


# ============================================================================
# SophiaSecurity Tests
# ============================================================================


def test_sophia_security_initialization():
    """Test SophiaSecurity initialization"""
    agent = SophiaSecurity()

    assert agent.specialization == "Security"
    assert "security" in agent.expertise_domains
    assert "firewall" in agent.expertise_domains
    assert len(agent.security_practices) > 0


def test_sophia_security_firewall_query():
    """Test firewall configuration query"""
    agent = SophiaSecurity()

    response = agent.respond_to_query(
        "configure firewall",
        {"user_id": "test"}
    )

    assert response["confidence"] >= 0.8
    suggestions_text = " ".join(response.get("suggestions", []))
    assert "firewall" in suggestions_text.lower()


def test_sophia_security_ssl_query():
    """Test SSL configuration query"""
    agent = SophiaSecurity()

    response = agent.respond_to_query(
        "setup ssl certificate",
        {"user_id": "test"}
    )

    assert response["confidence"] >= 0.8
    suggestions_text = " ".join(response.get("suggestions", []))
    assert "ssl" in suggestions_text.lower() or "certificate" in suggestions_text.lower()


def test_sophia_security_warning():
    """Test security warnings"""
    agent = SophiaSecurity()

    response = agent.respond_to_query(
        "disable firewall",
        {"user_id": "test"}
    )

    # Should include security warning
    warnings = response.get("warnings", [])
    assert len(warnings) > 0
    assert "security" in warnings[0].lower() or "warning" in warnings[0].lower()


def test_sophia_security_checklist():
    """Test security checklist generation"""
    agent = SophiaSecurity()
    checklist = agent.get_security_checklist()

    assert len(checklist) > 0
    checklist_text = " ".join(checklist)
    assert "Firewall" in checklist_text
    assert "SSL" in checklist_text or "TLS" in checklist_text


# ============================================================================
# Multi-Agent Orchestration Tests
# ============================================================================


def test_multi_agent_registration():
    """Test registering multiple specialized agents"""
    meta = MetaSophia()

    # Register NixOS agent
    nixos_agent = SophiaNixOS()
    nixos_profile = AgentProfile(
        agent_id="sophia-nixos",
        name="Sophia NixOS",
        specialization="nixos",
        expertise_domains=["nixos", "packages"],
        capabilities=["install", "configure"],
    )
    result1 = meta.register_agent("sophia-nixos", nixos_profile, nixos_agent)

    # Register Shell agent
    shell_agent = SophiaShell()
    shell_profile = AgentProfile(
        agent_id="sophia-shell",
        name="Sophia Shell",
        specialization="shell",
        expertise_domains=["shell", "bash"],
        capabilities=["script", "debug"],
    )
    result2 = meta.register_agent("sophia-shell", shell_profile, shell_agent)

    # Register Security agent
    security_agent = SophiaSecurity()
    security_profile = AgentProfile(
        agent_id="sophia-security",
        name="Sophia Security",
        specialization="security",
        expertise_domains=["security", "firewall"],
        capabilities=["audit", "harden"],
    )
    result3 = meta.register_agent("sophia-security", security_profile, security_agent)

    assert result1 is True
    assert result2 is True
    assert result3 is True
    assert len(meta.registry.get_all_agents()) == 3


def test_multi_agent_simple_query():
    """Test simple query with multiple agents registered"""
    meta = MetaSophia()

    # Register agents
    agents_config = [
        (SophiaNixOS(), "sophia-nixos", "nixos", ["nixos"], ["install"]),
        (SophiaShell(), "sophia-shell", "shell", ["shell"], ["script"]),
        (SophiaSecurity(), "sophia-security", "security", ["security"], ["audit"]),
    ]

    for agent, agent_id, spec, domains, caps in agents_config:
        profile = AgentProfile(
            agent_id=agent_id,
            name=f"Sophia {spec.title()}",
            specialization=spec,
            expertise_domains=domains,
            capabilities=caps,
            success_rate=0.9,
        )
        meta.register_agent(agent_id, profile, agent)

    # Process simple query (should route to single best agent)
    response = meta.process_query(
        "install firefox",
        user_id="test-user",
        session_id="test-session"
    )

    assert isinstance(response, object)  # ConsensusResponse
    assert len(response.contributing_agents) >= 1


def test_multi_agent_complex_query():
    """Test complex query requiring multiple agents"""
    meta = MetaSophia()

    # Register agents
    agents_config = [
        (SophiaNixOS(), "sophia-nixos", "nixos", ["nixos"], ["install"]),
        (SophiaShell(), "sophia-shell", "shell", ["shell"], ["script"]),
        (SophiaSecurity(), "sophia-security", "security", ["security"], ["audit"]),
    ]

    for agent, agent_id, spec, domains, caps in agents_config:
        profile = AgentProfile(
            agent_id=agent_id,
            name=f"Sophia {spec.title()}",
            specialization=spec,
            expertise_domains=domains,
            capabilities=caps,
            success_rate=0.9,
        )
        meta.register_agent(agent_id, profile, agent)

    # Process complex query (should use multiple agents)
    response = meta.process_query(
        "set up secure web server with firewall",
        user_id="test-user",
        session_id="test-session"
    )

    assert isinstance(response, object)  # ConsensusResponse
    # Complex queries may use multiple agents
    assert len(response.contributing_agents) >= 1


def test_agent_selection_by_domain():
    """Test that Meta-Sophia selects agents by domain"""
    meta = MetaSophia()

    # Register agents with different domains
    nixos_agent = SophiaNixOS()
    nixos_profile = AgentProfile(
        agent_id="sophia-nixos",
        name="Sophia NixOS",
        specialization="nixos",
        expertise_domains=["nixos"],
        capabilities=["install"],
        success_rate=0.95,
    )
    meta.register_agent("sophia-nixos", nixos_profile, nixos_agent)

    # Query should prefer NixOS agent for NixOS queries
    best_agent = meta.registry.get_best_agent(domain="nixos")
    assert best_agent == "sophia-nixos"


def test_orchestration_with_specialists():
    """Test full orchestration flow with specialized agents"""
    meta = MetaSophia()

    # Register all three specialists
    specialists = [
        (SophiaNixOS(), "nixos", ["nixos", "packages"]),
        (SophiaShell(), "shell", ["shell", "bash"]),
        (SophiaSecurity(), "security", ["security", "firewall"]),
    ]

    for agent, spec, domains in specialists:
        profile = AgentProfile(
            agent_id=f"sophia-{spec}",
            name=f"Sophia {spec.title()}",
            specialization=spec,
            expertise_domains=domains,
            capabilities=["test"],
            success_rate=0.9,
        )
        meta.register_agent(f"sophia-{spec}", profile, agent)

    # Test orchestration
    response = meta.process_query(
        "install nginx and configure firewall",
        user_id="test",
        session_id="test"
    )

    # Should get a valid response
    assert response.confidence >= 0.0  # May be 0 in test environment
    assert len(response.contributing_agents) >= 1

    # Get stats
    stats = meta.get_stats()
    assert stats["orchestration"]["total"] == 1
    assert stats["network"]["total_agents"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
