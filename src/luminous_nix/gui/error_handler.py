#!/usr/bin/env python3
"""
🛡️ Error Handler Utilities for AI-Driven Interface Generation
Provides comprehensive error handling across the system
"""

import logging
import functools
import sqlite3
from typing import Any, Callable, Optional, TypeVar, Union
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Type variable for generic return types
T = TypeVar('T')


class LuminousError(Exception):
    """Base exception for Luminous system"""
    pass


class DatabaseError(LuminousError):
    """Database operation errors"""
    pass


class InterfaceGenerationError(LuminousError):
    """Interface generation errors"""
    pass


class VoiceProcessingError(LuminousError):
    """Voice processing errors"""
    pass


class OptimizationError(LuminousError):
    """Optimization engine errors"""
    pass


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(name)


def safe_database_operation(
    default_return: Any = None,
    raise_on_error: bool = False
) -> Callable:
    """
    Decorator for safe database operations
    
    Args:
        default_return: Value to return on error
        raise_on_error: Whether to raise exception or return default
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            logger = get_logger(func.__module__)
            
            try:
                return func(*args, **kwargs)
            
            except sqlite3.IntegrityError as e:
                logger.error(f"Database integrity error in {func.__name__}: {e}")
                if raise_on_error:
                    raise DatabaseError(f"Integrity constraint violated: {e}")
                return default_return
            
            except sqlite3.OperationalError as e:
                logger.error(f"Database operational error in {func.__name__}: {e}")
                if raise_on_error:
                    raise DatabaseError(f"Database operation failed: {e}")
                return default_return
            
            except sqlite3.Error as e:
                logger.error(f"Database error in {func.__name__}: {e}")
                if raise_on_error:
                    raise DatabaseError(f"Database error: {e}")
                return default_return
            
            except Exception as e:
                logger.exception(f"Unexpected error in {func.__name__}: {e}")
                if raise_on_error:
                    raise
                return default_return
        
        return wrapper
    return decorator


def safe_interface_operation(
    default_return: Any = None,
    fallback_interface: bool = True
) -> Callable:
    """
    Decorator for safe interface generation operations
    
    Args:
        default_return: Value to return on error
        fallback_interface: Whether to generate a fallback interface
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            logger = get_logger(func.__module__)
            
            try:
                return func(*args, **kwargs)
            
            except InterfaceGenerationError as e:
                logger.error(f"Interface generation error in {func.__name__}: {e}")
                
                if fallback_interface:
                    # Generate a simple fallback interface
                    from nl_interface_builder_v2 import GeneratedInterface, UIComponent
                    
                    fallback = GeneratedInterface(
                        components=[
                            UIComponent(
                                id="error_message",
                                type="alert",
                                properties={
                                    "message": "Interface generation encountered an error. Please try again.",
                                    "type": "warning"
                                }
                            ),
                            UIComponent(
                                id="retry_button",
                                type="button",
                                properties={
                                    "label": "Retry",
                                    "action": "retry_generation"
                                }
                            )
                        ],
                        metadata={
                            "error": str(e),
                            "fallback": True,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    return fallback
                
                return default_return
            
            except Exception as e:
                logger.exception(f"Unexpected error in {func.__name__}: {e}")
                return default_return
        
        return wrapper
    return decorator


def safe_async_operation(
    default_return: Any = None
) -> Callable:
    """
    Decorator for safe async operations
    
    Args:
        default_return: Value to return on error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            
            try:
                return await func(*args, **kwargs)
            
            except asyncio.CancelledError:
                logger.warning(f"Async operation cancelled: {func.__name__}")
                raise  # Re-raise cancellation
            
            except asyncio.TimeoutError:
                logger.error(f"Async operation timed out: {func.__name__}")
                return default_return
            
            except Exception as e:
                logger.exception(f"Async error in {func.__name__}: {e}")
                return default_return
        
        return wrapper
    return decorator


def safe_file_operation(
    default_return: Any = None,
    create_if_missing: bool = False
) -> Callable:
    """
    Decorator for safe file operations
    
    Args:
        default_return: Value to return on error
        create_if_missing: Whether to create file/directory if missing
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            logger = get_logger(func.__module__)
            
            try:
                return func(*args, **kwargs)
            
            except FileNotFoundError as e:
                logger.warning(f"File not found in {func.__name__}: {e}")
                
                if create_if_missing:
                    # Try to create the file/directory
                    path = Path(str(e.filename)) if hasattr(e, 'filename') else None
                    if path:
                        if path.suffix:  # It's a file
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.touch()
                        else:  # It's a directory
                            path.mkdir(parents=True, exist_ok=True)
                        
                        # Retry the operation
                        try:
                            return func(*args, **kwargs)
                        except Exception as retry_error:
                            logger.error(f"Retry failed after creating path: {retry_error}")
                
                return default_return
            
            except PermissionError as e:
                logger.error(f"Permission denied in {func.__name__}: {e}")
                return default_return
            
            except IOError as e:
                logger.error(f"I/O error in {func.__name__}: {e}")
                return default_return
            
            except Exception as e:
                logger.exception(f"Unexpected error in {func.__name__}: {e}")
                return default_return
        
        return wrapper
    return decorator


def safe_external_api_call(
    default_return: Any = None,
    max_retries: int = 3,
    timeout: int = 30
) -> Callable:
    """
    Decorator for safe external API calls
    
    Args:
        default_return: Value to return on error
        max_retries: Maximum number of retries
        timeout: Timeout in seconds
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            logger = get_logger(func.__module__)
            
            for attempt in range(max_retries):
                try:
                    # Add timeout to kwargs if not present
                    if 'timeout' not in kwargs:
                        kwargs['timeout'] = timeout
                    
                    return func(*args, **kwargs)
                
                except (ConnectionError, TimeoutError) as e:
                    logger.warning(f"Connection error in {func.__name__} (attempt {attempt+1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    
                    return default_return
                
                except Exception as e:
                    logger.exception(f"API call error in {func.__name__}: {e}")
                    return default_return
            
            return default_return
        
        return wrapper
    return decorator


class ErrorCollector:
    """Collects and aggregates errors for analysis"""
    
    def __init__(self, max_errors: int = 100):
        self.errors = []
        self.max_errors = max_errors
    
    def add_error(
        self,
        error_type: str,
        message: str,
        context: Optional[dict] = None
    ):
        """Add an error to the collection"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'context': context or {}
        }
        
        self.errors.append(error_entry)
        
        # Keep only the most recent errors
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors:]
    
    def get_error_summary(self) -> dict:
        """Get a summary of collected errors"""
        if not self.errors:
            return {'total': 0, 'types': {}}
        
        error_types = {}
        for error in self.errors:
            error_type = error['type']
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
        
        return {
            'total': len(self.errors),
            'types': error_types,
            'recent': self.errors[-5:] if len(self.errors) >= 5 else self.errors
        }
    
    def clear(self):
        """Clear all collected errors"""
        self.errors = []


# Global error collector instance
error_collector = ErrorCollector()


def handle_graceful_degradation(
    primary_func: Callable,
    fallback_func: Callable,
    *args,
    **kwargs
) -> Any:
    """
    Try primary function, fall back to secondary on failure
    
    Args:
        primary_func: Primary function to try
        fallback_func: Fallback function if primary fails
        *args: Arguments to pass to functions
        **kwargs: Keyword arguments to pass to functions
    """
    logger = get_logger(__name__)
    
    try:
        return primary_func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Primary function {primary_func.__name__} failed: {e}")
        logger.info(f"Falling back to {fallback_func.__name__}")
        
        try:
            return fallback_func(*args, **kwargs)
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            raise LuminousError(f"Both primary and fallback failed: {e}, {fallback_error}")


import asyncio

def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator to retry a function on failure
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each failure
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = get_logger(func.__module__)
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    logger.info(f"Retrying in {current_delay} seconds...")
                    
                    import time
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # This should never be reached
            raise LuminousError(f"Retry logic error in {func.__name__}")
        
        return wrapper
    return decorator


# Example usage patterns:
if __name__ == "__main__":
    # Example: Safe database operation
    @safe_database_operation(default_return=[])
    def get_user_data(user_id: int):
        # This would normally query a database
        import sqlite3
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchall()
    
    # Example: Safe interface generation
    @safe_interface_operation(fallback_interface=True)
    def generate_complex_interface(request: str):
        # This would normally generate an interface
        if "error" in request:
            raise InterfaceGenerationError("Cannot generate interface")
        return {"interface": "complex"}
    
    # Example: Retry on failure
    @retry_on_failure(max_attempts=3, delay=0.5)
    def unreliable_operation():
        import random
        if random.random() < 0.7:
            raise ConnectionError("Random failure")
        return "Success"
    
    # Test the decorators
    print("Testing error handlers...")
    print(f"Database result: {get_user_data(1)}")
    print(f"Interface result: {generate_complex_interface('error test')}")
    
    try:
        print(f"Retry result: {unreliable_operation()}")
    except Exception as e:
        print(f"Retry failed: {e}")
    
    # Show error summary
    print(f"Error summary: {error_collector.get_error_summary()}")