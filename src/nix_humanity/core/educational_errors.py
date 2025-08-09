#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List, Optional
Educational Error Handling System

Makes errors helpful learning opportunities rather than frustrating dead ends.
Every error teaches the user something valuable about NixOS.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class ErrorCategory(Enum):
    """Categories of errors for targeted education"""
    PACKAGE_NOT_FOUND = "package_not_found"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    SYNTAX_ERROR = "syntax_error"
    DISK_SPACE = "disk_space"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    CHANNEL_ERROR = "channel_error"
    BUILD_ERROR = "build_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN = "unknown"


@dataclass
class EducationalError:
    """An error that teaches"""
    category: ErrorCategory
    user_message: str
    explanation: str
    learn_more: List[str]
    suggestions: List[str]
    example: Optional[str] = None
    prevention: Optional[str] = None


class EducationalErrorHandler:
    """Transform cryptic errors into learning opportunities"""
    
    def __init__(self):
        self.error_patterns = self._build_error_patterns()
        self.educational_content = self._build_educational_content()
    
    def _build_error_patterns(self) -> List[Tuple[re.Pattern, ErrorCategory]]:
        """Build patterns to recognize different error types"""
        return [
            # Package not found
            (re.compile(r"attribute.*not found|package.*not found", re.I), 
             ErrorCategory.PACKAGE_NOT_FOUND),
            
            # Permission denied
            (re.compile(r"permission denied|access denied|sudo.*required", re.I),
             ErrorCategory.PERMISSION_DENIED),
            
            # Network errors
            (re.compile(r"network.*unreachable|connection.*refused|timeout|no route", re.I),
             ErrorCategory.NETWORK_ERROR),
            
            # Disk space
            (re.compile(r"no space left|disk.*full|out of.*space", re.I),
             ErrorCategory.DISK_SPACE),
            
            # Dependency conflicts
            (re.compile(r"collision|conflict|incompatible|version mismatch", re.I),
             ErrorCategory.DEPENDENCY_CONFLICT),
            
            # Channel errors
            (re.compile(r"channel.*not found|update.*channel", re.I),
             ErrorCategory.CHANNEL_ERROR),
            
            # Build errors
            (re.compile(r"build.*failed|compilation.*error|make.*error", re.I),
             ErrorCategory.BUILD_ERROR),
            
            # Configuration errors
            (re.compile(r"configuration\.nix|syntax error|unexpected", re.I),
             ErrorCategory.CONFIGURATION_ERROR),
        ]
    
    def _build_educational_content(self) -> Dict[ErrorCategory, EducationalError]:
        """Build educational content for each error category"""
        return {
            ErrorCategory.PACKAGE_NOT_FOUND: EducationalError(
                category=ErrorCategory.PACKAGE_NOT_FOUND,
                user_message="I couldn't find that package in the current channels.",
                explanation="""In NixOS, packages come from 'channels' - think of them as app stores.
If a package isn't found, it might be:
1. Named differently in Nix (e.g., 'google-chrome' → 'chromium')
2. In a different channel (unstable vs stable)
3. Not packaged for NixOS yet""",
                learn_more=[
                    "NixOS uses its own package names which sometimes differ from other distros",
                    "You can search packages at search.nixos.org",
                    "Package names are case-sensitive in Nix"
                ],
                suggestions=[
                    "Try searching for a similar name: 'search <keyword>'",
                    "Check the exact package name at search.nixos.org",
                    "Update your channels: 'update channels'",
                    "Search with partial name: 'search chrome' instead of 'google-chrome'"
                ],
                example="For example: 'search browser' to find web browsers",
                prevention="Always search first before trying to install: 'search <keyword>'"
            ),
            
            ErrorCategory.PERMISSION_DENIED: EducationalError(
                category=ErrorCategory.PERMISSION_DENIED,
                user_message="This operation needs administrator privileges.",
                explanation="""NixOS has two types of operations:
1. User operations: Install packages for yourself (no sudo needed)
2. System operations: Change system configuration (needs sudo)

System-wide changes like 'nixos-rebuild' need sudo, but personal package
installations usually don't!""",
                learn_more=[
                    "User packages are installed to ~/.nix-profile/",
                    "System packages are in /run/current-system/",
                    "You can install most software without sudo using nix-env"
                ],
                suggestions=[
                    "For system changes, I'll show you the sudo command",
                    "For user packages, try: 'nix-env -iA nixos.<package>'",
                    "Consider using Home Manager for user configurations"
                ],
                example="Install for yourself: 'nix-env -iA nixos.firefox'\nInstall system-wide: Add to configuration.nix",
                prevention="Use user installations when possible to avoid permission issues"
            ),
            
            ErrorCategory.NETWORK_ERROR: EducationalError(
                category=ErrorCategory.NETWORK_ERROR,
                user_message="I'm having trouble connecting to the network.",
                explanation="""Network issues can prevent NixOS from downloading packages.
Common causes:
1. No internet connection
2. Firewall blocking connections
3. DNS resolution problems
4. Proxy configuration needed""",
                learn_more=[
                    "NixOS downloads packages from cache.nixos.org",
                    "Binary caches speed up installations",
                    "You can use local/offline installations too"
                ],
                suggestions=[
                    "Check your internet connection: 'ping google.com'",
                    "Check DNS: 'nslookup cache.nixos.org'",
                    "If behind proxy, set: 'export https_proxy=...'",
                    "Try again in a few minutes (temporary network issue)"
                ],
                example="Test connection: 'curl -I https://cache.nixos.org'",
                prevention="Ensure stable internet before large operations"
            ),
            
            ErrorCategory.DISK_SPACE: EducationalError(
                category=ErrorCategory.DISK_SPACE,
                user_message="Your disk is running out of space.",
                explanation="""NixOS keeps old versions of everything for rollbacks, which is
amazing for safety but can use disk space. The Nix store at /nix/store
contains all packages and their dependencies.""",
                learn_more=[
                    "Each package version is kept separately for reliability",
                    "Old generations can be safely cleaned up",
                    "Garbage collection removes unused packages"
                ],
                suggestions=[
                    "Free space now: 'sudo nix-collect-garbage -d'",
                    "See what's using space: 'du -sh /nix/store'",
                    "Remove old generations: 'sudo nix-collect-garbage --delete-older-than 7d'",
                    "Check disk usage: 'df -h'"
                ],
                example="Quick cleanup: 'sudo nix-collect-garbage -d' (deletes ALL old generations)",
                prevention="Run garbage collection weekly: 'sudo nix-collect-garbage --delete-older-than 7d'"
            ),
            
            ErrorCategory.DEPENDENCY_CONFLICT: EducationalError(
                category=ErrorCategory.DEPENDENCY_CONFLICT,
                user_message="There's a conflict between package dependencies.",
                explanation="""NixOS prevents 'dependency hell' by isolating packages, but sometimes
two packages want different versions of the same library in the same
environment. This is actually NixOS protecting you from broken software!""",
                learn_more=[
                    "Each package in Nix has its own dependencies",
                    "Conflicts only occur when building environments",
                    "You can have multiple versions installed separately"
                ],
                suggestions=[
                    "Install packages separately, not in same environment",
                    "Use nix-shell for isolated development environments",
                    "Check package compatibility at search.nixos.org",
                    "Consider using overlays to fix version conflicts"
                ],
                example="Instead of installing together, use separate profiles or nix-shell",
                prevention="Test package combinations in nix-shell before installing"
            ),
            
            ErrorCategory.CONFIGURATION_ERROR: EducationalError(
                category=ErrorCategory.CONFIGURATION_ERROR,
                user_message="There's an issue with the NixOS configuration.",
                explanation="""Your configuration.nix file has a syntax error or invalid option.
NixOS configurations are written in the Nix language, which is:
- Declarative (you describe what you want)
- Functional (no side effects)
- Strongly typed (catches errors early)""",
                learn_more=[
                    "Configuration errors are caught before system changes",
                    "You can always rollback to previous configuration",
                    "The Nix language has helpful error messages"
                ],
                suggestions=[
                    "Check syntax: 'sudo nixos-rebuild test'",
                    "Look for missing semicolons or brackets",
                    "Verify option names at search.nixos.org/options",
                    "Start with small changes and test each one"
                ],
                example="Test without applying: 'sudo nixos-rebuild test'",
                prevention="Always test configuration before switching: 'sudo nixos-rebuild test'"
            ),
            
            ErrorCategory.UNKNOWN: EducationalError(
                category=ErrorCategory.UNKNOWN,
                user_message="I encountered an unexpected error.",
                explanation="I'm not sure what went wrong, but here's how we can figure it out together.",
                learn_more=[
                    "NixOS has excellent error recovery - you can always rollback",
                    "Most errors are temporary or fixable",
                    "The community is very helpful with troubleshooting"
                ],
                suggestions=[
                    "Try the operation again (might be temporary)",
                    "Check the full error message for clues",
                    "Search the error message online",
                    "Ask the NixOS community for help"
                ],
                example="Share the full error at discourse.nixos.org for help",
                prevention="Keep your system updated and maintain backups"
            )
        }
    
    def transform_error(self, error_message: str) -> EducationalError:
        """Transform a raw error message into educational content"""
        # Identify error category
        category = ErrorCategory.UNKNOWN
        for pattern, cat in self.error_patterns:
            if pattern.search(error_message):
                category = cat
                break
        
        # Get educational content
        educational_error = self.educational_content.get(
            category,
            self.educational_content[ErrorCategory.UNKNOWN]
        )
        
        # Customize message if possible
        if "attribute" in error_message.lower() and "not found" in error_message.lower():
            # Extract package name if possible
            match = re.search(r"attribute ['\"]?(\w+)['\"]?", error_message)
            if match:
                package = match.group(1)
                educational_error.user_message = f"I couldn't find the package '{package}'."
                educational_error.suggestions.insert(
                    0, f"Try searching for '{package}': 'search {package}'"
                )
        
        return educational_error
    
    def format_for_cli(self, error: EducationalError, verbose: bool = False) -> str:
        """Format educational error for CLI output"""
        output = [
            f"❌ {error.user_message}",
            "",
            f"💡 What this means:",
            error.explanation,
            "",
            "✨ What you can do:",
        ]
        
        for i, suggestion in enumerate(error.suggestions, 1):
            output.append(f"  {i}. {suggestion}")
        
        if error.example:
            output.extend(["", "📝 Example:", f"  {error.example}"])
        
        if verbose and error.learn_more:
            output.extend(["", "📚 Learn more:"])
            for fact in error.learn_more:
                output.append(f"  • {fact}")
        
        if error.prevention:
            output.extend(["", "🛡️ Prevention tip:", f"  {error.prevention}"])
        
        return "\n".join(output)
    
    def format_for_tui(self, error: EducationalError) -> Dict[str, any]:
        """Format educational error for TUI display"""
        return {
            "title": error.user_message,
            "explanation": error.explanation,
            "suggestions": error.suggestions,
            "example": error.example,
            "learn_more": error.learn_more,
            "prevention": error.prevention,
            "category": error.category.value
        }


# Convenience function
def make_error_educational(error_message: str, verbose: bool = False) -> str:
    """Transform any error into an educational opportunity"""
    handler = EducationalErrorHandler()
    educational_error = handler.transform_error(error_message)
    return handler.format_for_cli(educational_error, verbose)


if __name__ == "__main__":
    # Test the educational error system
    test_errors = [
        "error: attribute 'firefox' in selection path 'nixos.firefox' not found",
        "error: permission denied",
        "error: no space left on device",
        "error: network unreachable",
        "error: collision between packages",
        "error: syntax error, unexpected $end, expecting ';'",
        "some random error message"
    ]
    
    handler = EducationalErrorHandler()
    
    for error in test_errors:
        print("=" * 60)
        print(f"Original: {error}")
        print("-" * 60)
        educational = handler.transform_error(error)
        print(handler.format_for_cli(educational, verbose=True))
        print()