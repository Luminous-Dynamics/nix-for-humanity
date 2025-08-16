"""
Unit tests for the caching layer - Consciousness-First Testing

Tests cache manager, specialized caches, and invalidation strategies
using deterministic test implementations instead of mocks.
"""

import sys
import time
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from luminous_nix.core.types import (
    ExecutionResult,
    Intent,
    IntentType,
    Request,
    Response,
)

from luminous_nix.cache.redis_cache import (
    CacheConfig,
    CacheInvalidator,
    CacheManager,
    CacheType,
    CommandResultCache,
    ResponseCache,
    XAIExplanationCache,
)

# v2.0+ feature: from luminous_nix.ai.xai_engine import ExplanationLevel
# v2.0+ feature: from luminous_nix.xai.causal_engine import CausalExplanation

class TestCacheManager:
    """Test core cache manager functionality"""

    @pytest.fixture
    def cache_manager(self, tmp_path):
        """Create cache manager with test config"""
        config = CacheConfig(
            cache_type=CacheType.HYBRID,
            memory_size_mb=1,  # Small for testing
            cache_dir=tmp_path / "test_cache",
            response_ttl=2,  # Short TTL for testing
            enable_compression=True,
        )
        return CacheManager(config)

    def test_memory_cache_basic_operations(self, cache_manager):
        """Test basic get/set operations"""
        # Set value
        cache_manager.set("test_key", "test_value", ttl=10)

        # Get value
        value = cache_manager.get("test_key")
        assert value == "test_value"

        # Cache hit should be recorded
        stats = cache_manager.get_statistics()
        assert stats["hits"] == 1
        assert stats["misses"] == 0

    def test_cache_miss(self, cache_manager):
        """Test cache miss behavior"""
        value = cache_manager.get("nonexistent_key")
        assert value is None

        stats = cache_manager.get_statistics()
        assert stats["hits"] == 0
        assert stats["misses"] == 1

    def test_ttl_expiration(self, cache_manager):
        """Test TTL expiration"""
        # Set with short TTL
        cache_manager.set("expire_key", "value", ttl=1)

        # Should exist immediately
        assert cache_manager.get("expire_key") == "value"

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired
        assert cache_manager.get("expire_key") is None

    def test_lru_eviction(self, cache_manager):
        """Test LRU eviction when memory is full"""
        # Fill cache to capacity
        for i in range(100):
            cache_manager.set(f"key_{i}", f"value_{i}" * 100)  # Large values

        # Check evictions occurred
        stats = cache_manager.get_statistics()
        assert stats["evictions"] > 0

    def test_disk_spillover(self, cache_manager):
        """Test hybrid mode disk spillover"""
        # Set large value that should go to disk
        large_value = "x" * 10000  # 10KB
        cache_manager.set("large_key", large_value)

        # Should be retrievable
        assert cache_manager.get("large_key") == large_value

    def test_compression(self, cache_manager):
        """Test compression for large entries"""
        # Large compressible data
        large_data = "a" * 5000  # Highly compressible
        cache_manager.set("compress_key", large_data)

        # Should be stored and retrieved correctly
        assert cache_manager.get("compress_key") == large_data

    def test_invalidation(self, cache_manager):
        """Test cache invalidation"""
        # Set multiple entries
        cache_manager.set("prefix_1", "value1")
        cache_manager.set("prefix_2", "value2")
        cache_manager.set("other_key", "value3")

        # Invalidate by pattern
        count = cache_manager.invalidate("prefix_")
        assert count == 2

        # Prefix entries should be gone
        assert cache_manager.get("prefix_1") is None
        assert cache_manager.get("prefix_2") is None

        # Other entry should remain
        assert cache_manager.get("other_key") == "value3"

class TestResponseCache:
    """Test response caching with fuzzy matching"""

    @pytest.fixture
    def response_cache(self, tmp_path):
        """Create response cache"""
        config = CacheConfig(cache_dir=tmp_path / "test_cache")
        cache_manager = CacheManager(config)
        return ResponseCache(cache_manager)

    def test_exact_match_caching(self, response_cache):
        """Test exact query match"""
        request = Request(
            query="install firefox", context={"session_id": "test"}, dry_run=True
        )

        response = Response(
            success=True,
            intent=Intent(type=IntentType.INSTALL_PACKAGE),
            message="Installing firefox...",
        )

        # Cache response
        response_cache.set(request, response)

        # Should get cached response
        cached = response_cache.get(request)
        assert cached is not None
        assert cached.message == response.message

    def test_normalized_query_matching(self, response_cache):
        """Test normalized query matching"""
        # Cache with one phrasing
        request1 = Request(
            query="Please install firefox for me", context={"session_id": "test"}
        )
        response = Response(success=True)
        response_cache.set(request1, response)

        # Should match with different phrasing
        request2 = Request(
            query="install firefox",  # Normalized version
            context={"session_id": "test"},
        )
        cached = response_cache.get(request2)
        assert cached is not None

    def test_context_compatibility(self, response_cache):
        """Test context affects caching"""
        request1 = Request(query="install firefox", context={"persona": "grandma_rose"})
        request2 = Request(query="install firefox", context={"persona": "dr_sarah"})

        response = Response(success=True)
        response_cache.set(request1, response)

        # Different context should not match
        cached = response_cache.get(request2)
        assert cached is None

    def test_query_variation_learning(self, response_cache):
        """Test system learns query variations"""
        base_request = Request(query="install firefox")
        variations = [
            "please install firefox",
            "can you install firefox",
            "i need firefox",
            "get me firefox",
        ]

        response = Response(success=True)
        response_cache.set(base_request, response)

        # Cache variations
        for var in variations:
            var_request = Request(query=var)
            response_cache.set(var_request, response)

        # Should have learned variations
        stats = response_cache.get_statistics()
        assert stats["variations_learned"] > 0

class TestCommandCache:
    """Test command result caching"""

    @pytest.fixture
    def command_cache(self, tmp_path):
        """Create command cache"""
        config = CacheConfig(cache_dir=tmp_path / "test_cache")
        cache_manager = CacheManager(config)
        return CommandResultCache(cache_manager)

    def test_safe_command_caching(self, command_cache):
        """Test caching of safe commands"""
        command = {"command": "nix-env -q", "args": []}
        result = ExecutionResult(
            success=True,
            output="firefox-1.0\nvim-8.0",
            error="",
            exit_code=0,
            duration=1.0,
        )

        # Should cache
        command_cache.set(command, result)
        cached = command_cache.get(command)
        assert cached is not None
        assert cached.output == result.output

    def test_unsafe_command_not_cached(self, command_cache):
        """Test unsafe commands are not cached"""
        command = {"command": "rm", "args": ["-rf", "/tmp/test"]}
        result = ExecutionResult(success=True)

        # Should not cache
        command_cache.set(command, result)
        cached = command_cache.get(command)
        assert cached is None

    def test_invalidation_by_command(self, command_cache):
        """Test cache invalidation by related commands"""
        # Cache package list
        list_command = {"command": "nix-env -q"}
        # Use a real test result instead of mock
        list_result = ExecutionResult(
            success=True,
            output="firefox-1.0\nvim-8.0",
            error="",
            exit_code=0,
            duration=0.5,
        )
        command_cache.set(list_command, list_result)

        # Install command should invalidate list
        install_command = {"command": "nix-env -i", "args": ["firefox"]}
        invalidated = command_cache.invalidate_by_command(install_command)

        assert invalidated > 0
        assert command_cache.get(list_command) is None

class TestXAICache:
    """Test XAI explanation caching"""

    @pytest.fixture
    def xai_cache(self, tmp_path):
        """Create XAI cache"""
        config = CacheConfig(cache_dir=tmp_path / "test_cache")
        cache_manager = CacheManager(config)
        return XAIExplanationCache(cache_manager)

    def test_explanation_caching(self, xai_cache):
        """Test caching of XAI explanations"""
        explanation = CausalExplanation(
            decision_type="intent_recognition",
            decision_value="install_package",
            explanation="I understood you want to install software",
            confidence=0.9,
            level=ExplanationLevel.SIMPLE,
        )

        # Cache explanation
        xai_cache.set(
            "intent_recognition",
            "install_package",
            {"user_input": "install firefox"},
            ExplanationLevel.SIMPLE,
            explanation,
            0.5,  # computation time
        )

        # Should retrieve
        cached = xai_cache.get(
            "intent_recognition",
            "install_package",
            {"user_input": "install firefox"},
            ExplanationLevel.SIMPLE,
        )

        assert cached is not None
        assert cached.explanation == explanation.explanation

    def test_multi_level_caching(self, xai_cache):
        """Test caching multiple explanation levels"""
        explanations = {
            ExplanationLevel.SIMPLE: (
                CausalExplanation(
                    decision_type="test",
                    decision_value="test",
                    explanation="Simple",
                    level=ExplanationLevel.SIMPLE,
                ),
                0.1,
            ),
            ExplanationLevel.DETAILED: (
                CausalExplanation(
                    decision_type="test",
                    decision_value="test",
                    explanation="Detailed",
                    level=ExplanationLevel.DETAILED,
                ),
                0.3,
            ),
        }

        # Cache all levels
        xai_cache.set_multi_level("test", "test", {}, explanations)

        # Should retrieve all
        cached = xai_cache.get_multi_level("test", "test", {})
        assert cached[ExplanationLevel.SIMPLE] is not None
        assert cached[ExplanationLevel.DETAILED] is not None

    def test_computation_time_tracking(self, xai_cache):
        """Test tracking of computation times"""
        # Cache with computation time using real explanation object
        explanation = CausalExplanation(
            decision_type="test",
            decision_value="test",
            explanation="Test explanation for timing",
            confidence=0.85,
            level=ExplanationLevel.SIMPLE,
        )
        xai_cache.set(
            "test", "test", {}, ExplanationLevel.SIMPLE, explanation, 1.5  # seconds
        )

        # Should track in statistics
        stats = xai_cache.get_statistics()
        assert "avg_computation_times" in stats
        assert len(stats["avg_computation_times"]) > 0

class TestCacheInvalidator:
    """Test intelligent cache invalidation"""

    @pytest.fixture
    def invalidator(self, tmp_path):
        """Create cache invalidator"""
        config = CacheConfig(cache_dir=tmp_path / "test_cache")
        cache_manager = CacheManager(config)
        return CacheInvalidator(cache_manager)

    def test_event_based_invalidation(self, invalidator):
        """Test invalidation triggered by events"""
        # Populate cache
        invalidator.cache_manager.set("response:test", "value")
        invalidator.cache_manager.set("command:test", "value")

        # Trigger system update event
        count = invalidator.trigger_event({"type": "system_update"})

        # Should invalidate entries
        assert count > 0
        assert invalidator.cache_manager.get("response:test") is None

    def test_pattern_based_invalidation(self, invalidator):
        """Test pattern-based invalidation"""
        # Populate cache
        invalidator.cache_manager.set("test:1", "value1")
        invalidator.cache_manager.set("test:2", "value2")
        invalidator.cache_manager.set("other:1", "value3")

        # Invalidate by pattern
        count = invalidator.invalidate_pattern("test:")

        assert count == 2
        assert invalidator.cache_manager.get("test:1") is None
        assert invalidator.cache_manager.get("other:1") == "value3"

    def test_dependency_cascading(self, invalidator):
        """Test dependency-based cascading invalidation"""
        # Set up entries with dependencies
        invalidator.cache_manager.set("primary:1", "value1")
        invalidator.cache_manager.set("dependent:1", "value2")

        # Invalidate with cascade
        count = invalidator.invalidate_pattern("primary:", cascade=True)

        # Should invalidate dependencies too
        assert count >= 1  # At least the primary

    def test_invalidation_history(self, invalidator):
        """Test invalidation history tracking"""
        # Trigger some invalidations
        invalidator.trigger_event({"type": "package_install"})
        invalidator.trigger_event({"type": "config_change"})

        # Should have history
        history = invalidator.get_invalidation_history()
        assert len(history) >= 2
        assert history[-1]["event"]["type"] == "config_change"
