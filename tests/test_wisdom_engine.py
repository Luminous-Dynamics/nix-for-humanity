"""
WisdomEngine Integration Tests

Tests the Python bridge to WisdomEngine pattern intelligence.
Based on the NixOS Codex test suite from mycelix-core-types.
"""

import pytest
import sys
import tempfile
from pathlib import Path

# Add wisdom module to path for direct testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src/luminous_nix/mycelix/wisdom"))

from wisdom_bridge import (
    WisdomBridge,
    get_wisdom_engine,
    PatternOutcome,
    TrustLevel,
    Pattern,
)
from nixos_patterns import (
    NixOSPatterns,
    NIXOS_DOMAINS,
    NIXOS_PATTERN_CATALOG,
)


@pytest.fixture
def engine():
    """Create a fresh WisdomEngine for each test"""
    storage = Path(tempfile.mkdtemp())
    return WisdomBridge(storage)


@pytest.fixture
def seeded_engine():
    """Create an engine with NixOS patterns and community wisdom"""
    storage = Path(tempfile.mkdtemp())
    engine = WisdomBridge(storage)
    NixOSPatterns.initialize_engine(engine)
    NixOSPatterns.seed_with_community_wisdom(engine)
    return engine


class TestPatternRegistration:
    """Test pattern registration and basic operations"""

    def test_register_pattern(self, engine):
        """Can register a new pattern"""
        pattern_id = engine.register_pattern(
            name="Test Pattern",
            description="A test pattern",
            domain="test_domain",
            tags=["test"],
            trust_level=TrustLevel.TESTIMONIAL,
        )

        assert pattern_id is not None
        pattern = engine.get_pattern(pattern_id)
        assert pattern is not None
        assert pattern.name == "Test Pattern"

    def test_register_domain(self, engine):
        """Can register domains with hierarchy"""
        engine.register_domain("parent", "Parent Domain")
        engine.register_domain("child", "Child Domain", parent="parent")

        ancestors = engine.domains.get_ancestors("child")
        assert "parent" in ancestors

    def test_nixos_catalog_initialization(self, engine):
        """Can initialize with full NixOS catalog"""
        count = NixOSPatterns.initialize_engine(engine)

        assert count == len(NIXOS_PATTERN_CATALOG)
        assert count >= 20  # We have 21 patterns

        # Check key patterns exist
        assert engine.get_pattern("flakes") is not None
        assert engine.get_pattern("agenix") is not None
        assert engine.get_pattern("nvidia_driver") is not None


class TestOutcomeTracking:
    """Test success/failure tracking"""

    def test_record_success(self, engine):
        """Successes are tracked"""
        pattern_id = engine.register_pattern(
            name="Success Test",
            description="Test",
            domain="test",
        )

        engine.record_success(pattern_id)
        engine.record_success(pattern_id)

        pattern = engine.get_pattern(pattern_id)
        assert pattern.success_count == 2
        assert pattern.failure_count == 0
        assert pattern.success_rate == 1.0

    def test_record_failure(self, engine):
        """Failures are tracked"""
        pattern_id = engine.register_pattern(
            name="Failure Test",
            description="Test",
            domain="test",
        )

        engine.record_failure(pattern_id)

        pattern = engine.get_pattern(pattern_id)
        assert pattern.failure_count == 1

    def test_success_rate_calculation(self, engine):
        """Success rate is correctly calculated"""
        pattern_id = engine.register_pattern(
            name="Rate Test",
            description="Test",
            domain="test",
        )

        # 7 successes, 3 failures = 70% success rate
        for _ in range(7):
            engine.record_success(pattern_id)
        for _ in range(3):
            engine.record_failure(pattern_id)

        pattern = engine.get_pattern(pattern_id)
        assert pattern.success_rate == 0.7
        assert pattern.total_uses == 10


class TestPatternSuccession:
    """Test pattern deprecation and succession"""

    def test_deprecate_pattern(self, engine):
        """Patterns can be deprecated"""
        old_id = engine.register_pattern(
            name="Old Pattern",
            description="Legacy",
            domain="test",
        )
        new_id = engine.register_pattern(
            name="New Pattern",
            description="Modern",
            domain="test",
        )

        engine.deprecate_pattern(old_id, successor_id=new_id)

        pattern = engine.get_pattern(old_id)
        assert pattern.state == "deprecated"
        assert engine.get_successor(old_id) == new_id

    def test_flakes_succeed_channels(self, seeded_engine):
        """Flakes should be recommended over channels"""
        engine = seeded_engine

        # Both should be registered
        channels = engine.get_pattern("nix_channel")
        flakes = engine.get_pattern("flakes")

        assert channels is not None
        assert flakes is not None

        # Channels should be deprecated
        assert channels.state == "deprecated"

        # Flakes should be active
        assert flakes.state == "active"

        # Flakes should have higher success rate after seeding
        assert flakes.success_rate > channels.success_rate


class TestRecommendations:
    """Test pattern recommendations"""

    def test_recommend_for_domain(self, seeded_engine):
        """Get recommendations for a domain"""
        recs = seeded_engine.recommend_patterns(
            domain=NIXOS_DOMAINS.DEVELOPMENT,
            limit=3
        )

        assert len(recs) > 0
        # devShells should be top recommendation
        assert recs[0].pattern_name == "devShells (Flakes)"

    def test_deprecated_patterns_ranked_lower(self, seeded_engine):
        """Deprecated patterns should score lower"""
        # Get all package management patterns (includes channels)
        recs = seeded_engine.recommend_patterns(
            domain=NIXOS_DOMAINS.PACKAGE_MANAGEMENT,
            include_deprecated=True,
            limit=10
        )

        # Find channels and flakes in results
        channel_rec = next((r for r in recs if r.pattern_id == "nix_channel"), None)
        flakes_rec = next((r for r in recs if r.pattern_id == "flakes"), None)

        # Flakes should score higher
        if channel_rec and flakes_rec:
            assert flakes_rec.score > channel_rec.score

    def test_context_affects_recommendations(self, seeded_engine):
        """Context should influence recommendations"""
        # Get dev recommendations with python context
        recs = seeded_engine.recommend_patterns(
            domain=NIXOS_DOMAINS.DEVELOPMENT,
            context="python project",
            limit=3
        )

        # Should still recommend devShells
        assert any("devShells" in r.pattern_name for r in recs)

    def test_hardware_domain_isolation(self, seeded_engine):
        """Hardware domains should be isolated"""
        nvidia_recs = seeded_engine.recommend_patterns(
            domain=NIXOS_DOMAINS.HARDWARE_NVIDIA,
            limit=5
        )

        amd_recs = seeded_engine.recommend_patterns(
            domain=NIXOS_DOMAINS.HARDWARE_AMD,
            limit=5
        )

        # NVIDIA recommendations should not include AMD patterns
        nvidia_names = [r.pattern_name.lower() for r in nvidia_recs]
        assert not any("amd" in name for name in nvidia_names)

        # AMD recommendations should not include NVIDIA patterns
        amd_names = [r.pattern_name.lower() for r in amd_recs]
        assert not any("nvidia" in name for name in amd_names)


class TestTrustScoring:
    """Test trust level affects scoring"""

    def test_cryptographic_scores_higher(self, engine):
        """Cryptographically verified patterns should score higher"""
        # Register two similar patterns with different trust
        testimonial_id = engine.register_pattern(
            name="Testimonial Pattern",
            description="User says it works",
            domain="test",
            trust_level=TrustLevel.TESTIMONIAL,
        )

        crypto_id = engine.register_pattern(
            name="Crypto Pattern",
            description="Cryptographically verified",
            domain="test",
            trust_level=TrustLevel.CRYPTOGRAPHIC,
        )

        # Give both same usage stats
        for _ in range(10):
            engine.record_success(testimonial_id)
            engine.record_success(crypto_id)

        recs = engine.recommend_patterns(domain="test", limit=2)

        # Crypto should rank first
        assert recs[0].pattern_id == crypto_id

    def test_agenix_over_plaintext(self, seeded_engine):
        """Agenix should be recommended over plaintext secrets"""
        recs = seeded_engine.recommend_patterns(
            domain=NIXOS_DOMAINS.SECRETS,
            include_deprecated=True,
            limit=5
        )

        # Find both patterns
        agenix_rec = next((r for r in recs if r.pattern_id == "agenix"), None)
        plaintext_rec = next((r for r in recs if r.pattern_id == "plaintext_secrets"), None)

        assert agenix_rec is not None
        if plaintext_rec:  # May be filtered out
            assert agenix_rec.score > plaintext_rec.score


class TestPersistence:
    """Test state persistence"""

    def test_state_persists(self):
        """State should persist across engine restarts"""
        storage = Path(tempfile.mkdtemp())

        # Create engine and add data
        engine1 = WisdomBridge(storage)
        pattern_id = engine1.register_pattern(
            name="Persistent Pattern",
            description="Should survive restart",
            domain="test",
        )
        engine1.record_success(pattern_id)

        # Create new engine with same storage
        engine2 = WisdomBridge(storage)

        # Pattern should exist
        pattern = engine2.get_pattern(pattern_id)
        assert pattern is not None
        assert pattern.name == "Persistent Pattern"
        assert pattern.success_count == 1


class TestNixOSCodexScenarios:
    """Test real NixOS usage scenarios from the Codex"""

    def test_legacy_to_modern_migration(self, seeded_engine):
        """Simulate migration from channels to flakes"""
        engine = seeded_engine

        # Initial state: user on channels
        # Engine should recommend flakes as successor
        successor = engine.get_successor("nix_channel")
        assert successor == "flakes"

    def test_secrets_evolution(self, seeded_engine):
        """Secrets management should evolve from plaintext to encrypted"""
        engine = seeded_engine

        # Plaintext should point to agenix
        successor = engine.get_successor("plaintext_secrets")
        assert successor == "agenix"

        # Agenix should be top recommendation for secrets
        recs = engine.recommend_patterns(
            domain=NIXOS_DOMAINS.SECRETS,
            limit=1
        )
        assert recs[0].pattern_id == "agenix"

    def test_development_workflow(self, seeded_engine):
        """Modern dev workflow should prefer flake devShells"""
        engine = seeded_engine

        recs = engine.recommend_patterns(
            domain=NIXOS_DOMAINS.DEVELOPMENT,
            context="new project",
            limit=2
        )

        # DevShells should be top
        assert recs[0].pattern_id == "dev_shell"

        # Should explain why
        assert any("High success rate" in r for r in recs[0].reasons)


class TestEngineStats:
    """Test engine statistics"""

    def test_stats_after_seeding(self, seeded_engine):
        """Stats should reflect seeded state"""
        stats = seeded_engine.get_stats()

        assert stats["total_patterns"] == 21
        assert stats["active_patterns"] == 16
        assert stats["deprecated_patterns"] == 5
        assert stats["total_uses"] > 400
        assert stats["overall_success_rate"] > 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
