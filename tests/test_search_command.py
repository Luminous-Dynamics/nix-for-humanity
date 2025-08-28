#!/usr/bin/env python3
"""
Test the search command functionality - REAL tests, not aspirational
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from luminous_nix.frontends.cli import UnifiedNixAssistant
from luminous_nix.core.intent_pipeline import Intent, IntentRecognitionPipeline, Entity
from luminous_nix.core.executor import CommandExecutor, CommandType


class TestSearchCommand:
    """Test search command parsing and execution"""
    
    def setup_method(self):
        """Set up test environment"""
        self.assistant = UnifiedNixAssistant()
        self.assistant.dry_run = True
        self.assistant.skip_confirmation = True
        
    def test_basic_search_command(self):
        """Test that 'search firefox' works correctly"""
        with patch('subprocess.run') as mock_run:
            # Simulate search results
            mock_run.return_value = Mock(
                returncode=0,
                stdout='* nixpkgs.firefox (firefox-123.0)\n  Web browser',
                stderr=''
            )
            
            self.assistant._handle_search("search firefox")
            
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            # Should use nix search command
            assert 'nix' in call_args
            assert 'search' in call_args
            assert 'firefox' in str(call_args)
    
    def test_natural_language_search(self):
        """Test natural language like 'find me a text editor'"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='* nixpkgs.vim (vim-9.0)\n  Text editor',
                stderr=''
            )
            
            self.assistant._handle_search("find me a text editor")
            
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            # Should translate to search for text and editor
            assert 'search' in call_args
            assert any('text' in str(arg).lower() or 'editor' in str(arg).lower() 
                      for arg in call_args)
    
    def test_search_without_query(self):
        """Test search command without specifying what to search"""
        with patch('builtins.print') as mock_print:
            self.assistant._handle_search("search")
            
            # Should print error message
            mock_print.assert_any_call("❌ Please specify what to search for")
    
    def test_search_with_multiple_terms(self):
        """Test searching with multiple terms"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='', stderr='')
            
            self.assistant._handle_search("search python development environment")
            
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            # Should include all search terms
            command_str = ' '.join(str(arg) for arg in call_args)
            assert 'python' in command_str.lower()
    
    def test_search_result_parsing(self):
        """Test parsing and displaying search results"""
        with patch('subprocess.run') as mock_run:
            # Simulate multiple results
            mock_run.return_value = Mock(
                returncode=0,
                stdout="""* nixpkgs.firefox (firefox-123.0)
  Mozilla Firefox web browser
  
* nixpkgs.firefox-esr (firefox-esr-115.0)  
  Mozilla Firefox ESR (Extended Support Release)
  
* nixpkgs.firefox-devedition (firefox-devedition-123.0)
  Mozilla Firefox Developer Edition""",
                stderr=''
            )
            
            with patch('builtins.print') as mock_print:
                self.assistant._handle_search("search firefox")
                
                # Should display formatted results
                assert mock_run.called
                # Check that results were printed (not exact format)
                assert mock_print.called
    
    def test_search_no_results(self):
        """Test handling when search returns no results"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='',  # No results
                stderr=''
            )
            
            with patch('builtins.print') as mock_print:
                self.assistant._handle_search("search nonexistentpackage12345")
                
                # Should indicate no results found
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any('no' in str(call).lower() or 'not found' in str(call).lower() 
                          for call in print_calls)
    
    def test_search_error_handling(self):
        """Test handling search command errors"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout='',
                stderr='error: unable to download'
            )
            
            with patch('builtins.print') as mock_print:
                self.assistant._handle_search("search firefox")
                
                # Should show error message
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any('error' in str(call).lower() for call in print_calls)
    
    def test_command_executor_search(self):
        """Test that command executor creates correct search command"""
        from luminous_nix.core.executor import CommandExecutor, CommandType
        
        executor = CommandExecutor()
        cmd = executor.create_command(CommandType.SEARCH, ['firefox'])
        
        # Should use nix search
        assert 'nix' in cmd.command
        assert 'search' in cmd.command
        assert 'nixpkgs' in cmd.command
        assert 'firefox' in cmd.command
        assert cmd.can_rollback == False  # Search shouldn't be rollbackable


class TestSearchIntegration:
    """Test search with intent recognition pipeline"""
    
    def test_intent_recognition_for_search(self):
        """Test that various search phrases are recognized"""
        pipeline = IntentRecognitionPipeline()
        
        test_phrases = [
            "search firefox",
            "find firefox",
            "look for firefox", 
            "search for a browser",
            "find me a text editor",
            "what packages are available for python"
        ]
        
        for phrase in test_phrases:
            result = pipeline.recognize(phrase)
            # Should recognize as search intent
            assert result.primary_intent == Intent.SEARCH, \
                f"Failed to recognize search intent in: {phrase}"
    
    def test_search_entities_extraction(self):
        """Test extracting search terms as entities"""
        pipeline = IntentRecognitionPipeline()
        
        result = pipeline.recognize("search for markdown editor")
        
        # Should extract search terms
        search_entities = [e for e in result.entities if e.type == 'query']
        assert len(search_entities) > 0 or \
               any('markdown' in e.value.lower() or 'editor' in e.value.lower() 
                   for e in result.entities)


if __name__ == "__main__":
    # Run the tests
    test_search = TestSearchCommand()
    test_search.setup_method()
    
    print("Testing search command...")
    test_search.test_basic_search_command()
    print("✅ Basic search command works")
    
    test_search.test_natural_language_search()
    print("✅ Natural language search works")
    
    test_search.test_search_without_query()
    print("✅ Error handling for missing query works")
    
    test_search.test_search_with_multiple_terms()
    print("✅ Multiple search terms work")
    
    test_search.test_search_result_parsing()
    print("✅ Search result parsing works")
    
    test_search.test_search_no_results()
    print("✅ No results handling works")
    
    test_search.test_search_error_handling()
    print("✅ Error handling works")
    
    test_search.test_command_executor_search()
    print("✅ Command executor search works")
    
    print("\nTesting search integration...")
    test_integration = TestSearchIntegration()
    
    test_integration.test_intent_recognition_for_search()
    print("✅ Intent recognition for search works")
    
    test_integration.test_search_entities_extraction()
    print("✅ Search entity extraction works")
    
    print("\n🎉 All search tests passed!")