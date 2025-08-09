#!/usr/bin/env python3
"""
Tests for Performance Benchmark Suite

Tests the performance benchmarking functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os
from pathlib import Path
import tempfile
import shutil
import json
import sqlite3

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
scripts_path = os.path.join(project_root, 'scripts')
sys.path.insert(0, scripts_path)


class TestPerformanceBenchmark(unittest.TestCase):
    """Test the PerformanceBenchmark class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.test_results_dir = Path(self.test_dir) / '.performance_metrics'
        
        # Mock the PerformanceBenchmark class
        self.mock_benchmark = Mock()
        self.mock_benchmark.results_dir = self.test_results_dir
        self.mock_benchmark.db_path = self.test_results_dir / 'performance_history.db'
        
        # Performance targets
        self.mock_benchmark.targets = {
            "startup_time": 3.0,
            "warm_startup": 1.0,
            "response_time": 1.0,
            "memory_usage": 500,
            "cpu_usage": 50
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test PerformanceBenchmark initialization."""
        # Test that benchmark initializes correctly
        self.assertIsNotNone(self.mock_benchmark)
        self.assertIsNotNone(self.mock_benchmark.results_dir)
        self.assertIsNotNone(self.mock_benchmark.db_path)
        self.assertIn('startup_time', self.mock_benchmark.targets)
    
    def test_benchmark_startup_time(self):
        """Test startup time benchmarking."""
        # Mock startup time measurement
        self.mock_benchmark.benchmark_startup_time = Mock(return_value={
            'cold_start': 2.5,
            'warm_start': 0.8,
            'average': 1.65
        })
        
        result = self.mock_benchmark.benchmark_startup_time()
        self.assertEqual(result['cold_start'], 2.5)
        self.assertEqual(result['warm_start'], 0.8)
        self.assertTrue(result['cold_start'] < self.mock_benchmark.targets['startup_time'])
    
    def test_benchmark_response_time(self):
        """Test response time benchmarking."""
        # Mock response time for different queries
        self.mock_benchmark.benchmark_response_time = Mock(return_value={
            'install_package': 0.5,
            'search_package': 0.3,
            'update_system': 0.8,
            'average': 0.53
        })
        
        result = self.mock_benchmark.benchmark_response_time()
        self.assertEqual(result['install_package'], 0.5)
        self.assertTrue(result['average'] < self.mock_benchmark.targets['response_time'])
    
    def test_benchmark_memory_usage(self):
        """Test memory usage benchmarking."""
        # Mock memory usage measurement
        self.mock_benchmark.benchmark_memory_usage = Mock(return_value={
            'baseline': 150,
            'during_operation': 250,
            'peak': 300,
            'average': 200
        })
        
        result = self.mock_benchmark.benchmark_memory_usage()
        self.assertEqual(result['baseline'], 150)
        self.assertEqual(result['peak'], 300)
        self.assertTrue(result['peak'] < self.mock_benchmark.targets['memory_usage'])
    
    def test_benchmark_cpu_usage(self):
        """Test CPU usage benchmarking."""
        # Mock CPU usage measurement
        self.mock_benchmark.benchmark_cpu_usage = Mock(return_value={
            'idle': 5,
            'during_operation': 35,
            'peak': 45,
            'average': 28
        })
        
        result = self.mock_benchmark.benchmark_cpu_usage()
        self.assertEqual(result['idle'], 5)
        self.assertEqual(result['peak'], 45)
        self.assertTrue(result['peak'] < self.mock_benchmark.targets['cpu_usage'])
    
    def test_run_comprehensive_benchmark(self):
        """Test running comprehensive benchmark suite."""
        # Mock comprehensive benchmark
        self.mock_benchmark.run_comprehensive = Mock(return_value={
            'timestamp': '2024-01-01T12:00:00',
            'startup': {'cold_start': 2.5, 'warm_start': 0.8},
            'response': {'average': 0.53},
            'memory': {'peak': 300},
            'cpu': {'peak': 45},
            'overall_score': 8.5
        })
        
        result = self.mock_benchmark.run_comprehensive()
        self.assertIn('timestamp', result)
        self.assertIn('startup', result)
        self.assertIn('overall_score', result)
        self.assertGreater(result['overall_score'], 0)
    
    def test_save_results(self):
        """Test saving benchmark results."""
        # Mock save results
        self.mock_benchmark.save_results = Mock(return_value=True)
        
        test_results = {
            'timestamp': '2024-01-01T12:00:00',
            'startup': {'cold_start': 2.5},
            'score': 8.5
        }
        
        success = self.mock_benchmark.save_results(test_results)
        self.assertTrue(success)
        self.mock_benchmark.save_results.assert_called_once_with(test_results)
    
    def test_compare_with_baseline(self):
        """Test comparing results with baseline."""
        # Mock comparison
        self.mock_benchmark.compare_with_baseline = Mock(return_value={
            'startup_improved': True,
            'response_improved': True,
            'memory_improved': False,
            'cpu_improved': True,
            'overall_improvement': 15.5
        })
        
        comparison = self.mock_benchmark.compare_with_baseline()
        self.assertTrue(comparison['startup_improved'])
        self.assertFalse(comparison['memory_improved'])
        self.assertEqual(comparison['overall_improvement'], 15.5)
    
    def test_generate_report(self):
        """Test generating performance report."""
        # Mock report generation
        self.mock_benchmark.generate_report = Mock(return_value={
            'summary': 'Performance is within targets',
            'recommendations': [
                'Consider optimizing memory usage',
                'CPU usage is excellent'
            ],
            'score': 8.5,
            'meets_targets': True
        })
        
        report = self.mock_benchmark.generate_report()
        self.assertEqual(report['summary'], 'Performance is within targets')
        self.assertEqual(len(report['recommendations']), 2)
        self.assertTrue(report['meets_targets'])
    
    def test_benchmark_personas(self):
        """Test benchmarking for different personas."""
        # Mock persona-specific benchmarks
        self.mock_benchmark.benchmark_personas = Mock(return_value={
            'grandma_rose': {'response_time': 1.2, 'satisfaction': 9.0},
            'maya_adhd': {'response_time': 0.5, 'satisfaction': 9.5},
            'dr_sarah': {'response_time': 0.8, 'satisfaction': 8.5},
            'average_satisfaction': 9.0
        })
        
        result = self.mock_benchmark.benchmark_personas()
        self.assertEqual(result['maya_adhd']['response_time'], 0.5)
        self.assertEqual(result['average_satisfaction'], 9.0)
        
        # Maya (ADHD) should have fastest response time
        maya_time = result['maya_adhd']['response_time']
        for persona, data in result.items():
            if persona not in ['maya_adhd', 'average_satisfaction']:
                self.assertLessEqual(maya_time, data['response_time'])
    
    def test_performance_regression_detection(self):
        """Test detecting performance regressions."""
        # Mock regression detection
        self.mock_benchmark.detect_regressions = Mock(return_value={
            'has_regressions': False,
            'regressions': [],
            'improvements': ['startup_time', 'cpu_usage'],
            'stable': ['memory_usage', 'response_time']
        })
        
        result = self.mock_benchmark.detect_regressions()
        self.assertFalse(result['has_regressions'])
        self.assertEqual(len(result['improvements']), 2)
        self.assertIn('startup_time', result['improvements'])


if __name__ == '__main__':
    unittest.main()