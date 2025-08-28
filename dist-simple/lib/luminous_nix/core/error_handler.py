#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Comprehensive Error Handling for Nix for Humanity
Provides consistent error handling, logging, and user-friendly error messages
"""

import logging
import traceback
import sys
import re
from typing import Optional, Dict, Any, List, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)


# Educational error message templates for v1.0
EDUCATIONAL_TEMPLATES = {'PACKAGE_NOT_FOUND': {'message': "I couldn't find the package '{package}' in the NixOS repositories.", 'education': "\n🎓 **Understanding NixOS Packages**\n\nNixOS packages are stored in channels (repositories). Sometimes a package:\n- Has a different name than expected (e.g., 'neovim' instead of 'nvim')\n- Is in a different channel (unstable vs stable)\n- Requires special attributes (e.g., 'python3Packages.numpy')\n", 'suggestions': ['Search for similar packages: `nix search nixpkgs {query}`', 'Check the exact name at: https://search.nixos.org', "Try variations: '{package}', '{package}-bin', '{package}Packages'", 'For Python packages: `python3Packages.{package}`', 'For Node packages: `nodePackages.{package}`'], 'next_steps': "Would you like me to search for packages similar to '{package}'?"}, 'PERMISSION_ERROR': {'message': 'This operation requires administrator privileges.', 'education': "\n🎓 **Understanding NixOS Permissions**\n\nNixOS has two types of operations:\n1. **User operations** - Install packages for your user only\n2. **System operations** - Modify the system configuration\n\nSystem operations need 'sudo' because they affect all users.\n", 'suggestions': ["For system-wide changes: Add 'sudo' before the command", 'For user-only installation: Use `nix profile install` instead', "Check if you're in the 'wheel' group for sudo access", 'Consider using Home Manager for user-specific configs'], 'next_steps': 'Should I show you both user and system installation methods?'}, 'NETWORK_ERROR': {'message': "I'm having trouble connecting to the NixOS package servers.", 'education': '\n🎓 **How NixOS Downloads Packages**\n\nNixOS fetches packages from binary caches:\n- Main cache: cache.nixos.org\n- Community cache: cachix.org\n- Your network needs to reach these servers\n', 'suggestions': ['Check your internet connection: `ping 8.8.8.8`', 'Test NixOS cache: `curl -I https://cache.nixos.org`', 'Try again - could be temporary', 'Check proxy settings if behind a firewall', 'Use `--offline` for already-downloaded packages'], 'next_steps': 'Would you like me to help diagnose your network connection?'}, 'CONFIG_SYNTAX_ERROR': {'message': "There's a syntax error in your NixOS configuration.", 'education': '\n🎓 **NixOS Configuration Language**\n\nNixOS uses the Nix language, which is:\n- **Functional** - Everything is an expression\n- **Pure** - No side effects\n- **Lazy** - Only evaluates what\'s needed\n\nCommon syntax rules:\n- Statements end with `;`\n- Lists use `[ ]`\n- Sets (objects) use `{ }`\n- Strings can use `"` or `\'\'`\n', 'suggestions': ['Check for missing semicolons (;)', 'Ensure all brackets match: { }, [ ], ( )', 'Verify string quotes are closed', 'Use `nixos-rebuild test` to validate', 'Try `nix-instantiate --parse` to check syntax'], 'next_steps': 'Would you like me to help identify the syntax issue?'}, 'DISK_SPACE_ERROR': {'message': 'Not enough disk space to complete this operation.', 'education': '\n🎓 **NixOS Storage Management**\n\nNixOS keeps all package versions in /nix/store:\n- Old versions are kept for rollbacks\n- This provides safety but uses disk space\n- Garbage collection removes unused packages\n', 'suggestions': ['Free space: `sudo nix-collect-garbage -d`', 'Check disk usage: `df -h`', 'See Nix store size: `du -sh /nix/store`', 'Remove old generations: `sudo nix-collect-garbage --delete-older-than 7d`', 'Consider moving /nix to a larger partition'], 'next_steps': 'Would you like me to help you free up disk space safely?'}, 'CHANNEL_ERROR': {'message': "There's an issue with your NixOS channels.", 'education': '\n🎓 **Understanding NixOS Channels**\n\nChannels are like package repositories:\n- **stable** - Well-tested, updated ~6 months\n- **unstable** - Latest packages, updated daily\n- You can mix channels for flexibility\n', 'suggestions': ['Update channels: `sudo nix-channel --update`', 'List channels: `sudo nix-channel --list`', 'Add nixos-unstable: `sudo nix-channel --add https://nixos.org/channels/nixos-unstable`', 'Check channel status: `nix-channel --list`', 'Rebuild after channel changes: `sudo nixos-rebuild switch`'], 'next_steps': 'Should I help you manage your channels?'}, 'BUILD_ERROR': {'message': 'The package failed to build from source.', 'education': "\n🎓 **NixOS Build System**\n\nSometimes NixOS builds packages from source when:\n- No binary cache is available\n- You've modified the package\n- You're using an overlay\n\nThis requires development tools and can take time.\n", 'suggestions': ['Check if a binary is available: `nix-env -qa {package}`', 'Look for build logs: `nix log {derivation}`', 'Try a different version or channel', 'Ensure build dependencies are available', 'Consider using a binary cache: cachix'], 'next_steps': 'Would you like to see the detailed build error?'}, 'SERVICE_ERROR': {'message': "The service '{service}' encountered an error.", 'education': '\n🎓 **NixOS Services**\n\nServices in NixOS are:\n- Defined declaratively in configuration.nix\n- Managed by systemd\n- Can have complex dependencies\n\nService states: active, failed, inactive\n', 'suggestions': ['Check service status: `systemctl status {service}`', 'View service logs: `journalctl -u {service} -e`', 'Restart service: `sudo systemctl restart {service}`', 'Check configuration: `nixos-option services.{service}`', 'Validate config: `sudo nixos-rebuild test`'], 'next_steps': 'Would you like me to help diagnose the service issue?'}}



class ErrorCategory(Enum):
    """Categories of errors for better handling and user messaging"""
    SECURITY = "security"            # Security violations
    PERMISSION = "permission"        # Permission denied
    VALIDATION = "validation"        # Input validation failures
    NETWORK = "network"             # Network-related errors
    NIXOS = "nixos"                # NixOS-specific errors
    SYSTEM = "system"              # System/OS errors
    CONFIGURATION = "configuration" # Configuration errors
    USER = "user"                  # User errors (wrong input)
    INTERNAL = "internal"          # Internal application errors
    UNKNOWN = "unknown"            # Unknown errors


class ErrorSeverity(Enum):
    """Severity levels for errors"""
    DEBUG = "debug"        # Debug information
    INFO = "info"          # Informational
    WARNING = "warning"    # Warning - operation continues
    ERROR = "error"        # Error - operation fails
    CRITICAL = "critical"  # Critical - system issue


@dataclass
class ErrorContext:
    """Context information for an error"""
    operation: str = ""              # What operation was being performed
    user_input: str = ""            # What the user provided
    command: List[str] = field(default_factory=list)  # Command that failed
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional info
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NixError:
    """Structured error information"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str                     # Technical error message
    user_message: str               # User-friendly message
    suggestions: List[str] = field(default_factory=list)
    context: Optional[ErrorContext] = None
    exception: Optional[Exception] = None
    traceback: Optional[str] = None
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'category': self.category.value,
            'severity': self.severity.value,
            'message': self.message,
            'user_message': self.user_message,
            'suggestions': self.suggestions,
            'error_code': self.error_code,
            'timestamp': self.context.timestamp.isoformat() if self.context else None,
            'operation': self.context.operation if self.context else None
        }


class ErrorHandler:
    """
    Comprehensive error handler for Nix for Humanity
    
    Features:
    - Categorized error handling
    - User-friendly error messages
    - Helpful suggestions for recovery
    - Logging with appropriate severity
    - Error pattern learning (future)
    """
    
    # Common NixOS error patterns and their handling
    NIXOS_ERROR_PATTERNS = {
        r"attribute.*not found": {
            'category': ErrorCategory.NIXOS,
            'user_message': "Package or attribute not found in NixOS",
            'suggestions': [
                "Check if the package name is spelled correctly",
                "Try searching with: nix search nixpkgs <name>",
                "The package might be in a different channel"
            ]
        },
        r"permission denied": {
            'category': ErrorCategory.PERMISSION,
            'user_message': "Permission denied for this operation",
            'suggestions': [
                "This operation requires elevated privileges",
                "Try running with sudo if appropriate",
                "Check file permissions"
            ]
        },
        r"read-only file system": {
            'category': ErrorCategory.SYSTEM,
            'user_message': "Cannot write to read-only file system",
            'suggestions': [
                "The Nix store is immutable",
                "Use proper NixOS configuration methods",
                "Check if the filesystem is mounted correctly"
            ]
        },
        r"network.*unreachable": {
            'category': ErrorCategory.NETWORK,
            'user_message': "Network connection issue",
            'suggestions': [
                "Check your internet connection",
                "Verify network settings",
                "Try again in a moment"
            ]
        },
        r"out of memory": {
            'category': ErrorCategory.SYSTEM,
            'user_message': "System ran out of memory",
            'suggestions': [
                "Close some applications to free memory",
                "Consider increasing swap space",
                "Try a lighter operation"
            ]
        },
        r"hash mismatch": {
            'category': ErrorCategory.NIXOS,
            'user_message': "Package integrity check failed",
            'suggestions': [
                "This might be a temporary issue",
                "Try updating your channels: nix-channel --update",
                "Clear the cache and try again"
            ]
        }
    }
    
    def __init__(self, log_errors: bool = True, collect_metrics: bool = False):
        """
        Initialize error handler
        
        Args:
            log_errors: Whether to log errors
            collect_metrics: Whether to collect error metrics for learning
        """
        self.log_errors = log_errors
        self.collect_metrics = collect_metrics
        self.error_callbacks: List[Callable[[NixError], None]] = []
        
    def handle_error(self, 
                    exception: Exception,
                    context: Optional[ErrorContext] = None,
                    category: Optional[ErrorCategory] = None,
                    severity: Optional[ErrorSeverity] = None) -> NixError:
        """
        Handle an exception and return structured error information
        
        Args:
            exception: The exception that occurred
            context: Context about what was happening
            category: Error category (will be detected if not provided)
            severity: Error severity (will be detected if not provided)
            
        Returns:
            NixError with all relevant information
        """
        # Detect category and create appropriate error
        if category is None:
            category = self._detect_category(exception)
            
        if severity is None:
            severity = self._detect_severity(exception, category)
            
        # Get user-friendly message and suggestions
        user_message, suggestions = self._get_user_friendly_info(exception, category)
        
        # Create structured error
        nix_error = NixError(
            category=category,
            severity=severity,
            message=str(exception),
            user_message=user_message,
            suggestions=suggestions,
            context=context,
            exception=exception,
            traceback=traceback.format_exc() if self.log_errors else None,
            error_code=self._generate_error_code(category, exception)
        )
        
        # Log if enabled
        if self.log_errors:
            self._log_error(nix_error)
            
        # Collect metrics if enabled
        if self.collect_metrics:
            self._collect_error_metrics(nix_error)
            
        # Call registered callbacks
        for callback in self.error_callbacks:
            try:
                callback(nix_error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
                
        return nix_error
        
    def _detect_category(self, exception: Exception) -> ErrorCategory:
        """Detect error category from exception"""
        error_str = str(exception).lower()
        
        # Check common patterns
        import re
        for pattern, info in self.NIXOS_ERROR_PATTERNS.items():
            if re.search(pattern, error_str, re.IGNORECASE):
                return info['category']
                
        # Check exception types
        if isinstance(exception, PermissionError):
            return ErrorCategory.PERMISSION
        elif isinstance(exception, ValueError):
            return ErrorCategory.VALIDATION
        elif isinstance(exception, ConnectionError):
            return ErrorCategory.NETWORK
        elif isinstance(exception, OSError):
            return ErrorCategory.SYSTEM
        elif hasattr(exception, '__module__') and 'security' in exception.__module__:
            return ErrorCategory.SECURITY
            
        return ErrorCategory.UNKNOWN
        
    def _detect_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Detect error severity"""
        # Critical errors
        if category in [ErrorCategory.SECURITY, ErrorCategory.SYSTEM]:
            if "critical" in str(exception).lower():
                return ErrorSeverity.CRITICAL
                
        # Errors
        if category in [ErrorCategory.PERMISSION, ErrorCategory.NIXOS, ErrorCategory.VALIDATION]:
            return ErrorSeverity.ERROR
            
        # Warnings
        if "warning" in str(exception).lower():
            return ErrorSeverity.WARNING
            
        return ErrorSeverity.ERROR
        
    def _get_user_friendly_info(self, exception: Exception, category: ErrorCategory) -> tuple[str, List[str]]:
        """
        Get user-friendly error message and suggestions
        Enhanced with educational content for v1.0
        """
        error_str = str(exception).lower()
        
        # Check for specific error patterns
        if category == ErrorCategory.NIXOS:
            if "not found" in error_str or "attribute" in error_str:
                # Extract package name if possible
                package_match = re.search(r"attribute ['\"]?(\w+)['\"]?", str(exception))
                package = package_match.group(1) if package_match else "the package"
                
                template = EDUCATIONAL_TEMPLATES["PACKAGE_NOT_FOUND"]
                return (
                    template["message"].format(package=package),
                    template["suggestions"] + ["\n🎓 " + template["education"]]
                )
            elif "hash mismatch" in error_str:
                return (
                    "Package integrity check failed. This usually means the package definition changed.",
                    [
                        "Update your channels: sudo nix-channel --update",
                        "Try again - this is often temporary",
                        "Clear cache if persistent: nix-collect-garbage",
                        "\n🎓 NixOS verifies all packages with cryptographic hashes for security"
                    ]
                )
                
        elif category == ErrorCategory.PERMISSION:
            template = EDUCATIONAL_TEMPLATES["PERMISSION_ERROR"]
            return (
                template["message"],
                template["suggestions"] + ["\n🎓 " + template["education"]]
            )
            
        elif category == ErrorCategory.NETWORK:
            template = EDUCATIONAL_TEMPLATES["NETWORK_ERROR"]
            return (
                template["message"],
                template["suggestions"] + ["\n🎓 " + template["education"]]
            )
            
        elif category == ErrorCategory.SYSTEM:
            if "no space left" in error_str or "disk full" in error_str:
                template = EDUCATIONAL_TEMPLATES["DISK_SPACE_ERROR"]
                return (
                    template["message"],
                    template["suggestions"] + ["\n🎓 " + template["education"]]
                )
                
        elif category == ErrorCategory.CONFIGURATION:
            if "syntax" in error_str or "parse" in error_str:
                template = EDUCATIONAL_TEMPLATES["CONFIG_SYNTAX_ERROR"]
                return (
                    template["message"],
                    template["suggestions"] + ["\n🎓 " + template["education"]]
                )
        
        # Check pattern matching for any category
        for pattern, info in self.NIXOS_ERROR_PATTERNS.items():
            if re.search(pattern, error_str, re.IGNORECASE):
                # Add educational note to suggestions
                enhanced_suggestions = info['suggestions'].copy()
                if info['category'] == ErrorCategory.NIXOS:
                    enhanced_suggestions.append("\n🎓 Learn more at: https://nixos.org/manual/")
                return info['user_message'], enhanced_suggestions
                
        # Default messages with educational hints
        default_messages = {
            ErrorCategory.SECURITY: (
                "Security check failed for safety reasons", 
                ["Verify the source is trusted", "Check for typos in commands", "\n🎓 NixOS prioritizes security"]
            ),
            ErrorCategory.VALIDATION: (
                "The input doesn't match what I expected",
                ["Check the command format", "Use 'help' to see examples", "\n🎓 Proper syntax helps me help you better"]
            ),
            ErrorCategory.USER: (
                "I couldn't understand that request",
                ["Try rephrasing more simply", "Use 'help' for examples", "\n🎓 I'm still learning natural language"]
            ),
            ErrorCategory.INTERNAL: (
                "Something went wrong on my end",
                ["Try again in a moment", "Report this if it persists", "\n🎓 Even AI assistants have hiccups sometimes"]
            )
        }
        
        return default_messages.get(
            category, 
            ("An unexpected error occurred", ["Try again or ask for help", "\n🎓 Learning from errors makes us better"])
        )
    def _generate_error_code(self, category: ErrorCategory, exception: Exception) -> str:
        """Generate a unique error code for tracking"""
        import hashlib
        error_str = f"{category.value}:{type(exception).__name__}:{str(exception)[:50]}"
        return f"NIX-{category.value.upper()[:3]}-{hashlib.md5(error_str.encode()).hexdigest()[:6].upper()}"
        
    def _log_error(self, error: NixError):
        """Log error with appropriate level"""
        log_func = {
            ErrorSeverity.DEBUG: logger.debug,
            ErrorSeverity.INFO: logger.info,
            ErrorSeverity.WARNING: logger.warning,
            ErrorSeverity.ERROR: logger.error,
            ErrorSeverity.CRITICAL: logger.critical
        }.get(error.severity, logger.error)
        
        log_func(
            f"[{error.error_code}] {error.category.value}: {error.message}",
            extra={
                'error_code': error.error_code,
                'category': error.category.value,
                'operation': error.context.operation if error.context else None
            }
        )
        
        if error.traceback and error.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            logger.debug(f"Traceback:\n{error.traceback}")
            
    def _collect_error_metrics(self, error: NixError):
        """Collect error metrics for learning (future feature)"""
        # This could store errors for pattern analysis
        # For now, just log that we would collect it
        logger.debug(f"Would collect metrics for error: {error.error_code}")
        
    def register_callback(self, callback: Callable[[NixError], None]):
        """Register a callback to be called on errors"""
        self.error_callbacks.append(callback)
        
    def wrap_operation(self, operation_name: str):
        """Decorator to wrap operations with error handling"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                context = ErrorContext(operation=operation_name)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error = self.handle_error(e, context)
                    # Re-raise with our error info attached
                    e.nix_error = error
                    raise
            return wrapper
        return decorator


# Global error handler instance
error_handler = ErrorHandler()


# Convenience functions
def handle_error(exception: Exception, 
                operation: str = "",
                user_input: str = "") -> NixError:
    """Convenience function to handle errors"""
    context = ErrorContext(
        operation=operation,
        user_input=user_input
    )
    return error_handler.handle_error(exception, context)


def safe_execute(func: Callable, 
                operation: str = "",
                default_return: Any = None,
                reraise: bool = False) -> Any:
    """Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        error = handle_error(e, operation)
        if reraise:
            raise
        return default_return