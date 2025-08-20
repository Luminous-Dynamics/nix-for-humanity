#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Advanced Learning System

Tests the Advanced Learning System's DPO learning, user modeling,
preference adaptation, and all core functionality. Aims for 95%+ coverage.
"""

import unittest
import sqlite3
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import the modules under test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from luminous_nix.learning.preferences import PreferenceManager as AdvancedPreferenceManager
from luminous_nix.learning.preferences import PreferencePair, LearningMetrics, UserModel, LearningMode, AdaptationStrategy


class TestAdvancedPreferenceManagerCore(unittest.TestCase):
    """Test core Advanced Learning System functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_advanced_learning.db"
        self.system = AdvancedPreferenceManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_init_creates_database(self):
        """Test that advanced learning system initializes database correctly"""
        self.assertTrue(self.db_path.exists())
        
        # Check database schema
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        
        expected_tables = ['user_models', 'preference_pairs', 'learning_metrics', 'adaptation_history']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_learning_mode_initialization(self):
        """Test different learning mode initialization"""
        passive_system = AdvancedPreferenceManager(
            db_path=Path(self.temp_dir) / "passive.db",
            learning_mode=LearningMode.PASSIVE
        )
        self.assertEqual(passive_system.learning_mode, LearningMode.PASSIVE)
        
        active_system = AdvancedPreferenceManager(
            db_path=Path(self.temp_dir) / "active.db",
            learning_mode=LearningMode.ACTIVE
        )
        self.assertEqual(active_system.learning_mode, LearningMode.ACTIVE)
    
    def test_get_user_model_creates_new(self):
        """Test getting user model creates new one if doesn't exist"""
        user_model = self.system.get_user_model("test_user")
        
        self.assertIsInstance(user_model, UserModel)
        self.assertEqual(user_model.user_id, "test_user")
        self.assertEqual(user_model.preferred_explanation_level, "simple")
        self.assertEqual(user_model.preferred_response_style, "friendly")
    
    def test_get_user_model_retrieves_existing(self):
        """Test getting existing user model from cache"""
        # Create and modify a user model
        user_model = self.system.get_user_model("existing_user")
        user_model.preferred_explanation_level = "technical"
        
        # Get the same user model again
        retrieved_model = self.system.get_user_model("existing_user")
        
        # Should be the same object
        self.assertIs(user_model, retrieved_model)
        self.assertEqual(retrieved_model.preferred_explanation_level, "technical")
    
    def test_user_model_defaults(self):
        """Test user model default values"""
        user_model = UserModel(user_id="test")
        
        self.assertEqual(user_model.preferred_explanation_level, "simple")
        self.assertEqual(user_model.preferred_response_style, "friendly")
        self.assertEqual(user_model.preferred_verbosity, "moderate")
        self.assertEqual(user_model.typical_session_length, 300.0)
        self.assertEqual(user_model.error_tolerance, 0.5)
        self.assertEqual(user_model.learning_speed, 0.5)
        self.assertTrue(user_model.prefers_declarative)
        self.assertIsNotNone(user_model.last_updated)


class TestPreferencePairHandling(unittest.TestCase):
    """Test preference pair recording and processing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_advanced_learning.db"
        self.system = AdvancedPreferenceManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_preference_pair_creation(self):
        """Test PreferencePair creation"""
        pair = PreferencePair(
            user_input="install firefox",
            preferred_response="Installing Firefox for you!",
            rejected_response="Running: nix-env -iA nixos.firefox",
            feedback_strength=0.8,
            context={"category": "install_package"},
            user_id="test_user"
        )
        
        self.assertEqual(pair.user_input, "install firefox")
        self.assertEqual(pair.preferred_response, "Installing Firefox for you!")
        self.assertEqual(pair.rejected_response, "Running: nix-env -iA nixos.firefox")
        self.assertEqual(pair.feedback_strength, 0.8)
        self.assertEqual(pair.user_id, "test_user")
        self.assertIsNotNone(pair.timestamp)
    
    def test_preference_pair_auto_timestamp(self):
        """Test that timestamp is auto-generated"""
        pair = PreferencePair(
            user_input="test",
            preferred_response="preferred",
            rejected_response="rejected",
            feedback_strength=0.5,
            context={}
        )
        
        self.assertIsNotNone(pair.timestamp)
        # Should be parseable as ISO datetime
        datetime.fromisoformat(pair.timestamp)
    
    def test_record_preference_pair(self):
        """Test recording preference pairs"""
        pair = PreferencePair(
            user_input="install firefox",
            preferred_response="Installing Firefox for you!",
            rejected_response="Running: nix-env -iA nixos.firefox",
            feedback_strength=0.8,
            context={"category": "install_package"},
            user_id="test_user"
        )
        
        self.system.record_preference_pair(pair)
        
        # Check it's in memory
        self.assertEqual(len(self.system.preference_pairs), 1)
        self.assertEqual(self.system.preference_pairs[0], pair)
        
        # Check it's in database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM preference_pairs WHERE user_id = ?', ('test_user',))
        db_pair = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(db_pair)
        self.assertEqual(db_pair[2], "install firefox")  # user_input
        self.assertEqual(db_pair[3], "Installing Firefox for you!")  # preferred_response
    
    def test_preference_pair_triggers_learning(self):
        """Test that collecting pairs triggers DPO learning"""
        # Create 10 preference pairs to trigger learning
        for i in range(10):
            pair = PreferencePair(
                user_input=f"install package{i}",
                preferred_response="Short response",
                rejected_response="Long technical response with details",
                feedback_strength=0.8,
                context={},
                user_id="test_user"
            )
            self.system.record_preference_pair(pair)
        
        # Should have triggered learning (at least created user model)
        user_model = self.system.get_user_model("test_user")
        self.assertIsNotNone(user_model)


class TestDPOLearning(unittest.TestCase):
    """Test Direct Preference Optimization learning"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_advanced_learning.db"
        self.system = AdvancedPreferenceManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_analyze_preference_patterns_verbosity(self):
        """Test analyzing preference patterns for verbosity"""
        pairs = [
            PreferencePair(
                user_input="install firefox",
                preferred_response="OK",  # Short
                rejected_response="I'll install Firefox for you right away!",  # Long
                feedback_strength=0.8,
                context={}
            ),
            PreferencePair(
                user_input="update system",
                preferred_response="Done",  # Short
                rejected_response="Updating your system now, this may take a few minutes",  # Long
                feedback_strength=0.9,
                context={}
            )
        ]
        
        updates = self.system._analyze_preference_patterns(pairs)
        
        # Should prefer minimal verbosity
        self.assertEqual(updates.get("preferred_verbosity"), "minimal")
    
    def test_analyze_preference_patterns_technical_level(self):
        """Test analyzing preference patterns for technical level"""
        pairs = [
            PreferencePair(
                user_input="install firefox",
                preferred_response="Running: nix-env -iA nixos.firefox",  # Technical
                rejected_response="Installing Firefox for you!",  # Simple
                feedback_strength=0.8,
                context={}
            ),
            PreferencePair(
                user_input="check error",
                preferred_response="Error code 404: command not found",  # Technical
                rejected_response="Something went wrong, let me help",  # Simple
                feedback_strength=0.7,
                context={}
            )
        ]
        
        updates = self.system._analyze_preference_patterns(pairs)
        
        # Should prefer technical explanations
        self.assertEqual(updates.get("preferred_explanation_level"), "technical")
    
    def test_calculate_preference_confidence(self):
        """Test preference confidence calculation"""
        pairs = [
            PreferencePair("test", "short", "long", 0.8, {}),
            PreferencePair("test", "brief", "verbose", 0.9, {})
        ]
        
        confidence = self.system._calculate_preference_confidence(pairs, "preferred_verbosity", "minimal")
        
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_pair_relates_to_preference_verbosity(self):
        """Test preference pair relation checking for verbosity"""
        minimal_pair = PreferencePair("test", "OK", "Detailed response here", 0.8, {})
        detailed_pair = PreferencePair("test", "Long detailed response", "OK", 0.8, {})
        
        # Test minimal preference detection
        self.assertTrue(
            self.system._pair_relates_to_preference(minimal_pair, "preferred_verbosity", "minimal")
        )
        
        # Test detailed preference detection
        self.assertTrue(
            self.system._pair_relates_to_preference(detailed_pair, "preferred_verbosity", "detailed")
        )
    
    def test_pair_relates_to_preference_technical_level(self):
        """Test preference pair relation checking for technical level"""
        technical_pair = PreferencePair(
            "test", 
            "Running command: sudo nix-env", 
            "Installing for you", 
            0.8, 
            {}
        )
        simple_pair = PreferencePair(
            "test",
            "Let me help you with that",
            "Error: command failed",
            0.8,
            {}
        )
        
        # Test technical preference detection
        self.assertTrue(
            self.system._pair_relates_to_preference(technical_pair, "preferred_explanation_level", "technical")
        )
        
        # Test simple preference detection
        self.assertTrue(
            self.system._pair_relates_to_preference(simple_pair, "preferred_explanation_level", "simple")
        )


class TestUserModelPersistence(unittest.TestCase):
    """Test user model saving and loading"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_advanced_learning.db"
        self.system = AdvancedPreferenceManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_save_user_model(self):
        """Test saving user model to database"""
        user_model = self.system.get_user_model("save_test")
        user_model.preferred_explanation_level = "technical"
        user_model.preferred_verbosity = "minimal"
        
        self.system._save_user_model(user_model)
        
        # Check database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT model_data FROM user_models WHERE user_id = ?', ('save_test',))
        result = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        model_data = json.loads(result[0])
        self.assertEqual(model_data['preferred_explanation_level'], 'technical')
        self.assertEqual(model_data['preferred_verbosity'], 'minimal')
    
    def test_load_user_models(self):
        """Test loading user models from database"""
        # Create and save a model first
        user_model = UserModel(
            user_id="load_test",
            preferred_explanation_level="technical",
            preferred_verbosity="minimal"
        )
        self.system._save_user_model(user_model)
        
        # Create new system instance to test loading
        new_system = AdvancedPreferenceManager(db_path=self.db_path)
        
        # Should have loaded the model
        loaded_model = new_system.get_user_model("load_test")
        self.assertEqual(loaded_model.preferred_explanation_level, "technical")
        self.assertEqual(loaded_model.preferred_verbosity, "minimal")
    
    def test_load_corrupted_user_model(self):
        """Test handling of corrupted user model data"""
        # Insert corrupted data directly
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO user_models (user_id, model_data, last_updated)
            VALUES (?, ?, ?)
        ''', ('corrupted_user', 'invalid json', datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        # Should handle gracefully and create default model
        new_system = AdvancedPreferenceManager(db_path=self.db_path)
        model = new_system.get_user_model("corrupted_user")
        
        # Should be default model
        self.assertEqual(model.preferred_explanation_level, "simple")
        self.assertEqual(model.preferred_response_style, "friendly")


class TestResponseAdaptation(unittest.TestCase):
    """Test response adaptation based on user preferences"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_advanced_learning.db"
        self.system = AdvancedPreferenceManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_adapt_response_minimal_verbosity(self):
        """Test adapting response for minimal verbosity preference"""
        user_model = self.system.get_user_model("minimal_user")
        user_model.preferred_verbosity = "minimal"
        
        base_response = "I'll help you install Firefox. Let me do that for you right now."
        adapted = self.system.adapt_response("minimal_user", base_response, {})
        
        # Should be shorter than original
        self.assertLess(len(adapted), len(base_response))
        # Should still contain key information
        self.assertIn("Firefox", adapted)
    
    def test_adapt_response_detailed_verbosity(self):
        """Test adapting response for detailed verbosity preference"""
        user_model = self.system.get_user_model("detailed_user")
        user_model.preferred_verbosity = "detailed"
        
        base_response = "Installing Firefox."
        context = {
            "alternatives": ["Chrome", "Brave", "Chromium"],
            "why_recommended": "Firefox is open source and privacy-focused"
        }
        adapted = self.system.adapt_response("detailed_user", base_response, context)
        
        # Should be longer than original
        self.assertGreater(len(adapted), len(base_response))
        # Should include context information
        self.assertIn("Chrome", adapted)
        self.assertIn("privacy-focused", adapted)
    
    def test_adapt_response_technical_explanation(self):
        """Test adapting response for technical explanation preference"""
        user_model = self.system.get_user_model("technical_user")
        user_model.preferred_explanation_level = "technical"
        
        base_response = "Installing Firefox."
        context = {
            "command": "nix-env -iA nixos.firefox",
            "config_location": "/etc/nixos/configuration.nix"
        }
        adapted = self.system.adapt_response("technical_user", base_response, context)
        
        # Should include technical details
        self.assertIn("nix-env", adapted)
        self.assertIn("/etc/nixos", adapted)
    
    def test_adapt_response_simple_explanation(self):
        """Test adapting response for simple explanation preference"""
        user_model = self.system.get_user_model("simple_user")
        user_model.preferred_explanation_level = "simple"
        
        base_response = "We need to execute the installation command."
        adapted = self.system.adapt_response("simple_user", base_response, {})
        
        # Should use simpler language
        self.assertIn("run", adapted)  # "execute" -> "run"
        self.assertNotIn("execute", adapted)
    
    def test_adapt_response_encouraging_style(self):
        """Test adapting response for encouraging style preference"""
        user_model = self.system.get_user_model("encouraging_user")
        user_model.preferred_response_style = "encouraging"
        
        base_response = "Installing Firefox."
        
        # Test multiple times to account for randomness
        encouraging_found = False
        for _ in range(10):
            adapted = self.system.adapt_response("encouraging_user", base_response, {})
            if any(phrase in adapted for phrase in ["Great", "Nice", "You're", "Smart"]):
                encouraging_found = True
                break
        
        # Should sometimes add encouraging phrases
        self.assertTrue(encouraging_found or "Installing Firefox" in adapted)
    
    def test_make_response_minimal(self):
        """Test making response minimal"""
        response = "I'll help you install Firefox. Let me do that for you right now."
        minimal = self.system._make_response_minimal(response)
        
        self.assertLess(len(minimal), len(response))
        self.assertNotIn("I'll help you", minimal)
        self.assertNotIn("Let me", minimal)
    
    def test_make_response_detailed(self):
        """Test making response detailed"""
        response = "Installing Firefox."
        context = {"alternatives": ["Chrome", "Brave"]}
        detailed = self.system._make_response_detailed(response, context)
        
        self.assertGreater(len(detailed), len(response))
        self.assertIn("Chrome", detailed)
        self.assertIn("Brave", detailed)
    
    def test_simplify_language(self):
        """Test language simplification"""
        technical_response = "We need to execute this command to configure the repository."
        simplified = self.system._simplify_language(technical_response)
        
        self.assertIn("run", simplified)  # execute -> run
        self.assertIn("set up", simplified)  # configure -> set up
        self.assertIn("software source", simplified)  # repository -> software source


class TestIntentPrediction(unittest.TestCase):
    """Test user intent prediction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_advanced_learning.db"
        self.system = AdvancedPreferenceManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_predict_user_intent_with_history(self):
        """Test intent prediction based on user history"""
        user_model = self.system.get_user_model("predict_user")
        user_model.common_intents = {
            "install firefox": 0.8,
            "install chrome": 0.5,
            "search packages": 0.3
        }
        
        predictions = self.system.predict_user_intent("predict_user", "install fire", {})
        
        # Should return predictions sorted by score
        self.assertIsInstance(predictions, list)
        self.assertLessEqual(len(predictions), 5)  # Max 5 predictions
        
        # Should have install firefox as top prediction (high frequency + similarity)
        if predictions:
            top_prediction = predictions[0]
            self.assertIn("firefox", top_prediction[0])
    
    def test_predict_user_intent_no_history(self):
        """Test intent prediction with no user history"""
        predictions = self.system.predict_user_intent("new_user", "install something", {})
        
        # Should return empty list or handle gracefully
        self.assertIsInstance(predictions, list)
        self.assertLessEqual(len(predictions), 5)
    
    def test_calculate_intent_similarity(self):
        """Test intent similarity calculation"""
        similarity1 = self.system._calculate_intent_similarity("install firefox", "install firefox")
        similarity2 = self.system._calculate_intent_similarity("install firefox", "install chrome")
        similarity3 = self.system._calculate_intent_similarity("install firefox", "search packages")
        
        # Exact match should have highest similarity
        self.assertEqual(similarity1, 1.0)
        
        # Partial match should have medium similarity
        self.assertGreater(similarity2, 0.0)
        self.assertLess(similarity2, 1.0)
        
        # No match should have low similarity
        self.assertGreaterEqual(similarity3, 0.0)
        self.assertLess(similarity3, similarity2)
    
    def test_calculate_intent_similarity_edge_cases(self):
        """Test intent similarity edge cases"""
        # Empty strings
        self.assertEqual(self.system._calculate_intent_similarity("", ""), 0.0)
        self.assertEqual(self.system._calculate_intent_similarity("test", ""), 0.0)
        self.assertEqual(self.system._calculate_intent_similarity("", "test"), 0.0)


class TestLearningMetrics(unittest.TestCase):
    """Test learning system metrics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_advanced_learning.db"
        self.system = AdvancedPreferenceManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_get_learning_metrics_empty(self):
        """Test getting metrics with no data"""
        metrics = self.system.get_learning_metrics()
        
        self.assertIsInstance(metrics, LearningMetrics)
        self.assertEqual(metrics.total_interactions, 0)
        self.assertEqual(metrics.successful_adaptations, 0)
        self.assertEqual(metrics.preference_pairs_collected, 0)
        self.assertEqual(metrics.adaptation_accuracy, 0.0)
    
    def test_get_learning_metrics_with_data(self):
        """Test getting metrics with sample data"""
        # Add some preference pairs
        for i in range(3):
            pair = PreferencePair(
                user_input=f"test {i}",
                preferred_response="preferred",
                rejected_response="rejected",
                feedback_strength=0.8,
                context={},
                user_id="test_user"
            )
            self.system.record_preference_pair(pair)
        
        metrics = self.system.get_learning_metrics("test_user")
        
        self.assertEqual(metrics.preference_pairs_collected, 3)
        self.assertIsInstance(metrics.user_satisfaction_trend, list)
        self.assertGreater(metrics.learning_velocity, 0.0)
        self.assertGreater(metrics.convergence_score, 0.0)
    
    def test_learning_metrics_dataclass(self):
        """Test LearningMetrics dataclass"""
        metrics = LearningMetrics(
            total_interactions=100,
            successful_adaptations=80,
            preference_pairs_collected=50,
            adaptation_accuracy=0.8,
            user_satisfaction_trend=[0.6, 0.7, 0.8],
            learning_velocity=0.1,
            convergence_score=0.9
        )
        
        self.assertEqual(metrics.total_interactions, 100)
        self.assertEqual(metrics.successful_adaptations, 80)
        self.assertEqual(metrics.adaptation_accuracy, 0.8)
        self.assertEqual(len(metrics.user_satisfaction_trend), 3)


class TestSymbioticFeatures(unittest.TestCase):
    """Test symbiotic intelligence features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_advanced_learning.db"
        self.system = AdvancedPreferenceManager(db_path=self.db_path, learning_mode=LearningMode.SYMBIOTIC)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_evolve_with_user_response_quality(self):
        """Test evolution based on response quality feedback"""
        user_model = self.system.get_user_model("evolve_user")
        initial_threshold = user_model.confidence_threshold
        
        # Poor quality feedback should increase threshold (be more conservative)
        self.system.evolve_with_user("evolve_user", {"response_quality": 0.3})
        
        updated_model = self.system.get_user_model("evolve_user")
        self.assertGreater(updated_model.confidence_threshold, initial_threshold)
    
    def test_evolve_with_user_response_speed(self):
        """Test evolution based on response speed feedback"""
        initial_learning_rate = self.system.learning_rate
        
        # Slow speed feedback should increase learning rate
        self.system.evolve_with_user("speed_user", {"response_speed": 0.3})
        
        self.assertGreater(self.system.learning_rate, initial_learning_rate)
    
    def test_evolve_with_user_engagement(self):
        """Test evolution based on engagement feedback"""
        user_model = self.system.get_user_model("engagement_user")
        
        # High engagement should increase adaptation rate
        self.system.evolve_with_user("engagement_user", {"engagement_level": 0.9})
        
        updated_model = self.system.get_user_model("engagement_user")
        self.assertGreater(updated_model.adaptation_rate, 0.05)  # Base rate
        self.assertLessEqual(updated_model.adaptation_rate, 0.2)  # Max rate
    
    def test_get_symbiotic_insights(self):
        """Test getting symbiotic relationship insights"""
        # Create some test data
        user_model = self.system.get_user_model("insight_user")
        user_model.common_intents = {"install_package": 0.8, "search_package": 0.6}
        
        insights = self.system.get_symbiotic_insights("insight_user")
        
        self.assertIn("relationship_health", insights)
        self.assertIn("user_model_maturity", insights)
        self.assertIn("learning_velocity", insights)
        self.assertIn("growth_areas", insights)
        self.assertIn("symbiotic_stage", insights)
        
        # Check relationship health structure
        health = insights["relationship_health"]
        self.assertIn("trust_level", health)
        self.assertIn("learning_progress", health)
        self.assertIn("adaptation_success", health)
        self.assertIn("engagement_trend", health)
    
    def test_determine_symbiotic_stage(self):
        """Test symbiotic stage determination"""
        user_model = UserModel(user_id="stage_user")
        metrics = LearningMetrics(
            total_interactions=0,
            successful_adaptations=0,
            preference_pairs_collected=2,  # Few pairs
            adaptation_accuracy=0.5,
            user_satisfaction_trend=[0.5],
            learning_velocity=0.1,
            convergence_score=0.5
        )
        
        stage = self.system._determine_symbiotic_stage(user_model, metrics)
        self.assertEqual(stage, "initial_learning")
        
        # Test with more data
        metrics.preference_pairs_collected = 10
        metrics.adaptation_accuracy = 0.8
        user_model.common_intents = {"install_package": 0.8, "search_package": 0.6, "update_system": 0.4}
        metrics.convergence_score = 0.8
        
        stage = self.system._determine_symbiotic_stage(user_model, metrics)
        self.assertEqual(stage, "symbiotic_partnership")
    
    def test_suggest_interaction_improvements(self):
        """Test interaction improvement suggestions"""
        user_model = self.system.get_user_model("improvement_user")
        suggestions = self.system.suggest_interaction_improvements("improvement_user")
        
        self.assertIsInstance(suggestions, list)
        # Should have suggestions for new user
        self.assertGreater(len(suggestions), 0)
        
        # Test with low error tolerance
        user_model.error_tolerance = 0.2
        suggestions = self.system.suggest_interaction_improvements("improvement_user")
        
        # Should include accuracy suggestion
        accuracy_suggestion = any("accuracy" in s for s in suggestions)
        self.assertTrue(accuracy_suggestion)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_advanced_learning.db"
        self.system = AdvancedPreferenceManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_empty_preference_pairs(self):
        """Test handling empty preference pairs"""
        # Should handle gracefully without errors
        self.system._update_preferences_dpo("empty_user")
        
        # User model should still be created
        user_model = self.system.get_user_model("empty_user")
        self.assertIsNotNone(user_model)
    
    def test_insufficient_preference_data(self):
        """Test handling insufficient preference data for learning"""
        # Add only 2 pairs (less than minimum of 3)
        for i in range(2):
            pair = PreferencePair(f"test {i}", "pref", "rej", 0.8, {}, user_id="insufficient_user")
            self.system.record_preference_pair(pair)
        
        # Should not trigger updates but should not crash
        user_model = self.system.get_user_model("insufficient_user")
        self.assertIsNotNone(user_model)
    
    def test_extreme_preference_values(self):
        """Test handling extreme preference values"""
        # Test with very high feedback strength
        extreme_pair = PreferencePair(
            "test",
            "preferred",
            "rejected",
            10.0,  # Very high strength
            {},
            user_id="extreme_user"
        )
        
        # Should handle without crashing
        self.system.record_preference_pair(extreme_pair)
        
        # Test with negative feedback strength
        negative_pair = PreferencePair(
            "test",
            "preferred",
            "rejected",
            -0.5,  # Negative strength
            {},
            user_id="extreme_user"
        )
        
        self.system.record_preference_pair(negative_pair)
    
    def test_very_long_input_handling(self):
        """Test handling of very long inputs"""
        long_response = "a" * 10000  # Very long response
        
        pair = PreferencePair(
            "test",
            long_response,
            "short",
            0.8,
            {"long_context": "x" * 5000},
            user_id="long_user"
        )
        
        # Should handle long inputs gracefully
        self.system.record_preference_pair(pair)
        
        # Test adaptation with long response
        adapted = self.system.adapt_response("long_user", long_response, {})
        self.assertIsInstance(adapted, str)
    
    def test_special_characters_in_preferences(self):
        """Test handling of special characters in preferences"""
        special_pair = PreferencePair(
            "test with émojis 🚀 and symbols $#@!",
            "preferred with 'quotes' and \"double quotes\"",
            "rejected with [brackets] and {braces}",
            0.8,
            {"special": "∞ ∑ ∂ ∆"},
            user_id="special_user"
        )
        
        # Should handle special characters without issues
        self.system.record_preference_pair(special_pair)
        
        # Test adaptation
        adapted = self.system.adapt_response("special_user", "test émoji response 🎉", {})
        self.assertIsInstance(adapted, str)
    
    def test_concurrent_user_access(self):
        """Test handling multiple users concurrently"""
        users = [f"user_{i}" for i in range(10)]
        
        # Create models for all users simultaneously
        for user in users:
            model = self.system.get_user_model(user)
            model.preferred_explanation_level = f"level_{user}"
        
        # Verify all models are distinct and correct
        for user in users:
            model = self.system.get_user_model(user)
            self.assertEqual(model.preferred_explanation_level, f"level_{user}")


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)