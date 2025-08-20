#!/usr/bin/env python3
"""
Comprehensive test suite for Nix for Humanity v1.0 core features

Tests all 10 core features:
1. Natural Language Understanding
2. Smart Package Discovery  
3. Native Python-Nix API
4. Beautiful TUI
5. Configuration Management
6. Home Manager Integration
7. Flake Support
8. Generation Management
9. Intelligent Error Handling
10. Settings & Profiles
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import v1.0 components
from luminous_nix.core import (
    NixForHumanityBackend,
    IntentRecognizer,
    Intent,
    IntentType,
    SafeExecutor,
    KnowledgeBase
)
from luminous_nix.api import Request, Response, Result

class TestV1CoreFeatures:
    """Test all 10 core v1.0 features"""
    
    @pytest.fixture
    def backend(self):
        """Create a test backend instance"""
        return NixForHumanityBackend()
    
    # Feature 1: Natural Language Understanding
    def test_natural_language_understanding(self, backend):
        """Test natural language parsing for common NixOS commands"""
        test_cases = [
            # Simple commands
            ("install firefox", IntentType.INSTALL, {"package": "firefox"}),
            ("remove vim", IntentType.REMOVE, {"package": "vim"}),
            ("search python", IntentType.SEARCH, {"query": "python"}),
            ("update system", IntentType.UPDATE, {}),
            ("rollback", IntentType.ROLLBACK, {}),
            
            # Natural variations
            ("please install firefox for me", IntentType.INSTALL, {"package": "firefox"}),
            ("can you remove vim?", IntentType.REMOVE, {"package": "vim"}),
            ("I want to search for python packages", IntentType.SEARCH, {"query": "python"}),
            ("update my nixos system", IntentType.UPDATE, {}),
            ("go back to previous generation", IntentType.ROLLBACK, {}),
            
            # Complex queries
            ("show me all installed packages", IntentType.LIST, {"target": "packages"}),
            ("what's my current generation?", IntentType.STATUS, {"target": "generation"}),
            ("help me install a web browser", IntentType.SEARCH, {"query": "browser"}),
        ]
        
        for query, expected_type, expected_entities in test_cases:
            start_time = time.time()
            
            request = Request(command=query)
            response = backend.process_request(request)
            
            # Performance check
            elapsed = time.time() - start_time
            assert elapsed < 0.5, f"Query '{query}' took {elapsed:.2f}s (> 0.5s limit)"
            
            # Correctness check
            assert response.success, f"Failed to process: {query}"
            assert response.intent.type == expected_type, f"Wrong intent for: {query}"
            
            for key, value in expected_entities.items():
                assert key in response.intent.entities
                assert response.intent.entities[key] == value
    
    # Feature 2: Smart Package Discovery
    def test_smart_package_discovery(self, backend):
        """Test intelligent package search and discovery"""
        test_cases = [
            # Direct package names
            ("firefox", ["firefox", "firefox-esr", "firefox-bin"]),
            ("python", ["python3", "python311", "python310", "python39"]),
            
            # Categories
            ("web browser", ["firefox", "chromium", "brave", "vivaldi"]),
            ("text editor", ["vim", "neovim", "emacs", "vscode", "sublime"]),
            ("development tools", ["git", "gcc", "make", "cmake", "nodejs"]),
            
            # Typos and fuzzy matching
            ("fierrfox", ["firefox"]),  # Typo correction
            ("pythn", ["python3", "python311"]),  # Fuzzy match
            ("neovmi", ["neovim"]),  # Close match
        ]
        
        for query, expected_packages in test_cases:
            start_time = time.time()
            
            results = backend.search_packages(query)
            
            # Performance check
            elapsed = time.time() - start_time
            assert elapsed < 0.5, f"Search '{query}' took {elapsed:.2f}s (> 0.5s limit)"
            
            # Result quality check
            assert len(results) > 0, f"No results for: {query}"
            
            # Check if expected packages are in results
            result_names = [pkg.name for pkg in results]
            for expected in expected_packages:
                assert any(expected in name for name in result_names), \
                    f"Expected '{expected}' not found in results for '{query}'"
    
    # Feature 3: Native Python-Nix API Performance
    @patch('backend.core.nix_integration.NixAPI')
    def test_native_nix_api_performance(self, mock_nix_api, backend):
        """Test native Python-Nix API performance improvements"""
        # Mock the native API
        mock_api = MagicMock()
        mock_nix_api.return_value = mock_api
        
        # Test operations that should be fast with native API
        operations = [
            ("list_generations", {}),
            ("get_current_generation", {}),
            ("search_packages", {"query": "firefox"}),
            ("get_package_info", {"package": "firefox"}),
            ("check_system_status", {}),
        ]
        
        for operation, params in operations:
            start_time = time.time()
            
            # Call the operation
            method = getattr(backend, operation)
            result = method(**params)
            
            # Performance check - should be very fast with native API
            elapsed = time.time() - start_time
            assert elapsed < 0.1, f"Operation '{operation}' took {elapsed:.2f}s (> 0.1s limit)"
            
            # Verify native API was used
            assert mock_api.called, f"Native API not used for {operation}"
    
    # Feature 4: Beautiful TUI
    def test_tui_components(self):
        """Test TUI components work correctly"""
        # Import TUI components (should not fail in v1.0)
        try:
            from tui.main import NixHumanityTUI
            tui = NixHumanityTUI()
            assert tui is not None
            
            # Test basic TUI properties
            assert hasattr(tui, 'render')
            assert hasattr(tui, 'handle_input')
            assert hasattr(tui, 'update_display')
            
        except ImportError:
            pytest.skip("TUI not available in test environment")
    
    # Feature 5: Configuration Management
    def test_configuration_management(self, backend):
        """Test editing and validating NixOS configuration files"""
        test_config = """
        { config, pkgs, ... }:
        {
          environment.systemPackages = with pkgs; [
            firefox
            vim
            git
          ];
        }
        """
        
        # Test configuration validation
        start_time = time.time()
        is_valid = backend.validate_configuration(test_config)
        elapsed = time.time() - start_time
        
        assert elapsed < 0.5, f"Config validation took {elapsed:.2f}s"
        assert is_valid, "Valid configuration marked as invalid"
        
        # Test configuration suggestions
        suggestions = backend.suggest_configuration_improvements(test_config)
        assert isinstance(suggestions, list)
        
        # Test adding a package to configuration
        new_config = backend.add_package_to_config(test_config, "htop")
        assert "htop" in new_config
        assert backend.validate_configuration(new_config)
    
    # Feature 6: Home Manager Integration
    def test_home_manager_integration(self, backend):
        """Test Home Manager package management"""
        # Check if home-manager is available
        has_home_manager = backend.check_home_manager_installed()
        
        if not has_home_manager:
            # Test installation suggestion
            suggestion = backend.suggest_home_manager_setup()
            assert "home-manager" in suggestion
            pytest.skip("Home Manager not installed")
        
        # Test user package management
        user_packages = backend.list_user_packages()
        assert isinstance(user_packages, list)
        
        # Test adding user package
        start_time = time.time()
        result = backend.add_user_package("firefox")
        elapsed = time.time() - start_time
        
        assert elapsed < 0.5, f"Adding user package took {elapsed:.2f}s"
        assert result.success
    
    # Feature 7: Flake Support
    def test_flake_support(self, backend):
        """Test modern NixOS flake workflows"""
        # Test flake detection
        has_flake = backend.detect_flake()
        
        # Test flake operations
        if has_flake:
            # Test flake update
            start_time = time.time()
            result = backend.update_flake()
            elapsed = time.time() - start_time
            
            assert elapsed < 2.0, f"Flake update took {elapsed:.2f}s"
            assert result.success
        
        # Test flake template suggestion
        template = backend.suggest_flake_template()
        assert "inputs" in template
        assert "outputs" in template
    
    # Feature 8: Generation Management
    def test_generation_management(self, backend):
        """Test system generation history and rollback"""
        # List generations (should be instant with native API)
        start_time = time.time()
        generations = backend.list_generations()
        elapsed = time.time() - start_time
        
        assert elapsed < 0.1, f"Listing generations took {elapsed:.2f}s"
        assert isinstance(generations, list)
        assert len(generations) > 0
        
        # Get current generation
        current = backend.get_current_generation()
        assert isinstance(current, int)
        assert current > 0
        
        # Test rollback (dry run)
        if len(generations) > 1:
            previous = generations[-2]
            result = backend.rollback_to_generation(previous.number, dry_run=True)
            assert result.success
            assert "would rollback" in result.message.lower()
    
    # Feature 9: Intelligent Error Handling
    def test_intelligent_error_handling(self, backend):
        """Test educational error messages and recovery suggestions"""
        # Test various error scenarios
        error_scenarios = [
            # Package not found
            {
                "command": "install nonexistentpackage12345",
                "expected_category": "PACKAGE_NOT_FOUND",
                "expected_suggestions": ["search", "similar packages"],
            },
            # Permission error
            {
                "command": "remove systemd",  # System-critical package
                "expected_category": "PERMISSION_ERROR",
                "expected_suggestions": ["sudo", "system package"],
            },
            # Syntax error
            {
                "command": "install firefox vim git",  # Multiple packages
                "expected_category": "SYNTAX_ERROR",
                "expected_suggestions": ["one at a time", "configuration.nix"],
            },
        ]
        
        for scenario in error_scenarios:
            response = backend.process_request(Request(command=scenario["command"]))
            
            # Should handle error gracefully
            assert not response.success
            assert response.error is not None
            
            # Should provide educational information
            assert response.error.category == scenario["expected_category"]
            assert response.error.explanation is not None
            assert len(response.error.explanation) > 50  # Meaningful explanation
            
            # Should provide recovery suggestions
            assert response.error.suggestions is not None
            for suggestion in scenario["expected_suggestions"]:
                assert any(suggestion in s.lower() for s in response.error.suggestions)
    
    # Feature 10: Settings & Profiles
    def test_settings_and_profiles(self, backend):
        """Test personalized settings and profile management"""
        # Test profile creation
        profile = backend.create_profile("beginner")
        assert profile.name == "beginner"
        assert profile.preferences is not None
        
        # Test preference management
        backend.set_preference("response_style", "detailed")
        backend.set_preference("confirmation_required", True)
        
        pref = backend.get_preference("response_style")
        assert pref == "detailed"
        
        # Test profile switching
        backend.switch_profile("expert")
        expert_pref = backend.get_preference("response_style")
        assert expert_pref != "detailed"  # Different from beginner
        
        # Test preference persistence
        backend.save_preferences()
        backend.load_preferences()
        
        loaded_pref = backend.get_preference("response_style") 
        assert loaded_pref == expert_pref

class TestV1Integration:
    """Integration tests for all features working together"""
    
    @pytest.fixture
    def backend(self):
        return NixForHumanityBackend()
    
    def test_complete_user_journey(self, backend):
        """Test a complete user journey using multiple features"""
        # 1. User asks naturally about installing software
        response = backend.process_request(Request(
            command="I want to install a web browser"
        ))
        assert response.success
        assert "firefox" in response.message.lower() or "chromium" in response.message.lower()
        
        # 2. User searches for specific package
        response = backend.process_request(Request(
            command="search for firefox"
        ))
        assert response.success
        assert len(response.results) > 0
        
        # 3. User installs package
        response = backend.process_request(Request(
            command="install firefox",
            dry_run=True  # Don't actually install in tests
        ))
        assert response.success
        assert "would install" in response.message.lower()
        
        # 4. User checks their system
        response = backend.process_request(Request(
            command="show me my current generation"
        ))
        assert response.success
        assert response.data.get("generation") is not None
        
        # 5. User manages preferences
        backend.set_preference("auto_confirm", False)
        response = backend.process_request(Request(
            command="update system",
            dry_run=True
        ))
        assert response.needs_confirmation

class TestV1Performance:
    """Performance benchmarks for v1.0"""
    
    @pytest.fixture
    def backend(self):
        return NixForHumanityBackend()
    
    def test_response_time_benchmarks(self, backend):
        """Ensure all operations meet <0.5s response time goal"""
        benchmarks = [
            ("Natural language parsing", "install firefox"),
            ("Package search", "search python"),
            ("Generation listing", "show generations"),
            ("Configuration validation", "validate config"),
            ("Error handling", "install nonexistent"),
            ("Profile switching", "switch to expert mode"),
        ]
        
        for name, command in benchmarks:
            times = []
            
            # Run multiple times for average
            for _ in range(10):
                start = time.time()
                response = backend.process_request(Request(command=command))
                elapsed = time.time() - start
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            assert avg_time < 0.3, f"{name} avg time {avg_time:.3f}s > 0.3s"
            assert max_time < 0.5, f"{name} max time {max_time:.3f}s > 0.5s"
            
            print(f"✅ {name}: avg={avg_time:.3f}s, max={max_time:.3f}s")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])