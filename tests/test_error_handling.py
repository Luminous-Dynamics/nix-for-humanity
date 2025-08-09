#!/usr/bin/env python3
"""
Test the comprehensive error handling system
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from nix_humanity.core.error_handler import (
    ErrorHandler, ErrorContext, ErrorCategory, ErrorSeverity,
    NixError, handle_error, safe_execute
)
from nix_humanity.utils.decorators import with_error_handling, with_timing, retry_on_error


class TestErrorHandler:
    """Test the error handler functionality"""
    
    def test_error_categorization(self):
        """Test that errors are correctly categorized"""
        handler = ErrorHandler()
        
        # Test permission error
        error = PermissionError("Access denied")
        category = handler._detect_category(error)
        assert category == ErrorCategory.PERMISSION
        
        # Test value error
        error = ValueError("Invalid input")
        category = handler._detect_category(error)
        assert category == ErrorCategory.VALIDATION
        
        # Test connection error
        error = ConnectionError("Network unreachable")
        category = handler._detect_category(error)
        assert category == ErrorCategory.NETWORK
        
        # Test NixOS-specific error
        error = Exception("attribute 'firefox' not found")
        category = handler._detect_category(error)
        assert category == ErrorCategory.NIXOS
    
    def test_severity_detection(self):
        """Test that severity is correctly detected"""
        handler = ErrorHandler()
        
        # Critical error
        error = Exception("critical system failure")
        severity = handler._detect_severity(error, ErrorCategory.SYSTEM)
        assert severity == ErrorSeverity.CRITICAL
        
        # Regular error
        error = Exception("permission denied")
        severity = handler._detect_severity(error, ErrorCategory.PERMISSION)
        assert severity == ErrorSeverity.ERROR
        
        # Warning
        error = Exception("warning: deprecated feature")
        severity = handler._detect_severity(error, ErrorCategory.UNKNOWN)
        assert severity == ErrorSeverity.WARNING
    
    def test_user_friendly_messages(self):
        """Test that user-friendly messages are generated"""
        handler = ErrorHandler()
        
        # Test NixOS error
        error = Exception("attribute 'firefox' not found")
        message, suggestions = handler._get_user_friendly_info(error, ErrorCategory.NIXOS)
        assert "Package or attribute not found" in message
        assert any("spell" in s.lower() for s in suggestions)
        
        # Test permission error
        error = PermissionError("permission denied")
        message, suggestions = handler._get_user_friendly_info(error, ErrorCategory.PERMISSION)
        assert "Permission denied" in message
        assert any("sudo" in s.lower() or "privilege" in s.lower() for s in suggestions)
    
    def test_error_code_generation(self):
        """Test that error codes are generated consistently"""
        handler = ErrorHandler()
        
        error1 = ValueError("test error")
        code1 = handler._generate_error_code(ErrorCategory.VALIDATION, error1)
        assert code1.startswith("NIX-VAL-")
        
        # Same error should generate same code
        error2 = ValueError("test error")
        code2 = handler._generate_error_code(ErrorCategory.VALIDATION, error2)
        assert code1 == code2
        
        # Different error should generate different code
        error3 = ValueError("different error")
        code3 = handler._generate_error_code(ErrorCategory.VALIDATION, error3)
        assert code1 != code3
    
    def test_handle_error_complete_flow(self):
        """Test the complete error handling flow"""
        handler = ErrorHandler(log_errors=False)  # Disable logging for tests
        
        context = ErrorContext(
            operation="install_package",
            user_input="install firefox",
            command=["nix-env", "-iA", "nixpkgs.firefox"]
        )
        
        error = Exception("attribute 'firefox' not found")
        nix_error = handler.handle_error(error, context)
        
        assert nix_error.category == ErrorCategory.NIXOS
        assert nix_error.user_message == "Package or attribute not found in NixOS"
        assert len(nix_error.suggestions) > 0
        assert nix_error.error_code.startswith("NIX-NIX-")
        assert nix_error.context == context
    
    def test_error_callbacks(self):
        """Test that error callbacks are called"""
        handler = ErrorHandler(log_errors=False)
        
        callback_called = False
        received_error = None
        
        def test_callback(error: NixError):
            nonlocal callback_called, received_error
            callback_called = True
            received_error = error
        
        handler.register_callback(test_callback)
        
        error = ValueError("test error")
        nix_error = handler.handle_error(error)
        
        assert callback_called
        assert received_error == nix_error


class TestDecorators:
    """Test the error handling decorators"""
    
    def test_with_error_handling_sync(self):
        """Test error handling decorator with sync functions"""
        @with_error_handling("test_operation", ErrorCategory.INTERNAL)
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError) as exc_info:
            failing_function()
        
        # Check that error was handled
        assert hasattr(exc_info.value, 'nix_error')
        assert exc_info.value.nix_error.category == ErrorCategory.INTERNAL
    
    @pytest.mark.asyncio
    async def test_with_error_handling_async(self):
        """Test error handling decorator with async functions"""
        @with_error_handling("test_async_operation", ErrorCategory.INTERNAL)
        async def async_failing_function():
            raise ValueError("Test async error")
        
        with pytest.raises(ValueError) as exc_info:
            await async_failing_function()
        
        # Check that error was handled
        assert hasattr(exc_info.value, 'nix_error')
        assert exc_info.value.nix_error.category == ErrorCategory.INTERNAL
    
    def test_retry_on_error(self):
        """Test retry decorator"""
        attempt_count = 0
        
        @retry_on_error(max_attempts=3, delay=0.01)
        def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Not yet!")
            return "Success"
        
        result = flaky_function()
        assert result == "Success"
        assert attempt_count == 3
    
    def test_retry_on_error_max_attempts(self):
        """Test retry decorator when max attempts exceeded"""
        @retry_on_error(max_attempts=2, delay=0.01)
        def always_failing():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_failing()


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_handle_error_convenience(self):
        """Test the convenience handle_error function"""
        error = ValueError("test error")
        nix_error = handle_error(
            error,
            operation="test_op",
            user_input="test input"
        )
        
        assert nix_error.category == ErrorCategory.VALIDATION
        assert nix_error.context.operation == "test_op"
        assert nix_error.context.user_input == "test input"
    
    def test_safe_execute(self):
        """Test safe_execute function"""
        def failing_func():
            raise ValueError("Test error")
        
        def working_func():
            return "Success"
        
        # Test with failing function - should return default
        result = safe_execute(failing_func, "test_op", "default")
        assert result == "default"
        
        # Test with working function
        result = safe_execute(working_func, "test_op", "default")
        assert result == "Success"
        
        # Test with reraise
        with pytest.raises(ValueError):
            safe_execute(failing_func, "test_op", reraise=True)


def test_nixos_error_patterns():
    """Test that NixOS-specific errors are recognized"""
    handler = ErrorHandler()
    
    patterns_to_test = [
        ("attribute 'firefox' not found", ErrorCategory.NIXOS),
        ("permission denied", ErrorCategory.PERMISSION),
        ("read-only file system", ErrorCategory.SYSTEM),
        ("network is unreachable", ErrorCategory.NETWORK),
        ("out of memory", ErrorCategory.SYSTEM),
        ("hash mismatch", ErrorCategory.NIXOS),
    ]
    
    for error_msg, expected_category in patterns_to_test:
        error = Exception(error_msg)
        category = handler._detect_category(error)
        assert category == expected_category, f"Failed for: {error_msg}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])