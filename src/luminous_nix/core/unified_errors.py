"""
Unified Error Intelligence System - Smart, educational, and friendly error handling.

This consolidates functionality from:
- error_handler.py
- error_intelligence.py
- error_intelligence_ast.py
- error_intelligence_unified.py
- error_recovery.py
- error_translator.py
- educational_errors.py
- friendly_errors.py
- graceful_degradation.py

Philosophy: Errors are teachers, not failures. Make them helpful, not scary.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ==================== Error Types ====================


class ErrorCategory(Enum):
    """Categories of errors for better handling."""

    PERMISSION = "permission"  # Permission denied
    NOT_FOUND = "not_found"  # Package/file not found
    NETWORK = "network"  # Network issues
    SYNTAX = "syntax"  # Command syntax errors
    CONFLICT = "conflict"  # Package conflicts
    SPACE = "space"  # Disk space issues
    TIMEOUT = "timeout"  # Operation timeouts
    CONFIG = "config"  # Configuration errors
    UNKNOWN = "unknown"  # Unknown errors


@dataclass
class ErrorIntelligence:
    """Intelligent error analysis result."""

    category: ErrorCategory
    original_error: str
    friendly_message: str
    educational_content: Optional[str] = None
    suggested_fix: Optional[str] = None
    recovery_action: Optional[str] = None
    learn_more_url: Optional[str] = None
    confidence: float = 1.0


# ==================== Error Patterns ====================


class ErrorPatternMatcher:
    """Match error messages to known patterns."""

    def __init__(self):
        """Initialize with error patterns."""
        self.patterns = [
            # Permission errors
            {
                "pattern": r"permission denied|access denied|operation not permitted",
                "category": ErrorCategory.PERMISSION,
                "friendly": "I don't have permission to do that",
                "educational": "This operation requires administrator privileges. NixOS protects system files for security.",
                "fix": "Try running with 'sudo' or check file permissions",
                "recovery": "retry_with_sudo",
            },
            # Not found errors
            {
                "pattern": r"not found|attribute.*not found|package.*not found|no such|missing",
                "category": ErrorCategory.NOT_FOUND,
                "friendly": "I couldn't find that package",
                "educational": "Package names in NixOS must match exactly. The package might have a different name or not be available.",
                "fix": "Try searching first: 'search {package}'",
                "recovery": "suggest_search",
            },
            # Network errors
            {
                "pattern": r"unable to download|connection refused|network unreachable|could not resolve",
                "category": ErrorCategory.NETWORK,
                "friendly": "I'm having trouble connecting to the internet",
                "educational": "NixOS needs to download packages from the internet. This could be a temporary network issue.",
                "fix": "Check your internet connection and try again",
                "recovery": "retry_later",
            },
            # Syntax errors
            {
                "pattern": r"syntax error|unexpected|invalid (?:option|argument)",
                "category": ErrorCategory.SYNTAX,
                "friendly": "There's something wrong with that command",
                "educational": "NixOS commands have specific syntax. Even small typos can cause errors.",
                "fix": "Check the command syntax and try again",
                "recovery": "show_help",
            },
            # Conflict errors
            {
                "pattern": r"collision between|conflicting|already installed",
                "category": ErrorCategory.CONFLICT,
                "friendly": "There's a conflict with another package",
                "educational": "Some packages can't be installed together because they provide the same files.",
                "fix": "You might need to remove the conflicting package first",
                "recovery": "resolve_conflict",
            },
            # Space errors
            {
                "pattern": r"no space left|disk full|out of space",
                "category": ErrorCategory.SPACE,
                "friendly": "Your disk is running out of space",
                "educational": "NixOS keeps old versions for rollback, which uses disk space.",
                "fix": "Run 'nix-collect-garbage -d' to free up space",
                "recovery": "free_space",
            },
            # Timeout errors
            {
                "pattern": r"timed? ?out|timeout expired|took too long",
                "category": ErrorCategory.TIMEOUT,
                "friendly": "This is taking longer than expected",
                "educational": "Some operations, especially downloads, can take a while on slower connections.",
                "fix": "Try again with a longer timeout or better connection",
                "recovery": "retry_with_timeout",
            },
            # Configuration errors
            {
                "pattern": r"configuration\.nix|undefined variable|infinite recursion",
                "category": ErrorCategory.CONFIG,
                "friendly": "There's an issue with your configuration",
                "educational": "NixOS configuration files must be valid Nix expressions.",
                "fix": "Check your configuration.nix for errors",
                "recovery": "validate_config",
            },
        ]

    def match(self, error_text: str) -> Optional[dict[str, Any]]:
        """Match error text to a pattern."""
        error_lower = error_text.lower()

        for pattern_info in self.patterns:
            if re.search(pattern_info["pattern"], error_lower):
                return pattern_info

        return None


# ==================== Error Intelligence Engine ====================


class ErrorIntelligenceEngine:
    """Main error intelligence engine."""

    def __init__(self, educational_mode: bool = True, friendly_mode: bool = True):
        """Initialize the engine.

        Args:
            educational_mode: Include educational content
            friendly_mode: Use friendly messages
        """
        self.educational_mode = educational_mode
        self.friendly_mode = friendly_mode
        self.matcher = ErrorPatternMatcher()
        self.recovery_strategies = self._init_recovery_strategies()

    def _init_recovery_strategies(self) -> dict[str, Any]:
        """Initialize recovery strategies."""
        return {
            "retry_with_sudo": lambda: "Would you like me to try with administrator privileges?",
            "suggest_search": lambda pkg: f"Let me search for similar packages to '{pkg}'",
            "retry_later": lambda: "I'll try again in a moment",
            "show_help": lambda: "Here's the correct usage for this command",
            "resolve_conflict": lambda: "I can help resolve this conflict",
            "free_space": lambda: "I can help free up some disk space",
            "retry_with_timeout": lambda: "I'll try again with a longer timeout",
            "validate_config": lambda: "Let me check your configuration for errors",
        }

    def analyze(
        self, error_text: str, context: Optional[dict] = None
    ) -> ErrorIntelligence:
        """Analyze an error and provide intelligence.

        Args:
            error_text: The raw error text
            context: Optional context about the error

        Returns:
            ErrorIntelligence with analysis results
        """
        # Try to match known patterns
        match = self.matcher.match(error_text)

        if match:
            # Extract package name if present
            package = None
            if context and "package" in context:
                package = context["package"]

            # Build intelligence
            intelligence = ErrorIntelligence(
                category=match["category"],
                original_error=error_text,
                friendly_message=self._make_friendly(match["friendly"], package),
                educational_content=match.get("educational")
                if self.educational_mode
                else None,
                suggested_fix=self._personalize_fix(match.get("fix"), package),
                recovery_action=match.get("recovery"),
                confidence=0.9,
            )
        else:
            # Unknown error - provide generic help
            intelligence = ErrorIntelligence(
                category=ErrorCategory.UNKNOWN,
                original_error=error_text,
                friendly_message=self._make_generic_friendly(error_text),
                educational_content="This error isn't in my knowledge base yet, but I'll do my best to help."
                if self.educational_mode
                else None,
                suggested_fix="Try checking the command syntax or searching for the error message online",
                confidence=0.5,
            )

        # Add learn more URLs based on category
        intelligence.learn_more_url = self._get_learn_more_url(intelligence.category)

        return intelligence

    def _make_friendly(self, template: str, package: Optional[str] = None) -> str:
        """Make a friendly error message."""
        if not self.friendly_mode:
            return template

        # Add empathy and personality
        friendly_prefixes = [
            "Oh no! ",
            "Hmm, ",
            "It looks like ",
            "I see that ",
        ]

        import random

        message = random.choice(friendly_prefixes) + template.lower()

        if package:
            message = message.replace("{package}", f"'{package}'")

        return message

    def _make_generic_friendly(self, error: str) -> str:
        """Make a generic friendly message."""
        if not self.friendly_mode:
            return "An error occurred"

        if len(error) > 100:
            return "Something went wrong with that operation. Let me help you figure it out."
        else:
            return "I encountered an issue: " + error[:100]

    def _personalize_fix(self, fix_template: str, package: Optional[str] = None) -> str:
        """Personalize fix suggestion."""
        if not fix_template:
            return None

        if package:
            return fix_template.replace("{package}", package)

        return fix_template

    def _get_learn_more_url(self, category: ErrorCategory) -> Optional[str]:
        """Get documentation URL for error category."""
        urls = {
            ErrorCategory.PERMISSION: "https://nixos.org/manual/nix/stable/installation/multi-user.html",
            ErrorCategory.NOT_FOUND: "https://search.nixos.org/packages",
            ErrorCategory.NETWORK: "https://nixos.org/manual/nix/stable/package-management/channels.html",
            ErrorCategory.CONFIG: "https://nixos.org/manual/nixos/stable/index.html#ch-configuration",
            ErrorCategory.CONFLICT: "https://nixos.org/guides/nix-pills/garbage-collector.html",
            ErrorCategory.SPACE: "https://nixos.org/manual/nix/stable/package-management/garbage-collection.html",
        }
        return urls.get(category)

    def format_for_display(self, intelligence: ErrorIntelligence) -> str:
        """Format error intelligence for display."""
        lines = []

        # Friendly message
        lines.append(f"❌ {intelligence.friendly_message}")

        # Educational content
        if intelligence.educational_content:
            lines.append("")
            lines.append(f"ℹ️  {intelligence.educational_content}")

        # Suggested fix
        if intelligence.suggested_fix:
            lines.append("")
            lines.append(f"💡 {intelligence.suggested_fix}")

        # Learn more
        if intelligence.learn_more_url:
            lines.append("")
            lines.append(f"📚 Learn more: {intelligence.learn_more_url}")

        return "\n".join(lines)


# ==================== Error Recovery ====================


class ErrorRecovery:
    """Automatic error recovery strategies."""

    def __init__(self, backend=None):
        """Initialize with optional backend for recovery actions."""
        self.backend = backend

    def attempt_recovery(
        self, intelligence: ErrorIntelligence
    ) -> tuple[bool, Optional[str]]:
        """Attempt to recover from an error.

        Args:
            intelligence: The error intelligence

        Returns:
            (success, result_message)
        """
        if not intelligence.recovery_action:
            return False, None

        recovery_map = {
            "retry_with_sudo": self._retry_with_sudo,
            "suggest_search": self._suggest_search,
            "retry_later": self._retry_later,
            "show_help": self._show_help,
            "resolve_conflict": self._resolve_conflict,
            "free_space": self._free_space,
            "retry_with_timeout": self._retry_with_timeout,
            "validate_config": self._validate_config,
        }

        recovery_func = recovery_map.get(intelligence.recovery_action)
        if recovery_func:
            return recovery_func(intelligence)

        return False, None

    def _retry_with_sudo(self, intelligence: ErrorIntelligence) -> tuple[bool, str]:
        """Suggest retrying with sudo."""
        return True, "Try running the command with 'sudo' for administrator privileges"

    def _suggest_search(self, intelligence: ErrorIntelligence) -> tuple[bool, str]:
        """Suggest searching for the package."""
        return True, "Try searching for the package first: 'search <package-name>'"

    def _retry_later(self, intelligence: ErrorIntelligence) -> tuple[bool, str]:
        """Suggest retrying later."""
        return True, "This might be a temporary issue. Try again in a few minutes"

    def _show_help(self, intelligence: ErrorIntelligence) -> tuple[bool, str]:
        """Show command help."""
        return True, "Use 'help' to see the correct command syntax"

    def _resolve_conflict(self, intelligence: ErrorIntelligence) -> tuple[bool, str]:
        """Suggest conflict resolution."""
        return True, "Remove the conflicting package first, then try again"

    def _free_space(self, intelligence: ErrorIntelligence) -> tuple[bool, str]:
        """Suggest freeing disk space."""
        return True, "Run 'nix-collect-garbage -d' to free up disk space"

    def _retry_with_timeout(self, intelligence: ErrorIntelligence) -> tuple[bool, str]:
        """Suggest longer timeout."""
        return True, "Try again with a longer timeout or better network connection"

    def _validate_config(self, intelligence: ErrorIntelligence) -> tuple[bool, str]:
        """Suggest config validation."""
        return True, "Run 'nixos-rebuild test' to validate your configuration"


# ==================== Convenience Functions ====================


def analyze_error(
    error_text: str,
    context: Optional[dict] = None,
    educational: bool = True,
    friendly: bool = True,
) -> ErrorIntelligence:
    """Convenience function to analyze an error."""
    engine = ErrorIntelligenceEngine(
        educational_mode=educational, friendly_mode=friendly
    )
    return engine.analyze(error_text, context)


def format_error(error_text: str, context: Optional[dict] = None) -> str:
    """Format an error for user display."""
    engine = ErrorIntelligenceEngine()
    intelligence = engine.analyze(error_text, context)
    return engine.format_for_display(intelligence)


def attempt_recovery(error_text: str, backend=None) -> tuple[bool, Optional[str]]:
    """Attempt to recover from an error."""
    engine = ErrorIntelligenceEngine()
    intelligence = engine.analyze(error_text)
    recovery = ErrorRecovery(backend)
    return recovery.attempt_recovery(intelligence)
