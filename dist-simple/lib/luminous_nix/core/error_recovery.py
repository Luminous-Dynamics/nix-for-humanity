"""
Intelligent error recovery system for Luminous Nix
"""

import re
import subprocess
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class ErrorType(Enum):
    """Types of errors we can handle"""
    PACKAGE_NOT_FOUND = "package_not_found"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    DISK_SPACE = "disk_space"
    BROKEN_PACKAGE = "broken_package"
    CHANNEL_ERROR = "channel_error"
    BUILD_ERROR = "build_error"
    CONFLICT = "conflict"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

@dataclass
class ErrorContext:
    """Context about an error"""
    error_type: ErrorType
    original_error: str
    command: Optional[str] = None
    package: Optional[str] = None
    suggestions: List[str] = None
    can_auto_fix: bool = False
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

@dataclass
class RecoveryStrategy:
    """A strategy for recovering from an error"""
    name: str
    description: str
    commands: List[str]
    requires_sudo: bool = False
    success_rate: float = 0.5  # Estimated success rate

class ErrorRecovery:
    """
    Intelligent error recovery system
    
    Features:
    - Error classification
    - Contextual recovery strategies
    - Learning from successful recoveries
    - User-friendly explanations
    """
    
    def __init__(self):
        """Initialize error recovery system"""
        # Error patterns for classification
        self.error_patterns = {
            ErrorType.PACKAGE_NOT_FOUND: [
                r"attribute .* not found",
                r"Package .* not found",
                r"error: undefined variable",
                r"no such package",
            ],
            ErrorType.PERMISSION_DENIED: [
                r"Permission denied",
                r"Operation not permitted",
                r"must be run as root",
                r"sudo.*required",
            ],
            ErrorType.NETWORK_ERROR: [
                r"Network.*unreachable",
                r"Connection.*refused",
                r"Unable to download",
                r"curl.*error",
                r"timeout.*exceeded",
            ],
            ErrorType.DISK_SPACE: [
                r"No space left on device",
                r"disk.*full",
                r"out of space",
            ],
            ErrorType.BROKEN_PACKAGE: [
                r"broken.*package",
                r"dependency.*broken",
                r"collision between",
            ],
            ErrorType.CHANNEL_ERROR: [
                r"channel.*not found",
                r"updating channel",
                r"nix-channel",
            ],
            ErrorType.BUILD_ERROR: [
                r"build.*failed",
                r"compilation.*error",
                r"make.*error",
            ],
            ErrorType.CONFLICT: [
                r"conflict",
                r"collision",
                r"already exists",
            ],
            ErrorType.TIMEOUT: [
                r"timeout",
                r"timed out",
                r"took too long",
            ]
        }
        
        # Recovery strategies for each error type
        self.recovery_strategies = {
            ErrorType.PACKAGE_NOT_FOUND: [
                RecoveryStrategy(
                    name="search_similar",
                    description="Search for similar package names",
                    commands=["nix search nixpkgs {package}"],
                    success_rate=0.7
                ),
                RecoveryStrategy(
                    name="update_channels",
                    description="Update package channels",
                    commands=["sudo nix-channel --update"],
                    requires_sudo=True,
                    success_rate=0.5
                ),
            ],
            ErrorType.PERMISSION_DENIED: [
                RecoveryStrategy(
                    name="use_sudo",
                    description="Retry with sudo privileges",
                    commands=["sudo {original_command}"],
                    requires_sudo=True,
                    success_rate=0.9
                ),
            ],
            ErrorType.NETWORK_ERROR: [
                RecoveryStrategy(
                    name="retry",
                    description="Retry the operation",
                    commands=["{original_command}"],
                    success_rate=0.6
                ),
                RecoveryStrategy(
                    name="use_cache",
                    description="Use cached version if available",
                    commands=["nix-env -iA nixos.{package} --option substitute true"],
                    success_rate=0.4
                ),
            ],
            ErrorType.DISK_SPACE: [
                RecoveryStrategy(
                    name="garbage_collect",
                    description="Clean up Nix store to free space",
                    commands=["nix-collect-garbage -d"],
                    success_rate=0.8
                ),
                RecoveryStrategy(
                    name="remove_old_generations",
                    description="Remove old system generations",
                    commands=["sudo nix-collect-garbage -d --delete-old"],
                    requires_sudo=True,
                    success_rate=0.7
                ),
            ],
            ErrorType.BROKEN_PACKAGE: [
                RecoveryStrategy(
                    name="repair",
                    description="Repair Nix store",
                    commands=["nix-store --verify --check-contents --repair"],
                    success_rate=0.6
                ),
                RecoveryStrategy(
                    name="rebuild",
                    description="Rebuild without the broken package",
                    commands=["sudo nixos-rebuild switch"],
                    requires_sudo=True,
                    success_rate=0.5
                ),
            ],
            ErrorType.CHANNEL_ERROR: [
                RecoveryStrategy(
                    name="add_channel",
                    description="Add the nixos channel",
                    commands=["sudo nix-channel --add https://nixos.org/channels/nixos-unstable nixos"],
                    requires_sudo=True,
                    success_rate=0.8
                ),
                RecoveryStrategy(
                    name="update_channel",
                    description="Update all channels",
                    commands=["sudo nix-channel --update"],
                    requires_sudo=True,
                    success_rate=0.7
                ),
            ],
            ErrorType.TIMEOUT: [
                RecoveryStrategy(
                    name="use_cache",
                    description="Use local cache instead",
                    commands=["nix search --use-cache {package}"],
                    success_rate=0.8
                ),
                RecoveryStrategy(
                    name="retry_patient",
                    description="Retry with longer timeout",
                    commands=["timeout 600 {original_command}"],
                    success_rate=0.5
                ),
            ],
        }
    
    def analyze_error(self, error_message: str, command: Optional[str] = None) -> ErrorContext:
        """
        Analyze an error message and classify it
        
        Args:
            error_message: The error message to analyze
            command: The command that caused the error
            
        Returns:
            ErrorContext with classification and suggestions
        """
        error_lower = error_message.lower()
        
        # Try to classify the error
        error_type = ErrorType.UNKNOWN
        for etype, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    error_type = etype
                    break
            if error_type != ErrorType.UNKNOWN:
                break
        
        # Extract package name if present
        package = self._extract_package_name(error_message, command)
        
        # Create error context
        context = ErrorContext(
            error_type=error_type,
            original_error=error_message,
            command=command,
            package=package
        )
        
        # Add suggestions based on error type
        if error_type in self.recovery_strategies:
            strategies = self.recovery_strategies[error_type]
            for strategy in strategies:
                context.suggestions.append(strategy.description)
            
            # Check if we can auto-fix
            if strategies and strategies[0].success_rate > 0.7:
                context.can_auto_fix = True
        
        return context
    
    def get_recovery_strategies(self, context: ErrorContext) -> List[RecoveryStrategy]:
        """
        Get recovery strategies for an error context
        
        Args:
            context: The error context
            
        Returns:
            List of applicable recovery strategies
        """
        if context.error_type in self.recovery_strategies:
            strategies = self.recovery_strategies[context.error_type]
            
            # Customize strategies with actual values
            customized = []
            for strategy in strategies:
                custom_strategy = RecoveryStrategy(
                    name=strategy.name,
                    description=strategy.description,
                    commands=[self._customize_command(cmd, context) for cmd in strategy.commands],
                    requires_sudo=strategy.requires_sudo,
                    success_rate=strategy.success_rate
                )
                customized.append(custom_strategy)
            
            return customized
        
        return []
    
    def explain_error(self, context: ErrorContext) -> str:
        """
        Generate a user-friendly explanation of an error
        
        Args:
            context: The error context
            
        Returns:
            Human-readable explanation
        """
        explanations = {
            ErrorType.PACKAGE_NOT_FOUND: f"""
❌ Package Not Found

The package '{context.package or 'you requested'}' couldn't be found in the NixOS repositories.

This usually happens when:
• The package name is misspelled
• The package is in a different channel
• The package doesn't exist in NixOS yet

Try:
• Searching for similar names: nix search {context.package or 'packagename'}
• Checking the NixOS package search: https://search.nixos.org
""",
            ErrorType.PERMISSION_DENIED: """
❌ Permission Denied

This operation requires administrator privileges.

Try:
• Running the command with sudo
• Checking if you're in the right user group
""",
            ErrorType.NETWORK_ERROR: """
❌ Network Connection Problem

Unable to connect to the NixOS package servers.

This could mean:
• Your internet connection is down
• The NixOS servers are temporarily unavailable
• A firewall is blocking the connection

Try:
• Checking your internet connection
• Waiting a few minutes and trying again
• Using cached packages if available
""",
            ErrorType.DISK_SPACE: """
❌ Not Enough Disk Space

Your system has run out of disk space.

The Nix store can grow quite large over time with old packages.

Try:
• Running: nix-collect-garbage -d
• Removing old system generations
• Checking disk usage with: df -h
""",
            ErrorType.BROKEN_PACKAGE: """
❌ Broken Package Detected

A package or its dependencies appear to be corrupted.

Try:
• Repairing the Nix store: nix-store --verify --repair
• Rebuilding your system configuration
• Rolling back to a previous generation
""",
            ErrorType.TIMEOUT: """
⏱️ Operation Timed Out

The operation took too long to complete.

This often happens with:
• Large package searches
• Slow network connections
• Overloaded servers

Try:
• Using cached results
• Being more specific in your search
• Trying again during off-peak hours
""",
        }
        
        return explanations.get(
            context.error_type,
            f"❌ An error occurred:\n\n{context.original_error}\n\nI'm not sure how to fix this specific error."
        )
    
    def attempt_recovery(
        self,
        context: ErrorContext,
        auto_fix: bool = False,
        verbose: bool = False
    ) -> Tuple[bool, str]:
        """
        Attempt to recover from an error
        
        Args:
            context: The error context
            auto_fix: Whether to automatically apply fixes
            verbose: Whether to show detailed output
            
        Returns:
            Tuple of (success, message)
        """
        strategies = self.get_recovery_strategies(context)
        
        if not strategies:
            return False, "No recovery strategies available for this error"
        
        # Sort strategies by success rate
        strategies.sort(key=lambda s: s.success_rate, reverse=True)
        
        if not auto_fix:
            # Just return the suggestions
            msg = "Suggested fixes:\n"
            for i, strategy in enumerate(strategies[:3], 1):
                msg += f"{i}. {strategy.description}\n"
                if verbose:
                    for cmd in strategy.commands:
                        msg += f"   Command: {cmd}\n"
            return True, msg
        
        # Try to auto-fix
        for strategy in strategies:
            if strategy.requires_sudo and not self._can_use_sudo():
                continue
            
            if verbose:
                print(f"Trying: {strategy.description}")
            
            success = True
            for cmd in strategy.commands:
                try:
                    result = subprocess.run(
                        cmd.split(),
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode != 0:
                        success = False
                        break
                except Exception:
                    success = False
                    break
            
            if success:
                return True, f"✅ Fixed using: {strategy.description}"
        
        return False, "Unable to automatically fix this error"
    
    def _extract_package_name(self, error_message: str, command: Optional[str]) -> Optional[str]:
        """Extract package name from error message or command"""
        # Try to extract from error message
        patterns = [
            r"attribute '([^']+)' not found",
            r"Package '([^']+)'",
            r"package '([^']+)'",
            r"nixos\.([^\s]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                return match.group(1)
        
        # Try to extract from command
        if command:
            parts = command.split()
            for i, part in enumerate(parts):
                if part in ['-iA', '--install']:
                    if i + 1 < len(parts):
                        pkg = parts[i + 1]
                        # Remove nixos. prefix if present
                        if pkg.startswith('nixos.'):
                            pkg = pkg[6:]
                        return pkg
        
        return None
    
    def _customize_command(self, command: str, context: ErrorContext) -> str:
        """Customize a command template with actual values"""
        result = command
        
        if context.package:
            result = result.replace('{package}', context.package)
        
        if context.command:
            result = result.replace('{original_command}', context.command)
        
        return result
    
    def _can_use_sudo(self) -> bool:
        """Check if we can use sudo"""
        try:
            result = subprocess.run(
                ['sudo', '-n', 'true'],
                capture_output=True,
                timeout=1
            )
            return result.returncode == 0
        except:
            return False