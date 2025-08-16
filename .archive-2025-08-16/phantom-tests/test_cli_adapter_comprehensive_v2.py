#!/usr/bin/env python3
"""
Comprehensive CLI Adapter Tests v2

Tests the actual CLI adapter implementation from src/nix_for_humanity/adapters/cli_adapter.py
Goal: Achieve 95%+ coverage for this critical component
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import uuid
import io
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from nix_humanity.adapters.cli_adapter import CLIAdapter
from nix_humanity.core import (
    
    Response,
    PersonalityStyle
)


class TestCLIAdapterComprehensive(unittest.TestCase):
    """Comprehensive tests for CLIAdapter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the core engine to avoid system dependencies
        self.mock_core_patcher = patch('nix_for_humanity.adapters.cli_adapter.NixForHumanityBackend')
        self.mock_core_class = self.mock_core_patcher.start()
        self.mock_core = self.mock_core_class.return_value
        
        # Mock UUID generation for predictable session IDs
        self.mock_uuid_patcher = patch('nix_for_humanity.adapters.cli_adapter.uuid.uuid4')
        self.mock_uuid = self.mock_uuid_patcher.start()
        mock_uuid_obj = Mock()
        mock_uuid_obj.__str__ = Mock(return_value='test-session-id-12345678')
        self.mock_uuid.return_value = mock_uuid_obj
        
        # Create the adapter
        self.adapter = CLIAdapter()
        
    def tearDown(self):
        """Clean up test fixtures"""
        self.mock_core_patcher.stop()
        self.mock_uuid_patcher.stop()
        
    def test_initialization_default_config(self):
        """Test CLIAdapter initialization with default configuration"""
        # Verify core was initialized with correct config
        expected_config = {
            'dry_run': False,
            'default_personality': 'friendly', 
            'enable_learning': True,
            'collect_feedback': True
        }
        self.mock_core_class.assert_called_once_with(expected_config)
        
        # Verify session ID was generated (first 8 chars of UUID string)
        self.assertEqual(self.adapter.session_id, 'test-ses')  # 'test-session-id-12345678'[:8]
        
        # Verify CLI-specific settings
        self.assertTrue(self.adapter.show_progress)
        self.assertIsInstance(self.adapter.visual_mode, bool)
        
    def test_check_rich_available_with_rich(self):
        """Test _check_rich_available when Rich is available"""
        with patch('nix_for_humanity.adapters.cli_adapter.CLIAdapter._check_rich_available') as mock_check:
            mock_check.return_value = True
            adapter = CLIAdapter()
            self.assertTrue(adapter.visual_mode)
            
    def test_check_rich_available_without_rich(self):
        """Test _check_rich_available when Rich is not available"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'rich'")):
            adapter = CLIAdapter() 
            self.assertFalse(adapter.visual_mode)
            
    def test_process_query_default_parameters(self):
        """Test process_query with default parameters"""
        # Setup mock response
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        # Process query
        result = self.adapter.process_query("install firefox")
        
        # Verify query was created correctly
        self.mock_core.process.assert_called_once()
        query_arg = self.mock_core.process.call_args[0][0]
        
        self.assertEqual(query_arg.text, "install firefox")
        self.assertEqual(query_arg.personality, "friendly")
        self.assertEqual(query_arg.mode.EXECUTE)
        self.assertEqual(query_arg.session_id, 'test-ses')
        
        # Verify response is returned
        self.assertEqual(result, mock_response)
        
    def test_process_query_with_dry_run(self):
        """Test process_query with dry_run=True"""
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        result = self.adapter.process_query("remove firefox", dry_run=True)
        
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.mode.DRY_RUN)
        
    def test_process_query_with_explain_mode(self):
        """Test process_query with execute=False (explain mode)"""
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        result = self.adapter.process_query("update system", execute=False)
        
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.mode.EXPLAIN)
        
    def test_process_query_with_custom_personality(self):
        """Test process_query with custom personality"""
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        result = self.adapter.process_query("help", personality="technical")
        
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.personality, "technical")
        
    def test_process_query_with_show_intent(self):
        """Test process_query with show_intent=True"""
        # Mock intent engine
        mock_intent = Mock()
        mock_intent.type.value = "INSTALL"
        mock_intent.entities.get("package") == "firefox"
        self.mock_core.intent_engine.recognize.return_value = mock_intent
        
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = self.adapter.process_query("install firefox", show_intent=True)
            
        # Verify intent was displayed
        mock_print.assert_any_call("\n🎯 Intent detected: INSTALL")
        mock_print.assert_any_call("📦 Target: firefox")
        
    def test_process_query_show_intent_no_target(self):
        """Test process_query with show_intent=True but no target"""
        mock_intent = Mock()
        mock_intent.type.value = "HELP"
        mock_intent.entities.get("package") == None
        self.mock_core.intent_engine.recognize.return_value = mock_intent
        
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = self.adapter.process_query("help", show_intent=True)
            
        # Verify only intent type was displayed (no target)
        mock_print.assert_any_call("\n🎯 Intent detected: HELP")
        # Should not print target line
        target_calls = [call for call in mock_print.call_args_list if "📦 Target:" in str(call)]
        self.assertEqual(len(target_calls), 0)
        
    def test_get_user_id_with_env_var(self):
        """Test _get_user_id with USER environment variable"""
        with patch.dict(os.environ, {'USER': 'testuser'}):
            user_id = self.adapter._get_user_id()
            self.assertEqual(user_id, 'testuser')
            
    def test_get_user_id_without_env_var(self):
        """Test _get_user_id without USER environment variable"""
        with patch.dict(os.environ, {}, clear=True):
            user_id = self.adapter._get_user_id()
            self.assertEqual(user_id, 'anonymous')
            
    def test_display_response_simple_mode(self):
        """Test display_response in simple (non-Rich) mode"""
        self.adapter.visual_mode = False
        
        mock_response = Mock()
        mock_response.text = "Firefox installed successfully"
        mock_response.suggestions = ["Try: firefox --help", "See: man firefox"]
        mock_response.feedback_requested = False
        
        with patch('builtins.print') as mock_print:
            self.adapter.display_response(mock_response)
            
        # Verify main text was printed
        mock_print.assert_any_call("Firefox installed successfully")
        
        # Verify suggestions were printed
        mock_print.assert_any_call("\n💡 Suggestions:")
        mock_print.assert_any_call("   • Try: firefox --help")
        mock_print.assert_any_call("   • See: man firefox")
        
    def test_display_response_no_suggestions(self):
        """Test display_response with no suggestions"""
        self.adapter.visual_mode = False
        
        mock_response = Mock()
        mock_response.text = "Command executed"
        mock_response.suggestions = None
        mock_response.feedback_requested = False
        
        with patch('builtins.print') as mock_print:
            self.adapter.display_response(mock_response)
            
        # Verify only main text was printed
        mock_print.assert_called_once_with("Command executed")
        
    def test_display_response_with_feedback_request(self):
        """Test display_response with feedback request"""
        self.adapter.visual_mode = False
        
        mock_response = Mock()
        mock_response.text = "System updated"
        mock_response.suggestions = None
        mock_response.feedback_requested = True
        
        with patch('builtins.print') as mock_print:
            with patch.object(self.adapter, '_gather_feedback') as mock_gather:
                self.adapter.display_response(mock_response)
                
        # Verify feedback was gathered
        mock_gather.assert_called_once_with(mock_response)
        
    def test_display_rich_mode_success(self):
        """Test _display_rich with Rich available"""
        self.adapter.visual_mode = True
        
        # Mock Rich components at import level
        mock_console = Mock()
        mock_panel = Mock()
        mock_markdown = Mock()
        
        with patch('rich.console.Console', return_value=mock_console):
            with patch('rich.panel.Panel', return_value=mock_panel):
                with patch('rich.markdown.Markdown', return_value=mock_markdown):
                    
                    mock_response = Mock()
                    mock_response.text = "Test response"
                    mock_response.suggestions = ["Suggestion 1"]
                    mock_response.feedback_requested = False
                    
                    self.adapter._display_rich(mock_response)
                    
        # Verify Rich components were used
        mock_console.print.assert_called()
        
    def test_display_rich_mode_fallback(self):
        """Test _display_rich fallback to simple when Rich import fails"""
        self.adapter.visual_mode = True
        
        mock_response = Mock()
        mock_response.text = "Fallback test"
        mock_response.suggestions = None
        mock_response.feedback_requested = False
        
        with patch('rich.console.Console', side_effect=ImportError("Rich not available")):
            with patch.object(self.adapter, '_display_simple') as mock_simple:
                self.adapter._display_rich(mock_response)
                
        # Verify fallback to simple display
        mock_simple.assert_called_once_with(mock_response)
        
    def test_gather_feedback_helpful(self):
        """Test _gather_feedback with positive response"""
        mock_response = Mock()
        
        with patch('builtins.input', return_value='y'):
            with patch('builtins.print') as mock_print:
                self.adapter._gather_feedback(mock_response)
                
        # Verify positive feedback message
        mock_print.assert_any_call("Great! Thank you for the feedback.")
        
    def test_gather_feedback_not_helpful(self):
        """Test _gather_feedback with negative response"""
        mock_response = Mock()
        
        with patch('builtins.input', side_effect=['n', 'Need better explanations']):
            with patch('builtins.print') as mock_print:
                self.adapter._gather_feedback(mock_response)
                
        # Verify improvement request was handled
        mock_print.assert_any_call("Thank you! I'll use this to improve.")
        
    def test_gather_feedback_not_helpful_no_comment(self):
        """Test _gather_feedback with negative response but no improvement comment"""
        mock_response = Mock()
        
        with patch('builtins.input', side_effect=['n', '']):
            with patch('builtins.print') as mock_print:
                self.adapter._gather_feedback(mock_response)
                
        # Should handle empty improvement comment gracefully
        mock_print.assert_any_call("\nI'd love to learn how to help better!")
        
    def test_gather_feedback_skip(self):
        """Test _gather_feedback with skip response"""
        mock_response = Mock()
        
        with patch('builtins.input', return_value='skip'):
            with patch('builtins.print') as mock_print:
                self.adapter._gather_feedback(mock_response)
                
        # Should exit early without follow-up questions
        # Verify separator was printed but not feedback messages
        calls = mock_print.call_args_list
        separator_found = any('=' in str(call) for call in calls)
        self.assertTrue(separator_found)
        
    def test_gather_feedback_keyboard_interrupt(self):
        """Test _gather_feedback handles KeyboardInterrupt gracefully"""
        mock_response = Mock()
        
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            # Should not raise exception
            try:
                self.adapter._gather_feedback(mock_response)
            except KeyboardInterrupt:
                self.fail("_gather_feedback should handle KeyboardInterrupt")
                
    def test_set_personality_valid(self):
        """Test set_personality with valid style"""
        # Mock the personality system
        mock_personality_system = Mock()
        self.mock_core.personality_system = mock_personality_system
        
        self.adapter.set_personality("technical")
        
        # Verify personality was set
        mock_personality_system.set_style.assert_called_once()
        # The actual PersonalityStyle enum is called
        call_args = mock_personality_system.set_style.call_args[0][0]
        self.assertIsInstance(call_args, PersonalityStyle)
        
    def test_set_personality_invalid(self):
        """Test set_personality with invalid style"""
        # Mock the personality system to raise ValueError
        mock_personality_system = Mock()
        mock_personality_system.set_style.side_effect = ValueError("Invalid style")
        self.mock_core.personality_system = mock_personality_system
        
        with patch('builtins.print') as mock_print:
            self.adapter.set_personality("invalid_style")
            
        # Verify error message was printed
        mock_print.assert_called_once_with("Unknown personality style: invalid_style")
        
    def test_get_stats_simple_data(self):
        """Test get_stats with simple statistics"""
        mock_stats = {
            'queries_processed': 42,
            'success_rate': 0.95,
            'uptime': '2 hours'
        }
        self.mock_core.get_system_stats.return_value = mock_stats
        
        with patch('builtins.print') as mock_print:
            self.adapter.get_stats()
            
        # Verify stats were displayed
        mock_print.assert_any_call("\n📊 System Statistics")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("queries_processed: 42")
        mock_print.assert_any_call("success_rate: 0.95")
        mock_print.assert_any_call("uptime: 2 hours")
        
    def test_get_stats_nested_data(self):
        """Test get_stats with nested dictionary data"""
        mock_stats = {
            'performance': {
                'avg_response_time': '1.2s',
                'memory_usage': '150MB'
            },
            'learning': {
                'patterns_learned': 25,
                'feedback_count': 15
            },
            'total_queries': 100
        }
        self.mock_core.get_system_stats.return_value = mock_stats
        
        with patch('builtins.print') as mock_print:
            self.adapter.get_stats()
            
        # Verify nested stats were displayed correctly
        mock_print.assert_any_call("\nperformance:")
        mock_print.assert_any_call("  avg_response_time: 1.2s")
        mock_print.assert_any_call("  memory_usage: 150MB")
        mock_print.assert_any_call("\nlearning:")
        mock_print.assert_any_call("  patterns_learned: 25")
        mock_print.assert_any_call("  feedback_count: 15")
        mock_print.assert_any_call("total_queries: 100")


class TestCLIAdapterEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_core_patcher = patch('nix_for_humanity.adapters.cli_adapter.NixForHumanityBackend')
        self.mock_core_class = self.mock_core_patcher.start()
        self.mock_core = self.mock_core_class.return_value
        
        self.adapter = CLIAdapter()
        
    def tearDown(self):
        """Clean up test fixtures"""
        self.mock_core_patcher.stop()
        
    def test_empty_query(self):
        """Test process_query with empty string"""
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        result = self.adapter.process_query("")
        
        # Should handle empty query gracefully
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.text, "")
        
    def test_whitespace_only_query(self):
        """Test process_query with whitespace-only string"""
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        result = self.adapter.process_query("   \t\n  ")
        
        # Should pass whitespace through to core
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.text, "   \t\n  ")
        
    def test_very_long_query(self):
        """Test process_query with very long input"""
        long_query = "install " + "firefox " * 1000 + "please"
        
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        result = self.adapter.process_query(long_query)
        
        # Should handle long queries
        self.assertEqual(result, mock_response)
        
    def test_unicode_query(self):
        """Test process_query with unicode characters"""
        unicode_query = "install café 🔥 ñoël"
        
        mock_response = Mock(spec=Response)
        self.mock_core.process.return_value = mock_response
        
        result = self.adapter.process_query(unicode_query)
        
        # Should handle unicode gracefully
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.text, unicode_query)
        
    def test_response_with_empty_suggestions(self):
        """Test display_response with empty suggestions list"""
        self.adapter.visual_mode = False
        
        mock_response = Mock()
        mock_response.text = "No suggestions"
        mock_response.suggestions = []  # Empty list
        mock_response.feedback_requested = False
        
        with patch('builtins.print') as mock_print:
            self.adapter.display_response(mock_response)
            
        # Should not print suggestions section for empty list
        suggestion_calls = [call for call in mock_print.call_args_list if "💡 Suggestions:" in str(call)]
        self.assertEqual(len(suggestion_calls), 0)
        
    def test_core_initialization_failure(self):
        """Test handling of core initialization failure"""
        with patch('nix_for_humanity.adapters.cli_adapter.NixForHumanityBackend', side_effect=Exception("Core init failed")):
            with self.assertRaises(Exception):
                adapter = CLIAdapter()
                
    def test_stats_with_none_values(self):
        """Test get_stats with None values in data"""
        mock_stats = {
            'valid_key': 'valid_value',
            'none_key': None,
            'nested': {
                'valid_nested': 'value',
                'none_nested': None
            }
        }
        self.mock_core.get_system_stats.return_value = mock_stats
        
        with patch('builtins.print') as mock_print:
            self.adapter.get_stats()
            
        # Should handle None values gracefully
        mock_print.assert_any_call("valid_key: valid_value")
        mock_print.assert_any_call("none_key: None")
        
    def test_personality_style_enum_conversion(self):
        """Test PersonalityStyle enum handling"""
        mock_personality_system = Mock()
        self.mock_core.personality_system = mock_personality_system
        
        # Test all valid personality styles
        valid_styles = ['minimal', 'friendly', 'encouraging', 'technical', 'symbiotic']
        
        for style in valid_styles:
            with self.subTest(style=style):
                self.adapter.set_personality(style)
                # Should not raise exception
                mock_personality_system.set_style.assert_called()


class TestCLIAdapterIntegration(unittest.TestCase):
    """Integration-style tests without mocking core completely"""
    
    def setUp(self):
        """Set up minimal fixtures"""
        # Only mock the actual NixOS execution, not the whole core
        self.adapter = CLIAdapter()
        
    def test_query_object_construction(self):
        """Test that Query objects are constructed correctly"""
        with patch.object(self.adapter.core, 'process') as mock_process:
            mock_process.return_value = Mock(spec=Response)
            
            self.adapter.process_query(
                query_text="install vim",
                personality="technical", 
                dry_run=True,
                show_intent=False
            )
            
            # Verify Query object was created with correct attributes
            query_arg = mock_process.call_args[0][0]
            self.assertIsInstance(query_arg)
            self.assertEqual(query_arg.text, "install vim")
            self.assertEqual(query_arg.personality, "technical")
            self.assertEqual(query_arg.mode.DRY_RUN)
            self.assertIsNotNone(query_arg.session_id)
            self.assertIsNotNone(query_arg.user_id)
            
    def test_session_consistency(self):
        """Test that session ID remains consistent across queries"""
        session_id = self.adapter.session_id
        
        with patch.object(self.adapter.core, 'process') as mock_process:
            mock_process.return_value = Mock(spec=Response)
            
            # Process multiple queries
            self.adapter.process_query("install firefox")
            self.adapter.process_query("remove firefox")
            self.adapter.process_query("help")
            
            # Verify all queries used same session ID
            for call in mock_process.call_args_list:
                query_arg = call[0][0]
                self.assertEqual(query_arg.session_id, session_id)


if __name__ == '__main__':
    unittest.main()