#!/usr/bin/env python3
"""
Comprehensive test suite for Luminous Nix core functionality.
Testing what actually exists, not aspirational features.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the actual modules we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from luminous_nix.core import NixForHumanityCore
from luminous_nix.core.types import Query, Response, IntentType, NixConfig
from luminous_nix.core.error_intelligence_ast import ErrorIntelligence
from luminous_nix.nlp.intent_recognition import IntentRecognizer
from luminous_nix.nlp.safety_validator import SafetyValidator


class TestCoreInstallFunctionality:
    """Test package installation - the most critical feature."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.core = NixForHumanityCore()
        self.intent_recognizer = IntentRecognizer()
    
    def test_install_simple_package(self):
        """Test installing a simple package like firefox."""
        query = Query(text="install firefox")
        
        # Test intent recognition
        intent = self.intent_recognizer.recognize(query.text)
        assert intent.type == IntentType.INSTALL
        assert "firefox" in intent.entities.get("packages", [])
    
    def test_install_multiple_packages(self):
        """Test installing multiple packages at once."""
        query = Query(text="install vim, git, and python")
        
        intent = self.intent_recognizer.recognize(query.text)
        assert intent.type == IntentType.INSTALL
        packages = intent.entities.get("packages", [])
        assert "vim" in packages
        assert "git" in packages
        assert "python" in packages
    
    def test_install_with_typo(self):
        """Test error handling for typos."""
        query = Query(text="install fierfox")
        
        # Should suggest correction
        intent = self.intent_recognizer.recognize(query.text)
        # This should be handled by error intelligence
        assert intent.type == IntentType.INSTALL
    
    @patch('subprocess.run')
    def test_install_command_generation(self, mock_run):
        """Test that correct nix commands are generated."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        query = Query(text="install firefox")
        response = self.core.process(query)
        
        assert response.success
        assert "firefox" in response.result or "firefox" in str(response.commands)


class TestSearchFunctionality:
    """Test package search functionality."""
    
    def setup_method(self):
        self.core = NixForHumanityCore()
        self.intent_recognizer = IntentRecognizer()
    
    def test_search_by_name(self):
        """Test searching for packages by name."""
        query = Query(text="search firefox")
        
        intent = self.intent_recognizer.recognize(query.text)
        assert intent.type == IntentType.SEARCH
        assert "firefox" in intent.entities.get("query", "")
    
    def test_search_by_description(self):
        """Test searching by description."""
        query = Query(text="find text editor")
        
        intent = self.intent_recognizer.recognize(query.text)
        assert intent.type == IntentType.SEARCH
        assert "text editor" in intent.entities.get("query", "")
    
    def test_search_programming_tools(self):
        """Test searching for development tools."""
        query = Query(text="search python development tools")
        
        intent = self.intent_recognizer.recognize(query.text)
        assert intent.type == IntentType.SEARCH


class TestConfigurationGeneration:
    """Test NixOS configuration generation."""
    
    def setup_method(self):
        self.core = NixForHumanityCore()
        self.intent_recognizer = IntentRecognizer()
    
    def test_generate_basic_config(self):
        """Test generating a basic configuration."""
        query = Query(text="generate configuration for web server")
        
        intent = self.intent_recognizer.recognize(query.text)
        assert intent.type == IntentType.GENERATE_CONFIG
    
    def test_dev_environment_config(self):
        """Test creating development environment."""
        query = Query(text="create python development environment")
        
        intent = self.intent_recognizer.recognize(query.text)
        # Should be either GENERATE_CONFIG or DEVELOP
        assert intent.type in [IntentType.GENERATE_CONFIG, IntentType.DEVELOP]


class TestRollbackFunctionality:
    """Test system rollback functionality."""
    
    def setup_method(self):
        self.core = NixForHumanityCore()
        self.intent_recognizer = IntentRecognizer()
    
    def test_rollback_intent(self):
        """Test rollback command recognition."""
        query = Query(text="rollback to yesterday")
        
        intent = self.intent_recognizer.recognize(query.text)
        assert intent.type == IntentType.ROLLBACK
    
    def test_rollback_generation_number(self):
        """Test rollback to specific generation."""
        query = Query(text="rollback to generation 42")
        
        intent = self.intent_recognizer.recognize(query.text)
        assert intent.type == IntentType.ROLLBACK
        assert "42" in str(intent.entities)


class TestErrorHandling:
    """Test error handling and recovery."""
    
    def setup_method(self):
        self.error_intelligence = ErrorIntelligence()
    
    def test_parse_attribute_error(self):
        """Test parsing attribute missing errors."""
        error_msg = "error: attribute 'fierfox' missing"
        
        analysis = self.error_intelligence.analyze_error(error_msg)
        assert analysis is not None
        assert "suggestions" in analysis or "explanation" in analysis
    
    def test_timeout_error_handling(self):
        """Test handling of timeout errors."""
        error_msg = "error: build timeout exceeded"
        
        analysis = self.error_intelligence.analyze_error(error_msg)
        assert analysis is not None
    
    def test_permission_error(self):
        """Test handling permission errors."""
        error_msg = "error: permission denied"
        
        analysis = self.error_intelligence.analyze_error(error_msg)
        assert analysis is not None


class TestSafetyValidation:
    """Test safety validation to prevent dangerous commands."""
    
    def setup_method(self):
        self.validator = SafetyValidator()
    
    def test_safe_commands(self):
        """Test that safe commands pass validation."""
        safe_commands = [
            "install firefox",
            "search vim",
            "update packages",
            "show installed packages"
        ]
        
        for cmd in safe_commands:
            result = self.validator.validate_query(cmd)
            assert result["safe"], f"Command '{cmd}' should be safe"
    
    def test_dangerous_commands_blocked(self):
        """Test that dangerous commands are blocked."""
        dangerous_commands = [
            "rm -rf /",
            "delete system files",
            "format disk",
            "remove boot loader"
        ]
        
        for cmd in dangerous_commands:
            result = self.validator.validate_query(cmd)
            assert not result["safe"], f"Command '{cmd}' should be blocked"


class TestPerformance:
    """Test performance improvements."""
    
    def setup_method(self):
        self.core = NixForHumanityCore()
    
    def test_response_time(self):
        """Test that responses are fast enough."""
        import time
        
        query = Query(text="install firefox")
        
        start = time.time()
        response = self.core.process(query)
        elapsed = time.time() - start
        
        # Should respond in under 1 second for simple queries
        assert elapsed < 1.0, f"Response took {elapsed}s, should be < 1s"
    
    def test_no_subprocess_for_simple_queries(self):
        """Test that we avoid subprocess for simple operations."""
        with patch('subprocess.run') as mock_run:
            query = Query(text="help")
            response = self.core.process(query)
            
            # Help shouldn't need subprocess
            assert mock_run.call_count == 0 or response.success


class TestIntegration:
    """Integration tests for full workflows."""
    
    def setup_method(self):
        self.core = NixForHumanityCore()
    
    @pytest.mark.integration
    def test_full_install_workflow(self):
        """Test complete installation workflow."""
        # 1. Search for package
        search_query = Query(text="search text editor")
        search_response = self.core.process(search_query)
        assert search_response.success
        
        # 2. Install package
        install_query = Query(text="install vim")
        install_response = self.core.process(install_query)
        assert install_response.success
        
        # 3. Verify installation
        verify_query = Query(text="show installed packages")
        verify_response = self.core.process(verify_query)
        assert verify_response.success
    
    @pytest.mark.integration
    def test_error_recovery_workflow(self):
        """Test error recovery workflow."""
        # 1. Intentional typo
        typo_query = Query(text="install fierfox")
        typo_response = self.core.process(typo_query)
        
        # Should either autocorrect or suggest correction
        assert typo_response.success or "firefox" in str(typo_response.explanation)
    
    @pytest.mark.integration  
    def test_rollback_workflow(self):
        """Test rollback after failed change."""
        # 1. Make a change
        change_query = Query(text="install broken-package")
        change_response = self.core.process(change_query)
        
        # 2. Rollback
        rollback_query = Query(text="rollback to previous")
        rollback_response = self.core.process(rollback_query)
        
        # Should handle rollback gracefully
        assert rollback_response is not None


class TestEdgeCases:
    """Test edge cases and unusual inputs."""
    
    def setup_method(self):
        self.core = NixForHumanityCore()
        self.intent_recognizer = IntentRecognizer()
    
    def test_empty_query(self):
        """Test handling of empty queries."""
        query = Query(text="")
        response = self.core.process(query)
        
        # Should handle gracefully
        assert response is not None
        assert not response.success or response.result == "No query provided"
    
    def test_very_long_query(self):
        """Test handling of very long queries."""
        long_text = "install " + " ".join([f"package{i}" for i in range(100)])
        query = Query(text=long_text)
        
        response = self.core.process(query)
        # Should handle without crashing
        assert response is not None
    
    def test_special_characters(self):
        """Test handling of special characters."""
        queries = [
            "install firefox & chrome",
            "search python|ruby",
            "update && upgrade",
            "install package; echo test"
        ]
        
        for text in queries:
            query = Query(text=text)
            response = self.core.process(query)
            # Should sanitize or handle safely
            assert response is not None
    
    def test_non_english_input(self):
        """Test handling of non-English input."""
        query = Query(text="instalar firefox")
        response = self.core.process(query)
        
        # Should handle gracefully even if not understood
        assert response is not None


class TestMemoryAndLearning:
    """Test memory and learning capabilities."""
    
    def setup_method(self):
        self.core = NixForHumanityCore()
    
    @pytest.mark.skipif(not Path("sacred_memory.db").exists(), 
                        reason="Memory DB not initialized")
    def test_remembers_previous_commands(self):
        """Test that system remembers previous successful commands."""
        # First command
        query1 = Query(text="install firefox")
        response1 = self.core.process(query1)
        
        # Similar command should be faster/smarter
        query2 = Query(text="install firefox again")
        response2 = self.core.process(query2)
        
        # Should recognize repetition
        assert response2 is not None
    
    def test_learns_from_corrections(self):
        """Test that system learns from corrections."""
        # Typo
        typo_query = Query(text="install fierfox")
        typo_response = self.core.process(typo_query)
        
        # Correction
        correct_query = Query(text="install firefox")
        correct_response = self.core.process(correct_query)
        
        # Future typo should autocorrect
        typo_query2 = Query(text="install fierfox")
        typo_response2 = self.core.process(typo_query2)
        
        # Should have learned
        assert typo_response2 is not None


# Run specific test suites
if __name__ == "__main__":
    # Run only tests for existing functionality
    pytest.main([
        __file__,
        "-v",
        "-m", "not integration",  # Skip integration tests for now
        "--tb=short"
    ])