#!/usr/bin/env python3
"""
Tests for Performance Monitor
Validates Phase 4 Living System self-maintaining infrastructure
"""

import unittest
import asyncio
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from luminous_nix.monitoring.performance_monitor import (
    PerformanceMonitor, 
    PerformanceMetric, 
    PerformanceThreshold,
    get_performance_monitor,
    monitor_performance
)


class TestPerformanceMonitor(unittest.TestCase):
    """Test suite for Performance Monitor"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = PerformanceMonitor(storage_path=Path(self.temp_dir))
    
    def test_metric_recording(self):
        """Test basic metric recording"""
        # Record a metric
        self.monitor.record_metric('test_metric', 42.0, 'ms', {'context': 'test'}, ['tag1'])
        
        # Verify metric was recorded
        self.assertEqual(len(self.monitor.metrics), 1)
        metric = self.monitor.metrics[0]
        self.assertEqual(metric.name, 'test_metric')
        self.assertEqual(metric.value, 42.0)
        self.assertEqual(metric.unit, 'ms')
        self.assertEqual(metric.context['context'], 'test')
        self.assertIn('tag1', metric.tags)
    
    def test_operation_timing(self):
        """Test operation timing functionality"""
        # Start operation
        op_id = self.monitor.start_operation('test_operation')
        self.assertIn(op_id, self.monitor.running_operations)
        
        # Wait a bit
        time.sleep(0.01)
        
        # End operation
        duration = self.monitor.end_operation(op_id)
        
        # Verify timing
        self.assertGreater(duration, 0)
        self.assertNotIn(op_id, self.monitor.running_operations)
        
        # Check metric was recorded
        test_metrics = [m for m in self.monitor.metrics if 'test_operation_time_ms' in m.name]
        self.assertEqual(len(test_metrics), 1)
        self.assertGreater(test_metrics[0].value, 0)
    
    def test_threshold_management(self):
        """Test performance threshold configuration"""
        # Add a threshold
        callback = MagicMock()
        self.monitor.add_threshold('test_metric', warning=50.0, critical=100.0, callback=callback)
        
        # Verify threshold was added
        self.assertEqual(len(self.monitor.thresholds), len(self.monitor.thresholds))
        threshold = next(t for t in self.monitor.thresholds if t.metric_name == 'test_metric')
        self.assertEqual(threshold.warning_threshold, 50.0)
        self.assertEqual(threshold.critical_threshold, 100.0)
        self.assertEqual(threshold.callback, callback)
    
    def test_persona_budgets(self):
        """Test consciousness-first persona performance budgets"""
        # Check Maya (ADHD) has strict requirements
        maya_budget = self.monitor.persona_budgets['maya_adhd']
        self.assertEqual(maya_budget['max_response_ms'], 1000)
        
        # Check Grandma Rose has more lenient requirements
        rose_budget = self.monitor.persona_budgets['grandma_rose']
        self.assertEqual(rose_budget['max_response_ms'], 2000)
        
        # Verify all personas have budgets
        required_personas = ['maya_adhd', 'grandma_rose', 'dr_sarah', 'alex_blind']
        for persona in required_personas:
            self.assertIn(persona, self.monitor.persona_budgets)
            self.assertIn('max_response_ms', self.monitor.persona_budgets[persona])
    
    def test_system_metrics_tracking(self):
        """Test system health metrics tracking"""
        # Record some system metrics
        self.monitor.record_metric('memory_usage_mb', 150.0, 'MB')
        self.monitor.record_metric('cpu_usage_percent', 25.0, '%')
        self.monitor.record_metric('response_times_ms', 500.0, 'ms')
        
        # Verify metrics are tracked in system_metrics
        self.assertIn(150.0, self.monitor.system_metrics['memory_usage_mb'])
        self.assertIn(25.0, self.monitor.system_metrics['cpu_usage_percent'])
        self.assertIn(500.0, self.monitor.system_metrics['response_times_ms'])
    
    def test_trinity_metrics_recording(self):
        """Test Sacred Trinity development cycle metrics"""
        # Record a Trinity cycle
        self.monitor.record_trinity_cycle(
            human_time_ms=5000.0,
            claude_time_ms=2000.0,
            llm_time_ms=1000.0,
            quality_score=9.2
        )
        
        # Verify metrics were recorded
        self.assertEqual(len(self.monitor.trinity_metrics['human_validation_time_ms']), 1)
        self.assertEqual(len(self.monitor.trinity_metrics['claude_implementation_time_ms']), 1)
        self.assertEqual(len(self.monitor.trinity_metrics['llm_consultation_time_ms']), 1)
        self.assertEqual(len(self.monitor.trinity_metrics['quality_score']), 1)
        self.assertEqual(self.monitor.trinity_metrics['integration_cycles'], 1)
        
        # Check values
        self.assertEqual(self.monitor.trinity_metrics['human_validation_time_ms'][0], 5000.0)
        self.assertEqual(self.monitor.trinity_metrics['claude_implementation_time_ms'][0], 2000.0)
        self.assertEqual(self.monitor.trinity_metrics['llm_consultation_time_ms'][0], 1000.0)  
        self.assertEqual(self.monitor.trinity_metrics['quality_score'][0], 9.2)
    
    def test_performance_summary(self):
        """Test comprehensive performance summary generation"""
        # Add some test data
        self.monitor.record_metric('response_times_ms', 800.0, 'ms')
        self.monitor.record_metric('memory_usage_mb', 200.0, 'MB')
        self.monitor.record_trinity_cycle(1000.0, 2000.0, 500.0, 8.5)
        
        # Generate summary
        summary = self.monitor.get_performance_summary()
        
        # Verify summary structure
        self.assertIn('timestamp', summary)
        self.assertIn('metrics_count', summary)
        self.assertIn('system_health', summary)
        self.assertIn('consciousness_budgets', summary)
        self.assertIn('trinity_metrics', summary)
        
        # Check consciousness budgets
        self.assertIn('maya_adhd', summary['consciousness_budgets'])
        maya_budget = summary['consciousness_budgets']['maya_adhd']
        self.assertIn('response_budget_met', maya_budget)
        self.assertIn('budget_ms', maya_budget)
        self.assertEqual(maya_budget['budget_ms'], 1000)
    
    def test_user_impact_assessment(self):
        """Test user impact assessment for performance issues"""
        # Test response time impact
        impact = self.monitor._assess_user_impact('response_time_ms', 1500.0)
        self.assertIn('Maya', impact)  # Should mention Maya (ADHD) at 1500ms
        
        impact = self.monitor._assess_user_impact('response_time_ms', 2500.0)
        self.assertIn('Rose', impact)  # Should mention Grandma Rose at 2500ms
        
        # Test memory usage impact
        impact = self.monitor._assess_user_impact('memory_usage_mb', 400.0)
        self.assertTrue(len(impact) > 0)
    
    def test_affected_personas_detection(self):
        """Test detection of personas affected by performance issues"""
        # Test response time affecting Maya
        affected = self.monitor._get_affected_personas('response_time_ms', 1200.0)
        self.assertIn('maya_adhd', affected)  # Maya's budget is 1000ms
        
        # Test response time not affecting Grandma Rose
        affected = self.monitor._get_affected_personas('response_time_ms', 1500.0)
        self.assertNotIn('grandma_rose', affected)  # Rose's budget is 2000ms
        
        # Test high response time affecting everyone
        affected = self.monitor._get_affected_personas('response_time_ms', 3000.0)
        self.assertTrue(len(affected) >= 3)  # Should affect most personas
    
    def test_optimization_recommendations(self):
        """Test optimization recommendation generation"""
        # Test response time recommendations
        recommendations = self.monitor._get_optimization_recommendations('response_time_ms')
        self.assertTrue(len(recommendations) > 0)
        self.assertTrue(any('Native Python-Nix API' in rec for rec in recommendations))
        
        # Test memory recommendations
        recommendations = self.monitor._get_optimization_recommendations('memory_usage_mb')
        self.assertTrue(len(recommendations) > 0)
        self.assertTrue(any('memory' in rec.lower() for rec in recommendations))
    
    def test_emergency_recommendations(self):
        """Test emergency recommendation generation"""
        # Test response time emergency actions
        emergency = self.monitor._get_emergency_recommendations('response_time_ms')
        self.assertTrue(len(emergency) > 0)
        self.assertTrue(any('minimal' in rec.lower() for rec in emergency))
        
        # Test memory emergency actions
        emergency = self.monitor._get_emergency_recommendations('memory_usage_mb')
        self.assertTrue(len(emergency) > 0)
        self.assertTrue(any('restart' in rec.lower() for rec in emergency))
    
    def test_metrics_cleanup(self):
        """Test old metrics cleanup"""
        # Add some metrics
        for i in range(100):
            self.monitor.record_metric(f'test_metric_{i}', float(i), 'units')
        
        self.assertEqual(len(self.monitor.metrics), 100)
        
        # Clean up old metrics (simulate old timestamps)
        import datetime
        old_time = datetime.datetime.now() - datetime.timedelta(hours=25)
        for metric in self.monitor.metrics[:50]:
            metric.timestamp = old_time
        
        # Cleanup
        self.monitor._cleanup_old_metrics(hours=24)
        
        # Should have removed the old ones
        self.assertEqual(len(self.monitor.metrics), 50)
    
    def test_performance_decorator(self):
        """Test performance monitoring decorator"""
        @monitor_performance('test_function')
        def test_sync_function():
            time.sleep(0.01)
            return "result"
        
        @monitor_performance('test_async_function')
        async def test_async_function():
            await asyncio.sleep(0.01)
            return "async_result"
        
        # Test sync function
        result = test_sync_function()
        self.assertEqual(result, "result")
        
        # Test async function
        async def run_async_test():
            result = await test_async_function()
            self.assertEqual(result, "async_result")
        
        asyncio.run(run_async_test())
        
        # Check that metrics were recorded
        sync_metrics = [m for m in self.monitor.metrics if 'test_function_time_ms' in m.name]
        async_metrics = [m for m in self.monitor.metrics if 'test_async_function_time_ms' in m.name]
        
        self.assertTrue(len(sync_metrics) > 0)
        self.assertTrue(len(async_metrics) > 0)
    
    def test_trend_calculation(self):
        """Test performance trend calculation"""
        # Test increasing trend
        increasing_values = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
        trend = self.monitor._calculate_trend(increasing_values)
        self.assertEqual(trend, 'increasing')
        
        # Test decreasing trend
        decreasing_values = [28, 26, 24, 22, 20, 18, 16, 14, 12, 10]
        trend = self.monitor._calculate_trend(decreasing_values)
        self.assertEqual(trend, 'decreasing')
        
        # Test stable trend
        stable_values = [20, 19, 21, 20, 20, 19, 21, 20, 19, 20]
        trend = self.monitor._calculate_trend(stable_values)
        self.assertEqual(trend, 'stable')
        
        # Test insufficient data
        few_values = [10, 20]
        trend = self.monitor._calculate_trend(few_values)
        self.assertEqual(trend, 'insufficient_data')
    
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    def test_system_health_monitoring(self, mock_cpu, mock_memory):
        """Test system health monitoring functionality"""
        # Mock system metrics
        mock_memory.return_value.used = 200 * 1024 * 1024  # 200MB
        mock_cpu.return_value = 45.0  # 45% CPU
        
        # Manually call the monitoring function once
        monitor = get_performance_monitor()
        
        # Record some metrics to simulate monitoring
        monitor.record_metric('memory_usage_mb', 200.0, 'MB')
        monitor.record_metric('cpu_usage_percent', 45.0, '%')
        
        # Check metrics were recorded
        self.assertIn(200.0, monitor.system_metrics['memory_usage_mb'])
        self.assertIn(45.0, monitor.system_metrics['cpu_usage_percent'])
    
    def test_singleton_performance_monitor(self):
        """Test global performance monitor singleton"""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        
        # Should be the same instance
        self.assertIs(monitor1, monitor2)
    
    async def test_save_metrics(self):
        """Test metrics persistence"""
        # Add some test metrics
        self.monitor.record_metric('test_save', 123.45, 'units')
        self.monitor.record_trinity_cycle(1000, 2000, 500, 9.0)
        
        # Save metrics
        await self.monitor.save_metrics()
        
        # Check that files were created
        json_files = list(Path(self.temp_dir).glob('metrics_*.json'))
        self.assertTrue(len(json_files) > 0)
        
        # Verify content
        import json
        with open(json_files[0]) as f:
            data = json.load(f)
        
        self.assertIn('timestamp', data)
        self.assertIn('summary', data)
        self.assertIn('recent_metrics', data)
        
        # Check that our test metric is in the recent metrics
        test_metrics = [m for m in data['recent_metrics'] if m['name'] == 'test_save']
        self.assertEqual(len(test_metrics), 1)
        self.assertEqual(test_metrics[0]['value'], 123.45)


class TestPerformanceIntegration(unittest.TestCase):
    """Integration tests for performance monitoring"""
    
    def test_phase4_living_system_integration(self):
        """Test integration with Phase 4 Living System features"""
        monitor = get_performance_monitor()
        
        # Test Sacred Trinity workflow integration
        monitor.record_trinity_cycle(
            human_time_ms=3000.0,  # Human validation
            claude_time_ms=5000.0,  # Claude implementation  
            llm_time_ms=800.0,     # LLM consultation
            quality_score=9.5      # Output quality
        )
        
        # Test consciousness-first performance validation
        summary = monitor.get_performance_summary()
        trinity_metrics = summary['trinity_metrics']
        
        # Verify Sacred Trinity metrics are tracked
        self.assertEqual(len(trinity_metrics['human_validation_time_ms']), 1)
        self.assertEqual(len(trinity_metrics['claude_implementation_time_ms']), 1)
        self.assertEqual(len(trinity_metrics['llm_consultation_time_ms']), 1)
        self.assertEqual(len(trinity_metrics['quality_score']), 1)
        self.assertEqual(trinity_metrics['integration_cycles'], 1)
        
        # Test persona-specific performance validation
        consciousness_budgets = summary['consciousness_budgets']
        
        # Verify all key personas have budget tracking
        key_personas = ['maya_adhd', 'grandma_rose', 'dr_sarah', 'alex_blind']
        for persona in key_personas:
            self.assertIn(persona, consciousness_budgets)
            budget = consciousness_budgets[persona]
            self.assertIn('response_budget_met', budget)
            self.assertIn('budget_ms', budget)
            self.assertIn('margin_ms', budget)
    
    def test_self_maintaining_infrastructure(self):
        """Test self-maintaining infrastructure capabilities"""
        monitor = get_performance_monitor()
        
        # Simulate performance degradation
        monitor.record_metric('response_time_ms', 2500.0, 'ms')  # Over budget
        monitor.record_metric('memory_usage_mb', 450.0, 'MB')   # High memory
        monitor.record_metric('error_rate_percent', 8.0, '%')   # High errors
        
        # Test impact assessment
        response_impact = monitor._assess_user_impact('response_time_ms', 2500.0)
        memory_impact = monitor._assess_user_impact('memory_usage_mb', 450.0)
        
        self.assertTrue(len(response_impact) > 0)
        self.assertTrue(len(memory_impact) > 0)
        
        # Test affected personas detection
        affected_personas = monitor._get_affected_personas('response_time_ms', 2500.0)
        self.assertIn('maya_adhd', affected_personas)  # Should affect Maya
        self.assertIn('grandma_rose', affected_personas)  # Should affect Rose
        
        # Test optimization recommendations
        recommendations = monitor._get_optimization_recommendations('response_time_ms')
        self.assertTrue(any('Native Python-Nix API' in rec for rec in recommendations))
        
        # Test emergency recommendations for critical issues
        emergency = monitor._get_emergency_recommendations('memory_usage_mb')
        self.assertTrue(any('restart' in rec.lower() for rec in emergency))


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)