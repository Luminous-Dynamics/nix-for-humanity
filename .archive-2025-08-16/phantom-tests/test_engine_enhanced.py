#!/usr/bin/env python3
"""
Enhanced unit tests for the NixForHumanityBackend engine - Consciousness-First Testing
Tests the central orchestrator using deterministic test implementations
"""

import pytest
import tempfile
import time
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils.test_implementations import (
    TestNLPEngine,
    TestKnowledgeBase,
    TestExecutionBackend,
    TestLearningEngine,
    TestDatabase,
    TestBackendAPI,
    PERSONA_TEST_DATA,
    create_successful_process
)

from nix_humanity.core.engine import NixForHumanityBackend
from nix_humanity.core.interface import (
     Response, Intent, IntentType
)
from nix_humanity.core.intents import Command, ExecutionResult
from nix_humanity.core.planning import Plan
from nix_humanity.core.responses import PersonalityStyle
from nix_humanity.learning.preferences import Interaction


class TestEngineEnhanced:
    """Enhanced tests for the NixForHumanityBackend engine - Consciousness-First Testing"""
    
    @pytest.fixture
    def test_database(self):
        """Create test database"""
        return TestDatabase()
    
    @pytest.fixture
    def test_components(self, test_database):
        """Create all test components with deterministic behavior"""
        return {
            'intent_engine': TestNLPEngine(),
            'knowledge_base': TestKnowledgeBase(),
            'execution_engine': TestExecutionBackend(),
            'learning_system': TestLearningEngine(test_database)
        }
    
    @pytest.fixture
    def config(self):
        """Default test configuration"""
        return {
            'dry_run': True,
            'collect_feedback': True,
            'enable_learning': True,
            'default_personality': 'friendly'
        }
    
    @pytest.fixture
    def engine(self, config, test_components):
        """Create engine with test components injected"""
        engine = NixForHumanityBackend(config)
        
        # Inject test components
        engine.intent_engine = test_components['intent_engine']
        engine.knowledge_base = test_components['knowledge_base']
        engine.execution_engine = test_components['execution_engine']
        engine.learning_system = test_components['learning_system']
        
        return engine
        
    def test_initialization_default(self):
        """Test default initialization"""
        engine = NixForHumanityBackend()
        
        # Check subsystems are initialized
        assert engine.intent_engine is not None
        assert engine.knowledge_base is not None
        assert engine.execution_engine is not None
        assert engine.personality_system is not None
        assert engine.learning_system is not None
        
        # Check default config
        assert engine.collect_feedback is True
        assert engine.enable_learning is True
        
    def test_initialization_with_config(self):
        """Test initialization with custom config"""
        config = {
            'dry_run': False,
            'collect_feedback': False,
            'enable_learning': False,
            'default_personality': 'minimal',
            'knowledge_db_path': '/tmp/test.db',
            'learning_db_path': '/tmp/learning.db'
        }
        
        with patch('nix_for_humanity.core.knowledge_base.KnowledgeBase') as MockKB, \
             patch('nix_for_humanity.core.learning_system.PreferenceManager') as MockLS:
            
            engine = NixForHumanityBackend(config)
            
            # Check config was passed through
            MockKB.assert_called_with('/tmp/test.db')
            MockLS.assert_called_with('/tmp/learning.db')
            self.assertFalse(engine.collect_feedback)
            self.assertFalse(engine.enable_learning)
            
    def test_plan_install_intent(self, engine, test_components):
        """Test planning for install intent with deterministic behavior"""
        # Use real test implementations
        query = {"query": "install firefox".DRY_RUN}
        
        # Test components provide deterministic responses
        # NLP engine will recognize install intent for firefox
        # Knowledge base has firefox information
        # Execution backend will create safe install command
        
        # Execute
        plan = engine.plan(query)
        
        # Verify deterministic behavior
        assert isinstance(plan, Plan)
        assert plan.intent.type == IntentType.INSTALL_PACKAGE
        assert plan.intent.entities.get('package') == 'firefox'
        assert plan.confidence >= 0.9  # High confidence for clear intent
        
        # Command should be safe and correct
        assert plan.command is not None
        assert 'firefox' in str(plan.command)
        assert plan.command.safe is True
        
        # Should not require confirmation for install
        assert plan.requires_confirmation is False
        
        # Response should be persona-adapted
        assert len(plan.text) > 0
        assert 'firefox' in plan.text.lower()
        
    def test_plan_remove_intent_requires_confirmation(self):
        """Test planning for remove intent requires confirmation"""
        query = {"query": "remove firefox"}
        intent = Intent(
            type=IntentType.REMOVE,
            entities={'target': 'firefox', 'package': 'firefox'},
            confidence=0.9,
            raw_input='remove firefox'
        )
        solution = {'found': True, 'solution': 'Removing firefox'}
        command = Command('nix', ['profile', 'remove', 'firefox'], True, False, 'Remove firefox')
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_execution_engine.build_command.return_value = command
        self.mock_personality_system.adapt_response.return_value = "I'll remove firefox"
        
        plan = self.engine.plan(query)
        
        self.assertTrue(plan.requires_confirmation)  # Remove needs confirmation
        
    def test_plan_update_intent(self):
        """Test planning for update intent"""
        query = {"query": "update system"}
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.85,
            raw_input='update'
        )
        solution = {'found': True, 'solution': 'Updating system'}
        command = Command('nixos-rebuild', ['switch'], True, True, 'Update system')
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_execution_engine.build_command.return_value = command
        self.mock_personality_system.adapt_response.return_value = "Let's update your system"
        
        plan = self.engine.plan(query)
        
        self.assertEqual(plan.command, command)
        self.assertTrue(plan.requires_confirmation)  # Update needs confirmation
        
    def test_plan_search_intent_with_results(self):
        """Test planning for search intent with results"""
        query = {"query": "search python"}
        intent = Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={'target': 'python', 'package': 'python'},
            confidence=0.9,
            raw_input='search python'
        )
        solution = {'found': True}
        
        search_results = [
            {'name': 'python3', 'version': '3.11.0', 'description': 'Python programming language'},
            {'name': 'python310', 'version': '3.10.0', 'description': 'Python 3.10'},
        ]
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_execution_engine.execute_safe_search.return_value = (True, search_results, "")
        self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x  # Return as-is
        
        plan = self.engine.plan(query)
        
        self.assertIn("Found 2 packages", plan.text)
        self.assertIn("python3", plan.text)
        self.assertIn("3.11.0", plan.text)
        
    def test_plan_search_intent_no_results(self):
        """Test planning for search intent with no results"""
        query = {"query": "search nonexistent"}
        intent = Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={'target': 'nonexistent', 'package': 'nonexistent'},
            confidence=0.9,
            raw_input='search nonexistent'
        )
        solution = {'found': True}
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_execution_engine.execute_safe_search.return_value = (True, [], "")
        self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
        
        plan = self.engine.plan(query)
        
        self.assertIn("No packages found", plan.text)
        self.assertIn("Try a different search term", plan.text)
        
    def test_plan_unknown_intent(self):
        """Test planning for unknown intent"""
        query = {"query": "do something weird"}
        intent = Intent(
            type=IntentType.UNKNOWN,
            entities={},
            confidence=0.3,
            raw_input='unknown'
        )
        solution = {
            'found': False,
            'suggestion': "I didn't understand that. Try 'help' for available commands."
        }
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
        
        plan = self.engine.plan(query)
        
        self.assertIsNone(plan.command)
        self.assertIn("I didn't understand", plan.text)
        
    def test_plan_with_custom_personality(self):
        """Test planning with custom personality in query"""
        query = {"query": "install vim", personality='minimal'}
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'target': 'vim', 'package': 'vim'},
            confidence=0.9,
            raw_input='install vim'
        )
        solution = {'found': True, 'solution': 'Installing vim'}
        command = Command('nix', ['profile', 'install', 'nixpkgs#vim'], True, False, '')
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_execution_engine.build_command.return_value = command
        self.mock_personality_system.adapt_response.return_value = "Installing vim."
        
        plan = self.engine.plan(query)
        
        # Verify personality adaptation was called with minimal style
        self.mock_personality_system.adapt_response.assert_called_with(
            unittest.mock.ANY,  # response text
            'install vim',      # query text
            PersonalityStyle.MINIMAL
        )
        
    def test_execute_plan_success(self):
        """Test successful plan execution"""
        command = Command('nix', ['search', 'test'], True, False, '')
        plan = Plan(
            text="Searching for test",
            intent=Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={'target': 'test', 'package': 'test'},
            confidence=0.9,
            raw_input='search test'
        ),
            command=command,
            suggestions=[],
            confidence=0.9,
            requires_confirmation=False
        )
        
        execution_result = {
            'success': True,
            'output': 'Found packages',
            'error': '',
            'exit_code': 0
        }
        
        self.mock_execution_engine.execute.return_value = execution_result
        
        result = self.engine.execute_plan(plan, user_id='test_user')
        
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.output, 'Found packages')
        self.assertEqual(result.exit_code, 0)
        
        # Verify learning was recorded
        self.mock_learning_system.record_interaction.assert_called_once()
        
    def test_execute_plan_failure(self):
        """Test failed plan execution"""
        command = Command('nix', ['install', 'badpackage'], True, False, '')
        plan = Plan(
            text="Installing badpackage",
            intent=Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'target': 'badpackage', 'package': 'badpackage'},
            confidence=0.9,
            raw_input='install badpackage'
        ),
            command=command,
            suggestions=[],
            confidence=0.9,
            requires_confirmation=False
        )
        
        execution_result = {
            'success': False,
            'output': '',
            'error': 'Package not found',
            'exit_code': 1
        }
        
        self.mock_execution_engine.execute.return_value = execution_result
        
        result = self.engine.execute_plan(plan, user_id='test_user')
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, 'Package not found')
        self.assertEqual(result.exit_code, 1)
        
    def test_execute_plan_no_command(self):
        """Test executing plan without command"""
        plan = Plan(
            text="No action needed",
            intent=Intent(
            type=IntentType.EXPLAIN,
            entities={},
            confidence=0.9,
            raw_input='info'
        ),
            command=None,
            suggestions=[],
            confidence=0.9,
            requires_confirmation=False
        )
        
        result = self.engine.execute_plan(plan)
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, "No action needed for this query.")
        
    def test_execute_plan_learning_disabled(self):
        """Test plan execution with learning disabled"""
        self.engine.enable_learning = False
        
        command = Command('nix', ['search', 'test'], True, False, '')
        plan = Plan(
            text="Searching",
            intent=Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={'target': 'test', 'package': 'test'},
            confidence=0.9,
            raw_input='search test'
        ),
            command=command,
            suggestions=[],
            confidence=0.9,
            requires_confirmation=False
        )
        
        self.mock_execution_engine.execute.return_value = {
            'success': True, 'output': 'Done', 'error': '', 'exit_code': 0
        }
        
        self.engine.execute_plan(plan, user_id='test_user')
        
        # Learning should not be called
        self.mock_learning_system.record_interaction.assert_not_called()
        
    def test_process_dry_run_mode(self):
        """Test full process pipeline in dry run mode"""
        query = {"query": "install firefox".DRY_RUN}
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'target': 'firefox', 'package': 'firefox'},
            confidence=0.9,
            raw_input='install firefox'
        )
        solution = {'found': True, 'solution': 'Installing firefox'}
        command = Command('nix', ['profile', 'install', 'nixpkgs#firefox'], True, False, '')
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_knowledge_base.get_install_methods.return_value = []
        self.mock_execution_engine.build_command.return_value = command
        self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
        
        with patch('time.time', side_effect=[0, 0.1]):  # 100ms processing time
            response = self.engine.process(query)
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.intent, intent)
        self.assertEqual(response.command, command)
        self.assertFalse(response.executed)  # Dry run doesn't execute
        self.assertIsNone(response.success)
        self.assertEqual(response.processing_time_ms, 100)
        
    def test_process_execute_mode(self):
        """Test full process pipeline in execute mode"""
        query = {"query": "install vim".EXECUTE, user_id='test_user'}
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'target': 'vim', 'package': 'vim'},
            confidence=0.9,
            raw_input='install vim'
        )
        solution = {'found': True, 'solution': 'Installing vim'}
        command = Command('nix', ['profile', 'install', 'nixpkgs#vim'], True, False, '')
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_knowledge_base.get_install_methods.return_value = []
        self.mock_execution_engine.build_command.return_value = command
        self.mock_execution_engine.execute.return_value = {
            'success': True, 'output': 'Installed', 'error': '', 'exit_code': 0
        }
        self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
        
        response = self.engine.process(query)
        
        self.assertTrue(response.executed)
        self.assertTrue(response.success)
        self.assertIn("✅ Command executed successfully!", response.text)
        
    def test_process_execute_mode_failure(self):
        """Test process with execution failure"""
        query = {"query": "install badpackage".EXECUTE}
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'target': 'badpackage', 'package': 'badpackage'},
            confidence=0.9,
            raw_input='install badpackage'
        )
        solution = {'found': True, 'solution': 'Installing badpackage'}
        command = Command('nix', ['profile', 'install', 'nixpkgs#badpackage'], True, False, '')
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_knowledge_base.get_install_methods.return_value = []
        self.mock_execution_engine.build_command.return_value = command
        self.mock_execution_engine.execute.return_value = {
            'success': False, 'output': '', 'error': 'Not found', 'exit_code': 1
        }
        self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
        
        response = self.engine.process(query)
        
        self.assertTrue(response.executed)
        self.assertFalse(response.success)
        self.assertIn("❌ Command failed: Not found", response.text)
        
    def test_process_symbiotic_feedback(self):
        """Test feedback requested for symbiotic personality"""
        query = {"query": "help me", personality='symbiotic'}
        intent = Intent(
            type=IntentType.HELP,
            entities={},
            confidence=0.9,
            raw_input='help'
        )
        solution = {'found': True, 'solution': 'Here is help'}
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
        
        response = self.engine.process(query)
        
        self.assertTrue(response.feedback_requested)
        
    def test_build_response_text_generic(self):
        """Test generic response text building"""
        intent = Intent(
            type=IntentType.HELP,
            entities={},
            confidence=0.9,
            raw_input='help'
        )
        solution = {
            'found': True,
            'solution': 'Here is help',
            'example': 'nix --help',
            'explanation': 'Use this for more info'
        }
        
        text = self.engine._build_response_text(intent, solution, "help")
        
        self.assertIn("Here is help", text)
        self.assertIn("nix --help", text)
        self.assertIn("Use this for more info", text)
        
    def test_get_suggestions(self):
        """Test suggestion generation"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'target': 'firefox', 'package': 'firefox'},
            confidence=0.9,
            raw_input='install firefox'
        )
        solution = {
            'found': True,
            'related': ['search firefox', 'remove firefox', None]
        }
        
        suggestions = self.engine._get_suggestions(intent, solution)
        
        self.assertIn("Try: search firefox", suggestions)
        self.assertIn("Try: remove firefox", suggestions)
        self.assertIn("Search first if unsure: 'search <name>'", suggestions)
        self.assertEqual(len(suggestions), 3)  # Limited to 3
        
    def test_get_user_preferences(self):
        """Test getting user preferences"""
        self.mock_learning_system.get_user_preferences.return_value = {
            'favorite_editor': 'vim',
            'install_method': 'declarative'
        }
        
        prefs = self.engine.get_user_preferences('test_user')
        
        self.assertEqual(prefs['favorite_editor'], 'vim')
        self.mock_learning_system.get_user_preferences.assert_called_with('test_user')
        
    def test_get_user_preferences_learning_disabled(self):
        """Test getting user preferences with learning disabled"""
        self.engine.enable_learning = False
        
        prefs = self.engine.get_user_preferences('test_user')
        
        self.assertEqual(prefs, {})
        self.mock_learning_system.get_user_preferences.assert_not_called()
        
    def test_get_system_stats(self):
        """Test getting system statistics"""
        self.mock_personality_system.current_style = PersonalityStyle.FRIENDLY
        self.mock_execution_engine.dry_run = True
        self.mock_learning_system.get_feedback_summary.return_value = {
            'total_interactions': 100,
            'positive_feedback': 85
        }
        
        stats = self.engine.get_system_stats()
        
        self.assertEqual(stats['personality'], 'friendly')
        self.assertTrue(stats['dry_run_mode'])
        self.assertTrue(stats['learning_enabled'])
        self.assertTrue(stats['feedback_enabled'])
        self.assertEqual(stats['learning_stats']['total_interactions'], 100)
        
    def test_get_system_stats_learning_disabled(self):
        """Test system stats with learning disabled"""
        self.engine.enable_learning = False
        
        stats = self.engine.get_system_stats()
        
        self.assertFalse(stats['learning_enabled'])
        self.assertNotIn('learning_stats', stats)
        
    def test_edge_case_empty_query(self):
        """Test handling empty query"""
        query = {"query": "".DRY_RUN}
        intent = Intent(
            type=IntentType.UNKNOWN,
            entities={},
            confidence=0.1,
            raw_input='unknown'
        )
        solution = {'found': False, 'suggestion': 'Please provide a command'}
        
        self.mock_intent_engine.recognize.return_value = intent
        self.mock_knowledge_base.get_solution.return_value = solution
        self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
        
        response = self.engine.process(query)
        
        self.assertIn("Please provide a command", response.text)
        
    def test_command_building_for_all_actions(self):
        """Test command building for all supported actions"""
        test_cases = [
            (IntentType.INSTALL_PACKAGE, 'firefox', True),
            (IntentType.REMOVE, 'firefox', True),
            (IntentType.UPDATE_SYSTEM, None, True),
            (IntentType.SEARCH_PACKAGE, 'python', True),
            (IntentType.ROLLBACK, None, True),
            (IntentType.EXPLAIN, None, True),  # Maps to 'list'
        ]
        
        for intent_type, target, should_have_command in test_cases:
            with self.subTest(intent_type=intent_type):
                query = {"query": f"test {intent_type.value}"}
                intent = Intent(intent_type, target, 0.9)
                solution = {'found': True, 'solution': 'Test'}
                
                self.mock_intent_engine.recognize.return_value = intent
                self.mock_knowledge_base.get_solution.return_value = solution
                self.mock_knowledge_base.get_install_methods.return_value = []
                
                if should_have_command:
                    command = Command('test', ['arg'], True, False, '')
                    self.mock_execution_engine.build_command.return_value = command
                else:
                    self.mock_execution_engine.build_command.return_value = None
                    
                self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
                
                plan = self.engine.plan(query)
                
                if should_have_command:
                    self.assertIsNotNone(plan.command)
                else:
                    self.assertIsNone(plan.command)
                    
    def test_confirmation_requirements(self):
        """Test which actions require confirmation"""
        requires_confirmation = {
            IntentType.REMOVE: True,
            IntentType.UPDATE_SYSTEM: True,
            IntentType.ROLLBACK: True,
            IntentType.INSTALL_PACKAGE: False,
            IntentType.SEARCH_PACKAGE: False,
            IntentType.EXPLAIN: False,
        }
        
        for intent_type, should_confirm in requires_confirmation.items():
            with self.subTest(intent_type=intent_type):
                query = {"query": f"test {intent_type.value}"}
                intent = Intent(intent_type, 'test', 0.9)
                solution = {'found': True, 'solution': 'Test'}
                command = Command('test', ['arg'], True, False, '')
                
                self.mock_intent_engine.recognize.return_value = intent
                self.mock_knowledge_base.get_solution.return_value = solution
                self.mock_knowledge_base.get_install_methods.return_value = []
                self.mock_execution_engine.build_command.return_value = command
                self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
                
                plan = self.engine.plan(query)
                
                self.assertEqual(plan.requires_confirmation, should_confirm)
                
    def test_concurrent_process_calls(self):
        """Test that engine can handle concurrent process calls safely"""
        import threading
        results = []
        
        def process_query(query_text):
            query = {"query": query_text}
            intent = Intent(
            type=IntentType.EXPLAIN,
            entities={},
            confidence=0.9,
            raw_input='info'
        )
            solution = {'found': True, 'solution': 'Info'}
            
            self.mock_intent_engine.recognize.return_value = intent
            self.mock_knowledge_base.get_solution.return_value = solution
            self.mock_personality_system.adapt_response.side_effect = lambda x, y, z: x
            
            response = self.engine.process(query)
            results.append(response)
            
        threads = []
        for i in range(5):
            thread = threading.Thread(target=process_query, args=(f"query {i}",))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # All queries should succeed
        self.assertEqual(len(results), 5)
        for response in results:
            self.assertIsNotNone(response)
            self.assertIsInstance(response, Response)


if __name__ == '__main__':
    unittest.main()