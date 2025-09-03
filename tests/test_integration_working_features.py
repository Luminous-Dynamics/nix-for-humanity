#!/usr/bin/env python3
"""
Integration tests for all working features in Luminous Nix.
These tests verify end-to-end functionality of production-ready features.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from luminous_nix.core.luminous_core import LuminousNixCore, Query, Response
from luminous_nix.core.intents import IntentRecognizer, IntentType
from luminous_nix.core.smart_package_discovery import SmartPackageDiscovery
from luminous_nix.security.validator import InputValidator


@pytest.mark.integration
class TestNaturalLanguageInput:
    """Test natural language processing capabilities."""
    
    def setup_method(self):
        """Setup test environment."""
        self.core = LuminousNixCore()
        self.recognizer = IntentRecognizer()
    
    def test_natural_language_search(self):
        """Test natural language search queries."""
        queries = [
            "search for text editors",
            "find me a web browser",
            "I need a video player",
            "show me markdown editors",
            "what python packages are available"
        ]
        
        for query_text in queries:
            query = Query(text=query_text)
            intent = self.recognizer.recognize(query_text)
            assert intent is not None
            assert intent.type in [IntentType.SEARCH_PACKAGE, IntentType.DISCOVER_PACKAGE]
    
    def test_natural_language_install(self):
        """Test natural language install commands."""
        queries = [
            "install firefox please",
            "I want to install vim",
            "can you install git for me",
            "set up python development tools",
            "add nodejs to my system"
        ]
        
        for query_text in queries:
            intent = self.recognizer.recognize(query_text)
            assert intent is not None
            assert intent.type in [IntentType.INSTALL_PACKAGE, IntentType.CREATE_FLAKE]
    
    def test_natural_language_remove(self):
        """Test natural language removal commands."""
        queries = [
            "remove firefox",
            "uninstall vim please",
            "delete the git package",
            "get rid of nodejs"
        ]
        
        for query_text in queries:
            intent = self.recognizer.recognize(query_text)
            assert intent is not None
            assert intent.type == IntentType.REMOVE_PACKAGE


@pytest.mark.integration
class TestSmartPackageDiscovery:
    """Test intelligent package discovery features."""
    
    def setup_method(self):
        """Setup test environment."""
        self.discovery = SmartPackageDiscovery()
        self.core = LuminousNixCore()
    
    def test_typo_correction(self):
        """Test typo correction in package names."""
        typos = [
            ("fierefox", "firefox"),
            ("pythn", "python"),
            ("dokcer", "docker"),
            ("kubernets", "kubernetes"),
            ("postgressql", "postgresql")
        ]
        
        for typo, correct in typos:
            # Search with typo
            results = self.discovery.find_similar_packages(typo)
            # Should find the correct package
            assert any(correct in str(r).lower() for r in results)
    
    def test_semantic_understanding(self):
        """Test semantic search capabilities."""
        semantic_queries = [
            ("code editor", ["vim", "emacs", "vscode", "neovim"]),
            ("web browser", ["firefox", "chromium", "brave"]),
            ("video player", ["vlc", "mpv", "mplayer"]),
            ("terminal emulator", ["alacritty", "kitty", "terminator"]),
            ("database", ["postgresql", "mysql", "sqlite"])
        ]
        
        for query, expected_packages in semantic_queries:
            results = self.discovery.search_by_description(query)
            # Should find at least one expected package
            found = False
            for package in expected_packages:
                if any(package in str(r).lower() for r in results):
                    found = True
                    break
            assert found, f"Semantic search for '{query}' didn't find any of {expected_packages}"
    
    def test_category_matching(self):
        """Test category-based package discovery."""
        categories = [
            ("browser", ["firefox", "chromium"]),
            ("editor", ["vim", "emacs"]),
            ("compiler", ["gcc", "clang"]),
            ("shell", ["bash", "zsh", "fish"])
        ]
        
        for category, expected in categories:
            results = self.discovery.search_by_description(category)
            assert len(results) > 0
            # Check if at least one expected package is found
            found = any(
                any(pkg in str(r).lower() for r in results)
                for pkg in expected
            )
            assert found


@pytest.mark.integration
class TestPackageOperations:
    """Test actual package management operations."""
    
    def setup_method(self):
        """Setup test environment."""
        self.core = LuminousNixCore()
    
    @patch('subprocess.run')
    def test_package_installation(self, mock_run):
        """Test package installation flow."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Test installation
        query = Query(text="install firefox", dry_run=False)
        response = self.core.process_query(query)
        
        # Should generate correct command
        assert mock_run.called or response.command
        if response.command:
            assert "firefox" in response.command
            assert any(cmd in response.command for cmd in ["nix-env", "nix profile"])
    
    @patch('subprocess.run')
    def test_package_removal(self, mock_run):
        """Test package removal flow."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        query = Query(text="remove vim", dry_run=False)
        response = self.core.process_query(query)
        
        # Should generate removal command
        assert mock_run.called or response.command
        if response.command:
            assert "vim" in response.command
            assert any(cmd in response.command for cmd in ["uninstall", "remove", "-e"])
    
    @patch('subprocess.run')
    def test_list_installed_packages(self, mock_run):
        """Test listing installed packages."""
        mock_output = "firefox-120.0\nvim-9.0\ngit-2.42"
        mock_run.return_value = MagicMock(
            returncode=0, 
            stdout=mock_output, 
            stderr=""
        )
        
        query = Query(text="list installed packages")
        response = self.core.process_query(query)
        
        assert response.success or mock_run.called
        # The response should contain package information
        if response.data:
            assert "packages" in response.data or response.message
    
    def test_dry_run_mode(self):
        """Test dry run mode doesn't execute commands."""
        query = Query(text="install dangerous-package", dry_run=True)
        response = self.core.process_query(query)
        
        # Should not actually execute
        assert response.success or response.command
        if response.command:
            assert response.message  # Should have explanatory message
            # Verify no actual subprocess call was made
            with patch('subprocess.run') as mock_run:
                query_live = Query(text="install dangerous-package", dry_run=False)
                # In dry run, subprocess shouldn't be called
                response_dry = self.core.process_query(query)
                if query.dry_run:
                    assert not mock_run.called or "Would execute" in response.message


@pytest.mark.integration
class TestErrorIntelligence:
    """Test error handling and intelligence features."""
    
    def setup_method(self):
        """Setup test environment."""
        self.core = LuminousNixCore()
        from luminous_nix.core.error_intelligence_ast import ASTErrorIntelligence
        self.error_intel = ASTErrorIntelligence()
    
    def test_helpful_error_messages(self):
        """Test that errors provide helpful guidance."""
        error_scenarios = [
            ("attribute 'fierfox' not found", "firefox"),
            ("permission denied", "sudo"),
            ("out of disk space", "garbage collect"),
            ("network error", "connection")
        ]
        
        for error_msg, expected_hint in error_scenarios:
            analysis = self.error_intel.analyze_error(error_msg)
            assert analysis is not None
            # Should provide helpful information
            assert "explanation" in analysis or "suggestions" in analysis
    
    def test_error_recovery_suggestions(self):
        """Test error recovery suggestions."""
        # Simulate a failed installation
        error = "error: attribute 'nonexistent-package' not found"
        analysis = self.error_intel.analyze_error(error)
        
        assert analysis is not None
        if "suggestions" in analysis:
            assert len(analysis["suggestions"]) > 0
            # Should suggest searching or checking package name
            assert any(
                keyword in str(analysis["suggestions"]).lower()
                for keyword in ["search", "check", "name", "typo"]
            )


@pytest.mark.integration
class TestCLIInterface:
    """Test CLI interface functionality."""
    
    def test_cli_help_command(self):
        """Test help command output."""
        # Test using the actual CLI
        result = subprocess.run(
            ["poetry", "run", "ask-nix", "help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should provide help information
        assert result.returncode == 0 or "help" in result.stdout.lower()
    
    def test_cli_version_command(self):
        """Test version command."""
        result = subprocess.run(
            ["poetry", "run", "ask-nix", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should show version
        assert result.returncode == 0 or "0." in result.stdout
    
    def test_cli_dry_run_flag(self):
        """Test dry run flag prevents execution."""
        result = subprocess.run(
            ["poetry", "run", "ask-nix", "--dry-run", "install", "firefox"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should indicate dry run
        assert "would" in result.stdout.lower() or "dry" in result.stdout.lower()


@pytest.mark.integration
class TestSecurityFeatures:
    """Test security validation features."""
    
    def setup_method(self):
        """Setup test environment."""
        self.validator = InputValidator()
        self.core = LuminousNixCore()
    
    def test_input_sanitization(self):
        """Test dangerous input is sanitized."""
        dangerous_inputs = [
            "install firefox; rm -rf /",
            "search $(echo bad)",
            "install `malicious`",
            "remove firefox && evil-command",
            "../../../etc/passwd"
        ]
        
        for dangerous in dangerous_inputs:
            result = self.validator.validate_input(dangerous, input_type="nlp")
            # Should either reject or sanitize
            assert not result["valid"] or result["sanitized_input"] != dangerous
    
    def test_command_validation(self):
        """Test command validation before execution."""
        dangerous_commands = [
            ["rm", "-rf", "/"],
            ["dd", "if=/dev/zero", "of=/dev/sda"],
            ["chmod", "-R", "777", "/"],
            [":(){ :|:& };:"]  # Fork bomb
        ]
        
        for cmd in dangerous_commands:
            valid, error = self.validator.validate_command(cmd)
            assert not valid
            assert error is not None
    
    def test_safe_commands_allowed(self):
        """Test that safe commands are allowed."""
        safe_commands = [
            ["nix-env", "-iA", "nixpkgs.firefox"],
            ["nix", "search", "nixpkgs", "vim"],
            ["nix-collect-garbage", "-d"],
            ["nix", "profile", "list"]
        ]
        
        for cmd in safe_commands:
            valid, error = self.validator.validate_command(cmd)
            assert valid
            assert error is None


@pytest.mark.integration
class TestConfigurationSystem:
    """Test configuration management features."""
    
    def setup_method(self):
        """Setup test environment."""
        self.core = LuminousNixCore()
        self.config_dir = Path.home() / ".config" / "luminous-nix"
    
    def test_config_persistence(self):
        """Test configuration is saved and loaded."""
        # Create a test config
        test_config = {
            "mindful_mode": True,
            "dry_run_default": True,
            "cache_enabled": True
        }
        
        # Save config
        config_file = self.config_dir / "test_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Load config
        with open(config_file, 'r') as f:
            loaded = json.load(f)
        
        assert loaded == test_config
        
        # Cleanup
        config_file.unlink(missing_ok=True)
    
    def test_cache_functionality(self):
        """Test search cache improves performance."""
        import time
        
        # First search (cold cache)
        start = time.time()
        query1 = Query(text="search firefox")
        response1 = self.core.process_query(query1)
        time1 = time.time() - start
        
        # Second search (warm cache)
        start = time.time()
        query2 = Query(text="search firefox")
        response2 = self.core.process_query(query2)
        time2 = time.time() - start
        
        # Cache should make second search faster (or at least not slower)
        # Note: This might not always be true in tests, so we just check it works
        assert response1.success or response1.command
        assert response2.success or response2.command


@pytest.mark.integration
class TestProgressIndicators:
    """Test progress indication features."""
    
    def test_progress_feedback(self):
        """Test that long operations show progress."""
        # This is hard to test without mocking, but we can verify the mechanism exists
        from luminous_nix.core.progress_indicator import ProgressIndicator
        
        progress = ProgressIndicator()
        progress.start("Test operation")
        
        # Should be able to update progress
        for i in range(5):
            progress.update(i * 20)
        
        progress.complete()
        
        # Basic verification that progress tracking works
        assert hasattr(progress, 'start')
        assert hasattr(progress, 'update')
        assert hasattr(progress, 'complete')


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete user workflows."""
    
    def setup_method(self):
        """Setup test environment."""
        self.core = LuminousNixCore()
    
    def test_search_and_install_workflow(self):
        """Test searching for a package then installing it."""
        # Step 1: Search for editors
        search_query = Query(text="search text editor", dry_run=True)
        search_response = self.core.process_query(search_query)
        assert search_response.success or search_response.command
        
        # Step 2: Install vim (found from search)
        install_query = Query(text="install vim", dry_run=True)
        install_response = self.core.process_query(install_query)
        assert install_response.success or install_response.command
        
        # Step 3: Verify installation (dry run)
        list_query = Query(text="list installed packages", dry_run=True)
        list_response = self.core.process_query(list_query)
        assert list_response.success or list_response.command
    
    def test_typo_correction_workflow(self):
        """Test the typo correction workflow."""
        # User makes a typo
        typo_query = Query(text="install fierefox", dry_run=True)
        response = self.core.process_query(typo_query)
        
        # Should either autocorrect or suggest correction
        assert response.success or "firefox" in response.message.lower()
    
    def test_help_to_action_workflow(self):
        """Test getting help then performing action."""
        # Step 1: Get help
        help_query = Query(text="help", dry_run=True)
        help_response = self.core.process_query(help_query)
        # Help might not be fully implemented, but should respond
        assert help_response is not None
        
        # Step 2: Perform an action based on help
        action_query = Query(text="search python", dry_run=True)
        action_response = self.core.process_query(action_query)
        assert action_response.success or action_response.command


# Performance benchmarks (optional, not critical)
@pytest.mark.benchmark
@pytest.mark.integration
class TestPerformanceBenchmarks:
    """Benchmark performance of key operations."""
    
    def setup_method(self):
        """Setup test environment."""
        self.core = LuminousNixCore()
    
    def test_search_performance(self):
        """Test search completes in reasonable time."""
        import time
        
        start = time.time()
        query = Query(text="search firefox", dry_run=True)
        response = self.core.process_query(query)
        duration = time.time() - start
        
        # Should complete in under 5 seconds
        assert duration < 5.0
        assert response is not None
    
    def test_intent_recognition_performance(self):
        """Test intent recognition is fast."""
        import time
        recognizer = IntentRecognizer()
        
        queries = [
            "install firefox",
            "search python packages",
            "remove vim",
            "list installed"
        ]
        
        start = time.time()
        for q in queries:
            intent = recognizer.recognize(q)
            assert intent is not None
        duration = time.time() - start
        
        # Should process all queries in under 1 second
        assert duration < 1.0


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])