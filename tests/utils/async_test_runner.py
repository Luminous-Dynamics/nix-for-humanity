"""Async test runner utilities."""

import asyncio
import unittest
from typing import Any, Coroutine


class AsyncTestCase(unittest.TestCase):
    """Base class for async test cases."""
    
    def run_async(self, coro: Coroutine) -> Any:
        """Run an async coroutine in a test."""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a new task
            task = asyncio.create_task(coro)
            return asyncio.run(asyncio.gather(task))[0]
        else:
            # Otherwise run normally
            return loop.run_until_complete(coro)
    
    def setUp(self):
        """Set up async test environment."""
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up async test environment."""
        # Cancel all pending tasks
        pending = asyncio.all_tasks(self.loop)
        for task in pending:
            task.cancel()
        
        # Run loop until all tasks are cancelled
        self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        
        # Close the loop
        self.loop.close()
        super().tearDown()
    
    def async_test(self, coro_func):
        """Decorator to run async test methods."""
        def wrapper(*args, **kwargs):
            coro = coro_func(*args, **kwargs)
            return self.run_async(coro)
        return wrapper
