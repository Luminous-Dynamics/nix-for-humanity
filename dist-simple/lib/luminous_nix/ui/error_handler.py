"""
from typing import List, Dict, Optional, Tuple
🚨 Enhanced Error Handling for TUI

Provides comprehensive error handling with:
- User-friendly error messages
- Context-aware suggestions
- Recovery options
- Educational opportunities
- Error tracking and reporting
"""

import logging
import traceback
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""

    INFO = "info"  # Informational, not really an error
    WARNING = "warning"  # Warning but operation continues
    ERROR = "error"  # Error but recoverable
    CRITICAL = "critical"  # Critical error, may need restart


class ErrorCategory(Enum):
    """Error categories for better handling"""

    NETWORK = "network"
    PERMISSION = "permission"
    PACKAGE = "package"
    CONFIGURATION = "configuration"
    SYNTAX = "syntax"
    DEPENDENCY = "dependency"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context about where and when error occurred"""

    timestamp: datetime
    component: str
    operation: str
    user_input: str | None = None
    system_state: dict[str, Any] | None = None


@dataclass
class ErrorSolution:
    """A potential solution to an error"""

    description: str
    command: str | None = None
    confidence: float = 0.8
    requires_sudo: bool = False
    estimated_time: str | None = None


@dataclass
class EnhancedError:
    """Enhanced error with all context and solutions"""

    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    technical_details: str | None = None
    context: ErrorContext | None = None
    solutions: list[ErrorSolution] = None
    learn_more_url: str | None = None
    error_code: str | None = None


class TUIErrorHandler:
    """Enhanced error handler for the TUI"""

    def __init__(self, log_dir: Path | None = None):
        self.log_dir = log_dir or Path.home() / ".local/share/nix-humanity/errors"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.error_history: list[EnhancedError] = []
        self.error_patterns = self._init_error_patterns()

    def _init_error_patterns(
        self,
    ) -> dict[str, tuple[ErrorCategory, list[ErrorSolution]]]:
        """Initialize common error patterns with solutions"""
        return {
            # Network errors
            "connection refused": (
                ErrorCategory.NETWORK,
                [
                    ErrorSolution(
                        "Check if the service is running",
                        "systemctl status nix-daemon",
                        confidence=0.9,
                    ),
                    ErrorSolution(
                        "Restart the Nix daemon",
                        "sudo systemctl restart nix-daemon",
                        requires_sudo=True,
                        confidence=0.8,
                    ),
                ],
            ),
            "network is unreachable": (
                ErrorCategory.NETWORK,
                [
                    ErrorSolution(
                        "Check your internet connection",
                        "ping -c 3 google.com",
                        confidence=0.9,
                    ),
                    ErrorSolution(
                        "Check network configuration", "ip addr show", confidence=0.7
                    ),
                ],
            ),
            # Permission errors
            "permission denied": (
                ErrorCategory.PERMISSION,
                [
                    ErrorSolution(
                        "Try with sudo",
                        None,  # Command will be modified
                        requires_sudo=True,
                        confidence=0.9,
                    ),
                    ErrorSolution("Check file permissions", "ls -la", confidence=0.7),
                ],
            ),
            "operation not permitted": (
                ErrorCategory.PERMISSION,
                [
                    ErrorSolution(
                        "This operation requires root privileges",
                        None,
                        requires_sudo=True,
                        confidence=0.9,
                    )
                ],
            ),
            # Package errors
            "package.*not found": (
                ErrorCategory.PACKAGE,
                [
                    ErrorSolution(
                        "Search for similar packages",
                        "ask-nix search {package}",
                        confidence=0.9,
                    ),
                    ErrorSolution(
                        "Update package database",
                        "sudo nix-channel --update",
                        requires_sudo=True,
                        confidence=0.7,
                        estimated_time="2-5 minutes",
                    ),
                ],
            ),
            "collision between": (
                ErrorCategory.PACKAGE,
                [
                    ErrorSolution(
                        "Remove one of the conflicting packages",
                        "ask-nix remove {package}",
                        confidence=0.8,
                    ),
                    ErrorSolution(
                        "Use priority to resolve conflict",
                        "ask-nix install {package} --priority 10",
                        confidence=0.9,
                    ),
                ],
            ),
            # Configuration errors
            "syntax error": (
                ErrorCategory.SYNTAX,
                [
                    ErrorSolution(
                        "Check configuration syntax",
                        "ask-nix config validate",
                        confidence=0.9,
                    ),
                    ErrorSolution(
                        "View the problematic line",
                        None,  # Will be filled with specific line
                        confidence=0.8,
                    ),
                ],
            ),
            "undefined variable": (
                ErrorCategory.CONFIGURATION,
                [
                    ErrorSolution(
                        "Check if the variable is imported", None, confidence=0.8
                    ),
                    ErrorSolution(
                        "Look for typos in variable name", None, confidence=0.7
                    ),
                ],
            ),
            # Dependency errors
            "dependency.*failed": (
                ErrorCategory.DEPENDENCY,
                [
                    ErrorSolution(
                        "Check dependency status", "ask-nix check-deps", confidence=0.8
                    ),
                    ErrorSolution(
                        "Try building dependencies first",
                        "ask-nix build-deps",
                        confidence=0.7,
                        estimated_time="5-10 minutes",
                    ),
                ],
            ),
        }

    def handle_error(
        self,
        error: Exception,
        component: str,
        operation: str,
        user_input: str | None = None,
    ) -> EnhancedError:
        """Handle an error and return enhanced error information"""

        # Create error context
        context = ErrorContext(
            timestamp=datetime.now(),
            component=component,
            operation=operation,
            user_input=user_input,
        )

        # Analyze error
        error_str = str(error).lower()
        error_type = type(error).__name__

        # Determine category and solutions
        category = ErrorCategory.UNKNOWN
        solutions = []

        # Check against patterns
        for pattern, (cat, sols) in self.error_patterns.items():
            if pattern in error_str:
                category = cat
                solutions = sols.copy()
                # Customize solutions based on context
                if user_input:
                    for sol in solutions:
                        if sol.command and "{package}" in sol.command:
                            # Extract package name from user input
                            parts = user_input.split()
                            if len(parts) > 1:
                                sol.command = sol.command.replace(
                                    "{package}", parts[-1]
                                )
                break

        # Determine severity
        severity = self._determine_severity(error, category)

        # Create user-friendly message
        user_message = self._create_user_message(error, category, error_type)

        # Get technical details
        technical_details = self._get_technical_details(error)

        # Create enhanced error
        enhanced_error = EnhancedError(
            severity=severity,
            category=category,
            message=user_message,
            technical_details=technical_details,
            context=context,
            solutions=solutions,
            learn_more_url=self._get_learn_more_url(category),
            error_code=f"{category.value.upper()}-{hash(str(error)) % 10000:04d}",
        )

        # Log error
        self._log_error(enhanced_error)

        # Add to history
        self.error_history.append(enhanced_error)

        return enhanced_error

    def _determine_severity(
        self, error: Exception, category: ErrorCategory
    ) -> ErrorSeverity:
        """Determine error severity"""
        # Critical errors
        if isinstance(error, (SystemExit, KeyboardInterrupt)):
            return ErrorSeverity.CRITICAL

        # Category-based severity
        if category in [ErrorCategory.SYSTEM, ErrorCategory.PERMISSION]:
            return ErrorSeverity.ERROR
        if category in [ErrorCategory.NETWORK, ErrorCategory.DEPENDENCY]:
            return ErrorSeverity.WARNING
        return ErrorSeverity.INFO

    def _create_user_message(
        self, error: Exception, category: ErrorCategory, error_type: str
    ) -> str:
        """Create user-friendly error message"""
        messages = {
            ErrorCategory.NETWORK: "I'm having trouble connecting to the network",
            ErrorCategory.PERMISSION: "I don't have permission to do that",
            ErrorCategory.PACKAGE: "There's an issue with the package",
            ErrorCategory.CONFIGURATION: "There's a problem with the configuration",
            ErrorCategory.SYNTAX: "I found a syntax error",
            ErrorCategory.DEPENDENCY: "Some dependencies are missing or broken",
            ErrorCategory.SYSTEM: "A system error occurred",
            ErrorCategory.UNKNOWN: f"An unexpected error occurred ({error_type})",
        }

        base_message = messages.get(category, "An error occurred")

        # Add specific context
        error_str = str(error)
        if len(error_str) < 100:
            return f"{base_message}: {error_str}"
        return base_message

    def _get_technical_details(self, error: Exception) -> str:
        """Get technical details for advanced users"""
        return traceback.format_exc()

    def _get_learn_more_url(self, category: ErrorCategory) -> str | None:
        """Get documentation URL for error category"""
        base_url = "https://nix-for-humanity.org/docs/errors"
        urls = {
            ErrorCategory.NETWORK: f"{base_url}/network",
            ErrorCategory.PERMISSION: f"{base_url}/permissions",
            ErrorCategory.PACKAGE: f"{base_url}/packages",
            ErrorCategory.CONFIGURATION: f"{base_url}/configuration",
            ErrorCategory.SYNTAX: f"{base_url}/syntax",
            ErrorCategory.DEPENDENCY: f"{base_url}/dependencies",
            ErrorCategory.SYSTEM: f"{base_url}/system",
        }
        return urls.get(category)

    def _log_error(self, error: EnhancedError) -> None:
        """Log error to file"""
        try:
            # Create daily log file
            log_file = (
                self.log_dir / f"errors_{datetime.now().strftime('%Y-%m-%d')}.log"
            )

            with open(log_file, "a") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Timestamp: {error.context.timestamp}\n")
                f.write(f"Error Code: {error.error_code}\n")
                f.write(f"Component: {error.context.component}\n")
                f.write(f"Operation: {error.context.operation}\n")
                f.write(f"User Input: {error.context.user_input}\n")
                f.write(f"Message: {error.message}\n")
                f.write(f"Category: {error.category.value}\n")
                f.write(f"Severity: {error.severity.value}\n")
                if error.technical_details:
                    f.write(f"\nTechnical Details:\n{error.technical_details}\n")

        except Exception as e:
            logger.error(f"Failed to log error: {e}")

    def format_error_for_display(
        self, error: EnhancedError, verbose: bool = False
    ) -> str:
        """Format error for display in TUI"""
        lines = []

        # Severity indicator
        severity_icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨",
        }

        icon = severity_icons.get(error.severity, "❓")

        # Main message
        lines.append(f"{icon} {error.message}")

        # Error code (for support)
        if error.error_code:
            lines.append(f"   Error Code: {error.error_code}")

        # Solutions
        if error.solutions:
            lines.append("\n💡 Suggested Solutions:")
            for i, solution in enumerate(error.solutions, 1):
                lines.append(f"   {i}. {solution.description}")
                if solution.command:
                    prefix = "sudo " if solution.requires_sudo else ""
                    lines.append(f"      → {prefix}{solution.command}")
                if solution.estimated_time:
                    lines.append(f"      ⏱️  Estimated time: {solution.estimated_time}")

        # Learn more
        if error.learn_more_url:
            lines.append(f"\n📚 Learn more: {error.learn_more_url}")

        # Technical details (verbose mode)
        if verbose and error.technical_details:
            lines.append("\n🔧 Technical Details:")
            lines.append(error.technical_details)

        return "\n".join(lines)

    def get_error_summary(self) -> str:
        """Get summary of recent errors"""
        if not self.error_history:
            return "No errors recorded in this session."

        # Count by category
        category_counts = {}
        for error in self.error_history:
            category_counts[error.category.value] = (
                category_counts.get(error.category.value, 0) + 1
            )

        lines = [f"📊 Error Summary ({len(self.error_history)} total):"]
        for category, count in sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"   • {category}: {count}")

        # Most recent errors
        lines.append("\n🕐 Recent Errors:")
        for error in self.error_history[-5:]:
            time_str = error.context.timestamp.strftime("%H:%M:%S")
            lines.append(f"   [{time_str}] {error.message[:50]}...")

        return "\n".join(lines)

    def clear_history(self) -> None:
        """Clear error history"""
        self.error_history.clear()

    def export_error_report(self) -> Path:
        """Export detailed error report"""
        report_file = (
            self.log_dir
            / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        with open(report_file, "w") as f:
            f.write("Nix for Humanity - Error Report\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("=" * 60 + "\n\n")

            for error in self.error_history:
                f.write(self.format_error_for_display(error, verbose=True))
                f.write("\n" + "-" * 60 + "\n\n")

        return report_file
