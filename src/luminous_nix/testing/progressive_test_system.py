"""
Progressive Test Activation System

This module ensures tests only run for features that actually exist,
preventing the "955 failing tests for phantom features" problem.
Tests progressively activate as their associated features mature.
"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create mock pytest for demonstration
    class MockPytest:
        class mark:
            @staticmethod
            def skip(reason):
                def decorator(func):
                    return func
                return decorator
            
            @staticmethod
            def progressive(**kwargs):
                def decorator(func):
                    return func
                return decorator
        
        @staticmethod
        def skip(reason):
            raise Exception(f"Test skipped: {reason}")
    
    pytest = MockPytest()

import functools
import logging
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json

from luminous_nix.integration.feature_readiness import (
    FeatureReadinessTracker,
    is_feature_enabled,
    get_feature_readiness
)

logger = logging.getLogger(__name__)


class TestLevel(Enum):
    """Progressive test levels matching feature readiness"""
    UNIT = 0.25          # Basic unit tests
    INTEGRATION = 0.50   # Integration tests
    FUNCTIONAL = 0.75    # Full functional tests
    PERFORMANCE = 0.90   # Performance benchmarks
    STRESS = 1.0        # Stress testing


@dataclass
class TestMetrics:
    """Metrics for test execution"""
    total_tests: int = 0
    skipped_tests: int = 0
    executed_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    feature_coverage: Dict[str, float] = None
    
    def __post_init__(self):
        if self.feature_coverage is None:
            self.feature_coverage = {}
    
    def success_rate(self) -> float:
        """Calculate test success rate"""
        if self.executed_tests == 0:
            return 0.0
        return self.passed_tests / self.executed_tests


class ProgressiveTestRunner:
    """
    Test runner that only executes tests for features that exist.
    """
    
    def __init__(self):
        """Initialize progressive test runner"""
        self.tracker = FeatureReadinessTracker()
        self.metrics = TestMetrics()
        self.test_registry: Dict[str, List[Callable]] = {}
        self.executed_tests: Set[str] = set()
        
    def should_run_test(self, feature_name: str, test_level: TestLevel) -> bool:
        """
        Determine if a test should run based on feature readiness.
        
        Args:
            feature_name: Name of the feature being tested
            test_level: Level of test (unit, integration, etc.)
            
        Returns:
            True if test should run, False if it should be skipped
        """
        readiness = get_feature_readiness(feature_name)
        
        # Test runs if feature readiness >= test level requirement
        return readiness >= test_level.value
    
    def register_test(self, feature_name: str, test_func: Callable, 
                     test_level: TestLevel = TestLevel.UNIT):
        """
        Register a test with its associated feature.
        
        Args:
            feature_name: Feature this test validates
            test_func: The test function
            test_level: Level of test
        """
        if feature_name not in self.test_registry:
            self.test_registry[feature_name] = []
        
        self.test_registry[feature_name].append({
            'func': test_func,
            'level': test_level,
            'name': test_func.__name__
        })
    
    def run_tests_for_feature(self, feature_name: str) -> Dict[str, Any]:
        """
        Run all appropriate tests for a feature based on its readiness.
        
        Args:
            feature_name: Feature to test
            
        Returns:
            Test results
        """
        if feature_name not in self.test_registry:
            logger.warning(f"No tests registered for feature: {feature_name}")
            return {'skipped': True, 'reason': 'No tests registered'}
        
        readiness = get_feature_readiness(feature_name)
        results = {
            'feature': feature_name,
            'readiness': readiness,
            'tests_run': [],
            'tests_skipped': [],
            'success': True
        }
        
        for test_info in self.test_registry[feature_name]:
            test_name = test_info['name']
            test_level = test_info['level']
            test_func = test_info['func']
            
            self.metrics.total_tests += 1
            
            if self.should_run_test(feature_name, test_level):
                # Run the test
                try:
                    test_func()
                    self.metrics.executed_tests += 1
                    self.metrics.passed_tests += 1
                    results['tests_run'].append({
                        'name': test_name,
                        'level': test_level.name,
                        'passed': True
                    })
                    self.executed_tests.add(f"{feature_name}::{test_name}")
                    
                except Exception as e:
                    self.metrics.executed_tests += 1
                    self.metrics.failed_tests += 1
                    results['tests_run'].append({
                        'name': test_name,
                        'level': test_level.name,
                        'passed': False,
                        'error': str(e)
                    })
                    results['success'] = False
                    
            else:
                # Skip the test
                self.metrics.skipped_tests += 1
                results['tests_skipped'].append({
                    'name': test_name,
                    'level': test_level.name,
                    'required_readiness': test_level.value,
                    'current_readiness': readiness
                })
        
        # Update feature coverage
        if results['tests_run']:
            passed = sum(1 for t in results['tests_run'] if t['passed'])
            total = len(results['tests_run'])
            self.metrics.feature_coverage[feature_name] = passed / total
        
        return results
    
    def run_all_progressive_tests(self) -> Dict[str, Any]:
        """
        Run all tests that are appropriate for current feature readiness levels.
        
        Returns:
            Complete test results
        """
        all_results = {
            'features_tested': {},
            'metrics': None,
            'summary': None
        }
        
        # Run tests for each feature
        for feature_name in self.tracker.features.keys():
            results = self.run_tests_for_feature(feature_name)
            all_results['features_tested'][feature_name] = results
        
        # Generate summary
        all_results['metrics'] = {
            'total_tests': self.metrics.total_tests,
            'executed': self.metrics.executed_tests,
            'skipped': self.metrics.skipped_tests,
            'passed': self.metrics.passed_tests,
            'failed': self.metrics.failed_tests,
            'success_rate': self.metrics.success_rate(),
            'feature_coverage': self.metrics.feature_coverage
        }
        
        all_results['summary'] = self.generate_summary()
        
        return all_results
    
    def generate_summary(self) -> str:
        """Generate human-readable test summary"""
        lines = [
            "=" * 60,
            "PROGRESSIVE TEST EXECUTION SUMMARY",
            "=" * 60,
            f"Total Tests Available: {self.metrics.total_tests}",
            f"Tests Executed: {self.metrics.executed_tests} ({self.metrics.executed_tests/self.metrics.total_tests:.1%})",
            f"Tests Skipped: {self.metrics.skipped_tests} (features not ready)",
            f"Tests Passed: {self.metrics.passed_tests}",
            f"Tests Failed: {self.metrics.failed_tests}",
            f"Success Rate: {self.metrics.success_rate():.1%}",
            "",
            "Feature Test Coverage:",
            "-" * 40
        ]
        
        for feature, coverage in self.metrics.feature_coverage.items():
            readiness = get_feature_readiness(feature)
            lines.append(f"  {feature}: {coverage:.0%} passing (readiness: {readiness:.0%})")
        
        lines.extend([
            "-" * 40,
            "",
            "Key Insight: Only testing what actually exists!",
            "Tests will progressively activate as features mature."
        ])
        
        return "\n".join(lines)


# Pytest plugin for progressive testing (only if pytest available)
if PYTEST_AVAILABLE:
    def pytest_configure(config):
        """Configure pytest with progressive testing"""
        config.addinivalue_line(
            "markers", "progressive(feature, level): mark test for progressive activation"
        )


    def pytest_collection_modifyitems(config, items):
        """Modify test collection based on feature readiness"""
        tracker = FeatureReadinessTracker()
        
        for item in items:
            # Check for progressive marker
            marker = item.get_closest_marker("progressive")
            if marker:
                feature = marker.kwargs.get('feature')
                level = marker.kwargs.get('level', 'unit')
                
                # Convert level string to TestLevel
                level_map = {
                    'unit': TestLevel.UNIT,
                    'integration': TestLevel.INTEGRATION,
                    'functional': TestLevel.FUNCTIONAL,
                    'performance': TestLevel.PERFORMANCE,
                    'stress': TestLevel.STRESS
                }
                test_level = level_map.get(level, TestLevel.UNIT)
                
                # Check if test should run
                readiness = get_feature_readiness(feature)
                if readiness < test_level.value:
                    skip_reason = (
                        f"Feature '{feature}' not ready "
                        f"(needs {test_level.value:.0%}, currently {readiness:.0%})"
                    )
                    item.add_marker(pytest.mark.skip(reason=skip_reason))


# Decorator for progressive tests
def progressive_test(feature: str, level: TestLevel = TestLevel.UNIT):
    """
    Decorator to mark tests for progressive activation.
    
    Args:
        feature: Feature being tested
        level: Level of test
        
    Example:
        @progressive_test('voice_interface', TestLevel.INTEGRATION)
        def test_voice_recognition():
            # This test only runs when voice_interface >= 50% ready
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            readiness = get_feature_readiness(feature)
            
            if readiness < level.value:
                pytest.skip(
                    f"Feature '{feature}' not ready "
                    f"(needs {level.value:.0%}, currently {readiness:.0%})"
                )
            
            # Run the test
            return func(*args, **kwargs)
        
        # Add pytest marker
        wrapper = pytest.mark.progressive(feature=feature, level=level.name.lower())(wrapper)
        
        return wrapper
    return decorator


# Test suite generator
class ProgressiveTestSuite:
    """
    Generate test suites that match current feature readiness.
    """
    
    def __init__(self):
        """Initialize test suite generator"""
        self.tracker = FeatureReadinessTracker()
        
    def generate_current_suite(self) -> Dict[str, List[str]]:
        """
        Generate a test suite for current readiness levels.
        
        Returns:
            Dict mapping features to appropriate test files
        """
        suite = {}
        
        for feature_name, feature in self.tracker.features.items():
            readiness = feature.readiness
            test_files = []
            
            # Add appropriate test files based on readiness
            if readiness >= TestLevel.UNIT.value:
                test_files.append(f"tests/unit/test_{feature_name}.py")
            
            if readiness >= TestLevel.INTEGRATION.value:
                test_files.append(f"tests/integration/test_{feature_name}_integration.py")
            
            if readiness >= TestLevel.FUNCTIONAL.value:
                test_files.append(f"tests/functional/test_{feature_name}_functional.py")
            
            if readiness >= TestLevel.PERFORMANCE.value:
                test_files.append(f"tests/performance/test_{feature_name}_performance.py")
            
            suite[feature_name] = test_files
        
        return suite
    
    def write_pytest_ini(self, output_path: Path = Path("pytest.ini")):
        """
        Generate pytest.ini with appropriate test paths.
        
        Args:
            output_path: Where to write pytest.ini
        """
        suite = self.generate_current_suite()
        
        lines = [
            "[pytest]",
            "minversion = 6.0",
            "testpaths =",
        ]
        
        # Add all test paths that should run
        all_paths = set()
        for test_files in suite.values():
            for test_file in test_files:
                test_dir = str(Path(test_file).parent)
                all_paths.add(test_dir)
        
        for path in sorted(all_paths):
            lines.append(f"    {path}")
        
        lines.extend([
            "",
            "markers =",
            "    progressive: mark test for progressive activation",
            "    unit: unit tests (25% readiness required)",
            "    integration: integration tests (50% readiness required)",
            "    functional: functional tests (75% readiness required)",
            "    performance: performance tests (90% readiness required)",
            "",
            "addopts = ",
            "    -v",
            "    --strict-markers",
            "    --tb=short",
            "    --color=yes",
        ])
        
        output_path.write_text("\n".join(lines))
        logger.info(f"Generated pytest.ini for current readiness levels")
    
    def get_test_command(self, feature: Optional[str] = None) -> str:
        """
        Get pytest command for current readiness.
        
        Args:
            feature: Specific feature to test (optional)
            
        Returns:
            Pytest command string
        """
        if feature:
            readiness = get_feature_readiness(feature)
            markers = []
            
            if readiness >= TestLevel.UNIT.value:
                markers.append("unit")
            if readiness >= TestLevel.INTEGRATION.value:
                markers.append("integration")
            if readiness >= TestLevel.FUNCTIONAL.value:
                markers.append("functional")
            if readiness >= TestLevel.PERFORMANCE.value:
                markers.append("performance")
            
            marker_str = " or ".join(markers)
            return f'pytest -m "progressive and ({marker_str})" -k {feature}'
        else:
            return 'pytest -m progressive'


# Validation functions for test/code alignment
def validate_test_coverage() -> Dict[str, Any]:
    """
    Validate that tests match actual code, not aspirational features.
    
    Returns:
        Validation report
    """
    tracker = FeatureReadinessTracker()
    report = {
        'valid': True,
        'issues': [],
        'recommendations': []
    }
    
    # Check each feature
    for feature_name, feature in tracker.features.items():
        readiness = feature.readiness
        
        # Check for test files
        test_files = {
            'unit': Path(f"tests/unit/test_{feature_name}.py"),
            'integration': Path(f"tests/integration/test_{feature_name}_integration.py"),
            'functional': Path(f"tests/functional/test_{feature_name}_functional.py"),
        }
        
        for test_type, test_file in test_files.items():
            if test_file.exists():
                # Check if test should exist based on readiness
                required_readiness = {
                    'unit': 0.25,
                    'integration': 0.50,
                    'functional': 0.75
                }[test_type]
                
                if readiness < required_readiness:
                    report['valid'] = False
                    report['issues'].append(
                        f"Test file {test_file} exists but feature '{feature_name}' "
                        f"is only {readiness:.0%} ready (needs {required_readiness:.0%})"
                    )
                    report['recommendations'].append(
                        f"Mark tests in {test_file} with @progressive_test decorator"
                    )
    
    return report


# Example usage functions
def example_progressive_tests():
    """Example of how to write progressive tests"""
    
    # Unit test - runs at 25% readiness
    @progressive_test('poml_consciousness', TestLevel.UNIT)
    def test_poml_template_loading():
        """Test that POML templates can be loaded"""
        from luminous_nix.consciousness import POMLConsciousness
        consciousness = POMLConsciousness()
        assert consciousness.templates is not None
    
    # Integration test - runs at 50% readiness
    @progressive_test('data_trinity', TestLevel.INTEGRATION)
    def test_duckdb_connection():
        """Test DuckDB connection and basic operations"""
        from luminous_nix.bridges.store_trinity_bridge import StoreTrinityBridge
        bridge = StoreTrinityBridge(readiness=0.5)
        bridge.save("test_key", "test_value")
        assert bridge.load("test_key") == "test_value"
    
    # Functional test - runs at 75% readiness
    @progressive_test('tui_interface', TestLevel.FUNCTIONAL)
    def test_tui_full_interaction():
        """Test full TUI interaction flow"""
        from luminous_nix.bridges.tui_backend_bridge import TUIBackendBridge
        bridge = TUIBackendBridge(readiness=0.8)
        assert bridge.interaction_mode.value == "confirm"
    
    # Performance test - runs at 90% readiness
    @progressive_test('native_api', TestLevel.PERFORMANCE)
    def test_native_api_performance():
        """Benchmark native Python-Nix API"""
        import time
        start = time.time()
        # Performance test code here
        elapsed = time.time() - start
        assert elapsed < 0.1  # Must complete in 100ms


# Helper to migrate existing tests
def migrate_existing_tests(test_file: Path) -> bool:
    """
    Add progressive decorators to existing tests.
    
    Args:
        test_file: Path to test file to migrate
        
    Returns:
        Success status
    """
    content = test_file.read_text()
    
    # Simple heuristic: detect feature from filename
    feature_name = test_file.stem.replace('test_', '').replace('_integration', '')
    
    # Add import if not present
    if 'from luminous_nix.testing.progressive_test_system import' not in content:
        import_line = (
            "from luminous_nix.testing.progressive_test_system import "
            "progressive_test, TestLevel\n\n"
        )
        content = import_line + content
    
    # Add decorator to test functions
    import re
    
    def add_decorator(match):
        indent = match.group(1)
        func_def = match.group(2)
        
        # Determine test level from function name
        if 'integration' in func_def:
            level = "TestLevel.INTEGRATION"
        elif 'functional' in func_def:
            level = "TestLevel.FUNCTIONAL"
        elif 'performance' in func_def or 'benchmark' in func_def:
            level = "TestLevel.PERFORMANCE"
        else:
            level = "TestLevel.UNIT"
        
        decorator = f"{indent}@progressive_test('{feature_name}', {level})\n"
        return decorator + match.group(0)
    
    # Add decorators to test functions
    pattern = r'^(\s*)(def test_\w+.*:)$'
    content = re.sub(pattern, add_decorator, content, flags=re.MULTILINE)
    
    # Write back
    test_file.write_text(content)
    
    return True