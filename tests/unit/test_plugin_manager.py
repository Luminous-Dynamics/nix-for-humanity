#!/usr/bin/env python3
"""
Comprehensive tests for Plugin Manager

Tests all plugin management functionality including:
- Plugin loading and initialization
- Personality management
- Intent handling
- Plugin info retrieval
- Metrics collection
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts/core'))

# Import the module we're testing
from core.plugin_manager import PluginManager, get_plugin_manager


class TestPluginManager(unittest.TestCase):
    """Test the PluginManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the PluginLoader
        self.plugin_loader_mock = Mock()
        # Set default return value for initialize_plugins to avoid TypeError
        self.plugin_loader_mock.initialize_plugins.return_value = {}
        self.plugin_loader_patch = patch('core.plugin_manager.PluginLoader', return_value=self.plugin_loader_mock)
        self.plugin_loader_patch.start()
        
        # Create manager instance
        self.manager = PluginManager()
        
    def tearDown(self):
        """Clean up patches."""
        self.plugin_loader_patch.stop()
        
        # Reset singleton
        import core.plugin_manager
        core.plugin_manager._plugin_manager = None
    
    @patch('core.plugin_manager.PluginLoader')
    def test_manager_initialization(self, mock_loader_class):
        """Test plugin manager initialization."""
        # Create a new manager to capture initialization
        manager = PluginManager()
        
        # Get the call args
        call_args = mock_loader_class.call_args[0][0]
        
        # Should have 3 plugin directories
        self.assertEqual(len(call_args), 3)
        self.assertTrue(any('plugins' in path for path in call_args))
        self.assertTrue(any('plugins/personality' in path for path in call_args))
        self.assertTrue(any('plugins/features' in path for path in call_args))
        
        # Check initial state
        self.assertFalse(manager.plugins_loaded)
        self.assertEqual(manager.active_personality, "friendly")
    
    def test_load_all_plugins_success(self):
        """Test successful plugin loading."""
        # Mock successful initialization
        self.plugin_loader_mock.initialize_plugins.return_value = {
            'plugin1': True,
            'plugin2': True,
            'plugin3': True
        }
        
        result = self.manager.load_all_plugins()
        
        # Verify success
        self.assertTrue(result)
        self.assertTrue(self.manager.plugins_loaded)
        
        # Verify loader methods were called
        self.plugin_loader_mock.load_all_plugins.assert_called_once()
        self.plugin_loader_mock.initialize_plugins.assert_called_once()
        
        # Check context was passed
        context = self.plugin_loader_mock.initialize_plugins.call_args[0][0]
        self.assertIn('cache_dir', context)
        self.assertIn('data_dir', context)
        self.assertIn('config', context)
    
    def test_load_all_plugins_with_failures(self):
        """Test plugin loading with some failures."""
        # Mock partial failure
        self.plugin_loader_mock.initialize_plugins.return_value = {
            'plugin1': True,
            'plugin2': False,  # Failed
            'plugin3': True
        }
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            result = self.manager.load_all_plugins()
        
        # Should return False due to failures
        self.assertFalse(result)
        self.assertTrue(self.manager.plugins_loaded)  # Still marked as loaded
        
        # Check warning was printed
        mock_print.assert_called_with("Warning: Failed to initialize plugins: plugin2")
    
    def test_load_plugins_idempotent(self):
        """Test that plugins are only loaded once."""
        self.plugin_loader_mock.initialize_plugins.return_value = {'plugin1': True}
        
        # Load plugins
        self.manager.load_all_plugins()
        
        # Try to load again
        result = self.manager.load_all_plugins()
        
        # Should return True without calling loader again
        self.assertTrue(result)
        self.assertEqual(self.plugin_loader_mock.load_all_plugins.call_count, 1)
        self.assertEqual(self.plugin_loader_mock.initialize_plugins.call_count, 1)
    
    def test_load_plugins_with_custom_context(self):
        """Test loading plugins with custom context."""
        custom_context = {
            'cache_dir': '/custom/cache',
            'data_dir': '/custom/data',
            'config': {'debug': True}
        }
        
        self.plugin_loader_mock.initialize_plugins.return_value = {'plugin1': True}
        
        self.manager.load_all_plugins(custom_context)
        
        # Verify custom context was used
        actual_context = self.plugin_loader_mock.initialize_plugins.call_args[0][0]
        self.assertEqual(actual_context, custom_context)
    
    def test_set_personality_success(self):
        """Test setting personality successfully."""
        # Mock personality plugin
        personality_plugin = Mock()
        personality_plugin.info.capabilities = ['friendly', 'minimal', 'technical']
        
        self.plugin_loader_mock.personality_plugins = {
            'basic_personality': personality_plugin
        }
        
        # Set personality
        result = self.manager.set_personality('minimal')
        
        self.assertTrue(result)
        self.assertEqual(self.manager.active_personality, 'minimal')
    
    def test_set_personality_not_found(self):
        """Test setting personality that doesn't exist."""
        # Mock personality plugin without requested style
        personality_plugin = Mock()
        personality_plugin.info.capabilities = ['friendly', 'minimal']
        
        self.plugin_loader_mock.personality_plugins = {
            'basic_personality': personality_plugin
        }
        
        # Try to set unsupported personality
        with patch('builtins.print') as mock_print:
            result = self.manager.set_personality('aggressive')
        
        self.assertFalse(result)
        self.assertEqual(self.manager.active_personality, 'friendly')  # Unchanged
        mock_print.assert_called_with("Warning: No plugin found for personality 'aggressive'")
    
    def test_apply_personality(self):
        """Test applying personality to response."""
        # Set up loader mock
        self.plugin_loader_mock.apply_personality.return_value = "Modified response with personality!"
        
        response = "Original response"
        result = self.manager.apply_personality(response)
        
        # Verify loader was called with correct params
        self.plugin_loader_mock.apply_personality.assert_called_once_with(
            response,
            'friendly',  # Default personality
            {'personality': 'friendly'}
        )
        
        self.assertEqual(result, "Modified response with personality!")
    
    def test_apply_personality_with_context(self):
        """Test applying personality with custom context."""
        self.plugin_loader_mock.apply_personality.return_value = "Modified!"
        
        response = "Original"
        context = {'user_id': 'test123', 'session': 'abc'}
        
        result = self.manager.apply_personality(response, context)
        
        # Verify context was merged with personality
        actual_context = self.plugin_loader_mock.apply_personality.call_args[0][2]
        self.assertEqual(actual_context['user_id'], 'test123')
        self.assertEqual(actual_context['session'], 'abc')
        self.assertEqual(actual_context['personality'], 'friendly')
    
    def test_apply_personality_loads_plugins(self):
        """Test that apply_personality loads plugins if needed."""
        self.plugin_loader_mock.initialize_plugins.return_value = {'plugin1': True}
        self.plugin_loader_mock.apply_personality.return_value = "Modified!"
        
        # Plugins not loaded yet
        self.assertFalse(self.manager.plugins_loaded)
        
        # Apply personality
        self.manager.apply_personality("Test")
        
        # Should have loaded plugins
        self.assertTrue(self.manager.plugins_loaded)
        self.plugin_loader_mock.load_all_plugins.assert_called_once()
    
    def test_handle_intent_found(self):
        """Test handling intent with available handler."""
        # Mock handler
        handler_mock = Mock()
        handler_mock.handle.return_value = {
            'success': True,
            'response': 'Intent handled successfully',
            'data': {'result': 42},
            'actions': ['action1', 'action2']
        }
        
        self.plugin_loader_mock.find_handler.return_value = handler_mock
        
        # Handle intent
        result = self.manager.handle_intent('test_intent', {'param': 'value'})
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertTrue(result['success'])
        self.assertEqual(result['response'], 'Intent handled successfully')
        self.assertEqual(result['data']['result'], 42)
        
        # Verify handler was called
        handler_mock.handle.assert_called_once_with('test_intent', {'param': 'value'})
    
    def test_handle_intent_not_found(self):
        """Test handling intent with no handler."""
        self.plugin_loader_mock.find_handler.return_value = None
        
        result = self.manager.handle_intent('unknown_intent', {})
        
        self.assertIsNone(result)
    
    def test_handle_intent_error(self):
        """Test handling intent when handler raises error."""
        # Mock handler that raises exception
        handler_mock = Mock()
        handler_mock.handle.side_effect = Exception("Handler error!")
        
        self.plugin_loader_mock.find_handler.return_value = handler_mock
        
        # Handle intent
        result = self.manager.handle_intent('error_intent', {})
        
        # Should return error response
        self.assertIsNotNone(result)
        self.assertFalse(result['success'])
        self.assertIn('Plugin error', result['response'])
        self.assertIn('Handler error!', result['response'])
        self.assertIsNone(result['data'])
        self.assertEqual(result['actions'], [])
    
    def test_get_all_flags(self):
        """Test getting all command-line flags."""
        # Mock flags
        mock_flags = [
            {'name': '--flag1', 'help': 'First flag'},
            {'name': '--flag2', 'help': 'Second flag'}
        ]
        
        self.plugin_loader_mock.get_all_flags.return_value = mock_flags
        
        flags = self.manager.get_all_flags()
        
        self.assertEqual(flags, mock_flags)
        self.plugin_loader_mock.get_all_flags.assert_called_once()
    
    def test_get_plugin_info(self):
        """Test getting plugin information."""
        # Mock plugin info
        plugin1 = Mock()
        plugin1.version = '1.0.0'
        plugin1.description = 'First plugin'
        plugin1.capabilities = ['cap1', 'cap2']
        
        plugin2 = Mock()
        plugin2.version = '2.0.0'
        plugin2.description = 'Second plugin'
        plugin2.capabilities = ['cap3']
        
        self.plugin_loader_mock.get_plugin_info.return_value = {
            'plugin1': plugin1,
            'plugin2': plugin2
        }
        
        self.plugin_loader_mock.personality_plugins = {'plugin1': plugin1}
        self.plugin_loader_mock.feature_plugins = {'plugin2': plugin2}
        
        # Get info
        info = self.manager.get_plugin_info()
        
        # Verify structure
        self.assertEqual(info['total_plugins'], 2)
        self.assertEqual(info['personality_plugins'], 1)
        self.assertEqual(info['feature_plugins'], 1)
        
        # Check plugin details
        self.assertEqual(info['plugins']['plugin1']['version'], '1.0.0')
        self.assertEqual(info['plugins']['plugin1']['description'], 'First plugin')
        self.assertEqual(info['plugins']['plugin1']['capabilities'], ['cap1', 'cap2'])
        
        self.assertEqual(info['plugins']['plugin2']['version'], '2.0.0')
        self.assertEqual(info['plugins']['plugin2']['description'], 'Second plugin')
        self.assertEqual(info['plugins']['plugin2']['capabilities'], ['cap3'])
    
    def test_get_metrics(self):
        """Test collecting metrics from plugins."""
        # Mock metrics
        mock_metrics = {
            'total_uses': 100,
            'average_response_time': 0.5,
            'errors': 2
        }
        
        self.plugin_loader_mock.collect_metrics.return_value = mock_metrics
        
        metrics = self.manager.get_metrics()
        
        self.assertEqual(metrics, mock_metrics)
        self.plugin_loader_mock.collect_metrics.assert_called_once()
    
    def test_auto_load_on_operations(self):
        """Test that various operations auto-load plugins if needed."""
        self.plugin_loader_mock.initialize_plugins.return_value = {'plugin1': True}
        
        # Test get_all_flags
        self.plugin_loader_mock.get_all_flags.return_value = []
        self.manager.get_all_flags()
        self.assertTrue(self.manager.plugins_loaded)
        
        # Reset
        self.manager.plugins_loaded = False
        
        # Test get_plugin_info
        self.plugin_loader_mock.get_plugin_info.return_value = {}
        self.plugin_loader_mock.personality_plugins = {}
        self.plugin_loader_mock.feature_plugins = {}
        self.manager.get_plugin_info()
        self.assertTrue(self.manager.plugins_loaded)
        
        # Reset
        self.manager.plugins_loaded = False
        
        # Test get_metrics
        self.plugin_loader_mock.collect_metrics.return_value = {}
        self.manager.get_metrics()
        self.assertTrue(self.manager.plugins_loaded)


class TestPluginManagerSingleton(unittest.TestCase):
    """Test the singleton behavior of plugin manager."""
    
    def tearDown(self):
        """Reset singleton after each test."""
        import core.plugin_manager
        core.plugin_manager._plugin_manager = None
    
    @patch('core.plugin_manager.PluginLoader')
    def test_get_plugin_manager_creates_singleton(self, mock_loader_class):
        """Test that get_plugin_manager creates singleton."""
        # First call creates instance
        manager1 = get_plugin_manager()
        self.assertIsNotNone(manager1)
        
        # Second call returns same instance
        manager2 = get_plugin_manager()
        self.assertIs(manager1, manager2)
        
        # Plugin loader only created once
        self.assertEqual(mock_loader_class.call_count, 1)
    
    @patch('core.plugin_manager.PluginLoader')
    def test_singleton_persists_state(self, mock_loader_class):
        """Test that singleton persists state between calls."""
        # Get manager and modify state
        manager1 = get_plugin_manager()
        manager1.active_personality = 'technical'
        manager1.plugins_loaded = True
        
        # Get manager again
        manager2 = get_plugin_manager()
        
        # State should be preserved
        self.assertEqual(manager2.active_personality, 'technical')
        self.assertTrue(manager2.plugins_loaded)


if __name__ == '__main__':
    unittest.main()