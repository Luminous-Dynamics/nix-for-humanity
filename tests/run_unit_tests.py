#!/usr/bin/env python3
"""
Run all unit tests for Luminous Nix core components
"""

import sys
import unittest
import os
from pathlib import Path

# Add both src directory and project root to Python path for comprehensive imports
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'

# Insert at beginning to prioritize our paths
sys.path.insert(0, str(project_root))  # For frontends.* imports
sys.path.insert(0, str(src_path))      # For luminous_nix.* imports

print(f"Added to Python path:")
print(f"  Project root: {project_root}")
print(f"  Source path: {src_path}")

def run_all_tests():
    """Discover and run all unit tests"""
    
    # Get the directory containing this script
    test_dir = Path(__file__).parent / 'unit'
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Discover all test files from tests directory (parent of unit)
    suite = loader.discover(
        start_dir=str(test_dir.parent),  # Use tests/ instead of tests/unit/
        pattern='test_*.py',
        top_level_dir=str(project_root)  # Use project root for imports
    )
    
    # Create test runner with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = runner.run(suite)
    
    # Return exit code based on success
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_module):
    """Run a specific test module"""
    
    # Import the test module
    test_dir = Path(__file__).parent / 'unit'
    sys.path.insert(0, str(test_dir))
    
    try:
        module = __import__(test_module)
        suite = unittest.TestLoader().loadTestsFromModule(module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1
    except ImportError as e:
        print(f"Error: Could not import test module '{test_module}': {e}")
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test module
        test_name = sys.argv[1]
        if not test_name.startswith('test_'):
            test_name = f'test_{test_name}'
        if not test_name.endswith('.py'):
            test_name = test_name.rstrip('.py')
        
        print(f"Running specific test: {test_name}")
        exit_code = run_specific_test(test_name)
    else:
        # Run all tests
        print("Running all unit tests...")
        print(f"Test directory: {Path(__file__).parent / 'unit'}")
        print(f"Source directory: {src_path}")
        print("-" * 70)
        
        exit_code = run_all_tests()
        
    sys.exit(exit_code)