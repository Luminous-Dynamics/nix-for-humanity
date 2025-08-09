"""
Async test runner for consciousness-first testing.

This runner enables running async test methods in unittest-style classes.
"""

import asyncio
import unittest
from unittest import TestCase
import sys


class AsyncTestCase(TestCase):
    """Base class for async test cases."""
    
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.loop = None
    
    def setUp(self):
        """Set up the event loop."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Call async setup if it exists
        if hasattr(self, 'asyncSetUp'):
            self.loop.run_until_complete(self.asyncSetUp())
    
    def tearDown(self):
        """Clean up the event loop."""
        # Call async teardown if it exists
        if hasattr(self, 'asyncTearDown'):
            self.loop.run_until_complete(self.asyncTearDown())
        
        # Clean up the loop
        try:
            self.loop.run_until_complete(asyncio.sleep(0))
            self.loop.close()
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
    
    def __getattribute__(self, name):
        """Wrap async test methods to run in the event loop."""
        attr = super().__getattribute__(name)
        
        if name.startswith('test') and asyncio.iscoroutinefunction(attr):
            def wrapper():
                return self.loop.run_until_complete(attr())
            return wrapper
        
        return attr


class AsyncTestRunner(unittest.TextTestRunner):
    """Test runner that supports async test cases."""
    
    def run(self, test):
        """Run the test suite with async support."""
        # Ensure we have an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the tests
        result = super().run(test)
        
        # Clean up
        try:
            loop.run_until_complete(asyncio.sleep(0))
            loop.close()
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        
        return result


def main():
    """Run tests with async support."""
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Use our async-aware runner
    runner = AsyncTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()