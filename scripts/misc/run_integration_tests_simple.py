#!/usr/bin/env python3
"""
Simple runner for integration tests
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Now import and run the test
try:
    from tests.integration.test_real_nixos_operations import TestRealNixOSOperations, TestErrorScenarios
    import unittest
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test methods from both classes
    for test_class in [TestRealNixOSOperations, TestErrorScenarios]:
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                suite.addTest(test_class(method_name))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
    
except Exception as e:
    print(f"Error running integration tests: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)