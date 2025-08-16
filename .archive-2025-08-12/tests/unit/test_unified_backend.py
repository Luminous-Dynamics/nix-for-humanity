#!/usr/bin/env python3
"""
Tests for the Unified Backend

Tests the core functionality of the unified backend system.
"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.api.schema import Context
from luminous_nix.api.schema import Result
from luminous_nix.core.backend import (
    ,
    Intent,
    IntentType,
    NixForHumanityBackend,
    Plugin,
    ,
)

class TestPlugin(Plugin):
    """Test plugin for testing plugin system"""

    @property
    def name(self) -> str:
        return "test_plugin"

    def can_handle(self, intent: Intent) -> bool:
        return intent.query == "test plugin"

    async def process(self, intent: Intent, context: Context):
        return Result(success=True, output="Test plugin executed", intent=intent)

class TestUnifiedBackend:
    """Test the unified backend"""

    @pytest.fixture
    def backend(self):
        """Create a test backend"""
        return NixForHumanityBackend(config={"dry_run": True})

    @pytest.mark.asyncio
    async def test_initialization(self, backend):
        """Test backend initialization"""
        await backend.initialize()
        assert backend.api is not None
        assert backend.knowledge is not None
        assert backend.executor is not None

    @pytest.mark.asyncio
    async def test_empty_query_handling(self, backend):
        """Test handling of empty queries"""
        await backend.initialize()

        # Test empty string
        result = await backend.execute("")
        assert not result.success
        assert "empty" in result.error.lower()
        assert len(result.suggestions) > 0

        # Test whitespace only
        result = await backend.execute("   ")
        assert not result.success
        assert "empty" in result.error.lower()

    @pytest.mark.asyncio
    async def test_basic_intent_understanding(self, backend):
        """Test basic intent understanding"""
        await backend.initialize()

        # Test install intent
        intent = await backend.understand("install firefox", Context())
        assert intent.type == IntentType.INSTALL
        assert intent.parameters.get("package") == "firefox"

        # Test search intent
        intent = await backend.understand("search for editor", Context())
        assert intent.type == IntentType.SEARCH
        assert "editor" in intent.query.lower()

    @pytest.mark.asyncio
    async def test_plugin_system(self, backend):
        """Test plugin registration and execution"""
        await backend.initialize()

        # Register test plugin
        test_plugin = TestPlugin()
        backend.register_plugin(test_plugin)

        # Execute query that should be handled by plugin
        result = await backend.execute("test plugin")
        assert result.success
        assert result.output == "Test plugin executed"

    @pytest.mark.asyncio
    async def test_context_history(self, backend):
        """Test context history management"""
        await backend.initialize()
        context = Context()

        # Execute multiple queries
        await backend.execute("install firefox", context)
        await backend.execute("search for editor", context)

        # Check history
        assert len(context.history) == 2
        assert context.history[0].parameters.get("package") == "firefox"
        assert "editor" in context.history[1].query.lower()

    @pytest.mark.asyncio
    async def test_error_handling(self, backend):
        """Test error handling and recovery"""
        await backend.initialize()

        # Test with query that will fail parsing
        result = await backend.execute("this is not a valid command ;&|")
        assert not result.success
        assert result.error is not None
        assert len(result.suggestions) > 0

    @pytest.mark.asyncio
    async def test_dry_run_mode(self, backend):
        """Test that dry run mode doesn't execute"""
        await backend.initialize()

        result = await backend.execute("install firefox")
        assert "[DRY RUN]" in result.output
        assert result.success
        # Should not actually install anything

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self, backend):
        """Test that execution time is tracked"""
        await backend.initialize()

        result = await backend.execute("install firefox")
        assert result.execution_time is not None
        assert result.execution_time > 0
        assert result.execution_time < 5  # Should be fast

    @pytest.mark.asyncio
    async def test_suggestions_on_failure(self, backend):
        """Test that suggestions are provided on failure"""
        await backend.initialize()

        # Intentionally cause a failure
        result = await backend.execute("")
        assert not result.success
        assert len(result.suggestions) > 0
        assert isinstance(result.suggestions, list)
        assert all(isinstance(s, str) for s in result.suggestions)

class TestIntentType:
    """Test IntentType enum"""

    def test_intent_types_exist(self):
        """Test that all expected intent types exist"""
        expected_types = [
            "INSTALL",
            "REMOVE",
            "SEARCH",
            "UPDATE",
            "ROLLBACK",
            "GENERATE_CONFIG",
            "UNKNOWN",
        ]

        for intent_type in expected_types:
            assert hasattr(IntentType, intent_type)

    def test_intent_type_values(self):
        """Test intent type values"""
        assert IntentType.INSTALL.value == "install"
        assert IntentType.SEARCH.value == "search"
        assert IntentType.UNKNOWN.value == "unknown"

class TestResult:
    """Test Result dataclass"""

    def test_result_to_dict(self):
        """Test result serialization"""
        result = Result(
            success=True,
            output="Test output",
            error=None,
            suggestions=["suggestion1", "suggestion2"],
            metadata={"key": "value"},
            execution_time=1.5,
        )

        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["output"] == "Test output"
        assert result_dict["error"] is None
        assert len(result_dict["suggestions"]) == 2
        assert result_dict["metadata"]["key"] == "value"
        assert result_dict["execution_time"] == 1.5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
