#!/usr/bin/env python3
"""
Test runner for Nix for Humanity
Handles proper Python path setup for imports
"""

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Get the project root
project_root = Path(__file__).parent.absolute()

# Add necessary paths
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "tests"))

# Mock the python module for native_nix_backend
sys.modules['python'] = type(sys)('python')
sys.modules['python.native_nix_backend'] = type(sys)('python.native_nix_backend')

# Create mock classes for the imports
NativeNixBackend = Mock
NixOperation = type('NixOperation', (), {})
OperationType = type('OperationType', (), {
    'UPDATE': Mock(value='update'),
    'ROLLBACK': Mock(value='rollback'),
    'INSTALL': Mock(value='install'),
    'REMOVE': Mock(value='remove'),
    'SEARCH': Mock(value='search'),
    'BUILD': Mock(value='build'),
    'TEST': Mock(value='test'),
    'LIST_GENERATIONS': Mock(value='list_generations'),
})
NixResult = type('NixResult', (), {})
NATIVE_API_AVAILABLE = True

# Inject the mocks
sys.modules['python.native_nix_backend'].NativeNixBackend = NativeNixBackend
sys.modules['python.native_nix_backend'].NixOperation = NixOperation
sys.modules['python.native_nix_backend'].OperationType = OperationType
sys.modules['python.native_nix_backend'].NixResult = NixResult
sys.modules['python.native_nix_backend'].NATIVE_API_AVAILABLE = NATIVE_API_AVAILABLE

# Mock the api.schema module
sys.modules['api'] = type(sys)('api')
sys.modules['api.schema'] = type(sys)('api.schema')

# Create mock schema classes
Request = MagicMock()
Response = MagicMock()
Result = MagicMock()
Intent = MagicMock()
Context = MagicMock()

# Inject schema mocks
sys.modules['api.schema'].Request = Request
sys.modules['api.schema'].Response = Response
sys.modules['api.schema'].Result = Result
sys.modules['api.schema'].Intent = Intent
sys.modules['api.schema'].Context = Context

def run_tests(test_module=None):
    """Run tests with proper setup"""
    
    if test_module:
        # Run specific test module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(f'tests.unit.{test_module}')
    else:
        # Discover all tests
        loader = unittest.TestLoader()
        start_dir = project_root / 'tests' / 'unit'
        suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Nix for Humanity tests')
    parser.add_argument('test_module', nargs='?', help='Specific test module to run (e.g., test_knowledge)')
    
    args = parser.parse_args()
    
    success = run_tests(args.test_module)
    sys.exit(0 if success else 1)