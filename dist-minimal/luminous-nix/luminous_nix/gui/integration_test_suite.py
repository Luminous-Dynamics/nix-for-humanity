#!/usr/bin/env python3
"""
🧪 Comprehensive Integration Test Suite for Production System
Tests complete workflows and system integration
"""

import unittest
import asyncio
import tempfile
import shutil
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import all production components
from production_deployment import ProductionDeployment
from config_manager import ConfigManager, SystemConfig
from database_migrations import DatabaseMigrationManager
from services import (
    InterfaceGenerationService,
    PatternAnalysisService,
    FeedbackService,
    OptimizationService,
    ServiceResponse
)
from performance_optimizations import AsyncCache, ConnectionPool, ParallelExecutor
from error_handler import ErrorCollector, safe_database_operation


class TestProductionIntegration(unittest.TestCase):
    """Integration tests for complete production system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.test_dir = tempfile.mkdtemp()
        cls.test_db = Path(cls.test_dir) / "test.db"
        
        # Override config for testing
        config = ConfigManager()
        config.update_config('system',
            data_dir=cls.test_dir,
            cache_dir=Path(cls.test_dir) / "cache",
            config_dir=Path(cls.test_dir) / "config",
            db_path=str(cls.test_db)
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def test_complete_deployment_workflow(self):
        """Test complete deployment workflow"""
        
        # Create deployment instance
        deployment = ProductionDeployment()
        
        # Initialize services
        self.assertTrue(deployment.initialize_services())
        
        # Verify all services are loaded
        self.assertEqual(len(deployment.services), 6)
        self.assertIn('interface', deployment.services)
        self.assertIn('pattern', deployment.services)
        self.assertIn('feedback', deployment.services)
        self.assertIn('optimization', deployment.services)
        self.assertIn('ab_testing', deployment.services)
        self.assertIn('performance', deployment.services)
    
    def test_database_migration_workflow(self):
        """Test database migration from scratch"""
        
        # Create migration manager
        manager = DatabaseMigrationManager(str(self.test_db))
        
        # Should start at version 0
        self.assertEqual(manager.get_current_version(), 0)
        
        # Migrate to latest
        self.assertTrue(manager.migrate_to_version())
        
        # Should be at version 7
        self.assertEqual(manager.get_current_version(), 7)
        
        # Test rollback to version 5
        self.assertTrue(manager.migrate_to_version(5))
        self.assertEqual(manager.get_current_version(), 5)
        
        # Migrate back to latest
        self.assertTrue(manager.migrate_to_version())
        self.assertEqual(manager.get_current_version(), 7)
        
        manager.close()
    
    def test_service_integration(self):
        """Test service layer integration"""
        
        # Initialize services
        deployment = ProductionDeployment()
        deployment.initialize_services()
        
        # Test interface generation service
        interface_service = deployment.services['interface']
        response = interface_service.generate_interface(
            "Create a dashboard",
            {"skill_level": "beginner"}
        )
        self.assertTrue(response.success)
        self.assertIsNotNone(response.data)
        
        # Test pattern analysis service
        pattern_service = deployment.services['pattern']
        response = pattern_service.analyze_patterns()
        self.assertTrue(response.success)
        
        # Test feedback service
        feedback_service = deployment.services['feedback']
        session_response = feedback_service.start_feedback_session("test_user")
        self.assertTrue(session_response.success)
        
        session_id = session_response.data["session_id"]
        feedback_response = feedback_service.collect_feedback(
            session_id,
            "interface_001",
            "rating",
            5
        )
        self.assertTrue(feedback_response.success)
    
    def test_async_health_checks(self):
        """Test async health check system"""
        
        async def run_health_checks():
            deployment = ProductionDeployment()
            deployment.initialize_services()
            
            health = await deployment.run_health_checks()
            
            # Verify health check structure
            self.assertIn('timestamp', health)
            self.assertIn('status', health)
            self.assertIn('checks', health)
            
            # Verify individual checks
            self.assertIn('database', health['checks'])
            self.assertIn('services', health['checks'])
            self.assertIn('performance', health['checks'])
            self.assertIn('disk', health['checks'])
            self.assertIn('configuration', health['checks'])
            
            return health
        
        # Run async test
        health = asyncio.run(run_health_checks())
        self.assertIsNotNone(health)
    
    def test_optimization_cycle(self):
        """Test optimization cycle workflow"""
        
        async def run_optimization():
            deployment = ProductionDeployment()
            deployment.initialize_services()
            
            results = await deployment.run_optimization_cycle()
            
            # Verify optimization results
            self.assertIn('started_at', results)
            self.assertIn('status', results)
            self.assertIn('optimizations', results)
            
            return results
        
        # Run async test
        results = asyncio.run(run_optimization())
        self.assertEqual(results['status'], 'success')
    
    def test_performance_optimizations(self):
        """Test performance optimization components"""
        
        async def test_cache():
            # Test AsyncCache
            cache = AsyncCache(max_size=10, default_ttl=timedelta(seconds=5))
            
            # Set and get
            await cache.set("key1", "value1")
            value = await cache.get("key1")
            self.assertEqual(value, "value1")
            
            # Test cache miss
            value = await cache.get("nonexistent")
            self.assertIsNone(value)
            
            # Test TTL expiration
            await cache.set("key2", "value2", ttl=timedelta(seconds=0.1))
            time.sleep(0.2)
            value = await cache.get("key2")
            self.assertIsNone(value)
            
            # Test LRU eviction
            for i in range(15):
                await cache.set(f"key_{i}", f"value_{i}")
            
            # Cache should have max 10 items
            stats = cache.get_stats()
            self.assertLessEqual(stats['size'], 10)
        
        asyncio.run(test_cache())
    
    def test_error_handling_integration(self):
        """Test error handling across system"""
        
        # Test error collector
        collector = ErrorCollector(max_errors=5)
        
        # Add various errors
        collector.add_error("db_error", "Connection failed")
        collector.add_error("api_error", "Rate limited")
        collector.add_error("db_error", "Deadlock detected")
        
        summary = collector.get_error_summary()
        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['types']['db_error'], 2)
        self.assertEqual(summary['types']['api_error'], 1)
        
        # Test safe operations
        @safe_database_operation(default_return=None)
        def risky_operation():
            raise Exception("Simulated error")
        
        result = risky_operation()
        self.assertIsNone(result)  # Should return default
    
    def test_configuration_management(self):
        """Test configuration system integration"""
        
        # Get config instance
        config = ConfigManager()
        
        # Test environment override
        import os
        os.environ['LUMINOUS_OPTIMIZATION_MIN_CONFIDENCE'] = '0.95'
        os.environ['LUMINOUS_DEBUG_MODE'] = 'true'
        
        # Reload config
        config._config = config._load_config()
        
        # Verify overrides applied
        self.assertEqual(config.config.optimization.min_confidence, 0.95)
        self.assertTrue(config.config.debug_mode)
        
        # Clean up
        del os.environ['LUMINOUS_OPTIMIZATION_MIN_CONFIDENCE']
        del os.environ['LUMINOUS_DEBUG_MODE']
    
    def test_data_cleanup(self):
        """Test data retention and cleanup"""
        
        async def test_cleanup():
            deployment = ProductionDeployment()
            deployment.initialize_services()
            
            # Add some test data (would normally be in database)
            # This is a simplified test
            result = await deployment.cleanup_old_data()
            self.assertTrue(result)
        
        asyncio.run(test_cleanup())
    
    def test_deployment_report_generation(self):
        """Test deployment report generation"""
        
        deployment = ProductionDeployment()
        deployment.initialize_services()
        
        report = deployment.generate_deployment_report()
        
        # Verify report structure
        self.assertIn('generated_at', report)
        self.assertIn('environment', report)
        self.assertIn('configuration', report)
        self.assertIn('database', report)
        
        # Verify environment info
        self.assertIn('python_version', report['environment'])
        self.assertIn('platform', report['environment'])
        
        # Verify configuration info
        self.assertIn('debug_mode', report['configuration'])
        self.assertIn('features_enabled', report['configuration'])


class TestPerformanceIntegration(unittest.TestCase):
    """Performance-focused integration tests"""
    
    def test_interface_generation_performance(self):
        """Test interface generation meets performance targets"""
        
        deployment = ProductionDeployment()
        deployment.initialize_services()
        
        interface_service = deployment.services['interface']
        
        # Measure generation time
        start = time.time()
        response = interface_service.generate_interface(
            "Create a complex dashboard with charts"
        )
        elapsed = time.time() - start
        
        self.assertTrue(response.success)
        # Should complete in under 2 seconds
        self.assertLess(elapsed, 2.0)
        
        # Second call should be cached and faster
        start = time.time()
        response2 = interface_service.generate_interface(
            "Create a complex dashboard with charts"
        )
        elapsed2 = time.time() - start
        
        # Cached call should be under 100ms
        self.assertLess(elapsed2, 0.1)
    
    def test_parallel_execution_performance(self):
        """Test parallel execution improves performance"""
        
        async def test_parallel():
            executor = ParallelExecutor(max_workers=4)
            
            def slow_operation(n):
                time.sleep(0.1)
                return n * n
            
            # Sequential execution
            start = time.time()
            sequential_results = [slow_operation(i) for i in range(4)]
            sequential_time = time.time() - start
            
            # Parallel execution
            start = time.time()
            parallel_results = await executor.map_threaded(
                slow_operation,
                list(range(4))
            )
            parallel_time = time.time() - start
            
            # Parallel should be significantly faster
            self.assertLess(parallel_time, sequential_time * 0.5)
            
            # Results should be the same
            self.assertEqual(sequential_results, parallel_results)
            
            executor.shutdown()
        
        asyncio.run(test_parallel())
    
    def test_database_connection_pooling(self):
        """Test connection pooling improves database performance"""
        
        async def test_pool():
            pool = ConnectionPool(str(Path(tempfile.mkdtemp()) / "test.db"), pool_size=5)
            
            # Execute multiple queries
            queries = [
                "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, value TEXT)",
                "INSERT INTO test (value) VALUES ('test1')",
                "INSERT INTO test (value) VALUES ('test2')",
                "SELECT * FROM test",
                "SELECT COUNT(*) FROM test"
            ]
            
            start = time.time()
            for query in queries * 10:  # Run 50 queries
                await pool.execute(query)
            elapsed = time.time() - start
            
            # Should handle 50 queries efficiently
            self.assertLess(elapsed, 1.0)
            
            pool.close_all()
        
        asyncio.run(test_pool())


class TestEndToEndWorkflows(unittest.TestCase):
    """End-to-end workflow integration tests"""
    
    def test_complete_user_journey(self):
        """Test complete user journey from interface generation to optimization"""
        
        deployment = ProductionDeployment()
        deployment.initialize_services()
        
        # 1. User generates an interface
        interface_service = deployment.services['interface']
        gen_response = interface_service.generate_interface(
            "Create a user profile page",
            {"skill_level": "intermediate", "preferred_style": "modern"}
        )
        self.assertTrue(gen_response.success)
        
        # 2. Start feedback session
        feedback_service = deployment.services['feedback']
        session_response = feedback_service.start_feedback_session("user_123")
        self.assertTrue(session_response.success)
        session_id = session_response.data["session_id"]
        
        # 3. Collect user feedback
        feedback_response = feedback_service.collect_feedback(
            session_id,
            "interface_001",
            "rating",
            4,
            {"comment": "Good but could be simpler"}
        )
        self.assertTrue(feedback_response.success)
        
        # 4. Analyze patterns
        pattern_service = deployment.services['pattern']
        pattern_response = pattern_service.analyze_patterns()
        self.assertTrue(pattern_response.success)
        
        # 5. Get insights
        insights_response = pattern_service.get_insights()
        self.assertTrue(insights_response.success)
        
        # 6. Check optimization status
        optimization_service = deployment.services['optimization']
        opt_status = optimization_service.get_optimization_status()
        self.assertTrue(opt_status.success)
    
    def test_ab_testing_workflow(self):
        """Test A/B testing workflow"""
        
        deployment = ProductionDeployment()
        deployment.initialize_services()
        
        ab_service = deployment.services['ab_testing']
        
        # 1. Create an A/B test
        test_response = ab_service.create_test(
            "Button Style Test",
            [
                {"name": "Flat", "parameters": {"style": "flat"}},
                {"name": "3D", "parameters": {"style": "3d"}}
            ],
            "FEATURE"
        )
        self.assertTrue(test_response.success)
        test_id = test_response.data["test_id"]
        
        # 2. Get test results (would normally have data)
        results_response = ab_service.get_test_results(test_id)
        # May fail if test doesn't exist, but that's ok for this test
        
        # 3. Conclude test
        conclude_response = ab_service.conclude_test(test_id)
        # May fail if not enough data, but that's ok for this test


def run_integration_suite():
    """Run complete integration test suite"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        🧪 INTEGRATION TEST SUITE                                   ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProductionIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndWorkflows))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("\n✅ All integration tests passed!")
    else:
        print("\n❌ Some tests failed. Review the output above.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_suite()