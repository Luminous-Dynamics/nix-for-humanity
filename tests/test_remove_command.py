#!/usr/bin/env python3
"""
Test the remove command functionality - REAL tests, not aspirational
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from luminous_nix.frontends.cli import UnifiedNixAssistant
from luminous_nix.core.intent_pipeline import Intent, IntentRecognitionPipeline, Entity
from luminous_nix.core.executor import CommandExecutor, CommandType


class TestRemoveCommand:
    """Test remove command parsing and execution"""
    
    def setup_method(self):
        """Set up test environment"""
        self.assistant = UnifiedNixAssistant()
        self.assistant.dry_run = True
        self.assistant.skip_confirmation = True
        
    def test_basic_remove_command(self):
        """Test that 'remove firefox' works correctly"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            self.assistant._handle_remove("remove firefox")
            
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            # Should use nix profile remove
            assert 'nix' in call_args
            assert 'profile' in call_args
            assert 'remove' in call_args
            assert 'firefox' in str(call_args)
            # Should NOT use nix-env
            assert 'nix-env' not in call_args
    
    def test_natural_language_remove(self):
        """Test natural language like 'uninstall firefox please'"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            self.assistant._handle_remove("uninstall firefox please")
            
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            assert 'firefox' in str(call_args)
            assert 'profile' in call_args
            assert 'remove' in call_args
    
    def test_remove_without_package(self):
        """Test remove command without specifying package"""
        with patch('builtins.print') as mock_print:
            self.assistant._handle_remove("remove")
            
            # Should print error message
            mock_print.assert_any_call("❌ Please specify what to remove")
    
    def test_remove_with_confirmation(self):
        """Test remove command confirmation prompt"""
        self.assistant.skip_confirmation = False
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            with patch('builtins.input', return_value='y') as mock_input:
                self.assistant._handle_remove("remove firefox")
                
                # Should ask for confirmation
                assert mock_input.called
                # Should proceed with removal
                assert mock_run.called
    
    def test_remove_cancelled_by_user(self):
        """Test user cancelling remove operation"""
        self.assistant.skip_confirmation = False
        
        with patch('subprocess.run') as mock_run:
            with patch('builtins.input', return_value='n') as mock_input:
                with patch('builtins.print') as mock_print:
                    self.assistant._handle_remove("remove firefox")
                    
                    # Should ask for confirmation
                    assert mock_input.called
                    # Should NOT proceed with removal
                    assert not mock_run.called
                    # Should print cancellation message
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any('cancel' in str(call).lower() for call in print_calls)
    
    def test_remove_package_not_installed(self):
        """Test removing a package that isn't installed"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout='',
                stderr='error: package not found'
            )
            
            with patch('builtins.print') as mock_print:
                self.assistant._handle_remove("remove nonexistentpackage")
                
                # Should show error message
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any('error' in str(call).lower() or 'not found' in str(call).lower()
                          for call in print_calls)
    
    def test_remove_filters_common_words(self):
        """Test that remove filters out command words from package name"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            # Test with "please remove firefox now"
            self.assistant._handle_remove("please remove firefox now")
            
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            command_str = ' '.join(str(arg) for arg in call_args)
            
            # Should have firefox but not please/now
            assert 'firefox' in command_str
            assert 'please' not in command_str
            assert 'now' not in command_str
    
    def test_command_executor_remove(self):
        """Test that command executor creates correct remove command"""
        from luminous_nix.core.executor import CommandExecutor, CommandType
        
        executor = CommandExecutor()
        cmd = executor.create_command(CommandType.REMOVE, ['firefox'])
        
        # Should use nix profile remove
        assert 'nix' in cmd.command
        assert 'profile' in cmd.command
        assert 'remove' in cmd.command
        assert 'firefox' in cmd.command
        # Should not have dry-run flag (nix profile doesn't support it)
        assert cmd.dry_run_flag is None
        # Remove should be rollbackable
        assert cmd.can_rollback == True


class TestRemoveIntegration:
    """Test remove with intent recognition pipeline"""
    
    def test_intent_recognition_for_remove(self):
        """Test that various remove phrases are recognized"""
        pipeline = IntentRecognitionPipeline()
        
        test_phrases = [
            "remove firefox",
            "uninstall firefox",
            "delete firefox",
            "get rid of firefox",
            "remove the firefox package",
            "can you uninstall vim"
        ]
        
        for phrase in test_phrases:
            result = pipeline.recognize(phrase)
            # Should recognize as remove intent
            assert result.primary_intent == Intent.REMOVE, \
                f"Failed to recognize remove intent in: {phrase}"
    
    def test_remove_entities_extraction(self):
        """Test extracting package name for removal"""
        pipeline = IntentRecognitionPipeline()
        
        result = pipeline.recognize("remove firefox from my system")
        
        # Should extract firefox as package
        package_entities = [e for e in result.entities if e.type == 'package']
        firefox_found = any('firefox' in e.value.lower() for e in package_entities)
        assert firefox_found, "Should extract 'firefox' as package to remove"
    
    def test_remove_doesnt_confuse_with_install(self):
        """Test that remove is not confused with install"""
        pipeline = IntentRecognitionPipeline()
        
        # These should all be REMOVE, not INSTALL
        remove_phrases = [
            "uninstall firefox",
            "remove vim package",
            "delete htop"
        ]
        
        for phrase in remove_phrases:
            result = pipeline.recognize(phrase)
            assert result.primary_intent == Intent.REMOVE, \
                f"'{phrase}' should be REMOVE, not {result.primary_intent}"
            assert result.primary_intent != Intent.INSTALL, \
                f"'{phrase}' incorrectly recognized as INSTALL"


class TestRemoveSafety:
    """Test safety features of remove command"""
    
    def test_remove_creates_snapshot(self):
        """Test that remove creates a system snapshot for rollback"""
        from luminous_nix.core.executor import CommandExecutor
        
        executor = CommandExecutor()
        executor.auto_snapshot = True
        executor.dry_run = False
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            with patch.object(executor, '_create_snapshot') as mock_snapshot:
                mock_snapshot.return_value = Mock()
                
                cmd = executor.create_command(CommandType.REMOVE, ['firefox'])
                executor.execute(cmd, preview_first=False, confirm=False)
                
                # Should create snapshot before removing
                assert mock_snapshot.called
    
    def test_remove_can_rollback(self):
        """Test that remove operations can be rolled back"""
        from luminous_nix.core.executor import CommandExecutor, CommandType
        
        executor = CommandExecutor()
        cmd = executor.create_command(CommandType.REMOVE, ['firefox'])
        
        # Remove should be marked as rollbackable
        assert cmd.can_rollback == True


if __name__ == "__main__":
    # Run the tests
    test_remove = TestRemoveCommand()
    test_remove.setup_method()
    
    print("Testing remove command...")
    test_remove.test_basic_remove_command()
    print("✅ Basic remove command works")
    
    test_remove.test_natural_language_remove()
    print("✅ Natural language remove works")
    
    test_remove.test_remove_without_package()
    print("✅ Error handling for missing package works")
    
    test_remove.test_remove_with_confirmation()
    print("✅ Confirmation prompt works")
    
    test_remove.test_remove_cancelled_by_user()
    print("✅ User cancellation works")
    
    test_remove.test_remove_package_not_installed()
    print("✅ Not installed error handling works")
    
    test_remove.test_remove_filters_common_words()
    print("✅ Common word filtering works")
    
    test_remove.test_command_executor_remove()
    print("✅ Command executor remove works")
    
    print("\nTesting remove integration...")
    test_integration = TestRemoveIntegration()
    
    test_integration.test_intent_recognition_for_remove()
    print("✅ Intent recognition for remove works")
    
    test_integration.test_remove_entities_extraction()
    print("✅ Remove entity extraction works")
    
    test_integration.test_remove_doesnt_confuse_with_install()
    print("✅ Remove not confused with install")
    
    print("\nTesting remove safety...")
    test_safety = TestRemoveSafety()
    
    test_safety.test_remove_creates_snapshot()
    print("✅ Snapshot creation works")
    
    test_safety.test_remove_can_rollback()
    print("✅ Rollback capability confirmed")
    
    print("\n🎉 All remove tests passed!")