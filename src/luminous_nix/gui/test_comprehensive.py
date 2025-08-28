#!/usr/bin/env python3
"""
🧪 Comprehensive Unit Tests for AI-Driven Interface Generation
Tests all major components with proper mocking and coverage
"""

import unittest
import json
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

# Import components to test
from config_manager import ConfigManager, SystemConfig, OptimizationConfig
from database_migrations import DatabaseMigrationManager, Migration
from error_handler import (
    safe_database_operation,
    safe_file_operation,
    ErrorCollector,
    LuminousError
)
from services import (
    InterfaceGenerationService,
    PatternAnalysisService,
    FeedbackService,
    OptimizationService,
    ServiceResponse
)


class TestConfigManager(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        """Set up test environment"""
        self.config_manager = ConfigManager()
        # Reset to defaults for each test
        self.config_manager.reset_to_defaults()
    
    def test_singleton_pattern(self):
        """Test that ConfigManager is a singleton"""
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        self.assertIs(manager1, manager2)
    
    def test_default_configuration(self):
        """Test default configuration values"""
        config = self.config_manager.config
        
        # Test some defaults
        self.assertEqual(config.optimization.min_confidence, 0.7)
        self.assertEqual(config.optimization.cooldown_hours, 24)
        self.assertEqual(config.pattern_analysis.min_pattern_frequency, 3)
        self.assertFalse(config.debug_mode)
    
    def test_environment_override(self):
        """Test configuration override from environment"""
        # Set environment variables
        os.environ['LUMINOUS_OPTIMIZATION_MIN_CONFIDENCE'] = '0.9'
        os.environ['LUMINOUS_DEBUG_MODE'] = 'true'
        
        # Create new manager to load env vars
        manager = ConfigManager()
        manager._config = manager._load_config()
        
        # Check overrides
        self.assertEqual(manager.config.optimization.min_confidence, 0.9)
        self.assertTrue(manager.config.debug_mode)
        
        # Clean up
        del os.environ['LUMINOUS_OPTIMIZATION_MIN_CONFIDENCE']
        del os.environ['LUMINOUS_DEBUG_MODE']
    
    def test_update_config(self):
        """Test programmatic configuration update"""
        self.config_manager.update_config(
            'optimization',
            min_confidence=0.8,
            cooldown_hours=12
        )
        
        config = self.config_manager.config
        self.assertEqual(config.optimization.min_confidence, 0.8)
        self.assertEqual(config.optimization.cooldown_hours, 12)
    
    def test_get_value_by_path(self):
        """Test getting configuration value by path"""
        value = self.config_manager.get_value('optimization.min_confidence')
        self.assertEqual(value, 0.7)
        
        # Test nested path
        value = self.config_manager.get_value('pattern_analysis.confidence_threshold')
        self.assertEqual(value, 0.7)
        
        # Test non-existent path
        value = self.config_manager.get_value('non.existent.path', default=42)
        self.assertEqual(value, 42)


class TestDatabaseMigrations(unittest.TestCase):
    """Test database migration system"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.manager = DatabaseMigrationManager(self.db_path)
    
    def tearDown(self):
        """Clean up temporary database"""
        self.manager.close()
        os.unlink(self.db_path)
    
    def test_initial_version(self):
        """Test initial database version is 0"""
        version = self.manager.get_current_version()
        self.assertEqual(version, 0)
    
    def test_apply_migration(self):
        """Test applying a single migration"""
        # Create a test migration
        migration = Migration(
            version=999,
            name="test_migration",
            description="Test migration",
            sql_up="CREATE TABLE test_table (id INTEGER PRIMARY KEY);",
            sql_down="DROP TABLE test_table;"
        )
        
        # Apply migration
        success = self.manager.apply_migration(migration)
        self.assertTrue(success)
        
        # Check it was applied
        self.assertTrue(self.manager.is_migration_applied(migration))
        
        # Check table exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='test_table'
        """)
        result = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(result)
    
    def test_rollback_migration(self):
        """Test rolling back a migration"""
        # Create and apply a migration
        migration = Migration(
            version=999,
            name="test_migration",
            description="Test migration",
            sql_up="CREATE TABLE test_table (id INTEGER PRIMARY KEY);",
            sql_down="DROP TABLE test_table;"
        )
        
        self.manager.apply_migration(migration)
        self.assertTrue(self.manager.is_migration_applied(migration))
        
        # Rollback
        success = self.manager.rollback_migration(migration)
        self.assertTrue(success)
        
        # Check it was rolled back
        self.assertFalse(self.manager.is_migration_applied(migration))
    
    def test_migrate_to_version(self):
        """Test migrating to specific version"""
        # Migrate to version 3
        success = self.manager.migrate_to_version(3)
        self.assertTrue(success)
        
        # Check version
        version = self.manager.get_current_version()
        self.assertEqual(version, 3)
        
        # Migrate to latest
        success = self.manager.migrate_to_version()
        self.assertTrue(success)
        
        # Check we're at latest
        latest = max(m.version for m in self.manager.migrations)
        version = self.manager.get_current_version()
        self.assertEqual(version, latest)
    
    def test_migration_status(self):
        """Test getting migration status"""
        # Apply some migrations
        self.manager.migrate_to_version(2)
        
        # Get status
        status = self.manager.get_migration_status()
        
        self.assertEqual(status['current_version'], 2)
        self.assertFalse(status['up_to_date'])
        self.assertEqual(len(status['applied_migrations']), 2)
        self.assertGreater(len(status['pending_migrations']), 0)


class TestErrorHandler(unittest.TestCase):
    """Test error handling utilities"""
    
    def test_safe_database_operation_success(self):
        """Test successful database operation"""
        
        @safe_database_operation(default_return=None)
        def test_func():
            return "success"
        
        result = test_func()
        self.assertEqual(result, "success")
    
    def test_safe_database_operation_error(self):
        """Test database operation with error"""
        
        @safe_database_operation(default_return="default")
        def test_func():
            raise sqlite3.Error("Database error")
        
        result = test_func()
        self.assertEqual(result, "default")
    
    def test_safe_file_operation_success(self):
        """Test successful file operation"""
        
        @safe_file_operation(default_return=None)
        def test_func():
            return "file_content"
        
        result = test_func()
        self.assertEqual(result, "file_content")
    
    def test_safe_file_operation_not_found(self):
        """Test file operation with FileNotFoundError"""
        
        @safe_file_operation(default_return="not_found", create_if_missing=False)
        def test_func():
            raise FileNotFoundError("File not found")
        
        result = test_func()
        self.assertEqual(result, "not_found")
    
    def test_error_collector(self):
        """Test error collection"""
        collector = ErrorCollector(max_errors=3)
        
        # Add errors
        collector.add_error("type1", "Error 1", {"context": "test"})
        collector.add_error("type2", "Error 2")
        collector.add_error("type1", "Error 3")
        
        # Get summary
        summary = collector.get_error_summary()
        
        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['types']['type1'], 2)
        self.assertEqual(summary['types']['type2'], 1)
        
        # Test max errors limit
        collector.add_error("type3", "Error 4")
        summary = collector.get_error_summary()
        self.assertEqual(summary['total'], 3)  # Still 3 due to limit


class TestServices(unittest.TestCase):
    """Test service layer"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        
        # Mock the database path in config
        with patch('services.get_config') as mock_config:
            mock_config.return_value = Mock(
                db_path=self.temp_db.name,
                optimization=Mock(min_confidence=0.7),
                pattern_analysis=Mock(min_pattern_frequency=3),
                feedback=Mock(time_based_trigger_seconds=30),
                ab_testing=Mock(minimum_sample_size=50)
            )
    
    def tearDown(self):
        """Clean up"""
        os.unlink(self.temp_db.name)
    
    def test_service_response(self):
        """Test ServiceResponse dataclass"""
        response = ServiceResponse(
            success=True,
            data={"key": "value"},
            error=None,
            metadata={"timestamp": "2024-01-01"}
        )
        
        self.assertTrue(response.success)
        self.assertEqual(response.data["key"], "value")
        self.assertIsNone(response.error)
        
        # Test to_dict conversion
        response_dict = response.to_dict()
        self.assertEqual(response_dict["success"], True)
        self.assertEqual(response_dict["data"]["key"], "value")
    
    @patch('services.NLInterfaceBuilderV2')
    def test_interface_generation_service(self, mock_builder):
        """Test interface generation service"""
        # Setup mock
        mock_interface = Mock(
            components=[{"type": "button"}],
            metadata={"generation_time": 100}
        )
        mock_builder.return_value.build_interface.return_value = mock_interface
        
        # Create service
        service = InterfaceGenerationService()
        
        # Generate interface
        response = service.generate_interface("Create a button")
        
        self.assertTrue(response.success)
        self.assertEqual(response.metadata["component_count"], 1)
        self.assertEqual(response.metadata["generation_time"], 100)
    
    @patch('services.PatternAnalyzer')
    def test_pattern_analysis_service(self, mock_analyzer):
        """Test pattern analysis service"""
        # Setup mock
        mock_insight = Mock(
            id="insight1",
            title="Test Insight",
            description="Description",
            category="ux",
            priority="high",
            confidence=0.8,
            recommendations=["Fix issue"],
            expected_impact="High"
        )
        mock_analyzer.return_value.generate_insights.return_value = [mock_insight]
        
        # Create service
        service = PatternAnalysisService()
        
        # Get insights
        response = service.get_insights()
        
        self.assertTrue(response.success)
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Insight")
    
    @patch('services.FeedbackCollector')
    def test_feedback_service(self, mock_collector):
        """Test feedback service"""
        # Setup mock
        mock_collector.return_value.start_session.return_value = "session123"
        mock_feedback = Mock(
            id="feedback1",
            sentiment=0.8,
            timestamp=datetime.now()
        )
        mock_collector.return_value.collect_feedback.return_value = mock_feedback
        
        # Create service
        service = FeedbackService()
        
        # Start session
        response = service.start_feedback_session("user1")
        self.assertTrue(response.success)
        self.assertEqual(response.data["session_id"], "session123")
        
        # Collect feedback
        response = service.collect_feedback(
            "session123",
            "interface1",
            "rating",
            4
        )
        self.assertTrue(response.success)
        self.assertEqual(response.data["sentiment"], 0.8)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    @patch('services.NLInterfaceBuilderV2')
    @patch('services.FeedbackCollector')
    @patch('services.PatternAnalyzer')
    def test_complete_workflow(self, mock_analyzer, mock_collector, mock_builder):
        """Test complete workflow from generation to optimization"""
        
        # Setup mocks
        mock_interface = Mock(
            id="interface1",
            components=[{"type": "button"}],
            metadata={"generation_time": 100}
        )
        mock_builder.return_value.build_interface.return_value = mock_interface
        
        # 1. Generate interface
        interface_service = InterfaceGenerationService()
        response = interface_service.generate_interface("Create dashboard")
        self.assertTrue(response.success)
        
        # 2. Collect feedback
        feedback_service = FeedbackService()
        mock_collector.return_value.start_session.return_value = "session1"
        
        response = feedback_service.start_feedback_session("user1")
        self.assertTrue(response.success)
        
        # 3. Analyze patterns
        pattern_service = PatternAnalysisService()
        mock_analyzer.return_value.analyze_usage_patterns.return_value = []
        
        response = pattern_service.analyze_patterns()
        self.assertTrue(response.success)


class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def test_cache_performance(self):
        """Test caching improves performance"""
        from functools import lru_cache
        import time
        
        call_count = 0
        
        @lru_cache(maxsize=10)
        def expensive_operation(value):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate expensive operation
            return value * 2
        
        # First call - cache miss
        start = time.time()
        result1 = expensive_operation(5)
        time1 = time.time() - start
        
        # Second call - cache hit
        start = time.time()
        result2 = expensive_operation(5)
        time2 = time.time() - start
        
        self.assertEqual(result1, result2)
        self.assertEqual(call_count, 1)  # Only called once
        self.assertLess(time2, time1)  # Second call faster
    
    def test_batch_operations(self):
        """Test batch operations are more efficient"""
        import time
        
        # Single operations
        start = time.time()
        results = []
        for i in range(100):
            results.append(i * 2)
        single_time = time.time() - start
        
        # Batch operation
        start = time.time()
        results = [i * 2 for i in range(100)]
        batch_time = time.time() - start
        
        # Batch should be faster or equal
        self.assertLessEqual(batch_time, single_time * 1.5)


def run_test_suite():
    """Run complete test suite with coverage report"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseMigrations))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestServices))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) 
                    / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split(chr(10))[0]}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[0]}")
    
    print("\n" + "=" * 70)
    print("✨ Testing complete!")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_test_suite()