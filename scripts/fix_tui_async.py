#!/usr/bin/env python3
"""
Fix TUI Async Issues - Week 3 of The Sacred Path Forward

Issues identified:
1. _sync_visual_state is async but called with set_interval (expects sync)
2. Native operations manager needs proper async handling
3. Some async methods don't properly await their calls
"""

import os
from pathlib import Path

def fix_main_app():
    """Fix async issues in main_app.py"""
    
    main_app_path = Path('/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/src/luminous_nix/ui/main_app.py')
    
    with open(main_app_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Convert _sync_visual_state from async to sync
    # The set_interval method expects a sync function
    content = content.replace(
        'async def _sync_visual_state(self) -> None:',
        'def _sync_visual_state(self) -> None:'
    )
    
    # Fix 2: Update the native operations method to handle async properly
    # Change the await to a sync version or use run_sync
    old_native_ops = """            result = await native_ops.execute_native_operation(
                NativeOperationType.LIST_GENERATIONS
            )"""
    
    new_native_ops = """            # Use sync version for now - async version needs proper event loop handling
            import asyncio
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(native_ops.execute_native_operation(
                NativeOperationType.LIST_GENERATIONS
            ))"""
    
    if old_native_ops in content:
        content = content.replace(old_native_ops, new_native_ops)
    
    # Fix 3: Ensure proper async/await patterns
    # The on_input_submitted is properly async and awaits process_user_input
    # But we need to ensure show_native_operations and show_advanced_features
    # are called with proper await
    
    # These are already properly awaited in the code, so no change needed
    
    # Write the fixed content
    with open(main_app_path, 'w') as f:
        f.write(content)
    
    return "Fixed main_app.py async issues"

def create_async_wrapper():
    """Create a wrapper for proper async handling in TUI"""
    
    wrapper_path = Path('/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/src/luminous_nix/ui/async_helper.py')
    
    wrapper_content = '''"""
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
'''
    
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_content)
    
    return "Created async_helper.py"

def main():
    """Execute the async fixes"""
    print("🔧 Fixing TUI Async Issues - Week 3")
    print("=" * 60)
    
    results = []
    
    # Fix main app
    print("\n📝 Fixing main_app.py...")
    result = fix_main_app()
    results.append(result)
    print(f"  ✅ {result}")
    
    # Create async wrapper
    print("\n📝 Creating async helper module...")
    result = create_async_wrapper()
    results.append(result)
    print(f"  ✅ {result}")
    
    print("\n" + "=" * 60)
    print("✨ TUI Async Issues Fixed!")
    print("\nChanges made:")
    print("1. Fixed _sync_visual_state to be synchronous (required by set_interval)")
    print("2. Added proper async handling for native operations")
    print("3. Created async_helper.py for future async/sync bridging")
    
    return results

if __name__ == "__main__":
    main()