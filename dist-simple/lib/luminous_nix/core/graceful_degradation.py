#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Graceful Degradation System for Nix for Humanity

Handles various failure scenarios gracefully, providing fallbacks and helpful
guidance when system resources or features are unavailable.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
import psutil
import logging
from datetime import datetime, timedelta

from .error_handler import ErrorCategory, ErrorSeverity, NixError, ErrorContext
from ..utils.logging import get_logger

logger = get_logger(__name__)


class DegradationLevel(Enum):
    """Levels of system degradation"""
    FULL = "full"              # All features available
    LIMITED = "limited"        # Some features disabled
    MINIMAL = "minimal"        # Basic functionality only
    OFFLINE = "offline"        # No network features
    EMERGENCY = "emergency"    # Bare minimum


class ResourceType(Enum):
    """Types of system resources"""
    MEMORY = "memory"
    DISK = "disk"
    CPU = "cpu"
    NETWORK = "network"
    NIX_DAEMON = "nix_daemon"
    PERMISSIONS = "permissions"


@dataclass
class SystemConstraints:
    """Current system constraints"""
    available_memory_mb: int = 0
    available_disk_mb: int = 0
    cpu_usage_percent: float = 0.0
    is_offline: bool = False
    nix_daemon_available: bool = True
    has_sudo: bool = True
    nixos_version: Optional[str] = None
    missing_features: List[str] = None
    
    def __post_init__(self):
        if self.missing_features is None:
            self.missing_features = []


@dataclass
class DegradationStrategy:
    """Strategy for handling degraded conditions"""
    level: DegradationLevel
    disabled_features: List[str]
    fallback_message: str
    recovery_suggestions: List[str]
    alternative_commands: Dict[str, str]


class GracefulDegradation:
    """
    Manages graceful degradation of functionality based on system constraints.
    
    Features:
    - Detects system limitations
    - Provides appropriate fallbacks
    - Offers helpful suggestions
    - Maintains core functionality
    """
    
    # Minimum requirements for different levels
    MIN_MEMORY_FULL = 512      # MB for full features
    MIN_MEMORY_LIMITED = 256   # MB for limited features
    MIN_MEMORY_MINIMAL = 128   # MB for minimal features
    MIN_DISK_SPACE = 100       # MB minimum disk space
    
    # Feature requirements
    FEATURE_REQUIREMENTS = {
        'voice_interface': {'memory': 1024, 'network': True},
        'learning_system': {'memory': 256, 'disk': 50},
        'cache_system': {'memory': 128, 'disk': 100},
        'visual_effects': {'memory': 256},
        'parallel_processing': {'memory': 512, 'cpu_cores': 2},
        'auto_complete': {'memory': 128},
        'rich_formatting': {'memory': 64},
        'progress_indicators': {'memory': 32}
    }
    
    def __init__(self):
        self.constraints = SystemConstraints()
        self.current_level = DegradationLevel.FULL
        self.disabled_features = set()
        self.fallback_callbacks: Dict[str, Callable] = {}
        self._last_check = None
        self._check_interval = timedelta(minutes=5)
        
    def check_system(self, force: bool = False) -> SystemConstraints:
        """Check current system constraints"""
        # Rate limit checks unless forced
        if not force and self._last_check:
            if datetime.now() - self._last_check < self._check_interval:
                return self.constraints
                
        try:
            # Memory check
            memory = psutil.virtual_memory()
            self.constraints.available_memory_mb = memory.available // (1024 * 1024)
            
            # Disk check
            disk = psutil.disk_usage('/')
            self.constraints.available_disk_mb = disk.free // (1024 * 1024)
            
            # CPU check
            self.constraints.cpu_usage_percent = psutil.cpu_percent(interval=0.1)
            
            # Network check
            self.constraints.is_offline = not self._check_network()
            
            # Nix daemon check
            self.constraints.nix_daemon_available = self._check_nix_daemon()
            
            # Permissions check
            self.constraints.has_sudo = self._check_sudo_available()
            
            # NixOS version
            self.constraints.nixos_version = self._get_nixos_version()
            
            # Check for missing commands/features
            self.constraints.missing_features = self._check_missing_features()
            
            self._last_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Error checking system constraints: {e}")
            
        return self.constraints
        
    def determine_level(self) -> DegradationLevel:
        """Determine appropriate degradation level"""
        constraints = self.check_system()
        
        # Emergency mode if critical resources missing
        if (constraints.available_memory_mb < self.MIN_MEMORY_MINIMAL or
            constraints.available_disk_mb < 10 or
            not shutil.which('nix')):
            return DegradationLevel.EMERGENCY
            
        # Offline mode if no network
        if constraints.is_offline:
            return DegradationLevel.OFFLINE
            
        # Minimal mode for very low resources
        if (constraints.available_memory_mb < self.MIN_MEMORY_LIMITED or
            constraints.available_disk_mb < self.MIN_DISK_SPACE):
            return DegradationLevel.MINIMAL
            
        # Limited mode for constrained resources
        if (constraints.available_memory_mb < self.MIN_MEMORY_FULL or
            not constraints.nix_daemon_available or
            constraints.cpu_usage_percent > 80):
            return DegradationLevel.LIMITED
            
        return DegradationLevel.FULL
        
    def get_strategy(self) -> DegradationStrategy:
        """Get degradation strategy for current conditions"""
        level = self.determine_level()
        self.current_level = level
        
        strategies = {
            DegradationLevel.FULL: DegradationStrategy(
                level=level,
                disabled_features=[],
                fallback_message="All features available",
                recovery_suggestions=[],
                alternative_commands={}
            ),
            
            DegradationLevel.LIMITED: DegradationStrategy(
                level=level,
                disabled_features=['voice_interface', 'parallel_processing'],
                fallback_message="Running with limited features due to resource constraints",
                recovery_suggestions=[
                    "Close some applications to free memory",
                    "Features will re-enable when resources are available"
                ],
                alternative_commands={
                    'voice': 'Use text input instead'
                }
            ),
            
            DegradationLevel.MINIMAL: DegradationStrategy(
                level=level,
                disabled_features=['voice_interface', 'learning_system', 'cache_system', 
                                   'visual_effects', 'parallel_processing', 'rich_formatting'],
                fallback_message="Running in minimal mode due to low resources",
                recovery_suggestions=[
                    "Free up system resources",
                    "Consider closing other applications",
                    "Basic functionality is still available"
                ],
                alternative_commands={
                    'search': 'Use simple search without caching',
                    'install': 'Installation will be slower'
                }
            ),
            
            DegradationLevel.OFFLINE: DegradationStrategy(
                level=level,
                disabled_features=['package_search', 'package_install', 'system_update',
                                   'online_help', 'remote_operations'],
                fallback_message="Running in offline mode",
                recovery_suggestions=[
                    "Check your internet connection",
                    "Local operations are still available",
                    "Package queries use cached data only"
                ],
                alternative_commands={
                    'search': 'search --cached',
                    'install': 'Use local packages only',
                    'help': 'Use offline documentation'
                }
            ),
            
            DegradationLevel.EMERGENCY: DegradationStrategy(
                level=level,
                disabled_features=['all_except_basic'],
                fallback_message="Emergency mode - only basic operations available",
                recovery_suggestions=[
                    "Critical system resources are exhausted",
                    "Free up disk space or memory urgently",
                    "Consider rebooting if system is unresponsive"
                ],
                alternative_commands={}
            )
        }
        
        strategy = strategies[level]
        
        # Update disabled features based on specific constraints
        self._update_disabled_features(strategy)
        
        return strategy
        
    def _update_disabled_features(self, strategy: DegradationStrategy) -> None:
        """Update disabled features based on specific requirements"""
        constraints = self.constraints
        
        for feature, requirements in self.FEATURE_REQUIREMENTS.items():
            should_disable = False
            
            # Check memory requirement
            if 'memory' in requirements:
                if constraints.available_memory_mb < requirements['memory']:
                    should_disable = True
                    
            # Check disk requirement
            if 'disk' in requirements:
                if constraints.available_disk_mb < requirements['disk']:
                    should_disable = True
                    
            # Check network requirement
            if requirements.get('network') and constraints.is_offline:
                should_disable = True
                
            # Check CPU cores
            if 'cpu_cores' in requirements:
                if psutil.cpu_count() < requirements['cpu_cores']:
                    should_disable = True
                    
            if should_disable and feature not in strategy.disabled_features:
                strategy.disabled_features.append(feature)
                self.disabled_features.add(feature)
                
    def is_feature_available(self, feature: str) -> bool:
        """Check if a feature is available"""
        if self.current_level == DegradationLevel.FULL:
            return True
            
        return feature not in self.disabled_features
        
    def get_fallback_command(self, original_command: str) -> Optional[str]:
        """Get fallback command for unavailable feature"""
        strategy = self.get_strategy()
        
        # Check for direct alternative
        for cmd, alternative in strategy.alternative_commands.items():
            if cmd in original_command:
                return alternative
                
        # Check for feature-specific fallbacks
        if not self.constraints.nix_daemon_available:
            if 'nixos-rebuild' in original_command:
                return "Use 'nixos-rebuild --no-build-nix' or start nix-daemon"
                
        if not self.constraints.has_sudo:
            if 'sudo' in original_command:
                return original_command.replace('sudo ', '') + " (without sudo)"
                
        return None
        
    def handle_resource_error(self, error: Exception, operation: str) -> NixError:
        """Handle resource-related errors gracefully"""
        context = ErrorContext(operation=operation)
        
        # Determine error type
        error_str = str(error).lower()
        
        if 'memory' in error_str or 'cannot allocate' in error_str:
            return self._handle_memory_error(error, context)
        elif 'no space' in error_str or 'disk full' in error_str:
            return self._handle_disk_error(error, context)
        elif 'network' in error_str or 'connection' in error_str:
            return self._handle_network_error(error, context)
        elif 'permission' in error_str:
            return self._handle_permission_error(error, context)
        else:
            return self._handle_generic_error(error, context)
            
    def _handle_memory_error(self, error: Exception, context: ErrorContext) -> NixError:
        """Handle out of memory errors"""
        available = self.constraints.available_memory_mb
        
        suggestions = [
            f"Only {available}MB memory available",
            "Close some applications to free memory",
            "Try the operation again with --minimal flag"
        ]
        
        if available < 100:
            suggestions.append("Consider adding swap space")
            
        return NixError(
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            user_message="Not enough memory to complete operation",
            suggestions=suggestions,
            context=context,
            exception=error
        )
        
    def _handle_disk_error(self, error: Exception, context: ErrorContext) -> NixError:
        """Handle disk space errors"""
        available = self.constraints.available_disk_mb
        
        suggestions = [
            f"Only {available}MB disk space available",
            "Run 'nix-collect-garbage -d' to free space",
            "Remove old generations with 'nix-env --delete-generations old'",
            "Check /tmp for large temporary files"
        ]
        
        return NixError(
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            user_message="Not enough disk space",
            suggestions=suggestions,
            context=context,
            exception=error
        )
        
    def _handle_network_error(self, error: Exception, context: ErrorContext) -> NixError:
        """Handle network errors"""
        suggestions = ["Check your internet connection"]
        
        if self.constraints.is_offline:
            suggestions.extend([
                "You appear to be offline",
                "Try using cached packages with --offline",
                "Some operations require internet access"
            ])
        else:
            suggestions.extend([
                "The remote server may be down",
                "Try again in a few moments",
                "Check proxy settings if applicable"
            ])
            
        return NixError(
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.WARNING,
            message=str(error),
            user_message="Network operation failed",
            suggestions=suggestions,
            context=context,
            exception=error
        )
        
    def _handle_permission_error(self, error: Exception, context: ErrorContext) -> NixError:
        """Handle permission errors"""
        suggestions = []
        
        if not self.constraints.has_sudo:
            suggestions.append("sudo is not available on this system")
            suggestions.append("Try running as root user if needed")
        else:
            suggestions.append("This operation requires elevated privileges")
            suggestions.append("Try with sudo if appropriate")
            
        suggestions.append("Check file ownership and permissions")
        
        return NixError(
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            user_message="Permission denied",
            suggestions=suggestions,
            context=context,
            exception=error
        )
        
    def _handle_generic_error(self, error: Exception, context: ErrorContext) -> NixError:
        """Handle generic errors with degradation context"""
        suggestions = ["An unexpected error occurred"]
        
        # Add relevant suggestions based on current state
        if self.current_level != DegradationLevel.FULL:
            suggestions.append(f"System running in {self.current_level.value} mode")
            
        strategy = self.get_strategy()
        if strategy.recovery_suggestions:
            suggestions.extend(strategy.recovery_suggestions)
            
        return NixError(
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            user_message="Operation failed",
            suggestions=suggestions,
            context=context,
            exception=error
        )
        
    def _check_network(self) -> bool:
        """Check if network is available"""
        try:
            import socket
            # Try to connect to common DNS servers
            for host in ['8.8.8.8', '1.1.1.1']:
                try:
                    socket.create_connection((host, 53), timeout=1)
                    return True
                except Exception:
                    continue
            return False
        except Exception:
            return False
            
    def _check_nix_daemon(self) -> bool:
        """Check if nix-daemon is available"""
        try:
            # Check systemd service
            result = subprocess.run(
                ['systemctl', 'is-active', 'nix-daemon'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return True
                
            # Check socket directly
            return Path('/nix/var/nix/daemon-socket/socket').exists()
        except Exception:
            return False
            
    def _check_sudo_available(self) -> bool:
        """Check if sudo is available"""
        return shutil.which('sudo') is not None
        
    def _get_nixos_version(self) -> Optional[str]:
        """Get NixOS version if available"""
        try:
            if Path('/etc/nixos/configuration.nix').exists():
                result = subprocess.run(
                    ['nixos-version'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return None
        
    def _check_missing_features(self) -> List[str]:
        """Check for missing system features"""
        missing = []
        
        # Check common commands
        commands = {
            'nix': 'Nix package manager',
            'home-manager': 'Home Manager',
            'git': 'Git version control',
            'curl': 'HTTP client'
        }
        
        for cmd, name in commands.items():
            if not shutil.which(cmd):
                missing.append(name)
                
        return missing
        
    def register_fallback(self, feature: str, callback: Callable) -> None:
        """Register a fallback handler for a feature"""
        self.fallback_callbacks[feature] = callback
        
    def get_status_message(self) -> str:
        """Get human-readable status message"""
        strategy = self.get_strategy()
        
        if self.current_level == DegradationLevel.FULL:
            return "✅ All systems operational"
            
        message = f"⚠️  {strategy.fallback_message}\n"
        
        if strategy.disabled_features:
            message += f"Disabled: {', '.join(strategy.disabled_features[:3])}"
            if len(strategy.disabled_features) > 3:
                message += f" (+{len(strategy.disabled_features)-3} more)"
                
        return message


# Global instance
degradation_handler = GracefulDegradation()


def check_degradation() -> DegradationStrategy:
    """Check current degradation level and get strategy"""
    return degradation_handler.get_strategy()


def handle_degraded_operation(operation: Callable, *args, **kwargs) -> Any:
    """Execute operation with degradation handling"""
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        # Check if this is a resource error
        error = degradation_handler.handle_resource_error(e, operation.__name__)
        
        # Log the error
        logger.error(f"Degraded operation failed: {error.user_message}")
        
        # Try fallback if available
        if operation.__name__ in degradation_handler.fallback_callbacks:
            fallback = degradation_handler.fallback_callbacks[operation.__name__]
            try:
                logger.info(f"Attempting fallback for {operation.__name__}")
                return fallback(*args, **kwargs)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                
        # Re-raise with our error attached
        e.nix_error = error
        raise