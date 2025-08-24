#!/usr/bin/env python3
"""
🥋 The Dojo of Errors - Transform Mistakes into Wisdom
Every error is a teacher, every confusion a doorway to understanding
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ErrorCategory(Enum):
    """Categories of errors for targeted teaching"""
    PACKAGE_NOT_FOUND = "package_not_found"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    SYNTAX_ERROR = "syntax_error"
    CONFIGURATION_ERROR = "configuration_error"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    DISK_SPACE = "disk_space"
    UNKNOWN = "unknown"


@dataclass
class ErrorTeaching:
    """A teaching derived from an error"""
    category: ErrorCategory
    explanation: str
    suggestion: str
    command_example: Optional[str] = None
    learn_more: Optional[str] = None


class ErrorDojo:
    """
    The Dojo where errors become teachers
    Transforms technical errors into learning opportunities
    """
    
    def __init__(self):
        # Pattern matching for error categorization
        self.error_patterns = {
            ErrorCategory.PACKAGE_NOT_FOUND: [
                r"attribute.*not found",
                r"package.*not found",
                r"undefined variable",
                r"cannot find.*package"
            ],
            ErrorCategory.PERMISSION_DENIED: [
                r"permission denied",
                r"operation not permitted",
                r"access denied",
                r"requires root",
                r"sudo.*required"
            ],
            ErrorCategory.NETWORK_ERROR: [
                r"network.*error",
                r"connection.*refused",
                r"timeout",
                r"could not download",
                r"fetch.*failed"
            ],
            ErrorCategory.SYNTAX_ERROR: [
                r"syntax error",
                r"unexpected.*token",
                r"parse error",
                r"invalid.*expression"
            ],
            ErrorCategory.CONFIGURATION_ERROR: [
                r"configuration.*error",
                r"invalid.*configuration",
                r"option.*not recognized",
                r"conflicting.*definitions"
            ],
            ErrorCategory.DEPENDENCY_CONFLICT: [
                r"collision between",
                r"dependency.*conflict",
                r"version.*mismatch",
                r"incompatible.*versions"
            ],
            ErrorCategory.DISK_SPACE: [
                r"no space left",
                r"disk.*full",
                r"insufficient.*space",
                r"out of.*space"
            ]
        }
        
        # Wisdom teachings for each category
        self.teachings = {
            ErrorCategory.PACKAGE_NOT_FOUND: self._teach_package_not_found,
            ErrorCategory.PERMISSION_DENIED: self._teach_permission_denied,
            ErrorCategory.NETWORK_ERROR: self._teach_network_error,
            ErrorCategory.SYNTAX_ERROR: self._teach_syntax_error,
            ErrorCategory.CONFIGURATION_ERROR: self._teach_configuration_error,
            ErrorCategory.DEPENDENCY_CONFLICT: self._teach_dependency_conflict,
            ErrorCategory.DISK_SPACE: self._teach_disk_space,
            ErrorCategory.UNKNOWN: self._teach_unknown
        }
    
    def transform_error(self, error: str, context: Optional[Dict[str, Any]] = None) -> ErrorTeaching:
        """
        Transform an error into a teaching moment
        The core transformation of the Dojo
        """
        # Categorize the error
        category = self._categorize_error(error)
        
        # Get the appropriate teaching
        teaching_func = self.teachings.get(category, self._teach_unknown)
        
        # Generate the teaching
        return teaching_func(error, context or {})
    
    def _categorize_error(self, error: str) -> ErrorCategory:
        """Categorize error based on patterns"""
        error_lower = error.lower()
        
        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_lower):
                    return category
        
        return ErrorCategory.UNKNOWN
    
    def _teach_package_not_found(self, error: str, context: Dict[str, Any]) -> ErrorTeaching:
        """Teaching for package not found errors"""
        # Extract package name if possible - try multiple patterns
        patterns = [
            r"attribute\s+([^\s]+)\s+not found",  # Without quotes
            r"attribute\s+'([^']+)'\s+not found",  # With quotes
            r"'([^']+)' not found",
            r"package '([^']+)'",
            r"undefined variable '([^']+)'"
        ]
        
        package = None
        for pattern in patterns:
            match = re.search(pattern, error, re.IGNORECASE)
            if match:
                package = match.group(1)
                break
        
        if not package:
            package = "the package"
        
        return ErrorTeaching(
            category=ErrorCategory.PACKAGE_NOT_FOUND,
            explanation=f"The package '{package}' doesn't exist or the name is incorrect.",
            suggestion="Let's find the right package name together",
            command_example=f"ask-nix 'search {package}'",
            learn_more="Package names in NixOS are case-sensitive and must match exactly"
        )
    
    def _teach_permission_denied(self, error: str, context: Dict[str, Any]) -> ErrorTeaching:
        """Teaching for permission errors"""
        return ErrorTeaching(
            category=ErrorCategory.PERMISSION_DENIED,
            explanation="This operation requires elevated privileges to modify system state.",
            suggestion="Some operations need admin rights for safety",
            command_example="sudo ask-nix 'your command'",
            learn_more="NixOS protects your system by requiring permission for system changes"
        )
    
    def _teach_network_error(self, error: str, context: Dict[str, Any]) -> ErrorTeaching:
        """Teaching for network errors"""
        return ErrorTeaching(
            category=ErrorCategory.NETWORK_ERROR,
            explanation="Unable to connect to the package repository.",
            suggestion="Check your internet connection and try again",
            command_example="ping cache.nixos.org",
            learn_more="NixOS downloads packages from online repositories when installing"
        )
    
    def _teach_syntax_error(self, error: str, context: Dict[str, Any]) -> ErrorTeaching:
        """Teaching for syntax errors"""
        return ErrorTeaching(
            category=ErrorCategory.SYNTAX_ERROR,
            explanation="The configuration has a formatting issue.",
            suggestion="Check for missing semicolons, brackets, or quotes",
            command_example="nixos-rebuild test",
            learn_more="Nix uses a functional language syntax - every statement needs proper termination"
        )
    
    def _teach_configuration_error(self, error: str, context: Dict[str, Any]) -> ErrorTeaching:
        """Teaching for configuration errors"""
        return ErrorTeaching(
            category=ErrorCategory.CONFIGURATION_ERROR,
            explanation="The system configuration has an issue.",
            suggestion="Review your configuration.nix for conflicts",
            command_example="sudo nixos-rebuild test",
            learn_more="Testing configurations before applying helps catch issues early"
        )
    
    def _teach_dependency_conflict(self, error: str, context: Dict[str, Any]) -> ErrorTeaching:
        """Teaching for dependency conflicts"""
        return ErrorTeaching(
            category=ErrorCategory.DEPENDENCY_CONFLICT,
            explanation="Two packages want different versions of the same dependency.",
            suggestion="Try installing packages separately or in a shell",
            command_example="nix-shell -p package1 package2",
            learn_more="NixOS prevents conflicts by isolating dependencies"
        )
    
    def _teach_disk_space(self, error: str, context: Dict[str, Any]) -> ErrorTeaching:
        """Teaching for disk space errors"""
        return ErrorTeaching(
            category=ErrorCategory.DISK_SPACE,
            explanation="Your system is running low on disk space.",
            suggestion="Clean up old generations and garbage collect",
            command_example="sudo nix-collect-garbage -d",
            learn_more="NixOS keeps old versions for rollback - cleaning frees space"
        )
    
    def _teach_unknown(self, error: str, context: Dict[str, Any]) -> ErrorTeaching:
        """Teaching for unknown errors"""
        # Try to be helpful even with unknown errors
        error_snippet = error[:100] if len(error) > 100 else error
        
        return ErrorTeaching(
            category=ErrorCategory.UNKNOWN,
            explanation="An unexpected situation occurred.",
            suggestion="Let's try a different approach",
            command_example="ask-nix 'help'",
            learn_more=f"Error details: {error_snippet}..."
        )
    
    def format_teaching(self, teaching: ErrorTeaching, user_level: str = "beginner") -> str:
        """
        Format teaching for display based on user level
        Adapts explanation depth to user expertise
        """
        if user_level == "beginner":
            # Simple, encouraging format
            output = f"💭 {teaching.explanation}\n\n"
            output += f"💡 {teaching.suggestion}\n"
            
            if teaching.command_example:
                output += f"\nTry this: `{teaching.command_example}`"
        
        elif user_level == "intermediate":
            # More detail, still friendly
            output = f"🔍 What happened: {teaching.explanation}\n\n"
            output += f"🛠️ Solution: {teaching.suggestion}\n"
            
            if teaching.command_example:
                output += f"\n📝 Example: `{teaching.command_example}`"
            
            if teaching.learn_more:
                output += f"\n\n📚 Good to know: {teaching.learn_more}"
        
        else:  # expert
            # Concise, technical
            output = f"[{teaching.category.value}] {teaching.explanation}\n"
            
            if teaching.command_example:
                output += f"→ {teaching.command_example}\n"
            
            if teaching.learn_more:
                output += f"Note: {teaching.learn_more}"
        
        return output
    
    def get_contextual_help(self, error: str, recent_commands: List[str]) -> str:
        """
        Provide help based on error and recent command history
        Context-aware assistance
        """
        teaching = self.transform_error(error)
        
        # Check if user has been trying similar things
        if len(recent_commands) > 2:
            # User might be stuck
            help_text = "I notice you've been working on this for a bit. "
            help_text += "Would you like me to suggest a different approach?\n\n"
        else:
            help_text = ""
        
        # Add the teaching
        help_text += self.format_teaching(teaching, "beginner")
        
        # Add encouragement
        if teaching.category != ErrorCategory.UNKNOWN:
            help_text += "\n\n🌟 You're learning! Every error brings us closer to understanding."
        
        return help_text


# Global Dojo instance
_DOJO: Optional[ErrorDojo] = None

def get_error_dojo() -> ErrorDojo:
    """Get or create the Error Dojo"""
    global _DOJO
    if _DOJO is None:
        _DOJO = ErrorDojo()
    return _DOJO


if __name__ == "__main__":
    # Test the Dojo
    dojo = get_error_dojo()
    
    test_errors = [
        "error: attribute 'firefox' not found",
        "error: permission denied",
        "error: could not download https://cache.nixos.org/...",
        "error: syntax error, unexpected '}'",
        "error: collision between packages",
        "error: no space left on device"
    ]
    
    print("🥋 Testing the Dojo of Errors\n")
    print("=" * 60)
    
    for error in test_errors:
        print(f"\nOriginal error: {error}")
        print("-" * 40)
        teaching = dojo.transform_error(error)
        print(dojo.format_teaching(teaching, "beginner"))
        print("=" * 60)