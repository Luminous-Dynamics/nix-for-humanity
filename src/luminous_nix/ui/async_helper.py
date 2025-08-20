"""
Async Helper for TUI - Proper async/sync bridging

This module provides utilities to properly handle async operations
in the Textual TUI framework.
"""

import asyncio
from typing import Any, Callable, Coroutine
from functools import wraps

def sync_wrapper(async_func: Callable[..., Coroutine]) -> Callable:
    """
    Wrap an async function to be called from sync context.
    
    This is needed when Textual's set_interval or other sync
    callbacks need to call async functions.
    """
    @wraps(async_func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            # Try to get the running loop
            loop = asyncio.get_running_loop()
            # Schedule the coroutine
            task = loop.create_task(async_func(*args, **kwargs))
            return task
        except RuntimeError:
            # No running loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(async_func(*args, **kwargs))
            finally:
                loop.close()
    
    return wrapper

def run_async_in_sync(coro: Coroutine) -> Any:
    """
    Run an async coroutine in a sync context.
    
    Useful for calling async operations from sync Textual callbacks.
    """
    try:
        loop = asyncio.get_running_loop()
        # If we're already in an async context, create a task
        return loop.create_task(coro)
    except RuntimeError:
        # No loop running, run it blocking
        return asyncio.run(coro)

class AsyncManager:
    """
    Manager for handling async operations in TUI.
    
    Provides a clean interface for bridging async/sync worlds.
    """
    
    def __init__(self):
        self._loop: asyncio.AbstractEventLoop | None = None
        
    def setup(self, loop: asyncio.AbstractEventLoop | None = None):
        """Setup the async manager with an event loop."""
        self._loop = loop or asyncio.get_event_loop()
        
    def run_async(self, coro: Coroutine) -> Any:
        """Run an async coroutine."""
        if self._loop and self._loop.is_running():
            return self._loop.create_task(coro)
        else:
            return asyncio.run(coro)
            
    def wrap_async(self, func: Callable[..., Coroutine]) -> Callable:
        """Wrap an async function for sync calling."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.run_async(func(*args, **kwargs))
        return wrapper
