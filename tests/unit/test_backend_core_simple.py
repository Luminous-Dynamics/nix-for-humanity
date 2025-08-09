#!/usr/bin/env python3
"""
import subprocess
Simplified tests for NixForHumanityBackend core functionality

Tests core backend methods without complex dependencies.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import sys
import os
import asyncio
from pathlib import Path

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
backend_path = os.path.join(project_root, 'nix_humanity')
sys.path.insert(0, backend_path)


class TestNixForHumanityBackendSimple(unittest.TestCase):
    """Test the NixForHumanityBackend class core functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock all the imports
        self.mock_modules = {
            'backend.api.schema': MagicMock(),
            'backend.core.intent': MagicMock(),
            'backend.core.executor': MagicMock(),
            'backend.core.knowledge': MagicMock(),
            'backend.core.error_handler': MagicMock(),
            'backend.security.input_validator': MagicMock(),
            'backend.core.nix_integration': MagicMock(),
        }
        
        for module_name, mock_module in self.mock_modules.items():
            sys.modules[module_name] = mock_module
        
        # Now import the backend
        from nix_humanity.core.engine import NixForHumanityBackend
        self.NixForHumanityBackend = NixForHumanityBackend
        
        # Create test instance with mocked dependencies
        with patch('nix_humanity.core.engine.IntentRecognizer') as mock_ir, \
             patch('nix_humanity.core.engine.SafeExecutor') as mock_se, \
             patch('nix_humanity.core.engine.KnowledgeBase') as mock_kb:
            
            self.mock_intent_recognizer = Mock()
            self.mock_executor = Mock()
            self.mock_knowledge = Mock()
            
            mock_ir.return_value = self.mock_intent_recognizer
            mock_se.return_value = self.mock_executor
            mock_kb.return_value = self.mock_knowledge
            
            self.backend = self.NixForHumanityBackend()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove mocked modules
        for module_name in self.mock_modules:
            if module_name in sys.modules:
                del sys.modules[module_name]
    
    def test_init_creates_components(self):
        """Test that initialization creates all necessary components."""
        self.assertEqual(self.backend.intent_recognizer, self.mock_intent_recognizer)
        self.assertEqual(self.backend.executor, self.mock_executor)
        self.assertEqual(self.backend.knowledge, self.mock_knowledge)
        self.assertIsNone(self.backend.nix_integration)
    
    def test_find_nixos_rebuild_path_returns_none_when_not_found(self):
        """Test finding nixos-rebuild path returns None when not found."""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1)
                
                result = self.backend._find_nixos_rebuild_path()
                
                self.assertIsNone(result)
    
    def test_has_python_api_initialized(self):
        """Test that Python API attribute is initialized."""
        # The backend initializes _has_python_api in _init_nixos_api
        # It may be True or False depending on whether imports succeed
        self.assertIsInstance(self.backend._has_python_api, bool)
    
    def test_explain_substitutes_entities(self):
        """Test that explain method substitutes entities in template."""
        # Create mock intent with entities
        mock_intent = Mock()
        mock_intent.type = Mock()
        mock_intent.entities = {'package': 'firefox'}
        
        # Mock IntentType enum to have INSTALL_PACKAGE attribute
        with patch('nix_humanity.core.engine.IntentType') as mock_intent_type:
            mock_intent_type.INSTALL_PACKAGE = Mock()
            mock_intent.type = mock_intent_type.INSTALL_PACKAGE
            
            explanation = self.backend._explain(mock_intent, [], None)
            
            self.assertIn('firefox', explanation)
    
    def test_extract_commands_from_plan(self):
        """Test extracting commands from action plan."""
        plan = [
            "Use nix profile install nixpkgs#vim",
            "Verify vim installation"
        ]
        
        commands = self.backend._extract_commands(plan)
        
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]['command'], "nix profile install nixpkgs#vim")
        self.assertEqual(commands[0]['description'], "Install package")
    
    def test_should_use_native_api_without_env(self):
        """Test native API check without environment variable."""
        # Mock request object
        mock_request = Mock()
        mock_request.text = "update system"
        
        # Clear environment
        with patch.dict(os.environ, {}, clear=True):
            result = self.backend._should_use_native_api(mock_request)
            
        self.assertFalse(result)
    
    def test_should_use_native_api_with_env(self):
        """Test native API check with environment variable."""
        # Mock request object
        mock_request = Mock()
        mock_request.text = "update system"
        
        # Set environment
        with patch.dict(os.environ, {'NIX_HUMANITY_PYTHON_BACKEND': 'true'}):
            result = self.backend._should_use_native_api(mock_request)
            
        self.assertTrue(result)
    
    def test_build_response_text_minimal_personality(self):
        """Test response text building with minimal personality."""
        # Mock intent
        mock_intent = Mock()
        mock_intent.type = Mock(value='install_package')
        
        knowledge = {
            'package': 'vim',
            'solution': 'Install vim using nix',
            'example': 'nix profile install nixpkgs#vim'
        }
        
        response = self.backend._build_response_text(mock_intent, knowledge, 'minimal')
        
        # Minimal should not have emojis or greetings
        self.assertNotIn('Hi there!', response)
        self.assertNotIn('😊', response)
        self.assertIn('vim', response)
    
    def test_build_response_text_friendly_personality(self):
        """Test response text building with friendly personality."""
        # Mock intent
        mock_intent = Mock()
        mock_intent.type = Mock(value='install_package')
        
        knowledge = {
            'package': 'vim',
            'solution': 'Install vim using nix',
            'example': 'nix profile install nixpkgs#vim'
        }
        
        response = self.backend._build_response_text(mock_intent, knowledge, 'friendly')
        
        # Friendly should have greeting and emoji
        self.assertIn('Hi there!', response)
        self.assertIn('😊', response)
    
    def test_build_response_text_no_knowledge(self):
        """Test response text when no knowledge is available."""
        mock_intent = Mock()
        
        response = self.backend._build_response_text(mock_intent, None, 'minimal')
        
        self.assertIn("I'm not sure how to help", response)


if __name__ == '__main__':
    unittest.main()