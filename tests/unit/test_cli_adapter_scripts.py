#!/usr/bin/env python3
"""
Comprehensive tests for CLI Adapter in scripts/adapters/cli_adapter.py

Tests all functionality including:
- Server and embedded mode
- Query processing
- Interactive session
- Feedback collection
- Error handling
- Special commands
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
from typing import Dict, Any

# Add scripts directory to path
scripts_dir = os.path.join(os.path.dirname(__file__), '../../scripts')
sys.path.insert(0, scripts_dir)

from adapters.cli_adapter import CLIAdapter, main, Context


class TestCLIAdapter(unittest.TestCase):
    """Test the CLIAdapter class."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock HeadlessEngine and JSONRPCClient
        self.mock_engine = Mock()
        self.mock_client = Mock()
        
        # Create test context
        self.context = Mock(spec=Context)
        self.context.user_id = "test_user"
        self.context.session_id = "test_session"
        self.context.personality = "friendly"
        self.context.capabilities = ['text', 'visual']
        self.context.execution_mode = "dry_run"
        self.context.collect_feedback = True
    
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_init_embedded_mode(self, mock_engine_class):
        """Test initialization in embedded mode."""
        adapter = CLIAdapter(use_server=False)
        
        mock_engine_class.assert_called_once()
        self.assertIsNotNone(adapter.engine)
        self.assertIsNone(adapter.client)
        self.assertFalse(adapter.use_server)
    
    @patch('adapters.cli_adapter.JSONRPCClient')
    def test_init_server_mode_unix_socket(self, mock_client_class):
        """Test initialization with Unix socket server."""
        adapter = CLIAdapter(use_server=True, server_address="/tmp/test.sock")
        
        mock_client_class.assert_called_once_with(socket_path="/tmp/test.sock")
        self.assertIsNone(adapter.engine)
        self.assertIsNotNone(adapter.client)
        self.assertTrue(adapter.use_server)
    
    @patch('adapters.cli_adapter.JSONRPCClient')
    def test_init_server_mode_tcp(self, mock_client_class):
        """Test initialization with TCP server."""
        adapter = CLIAdapter(use_server=True, server_address="tcp://localhost:9999")
        
        mock_client_class.assert_called_once_with(tcp_port=9999)
        self.assertIsNone(adapter.engine)
        self.assertIsNotNone(adapter.client)
        self.assertTrue(adapter.use_server)
    
    @patch('adapters.cli_adapter.JSONRPCClient')
    def test_init_server_mode_default(self, mock_client_class):
        """Test initialization with default server settings."""
        adapter = CLIAdapter(use_server=True)
        
        mock_client_class.assert_called_once_with(socket_path="/tmp/nix-for-humanity.sock")
    
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_process_query_embedded_mode(self, mock_engine_class):
        """Test query processing in embedded mode."""
        # Set up mocks
        mock_engine = Mock()
        mock_response = Mock()
        mock_response.to_dict.return_value = {
            'text': 'Installing Firefox...',
            'commands': ['nix-env -iA nixpkgs.firefox']
        }
        mock_engine.process.return_value = mock_response
        mock_engine_class.return_value = mock_engine
        
        # Create adapter and process query
        adapter = CLIAdapter(use_server=False)
        result = adapter.process_query("install firefox", self.context)
        
        # Verify
        mock_engine.process.assert_called_once_with("install firefox", self.context)
        self.assertEqual(result['text'], 'Installing Firefox...')
        self.assertEqual(result['commands'], ['nix-env -iA nixpkgs.firefox'])
    
    @patch('adapters.cli_adapter.JSONRPCClient')
    def test_process_query_server_mode(self, mock_client_class):
        """Test query processing in server mode."""
        # Set up mocks
        mock_client = Mock()
        mock_client.call.return_value = {
            'text': 'Installing Firefox...',
            'commands': ['nix-env -iA nixpkgs.firefox']
        }
        mock_client_class.return_value = mock_client
        
        # Create adapter and process query
        adapter = CLIAdapter(use_server=True)
        result = adapter.process_query("install firefox", self.context)
        
        # Verify
        expected_params = {
            'input': 'install firefox',
            'context': {
                'user_id': self.context.user_id,
                'session_id': self.context.session_id,
                'personality': self.context.personality,
                'capabilities': self.context.capabilities,
                'execution_mode': self.context.execution_mode.value,
                'collect_feedback': self.context.collect_feedback
            }
        }
        mock_client.call.assert_called_once_with('process', expected_params)
        self.assertEqual(result['text'], 'Installing Firefox...')
    
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_collect_feedback_embedded_mode(self, mock_engine_class):
        """Test feedback collection in embedded mode."""
        # Set up mocks
        mock_engine = Mock()
        mock_engine.collect_feedback.return_value = True
        mock_engine_class.return_value = mock_engine
        
        # Create adapter and collect feedback
        adapter = CLIAdapter(use_server=False)
        feedback = {'rating': 5, 'helpful': True}
        result = adapter.collect_feedback("test_session", feedback)
        
        # Verify
        mock_engine.collect_feedback.assert_called_once_with("test_session", feedback)
        self.assertTrue(result)
    
    @patch('adapters.cli_adapter.JSONRPCClient')
    def test_collect_feedback_server_mode(self, mock_client_class):
        """Test feedback collection in server mode."""
        # Set up mocks
        mock_client = Mock()
        mock_client.call.return_value = {'success': True}
        mock_client_class.return_value = mock_client
        
        # Create adapter and collect feedback
        adapter = CLIAdapter(use_server=True)
        feedback = {'rating': 5, 'helpful': True}
        result = adapter.collect_feedback("test_session", feedback)
        
        # Verify
        expected_params = {
            'session_id': 'test_session',
            'feedback': feedback
        }
        mock_client.call.assert_called_once_with('collect_feedback', expected_params)
        self.assertTrue(result)
    
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_get_stats_embedded_mode(self, mock_engine_class):
        """Test getting statistics in embedded mode."""
        # Set up mocks
        mock_engine = Mock()
        mock_engine.get_stats.return_value = {'queries': 10, 'users': 5}
        mock_engine_class.return_value = mock_engine
        
        # Create adapter and get stats
        adapter = CLIAdapter(use_server=False)
        stats = adapter.get_stats()
        
        # Verify
        mock_engine.get_stats.assert_called_once()
        self.assertEqual(stats['queries'], 10)
        self.assertEqual(stats['users'], 5)
    
    @patch('adapters.cli_adapter.JSONRPCClient')
    def test_get_stats_server_mode(self, mock_client_class):
        """Test getting statistics in server mode."""
        # Set up mocks
        mock_client = Mock()
        mock_client.call.return_value = {'queries': 10, 'users': 5}
        mock_client_class.return_value = mock_client
        
        # Create adapter and get stats
        adapter = CLIAdapter(use_server=True)
        stats = adapter.get_stats()
        
        # Verify
        mock_client.call.assert_called_once_with('get_stats')
        self.assertEqual(stats['queries'], 10)
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_run_interactive_exit_commands(self, mock_engine_class, mock_print, mock_input):
        """Test interactive mode with exit commands."""
        mock_engine_class.return_value = Mock()
        
        # Test various exit commands
        for exit_cmd in ['exit', 'quit', 'q']:
            with self.subTest(command=exit_cmd):
                mock_input.side_effect = [exit_cmd]
                mock_print.reset_mock()
                
                adapter = CLIAdapter(use_server=False)
                adapter.run_interactive(self.context)
                
                # Verify goodbye message
                mock_print.assert_any_call("👋 Goodbye!")
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_run_interactive_help_command(self, mock_engine_class, mock_print, mock_input):
        """Test interactive mode with help command."""
        mock_engine_class.return_value = Mock()
        mock_input.side_effect = ['help', 'exit']
        
        adapter = CLIAdapter(use_server=False)
        adapter.run_interactive(self.context)
        
        # Verify help was shown
        help_shown = any('Available commands:' in str(call) for call in mock_print.call_args_list)
        self.assertTrue(help_shown)
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_run_interactive_stats_command(self, mock_engine_class, mock_print, mock_input):
        """Test interactive mode with stats command."""
        mock_engine = Mock()
        mock_engine.get_stats.return_value = {'queries': 10, 'users': 5}
        mock_engine_class.return_value = mock_engine
        mock_input.side_effect = ['stats', 'exit']
        
        adapter = CLIAdapter(use_server=False)
        adapter.run_interactive(self.context)
        
        # Verify stats were shown
        stats_shown = any('📊 Stats:' in str(call) for call in mock_print.call_args_list)
        self.assertTrue(stats_shown)
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_run_interactive_query_processing(self, mock_engine_class, mock_print, mock_input):
        """Test interactive mode with regular query."""
        # Set up mocks
        mock_engine = Mock()
        mock_response = Mock()
        mock_response.to_dict.return_value = {
            'text': 'Installing Firefox...',
            'commands': ['nix-env -iA nixpkgs.firefox'],
            'feedback_request': {
                'prompt': 'Was this helpful?',
                'options': ['yes', 'no']
            }
        }
        mock_engine.process.return_value = mock_response
        mock_engine_class.return_value = mock_engine
        mock_input.side_effect = ['install firefox', '', 'exit']  # Empty for feedback skip
        
        adapter = CLIAdapter(use_server=False)
        adapter.run_interactive(self.context)
        
        # Verify response was shown
        mock_print.assert_any_call('\nInstalling Firefox...\n')
        mock_print.assert_any_call('📦 Commands:')
        mock_print.assert_any_call('  $ nix-env -iA nixpkgs.firefox')
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_run_interactive_keyboard_interrupt(self, mock_engine_class, mock_print, mock_input):
        """Test interactive mode with keyboard interrupt."""
        mock_engine_class.return_value = Mock()
        mock_input.side_effect = KeyboardInterrupt()
        
        adapter = CLIAdapter(use_server=False)
        adapter.run_interactive(self.context)
        
        # Verify goodbye message
        mock_print.assert_any_call("\n👋 Goodbye!")
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_run_interactive_error_handling(self, mock_engine_class, mock_print, mock_input):
        """Test interactive mode error handling."""
        mock_engine = Mock()
        mock_engine.process.side_effect = Exception("Test error")
        mock_engine_class.return_value = mock_engine
        mock_input.side_effect = ['test query', 'exit']
        
        adapter = CLIAdapter(use_server=False)
        adapter.run_interactive(self.context)
        
        # Verify error was shown
        error_shown = any('❌ Error: Test error' in str(call) for call in mock_print.call_args_list)
        self.assertTrue(error_shown)
    
    def test_choice_to_rating(self):
        """Test feedback choice to rating conversion."""
        adapter = CLIAdapter(use_server=False)
        
        test_cases = [
            ('perfect', 5),
            ('yes', 4),
            ('helpful', 4),
            ('partially helpful', 3),
            ('no', 2),
            ('not helpful', 1),
            ('unknown', 3)  # Default
        ]
        
        for choice, expected_rating in test_cases:
            with self.subTest(choice=choice):
                rating = adapter._choice_to_rating(choice)
                self.assertEqual(rating, expected_rating)
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_collect_feedback_interaction(self, mock_engine_class, mock_print, mock_input):
        """Test feedback collection interaction."""
        mock_engine = Mock()
        mock_engine.collect_feedback.return_value = True
        mock_engine_class.return_value = mock_engine
        
        adapter = CLIAdapter(use_server=False)
        
        result = {
            'text': 'Test response',
            'intent': {'query': 'test query'},
            'feedback_request': {
                'prompt': 'Was this helpful?',
                'options': ['yes', 'no']
            }
        }
        
        # Test numeric choice
        mock_input.side_effect = ['1']  # Choose 'yes'
        adapter._collect_feedback(result, self.context)
        
        # Verify feedback was collected
        feedback_call = mock_engine.collect_feedback.call_args[0]
        self.assertEqual(feedback_call[0], self.context.session_id)
        self.assertTrue(feedback_call[1]['helpful'])
        self.assertEqual(feedback_call[1]['rating'], 4)
        
        # Test text choice
        mock_input.side_effect = ['no', 'Should be more detailed']
        mock_engine.collect_feedback.reset_mock()
        adapter._collect_feedback(result, self.context)
        
        feedback_call = mock_engine.collect_feedback.call_args[0]
        self.assertFalse(feedback_call[1]['helpful'])
        self.assertEqual(feedback_call[1]['improved_response'], 'Should be more detailed')
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_collect_feedback_skip(self, mock_engine_class, mock_print, mock_input):
        """Test skipping feedback collection."""
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        
        adapter = CLIAdapter(use_server=False)
        
        result = {
            'feedback_request': {
                'prompt': 'Was this helpful?',
                'options': ['yes', 'no']
            }
        }
        
        # Test pressing Enter to skip
        mock_input.side_effect = ['']
        adapter._collect_feedback(result, self.context)
        
        # Verify no feedback was collected
        mock_engine.collect_feedback.assert_not_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('adapters.cli_adapter.HeadlessEngine')
    def test_collect_feedback_error_handling(self, mock_engine_class, mock_print, mock_input):
        """Test feedback collection error handling."""
        mock_engine = Mock()
        mock_engine.collect_feedback.side_effect = Exception("Feedback error")
        mock_engine_class.return_value = mock_engine
        
        adapter = CLIAdapter(use_server=False)
        
        result = {
            'text': 'Test response',
            'feedback_request': {
                'prompt': 'Was this helpful?',
                'options': ['yes', 'no']
            }
        }
        
        mock_input.side_effect = ['yes']
        adapter._collect_feedback(result, self.context)
        
        # Verify error was shown
        error_shown = any('⚠️  Feedback error:' in str(call) for call in mock_print.call_args_list)
        self.assertTrue(error_shown)


class TestCLIAdapterMain(unittest.TestCase):
    """Test the main entry point."""
    
    @patch('sys.argv', ['cli_adapter.py', 'install', 'firefox'])
    @patch('adapters.cli_adapter.CLIAdapter')
    @patch('builtins.print')
    def test_main_with_query(self, mock_print, mock_adapter_class):
        """Test main with query arguments."""
        # Set up mocks
        mock_adapter = Mock()
        mock_adapter.process_query.return_value = {
            'text': 'Installing Firefox...',
            'commands': ['nix-env -iA nixpkgs.firefox']
        }
        mock_adapter_class.return_value = mock_adapter
        
        # Run main
        main()
        
        # Verify adapter was created correctly
        mock_adapter_class.assert_called_once_with(
            use_server=False,
            server_address=None
        )
        
        # Verify query was processed
        mock_adapter.process_query.assert_called_once()
        call_args = mock_adapter.process_query.call_args[0]
        self.assertEqual(call_args[0], 'install firefox')
        
        # Verify output
        mock_print.assert_any_call('Installing Firefox...')
        mock_print.assert_any_call('\n📦 Commands:')
        mock_print.assert_any_call('  $ nix-env -iA nixpkgs.firefox')
    
    @patch('sys.argv', ['cli_adapter.py', '--server', '--server-address', 'tcp://localhost:8888'])
    @patch('adapters.cli_adapter.CLIAdapter')
    def test_main_server_mode(self, mock_adapter_class):
        """Test main with server mode."""
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        
        main()
        
        # Verify adapter was created with server settings
        mock_adapter_class.assert_called_once_with(
            use_server=True,
            server_address='tcp://localhost:8888'
        )
        
        # Verify interactive mode was started
        mock_adapter.run_interactive.assert_called_once()
    
    @patch('sys.argv', ['cli_adapter.py', '--minimal', '--execute', '--no-feedback'])
    @patch('adapters.cli_adapter.CLIAdapter')
    def test_main_with_options(self, mock_adapter_class):
        """Test main with various options."""
        mock_adapter = Mock()
        mock_adapter_class.return_value = mock_adapter
        
        main()
        
        # Verify context was created with correct options
        context_call = mock_adapter.run_interactive.call_args[0][0]
        self.assertEqual(context_call.personality, 'minimal')
        self.assertEqual(context_call.execution_mode.SAFE)
        self.assertFalse(context_call.collect_feedback)
    
    @patch('sys.argv', ['cli_adapter.py', '--technical'])
    @patch('adapters.cli_adapter.CLIAdapter')
    def test_main_personality_selection(self, mock_adapter_class):
        """Test main with different personality options."""
        personalities = [
            (['--minimal'], 'minimal'),
            (['--friendly'], 'friendly'),
            (['--encouraging'], 'encouraging'),
            (['--technical'], 'technical'),
            (['--symbiotic'], 'symbiotic'),
        ]
        
        for args, expected_personality in personalities:
            with self.subTest(personality=expected_personality):
                with patch('sys.argv', ['cli_adapter.py'] + args):
                    mock_adapter = Mock()
                    mock_adapter_class.return_value = mock_adapter
                    mock_adapter_class.reset_mock()
                    
                    main()
                    
                    context_call = mock_adapter.run_interactive.call_args[0][0]
                    self.assertEqual(context_call.personality, expected_personality)


if __name__ == '__main__':
    unittest.main()