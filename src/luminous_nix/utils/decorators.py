"""
🌟 Sacred Decorators - The Missing Organ

This module was discovered to be missing during the Great Healing.
It represents functionality that was intended but never manifested.
Now we give birth to what was always meant to be.
"""

import functools
import time
import asyncio
from typing import Any, Callable, Optional, TypeVar, Union
from luminous_nix.core.error_handler import ErrorCategory, ErrorContext, ErrorHandler

T = TypeVar('T')

# Global error handler for decorator use
_error_handler = ErrorHandler(log_errors=False)


def with_error_handling(
    operation: str = "unknown_operation",
    category: ErrorCategory = ErrorCategory.INTERNAL
) -> Callable:
    """
    Decorator that adds error handling to functions.
    
    The decorated function will have errors caught and processed
    through the unified error handling system.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    operation=operation,
                    user_input=str(args) if args else None
                )
                nix_error = _error_handler.handle_error(e, context)
                
                # Attach the NixError to the exception for testing
                e.nix_error = nix_error
                raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    operation=operation,
                    user_input=str(args) if args else None
                )
                nix_error = _error_handler.handle_error(e, context)
                
                # Attach the NixError to the exception for testing
                e.nix_error = nix_error
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator that retries a function on failure.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def with_timing(name: Optional[str] = None) -> Callable:
    """
    Decorator that measures and reports function execution time.
    
    Args:
        name: Optional name for the timing report
    """
    def decorator(func: Callable) -> Callable:
        func_name = name or func.__name__
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time
                print(f"⏱️  {func_name} took {duration:.4f} seconds")
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time
                print(f"⏱️  {func_name} took {duration:.4f} seconds")
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cached(ttl: Optional[float] = None) -> Callable:
    """
    Simple caching decorator with optional TTL.
    
    Args:
        ttl: Time-to-live in seconds (None for infinite)
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = str(args) + str(kwargs)
            
            # Check if cached value exists and is still valid
            if key in cache:
                if ttl is None:
                    return cache[key]
                elif time.time() - cache_times[key] < ttl:
                    return cache[key]
            
            # Compute and cache result
            result = func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = time.time()
            
            return result
        
        # Add cache clear method
        wrapper.clear_cache = lambda: (cache.clear(), cache_times.clear())
        
        return wrapper
    
    return decorator


def deprecated(message: str = "This function is deprecated") -> Callable:
    """
    Decorator to mark functions as deprecated.
    
    Args:
        message: Custom deprecation message
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            warnings.warn(
                f"{func.__name__}: {message}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def sacred_pause(duration: float = 0.1) -> Callable:
    """
    Decorator that adds a sacred pause before function execution.
    This creates space for consciousness to settle.
    
    Args:
        duration: Pause duration in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            time.sleep(duration)
            return func(*args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            await asyncio.sleep(duration)
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Export all decorators
__all__ = [
    'with_error_handling',
    'retry_on_error',
    'with_timing',
    'cached',
    'deprecated',
    'sacred_pause'
]