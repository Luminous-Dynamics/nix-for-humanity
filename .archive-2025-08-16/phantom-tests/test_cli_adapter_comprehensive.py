#!/usr/bin/env python3
"""
Comprehensive unit tests for the CLI Adapter (src/nix_for_humanity/adapters/cli_adapter.py)
Target: 95%+ coverage for the actual CLI adapter being measured

Following test philosophy: Test behavior at boundaries, implementation at core.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock, call, Mock
import os
import sys
from pathlib import Path
import uuid
import io
from contextlib import redirect_stdout, redirect_stderr

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Import the CLI adapter that needs coverage (the one under src/)
from luminous_nix.adapters.cli_adapter import CLIAdapter


# Mock classes to avoid core dependencies
class MockQuery:
    def __init__(self, text="", personality="friendly", mode=None, session_id="", user_id=""):
        self.text = text
        self.personality = personality
        self.mode = mode
        self.session_id = session_id
        self.user_id = user_id


class MockResponse:
    def __init__(self, text="", suggestions=None, feedback_requested=False):
        self.text = text
        self.suggestions = suggestions or []
        self.feedback_requested = feedback_requested


class MockIntent:
    def __init__(self, type_value="help", target=None):
        self.type = Mock()
        self.type.value = type_value
        self.target = target


class MockExecutionMode:
    DRY_RUN = "dry_run"
    EXECUTE = "execute"
    EXPLAIN = "explain"


class MockPersonalityStyle:
    def __init__(self, style):
        self.style = style


class TestCLIAdapter(unittest.TestCase):
    """Comprehensive tests for the CLI Adapter - targeting 95%+ coverage"""
    
    def setUp(self):
        """Set up test fixtures with mocked dependencies"""
        # Mock all the core dependencies
        self.mock_core_patcher = patch('nix_for_humanity.adapters.cli_adapter.NixForHumanityBackend')
        self.mock_query_patcher = patch('nix_for_humanity.adapters.cli_adapter.Query', MockQuery)
        self.mock_execution_mode_patcher = patch('nix_for_humanity.adapters.cli_adapter.ExecutionMode', MockExecutionMode)
        self.mock_personality_style_patcher = patch('nix_for_humanity.adapters.cli_adapter.PersonalityStyle', MockPersonalityStyle)
        self.mock_uuid_patcher = patch('nix_for_humanity.adapters.cli_adapter.uuid')
        
        # Start all patches
        self.mock_core_class = self.mock_core_patcher.start()
        self.mock_query_patcher.start()
        self.mock_execution_mode_patcher.start()
        self.mock_personality_style_patcher.start()
        self.mock_uuid = self.mock_uuid_patcher.start()
        
        # Set up mock core instance
        self.mock_core = MagicMock()
        self.mock_core_class.return_value = self.mock_core
        
        # Set up mock UUID - fix the slicing behavior
        mock_uuid_obj = Mock()
        mock_uuid_obj.__str__ = Mock(return_value='abcd1234-5678-9012-3456-789012345678')
        self.mock_uuid.uuid4.return_value = mock_uuid_obj
        
        # Create adapter
        self.adapter = CLIAdapter()
    
    def tearDown(self):
        """Clean up patches"""
        self.mock_core_patcher.stop()
        self.mock_query_patcher.stop()
        self.mock_execution_mode_patcher.stop()
        self.mock_personality_style_patcher.stop()
        self.mock_uuid_patcher.stop()
    
    def test_initialization(self):
        """Test CLIAdapter initialization"""
        # Verify core was initialized with correct config
        self.mock_core_class.assert_called_once_with({
            'dry_run': False,
            'default_personality': 'friendly',
            'enable_learning': True,
            'collect_feedback': True
        })
        
        # Verify session ID is set (mocked to return first 8 chars)
        self.assertEqual(self.adapter.session_id, 'abcd1234')
        
        # Verify other attributes
        self.assertTrue(self.adapter.show_progress)
        self.assertIsInstance(self.adapter.visual_mode, bool)
    
    def test_check_rich_available_true(self):
        """Test rich library availability check when available"""
        with patch('builtins.__import__') as mock_import:
            # Create fresh adapter to test the rich check
            adapter = CLIAdapter()
            # Should not raise ImportError
            result = adapter._check_rich_available()
            self.assertIsInstance(result, bool)
    
    def test_check_rich_available_false(self):
        """Test rich library availability check when not available"""
        with patch('builtins.__import__', side_effect=ImportError):
            adapter = CLIAdapter()
            result = adapter._check_rich_available()
            self.assertFalse(result)
    
    def test_get_user_id_with_user_env(self):
        """Test user ID retrieval with USER environment variable"""
        with patch.dict(os.environ, {'USER': 'testuser'}):
            user_id = self.adapter._get_user_id()
            self.assertEqual(user_id, 'testuser')
    
    def test_get_user_id_without_user_env(self):
        """Test user ID retrieval without USER environment variable"""
        with patch.dict(os.environ, {}, clear=True):
            user_id = self.adapter._get_user_id()
            self.assertEqual(user_id, 'anonymous')
    
    def test_process_query_dry_run_mode(self):
        """Test processing query with dry_run=True"""
        mock_response = MockResponse("Dry run response")
        self.mock_core.process.return_value = mock_response
        
        response = self.adapter.process_query("test query", dry_run=True)
        
        # Verify query was created with correct mode
        self.mock_core.process.assert_called_once()
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.text, "test query")
        self.assertEqual(query_arg.mode, "dry_run")
        self.assertEqual(query_arg.personality, "friendly")
        self.assertEqual(query_arg.session_id, 'abcd1234')
    
    def test_process_query_execute_mode(self):
        """Test processing query with execute=True"""
        mock_response = MockResponse("Execute response")
        self.mock_core.process.return_value = mock_response
        
        response = self.adapter.process_query("test query", execute=True)
        
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.mode, "execute")
    
    def test_process_query_explain_mode(self):
        """Test processing query with execute=False, dry_run=False"""
        mock_response = MockResponse("Explain response")
        self.mock_core.process.return_value = mock_response
        
        response = self.adapter.process_query("test query", execute=False, dry_run=False)
        
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.mode, "explain")
    
    def test_process_query_custom_personality(self):
        """Test processing query with custom personality"""
        mock_response = MockResponse("Custom personality response")
        self.mock_core.process.return_value = mock_response
        
        response = self.adapter.process_query("test query", personality="technical")
        
        query_arg = self.mock_core.process.call_args[0][0]
        self.assertEqual(query_arg.personality, "technical")
    
    def test_process_query_with_show_intent(self):
        """Test processing query with show_intent=True"""
        mock_intent = MockIntent("install_package", "firefox")
        self.mock_core.intent_engine.recognize.return_value = mock_intent
        mock_response = MockResponse("Install response")
        self.mock_core.process.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            response = self.adapter.process_query("install firefox", show_intent=True)
        
        # Verify intent was recognized and displayed
        self.mock_core.intent_engine.recognize.assert_called_once_with("install firefox")
        mock_print.assert_any_call("\n🎯 Intent detected: install")
        mock_print.assert_any_call("📦 Target: firefox")
    
    def test_process_query_show_intent_no_target(self):
        """Test show_intent with intent that has no target"""
        mock_intent = MockIntent("help", None)
        self.mock_core.intent_engine.recognize.return_value = mock_intent
        mock_response = MockResponse("Help response")
        self.mock_core.process.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            response = self.adapter.process_query("help", show_intent=True)
        
        # Verify only intent type was printed, not target
        mock_print.assert_any_call("\n🎯 Intent detected: help")
        # Should not print target line
        target_calls = [call for call in mock_print.call_args_list if "Target:" in str(call)]
        self.assertEqual(len(target_calls), 0)
    
    def test_display_response_simple_mode(self):
        """Test displaying response in simple mode"""
        self.adapter.visual_mode = False
        mock_response = MockResponse("Simple response", ["suggestion1", "suggestion2"])
        
        with patch('builtins.print') as mock_print:
            self.adapter.display_response(mock_response)
        
        mock_print.assert_any_call("Simple response")
        mock_print.assert_any_call("\n💡 Suggestions:")
        mock_print.assert_any_call("   • suggestion1")
        mock_print.assert_any_call("   • suggestion2")
    
    def test_display_response_rich_mode_success(self):
        """Test displaying response in rich mode when rich is available"""
        self.adapter.visual_mode = True
        mock_response = MockResponse("Rich response", ["suggestion1"])
        
        # Mock rich components at import level
        with patch('builtins.__import__') as mock_import:
            # Mock the imports that happen inside _display_rich
            mock_console_class = Mock()
            mock_panel_class = Mock()
            mock_markdown_class = Mock()
            mock_console_instance = Mock()
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'rich.console':
                    console_module = Mock()
                    console_module.Console = mock_console_class
                    return console_module
                elif name == 'rich.panel':
                    panel_module = Mock()
                    panel_module.Panel = mock_panel_class
                    return panel_module
                elif name == 'rich.markdown':
                    markdown_module = Mock()
                    markdown_module.Markdown = mock_markdown_class
                    return markdown_module
                else:
                    # Use the real import for other modules
                    return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            mock_console_class.return_value = mock_console_instance
            
            self.adapter._display_rich(mock_response)
            
            # Verify rich components were used
            mock_console_class.assert_called_once()
            mock_panel_class.assert_called_once()
            mock_markdown_class.assert_called_once_with("Rich response")
            mock_console_instance.print.assert_called()
    
    def test_display_response_rich_mode_fallback(self):
        """Test rich mode falling back to simple when import fails"""
        self.adapter.visual_mode = True
        mock_response = MockResponse("Fallback response")
        
        # Mock import error for rich
        with patch('builtins.__import__', side_effect=ImportError):
            with patch.object(self.adapter, '_display_simple') as mock_simple:
                self.adapter._display_rich(mock_response)
                mock_simple.assert_called_once_with(mock_response)
    
    def test_display_simple_no_suggestions(self):
        """Test simple display without suggestions"""
        mock_response = MockResponse("Simple response", [])
        
        with patch('builtins.print') as mock_print:
            self.adapter._display_simple(mock_response)
        
        mock_print.assert_called_with("Simple response")
        # Should not print suggestions section
        suggestion_calls = [call for call in mock_print.call_args_list if "Suggestions:" in str(call)]
        self.assertEqual(len(suggestion_calls), 0)
    
    def test_display_simple_with_feedback_request(self):
        """Test simple display with feedback request"""
        mock_response = MockResponse("Response with feedback", [], feedback_requested=True)
        
        with patch.object(self.adapter, '_gather_feedback') as mock_feedback:
            with patch('builtins.print'):
                self.adapter._display_simple(mock_response)
        
        mock_feedback.assert_called_once_with(mock_response)
    
    def test_gather_feedback_yes(self):
        """Test gathering positive feedback"""
        mock_response = MockResponse("Test response")
        
        with patch('builtins.input', return_value='y'):
            with patch('builtins.print') as mock_print:
                self.adapter._gather_feedback(mock_response)
        
        mock_print.assert_any_call("Great! Thank you for the feedback.")
    
    def test_gather_feedback_yes_verbose(self):
        """Test gathering positive feedback with 'yes'"""
        mock_response = MockResponse("Test response")
        
        with patch('builtins.input', return_value='yes'):
            with patch('builtins.print') as mock_print:
                self.adapter._gather_feedback(mock_response)
        
        mock_print.assert_any_call("Great! Thank you for the feedback.")
    
    def test_gather_feedback_no_with_comment(self):
        """Test gathering negative feedback with improvement comment"""
        mock_response = MockResponse("Test response")
        
        with patch('builtins.input', side_effect=['n', 'Better explanation needed']):
            with patch('builtins.print') as mock_print:
                self.adapter._gather_feedback(mock_response)
        
        mock_print.assert_any_call("\nI'd love to learn how to help better!")
        mock_print.assert_any_call("Thank you! I'll use this to improve.")
    
    def test_gather_feedback_no_without_comment(self):
        """Test gathering negative feedback without improvement comment"""
        mock_response = MockResponse("Test response")
        
        with patch('builtins.input', side_effect=['no', '']):
            with patch('builtins.print') as mock_print:
                self.adapter._gather_feedback(mock_response)
        
        mock_print.assert_any_call("\nI'd love to learn how to help better!")
        # Should not print thank you message when no comment
        thank_calls = [call for call in mock_print.call_args_list if "Thank you!" in str(call)]
        self.assertEqual(len(thank_calls), 0)
    
    def test_gather_feedback_keyboard_interrupt(self):
        """Test handling keyboard interrupt during feedback"""
        mock_response = MockResponse("Test response")
        
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            # Should not raise exception
            self.adapter._gather_feedback(mock_response)
    
    def test_set_personality_valid(self):
        """Test setting valid personality style"""
        mock_personality_system = Mock()
        self.mock_core.personality_system = mock_personality_system
        
        self.adapter.set_personality('minimal')
        
        # Verify personality system was called
        mock_personality_system.set_style.assert_called_once()
    
    def test_set_personality_invalid(self):
        """Test setting invalid personality style"""
        mock_personality_system = Mock()
        mock_personality_system.set_style.side_effect = ValueError
        self.mock_core.personality_system = mock_personality_system
        
        with patch('builtins.print') as mock_print:
            self.adapter.set_personality('invalid_style')
        
        mock_print.assert_called_with("Unknown personality style: invalid_style")
    
    def test_get_stats_simple_dict(self):
        """Test getting and displaying simple statistics"""
        mock_stats = {
            'queries_processed': 42,
            'uptime': '2 hours',
            'cache_size': '150MB'
        }
        self.mock_core.get_system_stats.return_value = mock_stats
        
        with patch('builtins.print') as mock_print:
            self.adapter.get_stats()
        
        # Verify stats header
        mock_print.assert_any_call("\n📊 System Statistics")
        mock_print.assert_any_call("=" * 50)
        
        # Verify stats display
        mock_print.assert_any_call("queries_processed: 42")
        mock_print.assert_any_call("uptime: 2 hours")
        mock_print.assert_any_call("cache_size: 150MB")
    
    def test_get_stats_nested_dict(self):
        """Test displaying nested statistics"""
        mock_stats = {
            'basic_stats': {
                'queries': 100,
                'errors': 2
            },
            'performance': {
                'avg_response_time': '1.2s',
                'cache_hits': '85%'
            },
            'simple_stat': 'simple_value'
        }
        self.mock_core.get_system_stats.return_value = mock_stats
        
        with patch('builtins.print') as mock_print:
            self.adapter.get_stats()
        
        # Verify nested stats display
        mock_print.assert_any_call("\nbasic_stats:")
        mock_print.assert_any_call("  queries: 100")
        mock_print.assert_any_call("  errors: 2")
        mock_print.assert_any_call("\nperformance:")
        mock_print.assert_any_call("  avg_response_time: 1.2s")
        mock_print.assert_any_call("  cache_hits: 85%")
        mock_print.assert_any_call("simple_stat: simple_value")
    
    def test_display_response_calls_appropriate_method(self):
        """Test that display_response calls the right display method"""
        mock_response = MockResponse("Test response")
        
        # Test visual mode
        self.adapter.visual_mode = True
        with patch.object(self.adapter, '_display_rich') as mock_rich:
            self.adapter.display_response(mock_response)
            mock_rich.assert_called_once_with(mock_response)
        
        # Test simple mode
        self.adapter.visual_mode = False
        with patch.object(self.adapter, '_display_simple') as mock_simple:
            self.adapter.display_response(mock_response)
            mock_simple.assert_called_once_with(mock_response)
    
    def test_rich_display_with_feedback(self):
        """Test rich display with feedback request"""
        self.adapter.visual_mode = True
        mock_response = MockResponse("Rich response", feedback_requested=True)
        
        with patch('builtins.__import__') as mock_import:
            # Mock the imports
            mock_console_class = Mock()
            mock_panel_class = Mock()
            mock_markdown_class = Mock()
            mock_console_instance = Mock()
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'rich.console':
                    console_module = Mock()
                    console_module.Console = mock_console_class
                    return console_module
                elif name == 'rich.panel':
                    panel_module = Mock()
                    panel_module.Panel = mock_panel_class
                    return panel_module
                elif name == 'rich.markdown':
                    markdown_module = Mock()
                    markdown_module.Markdown = mock_markdown_class
                    return markdown_module
                else:
                    return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            mock_console_class.return_value = mock_console_instance
            
            with patch.object(self.adapter, '_gather_feedback') as mock_feedback:
                self.adapter._display_rich(mock_response)
                
                # Verify feedback was called
                mock_feedback.assert_called_once_with(mock_response)
    
    def test_rich_display_suggestions(self):
        """Test rich display with suggestions"""
        self.adapter.visual_mode = True
        mock_response = MockResponse("Response", ["suggestion1", "suggestion2"])
        
        with patch('builtins.__import__') as mock_import:
            # Mock the imports
            mock_console_class = Mock()
            mock_panel_class = Mock()
            mock_markdown_class = Mock()
            mock_console_instance = Mock()
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'rich.console':
                    console_module = Mock()
                    console_module.Console = mock_console_class
                    return console_module
                elif name == 'rich.panel':
                    panel_module = Mock()
                    panel_module.Panel = mock_panel_class
                    return panel_module
                elif name == 'rich.markdown':
                    markdown_module = Mock()
                    markdown_module.Markdown = mock_markdown_class
                    return markdown_module
                else:
                    return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            mock_console_class.return_value = mock_console_instance
            
            self.adapter._display_rich(mock_response)
            
            # Verify suggestions were printed
            print_calls = [str(call) for call in mock_console_instance.print.call_args_list]
            suggestion_calls = [call for call in print_calls if "Suggestions:" in call]
            self.assertTrue(len(suggestion_calls) > 0)


class TestCLIAdapterEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up with minimal mocking for edge case testing"""
        with patch('nix_for_humanity.adapters.cli_adapter.NixForHumanityBackend'):
            with patch('nix_for_humanity.adapters.cli_adapter.Query', MockQuery):
                with patch('nix_for_humanity.adapters.cli_adapter.ExecutionMode', MockExecutionMode):
                    with patch('nix_for_humanity.adapters.cli_adapter.PersonalityStyle', MockPersonalityStyle):
                        with patch('nix_for_humanity.adapters.cli_adapter.uuid'):
                            self.adapter = CLIAdapter()
    
    def test_empty_suggestions_list(self):
        """Test handling empty suggestions list"""
        mock_response = MockResponse("Response", [])
        
        with patch('builtins.print') as mock_print:
            self.adapter._display_simple(mock_response)
        
        # Should only print response text, no suggestions section
        calls = [str(call) for call in mock_print.call_args_list]
        suggestion_calls = [call for call in calls if "Suggestions:" in call]
        self.assertEqual(len(suggestion_calls), 0)
    
    def test_none_suggestions(self):
        """Test handling None suggestions"""
        mock_response = MockResponse("Response", None)
        
        with patch('builtins.print') as mock_print:
            self.adapter._display_simple(mock_response)
        
        # Should handle None gracefully
        mock_print.assert_called_with("Response")
    
    def test_feedback_skip_variations(self):
        """Test various ways to skip feedback"""
        mock_response = MockResponse("Test")
        
        skip_inputs = ['skip', 'SKIP', 'Skip', 's', 'q', 'quit', 'other']
        
        for skip_input in skip_inputs:
            with patch('builtins.input', return_value=skip_input):
                with patch('builtins.print') as mock_print:
                    self.adapter._gather_feedback(mock_response)
                    
                    # Only 'skip' should be recognized as skip command
                    if skip_input.lower() == 'skip':
                        # Should only print separator, not feedback messages
                        calls = [str(call) for call in mock_print.call_args_list]
                        feedback_calls = [call for call in calls if "Thank you" in call or "help better" in call]
                        self.assertEqual(len(feedback_calls), 0)


if __name__ == '__main__':
    unittest.main()