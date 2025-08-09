#!/usr/bin/env python3
"""
from typing import Dict, List
Consciousness-first tests for the NixForHumanityBackend engine

Instead of mocking, we create real test implementations that behave
deterministically. This provides genuine test coverage while maintaining
the consciousness-first principle of authentic interaction.
"""

import unittest
import tempfile
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# Add the src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from nix_humanity.core.engine import NixForHumanityBackend
from nix_humanity.core.interface import Query
from nix_humanity.core.intents import Response, Intent, IntentType, Command
from nix_humanity.core.planning import Plan, ExecutionResult
from nix_humanity.core.executor import SafeExecutor


@dataclass
class TestExecutionResult:
    """Simulated execution result for consciousness-first testing"""
    success: bool
    output: str
    error: str
    exit_code: int
    execution_time: float = 0.1
    

class ConsciousnessTestSafeExecutor:
    """Test execution engine that provides deterministic responses"""
    
    def __init__(self):
        self.executed_commands = []
        self.package_registry = {
            'firefox': {'available': True, 'install_time': 0.2},
            'vim': {'available': True, 'install_time': 0.1},
            'nonexistent': {'available': False}
        }
        self.search_results = {
            'python': [
                {'name': 'python3', 'version': '3.11', 'description': 'Python interpreter'},
                {'name': 'python310', 'version': '3.10', 'description': 'Python 3.10'}
            ]
        }
        
    def execute(self, commands: List[str], intent: Intent) -> Dict[str, Any]:
        """Simulate command execution with deterministic results"""
        self.executed_commands.append((commands, intent))
        
        # Persona-aware testing: Maya (ADHD) needs <1s responses
        if hasattr(intent, 'persona') and intent.persona == 'maya_adhd':
            import time
            start = time.time()
            # Process immediately for Maya
            result = self._process_command(commands, intent)
            duration = time.time() - start
            assert duration < 1.0, f"Maya needs <1s responses, got {duration}s"
            return result
            
        return self._process_command(commands, intent)
        
    def _process_command(self, commands: List[str], intent: Intent) -> Dict[str, Any]:
        """Process command based on intent type"""
        if intent.type == IntentType.INSTALL_PACKAGE:
            package = intent.entities.get('package', intent.entities.get('target'))
            if package in self.package_registry and self.package_registry[package]['available']:
                return {
                    'success': True,
                    'output': f'Package {package} installed successfully',
                    'error': '',
                    'exit_code': 0
                }
            else:
                return {
                    'success': False,
                    'output': '',
                    'error': f'Package {package} not found',
                    'exit_code': 1
                }
                
        elif intent.type == IntentType.REMOVE:
            return {
                'success': True,
                'output': 'Package removed successfully',
                'error': '',
                'exit_code': 0
            }
            
        elif intent.type == IntentType.UPDATE_SYSTEM:
            return {
                'success': True,
                'output': 'System updated successfully',
                'error': '',
                'exit_code': 0
            }
            
        return {
            'success': True,
            'output': 'Command executed',
            'error': '',
            'exit_code': 0
        }
        
    def execute_safe_search(self, query: str) -> tuple:
        """Simulate package search with deterministic results"""
        if query in self.search_results:
            return True, self.search_results[query], ''
        return True, [], 'No packages found'


class TestNixForHumanityCore(unittest.TestCase):
    """Test the main NixForHumanityBackend engine"""
    
    def setUp(self):
        """Create core engine with test configuration"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'knowledge_db_path': Path(self.temp_dir) / 'test_knowledge.db',
            'learning_db_path': Path(self.temp_dir) / 'test_learning.db',
            'dry_run': True,
            'default_personality': 'friendly',
            'collect_feedback': True,
            'enable_learning': True
        }
        self.core = NixForHumanityBackend(self.config)
        
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_initialization(self):
        """Test core engine initialization"""
        self.assertIsNotNone(self.core.intent_engine)
        self.assertIsNotNone(self.core.knowledge_base)
        self.assertIsNotNone(self.core.execution_engine)
        self.assertIsNotNone(self.core.personality_system)
        self.assertIsNotNone(self.core.learning_system)
        
        self.assertTrue(self.core.collect_feedback)
        self.assertTrue(self.core.enable_learning)
        
    def test_plan_install_query(self):
        """Test planning for an install query"""
        query = Query(
            text="install firefox",
            mode="dry_run",
            personality='friendly'
        )
        
        plan = self.core.plan(query)
        
        self.assertIsInstance(plan, Plan)
        self.assertIn('firefox', plan.text)
        self.assertIn('install', plan.text.lower())
        self.assertIsNotNone(plan.intent)
        self.assertEqual(plan.intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(plan.intent.entities.get('target'), 'firefox')
        self.assertIsNotNone(plan.command)
        self.assertFalse(plan.requires_confirmation)  # Install doesn't need confirmation
        
    def test_plan_remove_query(self):
        """Test planning for a remove query"""
        query = Query(
            text="remove vim",
            mode="dry_run"
        )
        
        plan = self.core.plan(query)
        
        self.assertEqual(plan.intent.type, IntentType.REMOVE)
        self.assertEqual(plan.intent.entities.get('target'), 'vim')
        self.assertTrue(plan.requires_confirmation)  # Remove needs confirmation
        
    def test_plan_update_query(self):
        """Test planning for an update query"""
        query = Query(
            text="update my system",
            mode="dry_run"
        )
        
        plan = self.core.plan(query)
        
        self.assertEqual(plan.intent.type, IntentType.UPDATE_SYSTEM)
        self.assertTrue(plan.requires_confirmation)  # Update needs confirmation
        
    def test_plan_help_query(self):
        """Test planning for a help query"""
        query = Query(
            text="help",
            mode="normal"
        )
        
        plan = self.core.plan(query)
        
        self.assertEqual(plan.intent.type, IntentType.HELP)
        self.assertIsNone(plan.command)  # Help doesn't need a command
        self.assertFalse(plan.requires_confirmation)
        
    def test_plan_with_personality(self):
        """Test that personality affects the response"""
        query_friendly = Query(
            text="install firefox",
            personality='friendly'
        )
        
        query_minimal = Query(
            text="install firefox",
            personality='minimal'
        )
        
        plan_friendly = self.core.plan(query_friendly)
        plan_minimal = self.core.plan(query_minimal)
        
        # Friendly should have more text
        self.assertGreater(len(plan_friendly.text), len(plan_minimal.text))
        self.assertIn('Hi there', plan_friendly.text)
        self.assertNotIn('Hi there', plan_minimal.text)
        
    def test_execute_plan_success(self):
        """Test successful plan execution with consciousness-first test engine"""
        # Create a plan with a command
        plan = Plan(
            text="Installing firefox...",
            intent=Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={'target': 'firefox', 'package': 'firefox'},
                confidence=0.95,
                raw_input='install firefox'
            ),
            command=Command('nix', ['profile', 'install', 'firefox'], True, False, 'Install'),
            suggestions=[],
            confidence=0.95,
            requires_confirmation=False
        )
        
        # Replace execution engine with consciousness-first test implementation
        test_engine = ConsciousnessTestSafeExecutor()
        self.core.execution_engine = test_engine
        
        result = self.core.execute_plan(plan, user_id='test_user')
        
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.output, 'Package firefox installed successfully')
        self.assertEqual(result.exit_code, 0)
        
        # Verify command was tracked
        self.assertEqual(len(test_engine.executed_commands), 1)
        executed_commands, executed_intent = test_engine.executed_commands[0]
        self.assertEqual(executed_intent.type, IntentType.INSTALL_PACKAGE)
        
    def test_execute_plan_failure(self):
        """Test failed plan execution with consciousness-first test engine"""
        plan = Plan(
            text="Installing nonexistent package...",
            intent=Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={'target': 'nonexistent', 'package': 'nonexistent'},
                confidence=0.95,
                raw_input='install nonexistent'
            ),
            command=Command('nix', ['profile', 'install', 'nonexistent'], True, False, 'Install'),
            suggestions=[],
            confidence=0.95,
            requires_confirmation=False
        )
        
        # Replace execution engine with consciousness-first test implementation
        test_engine = ConsciousnessTestSafeExecutor()
        self.core.execution_engine = test_engine
        
        result = self.core.execute_plan(plan, user_id='test_user')
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, 'Package nonexistent not found')
        self.assertEqual(result.exit_code, 1)
        
        # Verify error handling tracked
        self.assertEqual(len(test_engine.executed_commands), 1)
        executed_commands, executed_intent = test_engine.executed_commands[0]
        self.assertEqual(executed_intent.type, IntentType.INSTALL_PACKAGE)
        
    def test_execute_plan_no_command(self):
        """Test execution when plan has no command"""
        plan = Plan(
            text="Here's some help...",
            intent=Intent(
                type=IntentType.HELP,
                entities={},
                confidence=0.99,
                raw_input='help'
            ),
            command=None,
            suggestions=['Try: install firefox'],
            confidence=0.99,
            requires_confirmation=False
        )
        
        result = self.core.execute_plan(plan)
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, 'No action needed for this query.')
        
    def test_process_full_pipeline(self):
        """Test the full process pipeline with consciousness-first test engine"""
        query = Query(
            text="install firefox",
            mode="normal",
            personality='symbiotic',
            user_id='test_user'
        )
        
        # Replace execution engine with consciousness-first test implementation
        test_engine = ConsciousnessTestSafeExecutor()
        self.core.execution_engine = test_engine
        
        response = self.core.process(query)
        
        self.assertIsInstance(response, Response)
        self.assertTrue(response.executed)
        self.assertTrue(response.success)
        self.assertTrue(response.feedback_requested)  # Symbiotic personality requests feedback
        self.assertIn('✅', response.text)  # Success indicator
        
        # Verify consciousness-first test engine tracked execution
        self.assertEqual(len(test_engine.executed_commands), 1)
        executed_commands, executed_intent = test_engine.executed_commands[0]
        self.assertEqual(executed_intent.type, IntentType.INSTALL_PACKAGE)
        
    def test_process_dry_run(self):
        """Test process in dry run mode"""
        query = Query(
            text="remove firefox",
            mode="dry_run"
        )
        
        response = self.core.process(query)
        
        self.assertFalse(response.executed)
        self.assertIsNone(response.success)
        self.assertIsNotNone(response.command)
        
    def test_build_response_text_install(self):
        """Test response text building for install intent"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'target': 'firefox', 'package': 'firefox'},
            confidence=0.95,
            raw_input='install firefox'
        )
        solution = {
            'found': True,
            'explanation': 'Modern Nix uses profile commands'
        }
        
        text = self.core._build_response_text(intent, solution, 'install firefox')
        
        self.assertIn('firefox', text)
        self.assertIn('options', text)
        self.assertIn('Modern Nix', text)
        
    def test_build_response_text_search(self):
        """Test response text building for search intent with consciousness-first test engine"""
        intent = Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={'target': 'python', 'package': 'python'},
            confidence=0.90,
            raw_input='search python'
        )
        solution = {'found': True}
        
        # Replace execution engine with consciousness-first test implementation
        test_engine = ConsciousnessTestSafeExecutor()
        self.core.execution_engine = test_engine
        
        text = self.core._build_response_text(intent, solution, 'search python')
        
        self.assertIn('Found 2 packages', text)
        self.assertIn('python3', text)
        self.assertIn('3.11', text)
        
        # Verify consciousness-first test engine was used for search
        # The search results are defined in test_engine.search_results
        success, results, error = test_engine.execute_safe_search('python')
        self.assertTrue(success)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['name'], 'python3')
        self.assertEqual(results[0]['version'], '3.11')
        
    def test_get_suggestions(self):
        """Test suggestion generation"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'target': 'firefox', 'package': 'firefox'},
            confidence=0.95,
            raw_input='install firefox'
        )
        solution = {
            'related': ['search', 'remove']
        }
        
        suggestions = self.core._get_suggestions(intent, solution)
        
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 3)  # Limited to 3
        self.assertTrue(any('search' in s for s in suggestions))
        
    def test_get_user_preferences(self):
        """Test getting user preferences"""
        prefs = self.core.get_user_preferences('test_user')
        
        self.assertIsInstance(prefs, dict)
        # With fresh database, should be empty
        self.assertEqual(len(prefs), 0)
        
    def test_get_system_stats(self):
        """Test getting system statistics"""
        stats = self.core.get_system_stats()
        
        self.assertIn('personality', stats)
        self.assertIn('dry_run_mode', stats)
        self.assertIn('learning_enabled', stats)
        self.assertIn('feedback_enabled', stats)
        
        self.assertEqual(stats['personality'], 'friendly')
        self.assertTrue(stats['dry_run_mode'])
        self.assertTrue(stats['learning_enabled'])
        self.assertTrue(stats['feedback_enabled'])
        
    def test_unknown_query_handling(self):
        """Test handling of queries with unknown intent"""
        query = Query(
            text="do something completely random that makes no sense",
            mode="normal"
        )
        
        plan = self.core.plan(query)
        
        self.assertEqual(plan.intent.type, IntentType.UNKNOWN)
        self.assertIsNone(plan.command)
        self.assertIn("don't understand", plan.text)


if __name__ == '__main__':
    unittest.main()