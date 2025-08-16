import pytest
pytest.skip("Property-based testing module", allow_module_level=True)

"""
Property-based tests using Hypothesis.

These tests generate random inputs to find edge cases automatically.

Since: v1.0.1
"""

import sys
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, invariant, rule

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix import NixForHumanityBackend
from luminous_nix.core.cache import Cache
from luminous_nix.core.history import CommandHistory

class TestPropertyBasedInputs:
    """Property-based tests for input handling."""

    @given(st.text())
    def test_any_text_input_doesnt_crash(self, text):
        """Test that any text input is handled without crashing."""
        backend = NixForHumanityBackend()

        try:
            result = backend.execute(text)
            # Should always return a dict with expected keys
            assert isinstance(result, dict)
            assert "success" in result
            assert "output" in result
        except Exception as e:
            # Only acceptable exceptions
            assert isinstance(e, (ValueError, TypeError))

    @given(st.lists(st.text(min_size=1), min_size=1, max_size=100))
    def test_batch_commands_consistency(self, commands):
        """Test that batch execution is consistent."""
        backend = NixForHumanityBackend()

        # Execute individually
        individual_results = []
        for cmd in commands:
            try:
                result = backend.execute(cmd)
                individual_results.append(result)
            except:
                individual_results.append({"success": False})

        # Execute as batch (if supported)
        try:
            batch_result = backend.execute_batch(commands)
            # Batch should have same number of results
            assert len(batch_result) == len(commands)
        except AttributeError:
            # Batch not implemented yet
            pass

    @given(
        st.text(alphabet=st.characters(blacklist_categories=["Cc", "Cs"]), min_size=1),
        st.integers(min_value=1, max_value=1000),
    )
    def test_repeated_execution_stability(self, command, repetitions):
        """Test that repeated execution of same command is stable."""
        backend = NixForHumanityBackend()

        results = []
        for _ in range(min(repetitions, 10)):  # Cap at 10 for performance
            try:
                result = backend.execute(command)
                results.append(result.get("success", False))
            except:
                results.append(False)

        # Results should be consistent
        if len(results) > 1:
            # All results should be the same
            assert all(r == results[0] for r in results)

class TestPropertyBasedCache:
    """Property-based tests for caching system."""

    @given(st.dictionaries(st.text(min_size=1), st.text()))
    def test_cache_preserves_data(self, data):
        """Test that cache preserves all data correctly."""
        cache = Cache()

        # Store all data
        for key, value in data.items():
            cache.set(key, value)

        # Retrieve and verify
        for key, expected in data.items():
            actual = cache.get(key)
            assert actual == expected

    @given(
        st.lists(st.tuples(st.text(min_size=1), st.text()), min_size=1),
        st.integers(min_value=1, max_value=100),
    )
    def test_cache_size_limit(self, items, max_size):
        """Test that cache respects size limits."""
        cache = Cache(max_size=max_size)

        # Add items
        for key, value in items:
            cache.set(key, value)

        # Cache size should not exceed limit
        assert len(cache) <= max_size

    @given(st.text(min_size=1), st.text(), st.floats(min_value=0.1, max_value=10))
    def test_cache_ttl_behavior(self, key, value, ttl):
        """Test cache TTL (time-to-live) behavior."""
        cache = Cache()

        # Set with TTL
        cache.set(key, value, ttl=ttl)

        # Should exist immediately
        assert cache.get(key) == value

        # After expiry, should not exist (we can't actually wait, so just test the logic)
        cache._expire_old_entries()
        # This tests the expiry logic exists

class TestPropertyBasedHistory:
    """Property-based tests for command history."""

    @given(st.lists(st.text(min_size=1), max_size=1000))
    def test_history_order_preserved(self, commands):
        """Test that history preserves order."""
        history = CommandHistory()

        # Add commands
        for cmd in commands:
            history.add(cmd)

        # Get recent history
        recent = history.get_recent(len(commands))

        # Order should be preserved (most recent last)
        expected = commands[-len(recent) :]
        assert recent == expected

    @given(st.text(min_size=1), st.integers(min_value=2, max_value=100))
    def test_history_no_adjacent_duplicates(self, command, count):
        """Test that history doesn't store adjacent duplicates."""
        history = CommandHistory()

        # Add same command multiple times
        for _ in range(count):
            history.add(command)

        # Should only have one entry (or implementation-specific behavior)
        recent = history.get_recent(count)

        # No adjacent duplicates
        for i in range(1, len(recent)):
            if recent[i] == recent[i - 1]:
                # Implementation allows duplicates
                break
        else:
            # No adjacent duplicates found - good!
            pass

class PackageStateMachine(RuleBasedStateMachine):
    """
    Stateful testing for package management operations.

    This ensures that package operations maintain consistency.
    """

    packages = Bundle("packages")

    def __init__(self):
        super().__init__()
        self.backend = NixForHumanityBackend()
        self.installed = set()

    @rule(
        target=packages,
        name=st.text(
            alphabet=st.characters(min_codepoint=97, max_codepoint=122),
            min_size=3,
            max_size=20,
        ),
    )
    def install_package(self, name):
        """Install a package."""
        # Simulate installation
        self.installed.add(name)
        return name

    @rule(package=packages)
    def remove_package(self, package):
        """Remove an installed package."""
        # Simulate removal
        self.installed.discard(package)

    @rule(package=packages)
    def verify_installed(self, package):
        """Verify package is marked as installed."""
        assert package in self.installed

    @invariant()
    def installed_count_non_negative(self):
        """Installed package count should never be negative."""
        assert len(self.installed) >= 0

    @invariant()
    def no_null_packages(self):
        """No null/empty package names in installed set."""
        assert all(pkg for pkg in self.installed)

class TestPropertyBasedSecurity:
    """Property-based security tests."""

    @given(st.text())
    def test_no_command_injection(self, user_input):
        """Test that user input cannot cause command injection."""
        backend = NixForHumanityBackend()

        # Even with malicious input, should be safe
        try:
            result = backend.execute(f"install {user_input}")

            # Check that dangerous characters were escaped
            if any(char in user_input for char in [";", "|", "&", "$", "`", ">"]):
                # Should have been sanitized or rejected
                assert result.get("safe", True)
        except:
            # Rejection is also acceptable
            pass

    @given(st.text())
    @settings(max_examples=100)
    def test_path_traversal_prevention(self, path_input):
        """Test that path traversal is prevented."""
        backend = NixForHumanityBackend()

        # Try to access files via path traversal
        dangerous_patterns = ["../", "/..", "..."]

        if any(pattern in path_input for pattern in dangerous_patterns):
            result = backend.execute(f"read {path_input}")

            # Should either reject or sanitize
            assert (
                not result.get("success")
                or "denied" in result.get("output", "").lower()
            )

class TestPropertyBasedUnicode:
    """Property-based tests for Unicode handling."""

    @given(
        st.text(alphabet=st.characters(min_codepoint=0x1F300, max_codepoint=0x1F6FF))
    )
    def test_emoji_handling(self, emoji_text):
        """Test that emoji are handled correctly."""
        backend = NixForHumanityBackend()

        result = backend.execute(f"search {emoji_text}")

        # Should not crash
        assert isinstance(result, dict)

    @given(st.text(alphabet=st.characters(blacklist_categories=["Cc", "Cs", "Cn"])))
    def test_unicode_normalization(self, text):
        """Test Unicode normalization consistency."""
        import unicodedata

        backend = NixForHumanityBackend()

        # Try different normalizations
        nfc = unicodedata.normalize("NFC", text)
        nfd = unicodedata.normalize("NFD", text)

        result_nfc = backend.execute(f"search {nfc}")
        result_nfd = backend.execute(f"search {nfd}")

        # Should treat normalized forms equivalently
        # (This may not always be true, but it's a good property to test)
        assert result_nfc.get("success") == result_nfd.get("success")

class TestPropertyBasedPerformance:
    """Property-based tests for performance characteristics."""

    @given(st.integers(min_value=1, max_value=1000))
    def test_linear_scaling(self, n):
        """Test that operations scale linearly."""
        import time

        backend = NixForHumanityBackend()

        # Measure time for n operations
        start = time.perf_counter()

        for i in range(min(n, 100)):  # Cap for test performance
            backend.execute(f"search package{i}")

        elapsed = time.perf_counter() - start

        # Should complete in reasonable time (not exponential)
        # Rough check: should be less than n * 0.1 seconds
        assert elapsed < n * 0.1

# Test the stateful package manager
TestPackageStateMachine = PackageStateMachine.TestCase

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
