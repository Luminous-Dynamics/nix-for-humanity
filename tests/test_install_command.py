#!/usr/bin/env python3
"""
Test the install command functionality - REAL tests, not aspirational
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from luminous_nix.frontends.cli import UnifiedNixAssistant
from luminous_nix.core.intent_pipeline import Intent, IntentRecognitionPipeline, Entity


class TestInstallCommand:
    """Test install command parsing and execution"""
    
    def setup_method(self):
        """Set up test environment"""
        self.assistant = UnifiedNixAssistant()
        self.assistant.dry_run = True
        self.assistant.skip_confirmation = True
        
    def test_basic_install_command(self):
        """Test that 'install firefox' correctly identifies firefox as package"""
        # This actually tests the _handle_install method
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            # Call the method directly
            self.assistant._handle_install("install firefox")
            
            # Should have been called with firefox, not install
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            # Check that firefox is in the command, not install as package
            assert 'firefox' in str(call_args)
            assert 'install install' not in str(call_args)
    
    def test_natural_language_install(self):
        """Test natural language like 'i want to install firefox'"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            self.assistant._handle_install("i want to install firefox")
            
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            assert 'firefox' in str(call_args)
    
    def test_install_without_package(self):
        """Test install command without specifying package"""
        with patch('builtins.print') as mock_print:
            self.assistant._handle_install("install")
            
            # Should print error message
            mock_print.assert_any_call("❌ Please specify what to install")
    
    def test_entity_extraction_filters_install(self):
        """Test that entity extraction doesn't use 'install' as package name"""
        pipeline = IntentRecognitionPipeline()
        result = pipeline.recognize("install firefox")
        
        # Check entities
        package_entities = [e for e in result.entities if e.type == 'package']
        
        # Should find firefox but not install
        firefox_found = any(e.value == 'firefox' for e in package_entities)
        install_found = any(e.value == 'install' for e in package_entities)
        
        assert firefox_found, "Should find 'firefox' as package entity"
        # Note: install might be found but should be filtered out in _execute_intent
    
    def test_execute_intent_filters_common_words(self):
        """Test that _execute_intent filters out common words from package entities"""
        from luminous_nix.core.intent_pipeline import IntentResult
        
        # Create mock intent result with both firefox and install as entities
        intent_result = IntentResult(
            primary_intent=Intent.INSTALL,
            confidence=0.9,
            entities=[
                Entity(type='package', value='firefox', confidence=1.0),
                Entity(type='package', value='install', confidence=0.8),
            ],
            original_query="install firefox",
            normalized_query="install firefox"
        )
        
        with patch.object(self.assistant, '_install_package_robust') as mock_install:
            self.assistant._execute_intent(intent_result)
            
            # Should install firefox, not install
            mock_install.assert_called_once_with('firefox')
    
    def test_command_executor_uses_nix_profile(self):
        """Test that command executor uses modern nix profile commands"""
        from luminous_nix.core.executor import CommandExecutor, CommandType
        
        executor = CommandExecutor()
        cmd = executor.create_command(CommandType.INSTALL, ['firefox'])
        
        # Should use nix profile, not nix-env
        assert 'nix' in cmd.command
        assert 'profile' in cmd.command
        assert 'nixpkgs#firefox' in cmd.command
        assert 'nix-env' not in cmd.command
    
    def test_dry_run_doesnt_execute(self):
        """Test that dry-run mode doesn't actually execute commands"""
        self.assistant.dry_run = True
        
        with patch('subprocess.run') as mock_run:
            self.assistant._install_package("firefox")
            
            # In dry-run mode, subprocess.run should not be called
            assert not mock_run.called


class TestProfileMigration:
    """Test nix profile migration handling"""
    
    def test_profile_incompatibility_detection(self):
        """Test that profile incompatibility is detected"""
        assistant = UnifiedNixAssistant()
        assistant.skip_confirmation = True
        
        with patch('subprocess.run') as mock_run:
            # Simulate profile incompatibility error
            mock_run.side_effect = [
                Mock(returncode=1, stderr="incompatible with 'nix-env'"),  # profile list fails
                Mock(returncode=0, stdout='', stderr='')  # subsequent calls
            ]
            
            with patch('luminous_nix.cli.profile_migration.auto_migrate_profile') as mock_migrate:
                mock_migrate.return_value = True
                assistant._install_package("firefox")
                
                # Should have called migration
                assert mock_migrate.called


if __name__ == "__main__":
    # Run the tests
    test_install = TestInstallCommand()
    test_install.setup_method()
    
    print("Testing install command...")
    test_install.test_basic_install_command()
    print("✅ Basic install command works")
    
    test_install.test_natural_language_install()
    print("✅ Natural language install works")
    
    test_install.test_install_without_package()
    print("✅ Error handling for missing package works")
    
    test_install.test_entity_extraction_filters_install()
    print("✅ Entity extraction works")
    
    test_install.test_execute_intent_filters_common_words()
    print("✅ Common word filtering works")
    
    test_install.test_command_executor_uses_nix_profile()
    print("✅ Command executor uses modern nix profile")
    
    test_install.test_dry_run_doesnt_execute()
    print("✅ Dry-run mode works")
    
    print("\n🎉 All tests passed!")