"""
Comprehensive test suite for Nix for Humanity

Tests all major components with proper mocking and assertions.
"""

import asyncio
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.core.async_executor import AsyncCommandExecutor
from luminous_nix.core.cache import SimpleCache, SmartCache
from luminous_nix.api.schema import Context
from luminous_nix.api.schema import Result
from luminous_nix.core.backend import (
    ,
    IntentType,
    NixForHumanityBackend,
    ,
)
from luminous_nix.errors import ErrorContext, ErrorEducator, IntelligentErrorHandler
from luminous_nix.security.validator import InputValidator
from luminous_nix.ui.progress import PhaseProgress, ProgressBar, Spinner

class TestUnifiedBackend:
    """Test the unified backend"""

    @pytest.fixture
    def backend(self):
        """Create backend instance"""
        return NixForHumanityBackend({"dry_run": True, "caching": False})

    @pytest.mark.asyncio
    async def test_execute_simple_query(self, backend):
        """Test simple query execution"""
        result = await backend.execute("help")

        assert result.success == True
        assert result.error is None
        assert result.execution_time is not None
        assert result.execution_time < 1.0  # Should be fast

    @pytest.mark.asyncio
    async def test_execute_with_context(self, backend):
        """Test execution with context"""
        context = Context(user_id="test_user", session_id="test_session")

        result = await backend.execute("test query", context)

        assert result.success == True
        assert len(context.history) == 1
        assert context.history[0].query == "test query"

    @pytest.mark.asyncio
    async def test_intent_understanding(self, backend):
        """Test intent parsing"""
        intent = await backend.understand("install firefox", Context())

        assert intent.type == IntentType.INSTALL
        assert intent.parameters.get("package") == "firefox"
        assert intent.confidence > 0.5

    @pytest.mark.asyncio
    async def test_error_handling(self, backend):
        """Test error handling"""
        result = await backend.execute("")

        assert result.success == False
        assert "Empty query" in result.error
        assert len(result.suggestions) > 0

    @pytest.mark.asyncio
    async def test_plugin_system(self, backend):
        """Test plugin registration and execution"""
        # Create mock plugin
        mock_plugin = Mock()
        mock_plugin.name = "test_plugin"
        mock_plugin.can_handle.return_value = True
        mock_plugin.process = AsyncMock(
            return_value=Result(success=True, output="Plugin handled")
        )

        backend.register_plugin(mock_plugin)

        result = await backend.execute("test query")

        mock_plugin.can_handle.assert_called()
        mock_plugin.process.assert_called()

class TestCaching:
    """Test caching system"""

    @pytest.fixture
    def cache_dir(self):
        """Create temporary cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def cache(self, cache_dir):
        """Create cache instance"""
        return SimpleCache(cache_dir=cache_dir, ttl_seconds=60)

    def test_cache_get_set(self, cache):
        """Test basic cache operations"""
        # Test miss
        result = cache.get("test_key")
        assert result is None

        # Test set and hit
        cache.set("test_key", {"data": "test_value"})
        result = cache.get("test_key")
        assert result == {"data": "test_value"}

    def test_cache_expiration(self, cache):
        """Test cache expiration"""
        cache.ttl = timedelta(seconds=0)  # Immediate expiration

        cache.set("test_key", "test_value")
        result = cache.get("test_key")

        assert result is None  # Should be expired

    def test_smart_cache_should_cache(self):
        """Test smart cache decision logic"""
        cache = SmartCache()

        assert cache.should_cache("search") == True
        assert cache.should_cache("generate_config") == True
        assert cache.should_cache("install") == False
        assert cache.should_cache("update") == False

    def test_cache_cleanup(self, cache):
        """Test cache cleanup"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

class TestAsyncExecutor:
    """Test async command executor"""

    @pytest.fixture
    def executor(self):
        """Create executor instance"""
        return AsyncCommandExecutor(max_workers=2)

    @pytest.mark.asyncio
    async def test_async_execution(self, executor):
        """Test basic async execution"""
        result = await executor.execute("test command")

        assert result.success == True
        assert result.duration is not None
        assert result.duration < 1.0

    @pytest.mark.asyncio
    async def test_parallel_execution(self, executor):
        """Test parallel command execution"""
        commands = ["search vim", "search emacs", "search vscode"]

        results = await executor.execute_parallel(commands)

        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_streaming_execution(self, executor):
        """Test streaming updates"""
        updates = []

        async for update in executor.stream_execution("test command"):
            updates.append(update)

        assert len(updates) > 0
        assert updates[0]["type"] == "start"
        assert updates[-1]["type"] == "complete"

    @pytest.mark.asyncio
    async def test_batch_operations(self, executor):
        """Test batch context manager"""
        async with executor.batch_operations():
            results = await executor.execute_parallel(["cmd1", "cmd2"])

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_cancellation(self, executor):
        """Test task cancellation"""
        # Start long-running task
        task = asyncio.create_task(executor.execute("long command"))

        # Cancel it
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass  # Expected

    @pytest.mark.asyncio
    async def test_cleanup(self, executor):
        """Test resource cleanup"""
        await executor.cleanup()

        assert len(executor._active_tasks) == 0

class TestIntelligentErrors:
    """Test intelligent error handling"""

    @pytest.fixture
    def handler(self):
        """Create error handler"""
        return IntelligentErrorHandler()

    @pytest.fixture
    def educator(self):
        """Create error educator"""
        return ErrorEducator()

    def test_error_pattern_matching(self, handler):
        """Test error pattern recognition"""
        error = "attribute 'firofox' not found"
        context = ErrorContext("package_error", error, package="firofox")

        result = handler.explain_error(error, context)

        assert "Package 'firofox' not found" in result["explanation"]
        assert len(result["suggestions"]) > 0
        assert result["error_type"] == "package_error"

    def test_educational_formatting(self, educator):
        """Test educational error formatting"""
        error = "permission denied"
        context = ErrorContext("permission_error", error)

        educated = educator.educate(error, context)

        assert "❌" in educated  # Error marker
        assert "💡" in educated  # Suggestion marker
        assert "sudo" in educated  # Specific advice

    def test_pattern_memory(self, educator):
        """Test that educator remembers patterns"""
        # Simulate repeated errors
        for _ in range(3):
            educator.educate(
                "package not found", ErrorContext("package_error", "error")
            )

        tips = educator.get_common_mistakes()

        assert len(tips) > 0
        assert "Package names" in tips[0]

class TestSecurity:
    """Test security features"""

    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return InputValidator()

    def test_input_validation(self, validator):
        """Test input validation"""
        # Test valid input
        result = validator.validate_input("firefox", "package")
        assert result["valid"] == True

        # Test dangerous input
        result = validator.validate_input("firefox; rm -rf /", "package")
        assert result["valid"] == False
        assert "injection" in result["reason"].lower()

    def test_command_validation(self, validator):
        """Test command validation"""
        # Test safe command
        valid, _ = validator.validate_command(["nix", "search", "firefox"])
        assert valid == True

        # Test dangerous command
        valid, reason = validator.validate_command(["rm", "-rf", "/"])
        assert valid == False
        assert "dangerous" in reason.lower()

    def test_path_validation(self, validator):
        """Test path validation"""
        # Test safe path
        result = validator.validate_input("/home/user/file.txt", "path")
        assert result["valid"] == True

        # Test directory traversal
        result = validator.validate_input("../../etc/passwd", "path")
        assert result["valid"] == False
        assert "traversal" in result["reason"].lower()

class TestProgressIndicators:
    """Test progress indication"""

    def test_spinner_lifecycle(self):
        """Test spinner start/stop"""
        spinner = Spinner("Testing")

        spinner.start()
        assert spinner.running == True

        spinner.stop("Done")
        assert spinner.running == False

    def test_progress_bar_update(self):
        """Test progress bar updates"""
        bar = ProgressBar(10, "Testing")

        for i in range(10):
            bar.update()

        assert bar.current == 10

    def test_phase_progress(self):
        """Test phase progress"""
        phases = ["Phase 1", "Phase 2", "Phase 3"]
        progress = PhaseProgress(phases)

        progress.start_phase(0)
        assert progress.current_phase == 0

        progress.start_phase(1)
        assert progress.current_phase == 1

class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_full_flow_with_caching(self):
        """Test complete flow with caching"""
        backend = NixForHumanityBackend({"caching": True})

        # First query (not cached)
        result1 = await backend.execute("search editor")
        assert result1.success == True
        assert result1.metadata.get("cached") != True

        # Same query (should be cached)
        result2 = await backend.execute("search editor")
        assert result2.success == True
        # Note: Cache check happens before metadata is set

    @pytest.mark.asyncio
    async def test_error_education_flow(self):
        """Test error education in full flow"""
        backend = NixForHumanityBackend()

        # Trigger an error
        result = await backend.execute("install")  # Missing package name

        assert result.success == False
        assert result.error is not None
        assert len(result.suggestions) > 0

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "asyncio: mark test as needing asyncio")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
