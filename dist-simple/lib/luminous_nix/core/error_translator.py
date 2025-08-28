#!/usr/bin/env python3
"""
from typing import Dict, List
NixOS Error Translation & Resolution Engine

Transforms cryptic Nix errors into compassionate, helpful guidance.
Every error becomes a learning opportunity.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from difflib import get_close_matches

@dataclass
class TranslatedError:
    """A human-friendly error explanation"""
    original_error: str
    simple_explanation: str
    detailed_explanation: str
    suggested_fixes: List[str]
    related_commands: List[str]
    learn_more_topics: List[str]
    confidence: float
    
    def format_for_persona(self, persona: str = "friendly") -> str:
        """Format the error for different personas"""
        if persona == "minimal":
            return f"{self.simple_explanation}\nFix: {self.suggested_fixes[0] if self.suggested_fixes else 'No automatic fix available'}"
        
        elif persona == "friendly":
            output = f"💡 {self.simple_explanation}\n\n"
            if self.suggested_fixes:
                output += "Here's how to fix it:\n"
                for i, fix in enumerate(self.suggested_fixes, 1):
                    output += f"  {i}. {fix}\n"
            return output
        
        elif persona == "encouraging":
            output = f"No worries! {self.simple_explanation}\n\n"
            output += "You're doing great! "
            if self.suggested_fixes:
                output += "Here's what you can try:\n"
                for fix in self.suggested_fixes:
                    output += f"  ✨ {fix}\n"
            return output
        
        elif persona == "technical":
            output = f"Error Analysis:\n"
            output += f"  Type: {self._detect_error_type()}\n"
            output += f"  Issue: {self.simple_explanation}\n"
            output += f"  Details: {self.detailed_explanation}\n"
            if self.suggested_fixes:
                output += f"  Fixes:\n"
                for fix in self.suggested_fixes:
                    output += f"    - {fix}\n"
            return output
        
        else:
            return self.simple_explanation
    
    def _detect_error_type(self) -> str:
        """Detect the type of error"""
        if "attribute" in self.original_error and "missing" in self.original_error:
            return "AttributeError"
        elif "collision" in self.original_error:
            return "PackageCollision"
        elif "undefined variable" in self.original_error:
            return "UndefinedVariable"
        elif "syntax error" in self.original_error:
            return "SyntaxError"
        else:
            return "GeneralError"


class ErrorTranslator:
    """Translates NixOS errors into helpful guidance"""
    
    def __init__(self):
        self.error_patterns = self._build_error_patterns()
        self.package_database = self._load_package_database()
        self.common_fixes = self._load_common_fixes()
        
    def _build_error_patterns(self) -> List[Dict[str, Any]]:
        """Build database of error patterns and translations"""
        return [
            # Attribute/Package Missing Errors
            {
                "pattern": r"attribute '([^']+)' missing",
                "type": "missing_attribute",
                "handler": self._handle_missing_attribute
            },
            {
                "pattern": r"Package '([^']+)' not found",
                "type": "package_not_found",
                "handler": self._handle_missing_attribute  # Same handler for both
            },
            
            # Syntax Errors
            {
                "pattern": r"syntax error, unexpected ([^,]+)",
                "type": "syntax_error",
                "handler": self._handle_syntax_error
            },
            {
                "pattern": r"error: undefined variable '([^']+)'",
                "type": "undefined_variable",
                "handler": self._handle_undefined_variable
            },
            
            # Collision Errors
            {
                "pattern": r"collision between .* and .*",
                "type": "package_collision",
                "handler": self._handle_collision
            },
            
            # Build Errors
            {
                "pattern": r"builder for '([^']+)' failed",
                "type": "build_failure",
                "handler": self._handle_build_failure
            },
            
            # Permission Errors
            {
                "pattern": r"error: opening .* Permission denied",
                "type": "permission_denied",
                "handler": self._handle_permission_error
            },
            
            # Disk Space
            {
                "pattern": r"No space left on device",
                "type": "disk_full",
                "handler": self._handle_disk_full
            },
            
            # Network Errors
            {
                "pattern": r"error: unable to download.*SSL.*",
                "type": "ssl_error",
                "handler": self._handle_ssl_error
            },
            {
                "pattern": r"error: unable to download.*network",
                "type": "network_error",
                "handler": self._handle_network_error
            },
            
            # Flake Errors
            {
                "pattern": r"error: flake .* does not exist",
                "type": "flake_not_found",
                "handler": self._handle_flake_not_found
            },
            
            # Module Errors
            {
                "pattern": r"The option .* does not exist",
                "type": "option_not_exist",
                "handler": self._handle_option_not_exist
            },
            
            # Type Errors
            {
                "pattern": r"value is .* while .* was expected",
                "type": "type_mismatch",
                "handler": self._handle_type_mismatch
            }
        ]
    
    def _load_package_database(self) -> Dict[str, List[str]]:
        """Load common package name mappings"""
        return {
            # Node.js versions
            "nodejs_16": ["nodejs_18", "nodejs_20", "nodejs"],
            "nodejs_18": ["nodejs_20", "nodejs"],
            "nodejs-16_x": ["nodejs_18", "nodejs_20", "nodejs"],
            
            # Python versions
            "python38": ["python39", "python310", "python311", "python3"],
            "python39": ["python310", "python311", "python3"],
            
            # Common renames/transitions
            "chromium-dev": ["chromium", "google-chrome"],
            "vscode": ["vscode", "vscodium", "code"],
            "ffmpeg-full": ["ffmpeg", "ffmpeg_6", "ffmpeg_5"],
            
            # Development tools
            "cargo": ["rustc", "rust"],
            "go": ["go_1_21", "go_1_20"],
            "gcc": ["gcc13", "gcc12", "gcc11"],
            
            # Services
            "postgresql": ["postgresql_15", "postgresql_14", "postgresql_13"],
            "mysql": ["mysql80", "mariadb"],
            
            # Common typos
            "firefox": ["firefox-esr", "firefox-bin"],
            "neovim": ["vim", "neovim-unwrapped"],
            "nodejs": ["nodejs_20", "nodejs_18"],
        }
    
    def _load_common_fixes(self) -> Dict[str, List[str]]:
        """Load database of common fixes"""
        return {
            "missing_attribute": [
                "Check if the package name is correct (case-sensitive)",
                "Search for the package: nix search nixpkgs#<package>",
                "Update your channel: sudo nix-channel --update",
                "Check available versions: nix search nixpkgs#<package> --json"
            ],
            "permission_denied": [
                "Run the command with sudo if system-wide changes are needed",
                "Check file ownership: ls -la <file>",
                "For user packages, use: nix profile install instead of system-wide",
                "Ensure you're in the correct directory"
            ],
            "disk_full": [
                "Free up space: nix-collect-garbage -d",
                "Remove old generations: nix-env --delete-generations old",
                "Check disk usage: df -h",
                "Clean build artifacts: nix-store --gc"
            ],
            "network_error": [
                "Check your internet connection",
                "Try again - it might be a temporary issue",
                "Check if you're behind a proxy",
                "Try a different Nix channel mirror"
            ]
        }
    
    def translate_error(self, error_text: str) -> TranslatedError:
        """Translate a Nix error into helpful guidance"""
        # Try each pattern
        for pattern_info in self.error_patterns:
            match = re.search(pattern_info["pattern"], error_text, re.IGNORECASE | re.MULTILINE)
            if match:
                return pattern_info["handler"](error_text, match)
        
        # If no pattern matches, provide generic help
        return self._handle_unknown_error(error_text)
    
    def _handle_missing_attribute(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle missing attribute/package errors"""
        package_name = match.group(1)
        
        # Check for common renames
        suggestions = []
        if package_name in self.package_database:
            suggestions = self.package_database[package_name]
        else:
            # Try fuzzy matching
            all_packages = list(self.package_database.keys())
            close_matches = get_close_matches(package_name, all_packages, n=3, cutoff=0.6)
            if close_matches:
                for match in close_matches:
                    suggestions.extend(self.package_database.get(match, [match]))
        
        simple = f"Package '{package_name}' not found in NixOS packages."
        
        detailed = f"The package '{package_name}' doesn't exist in the current NixOS channel. "
        detailed += "This could mean:\n"
        detailed += "1. The package name is misspelled\n"
        detailed += "2. The package was renamed or removed\n"
        detailed += "3. You need to update your channel\n"
        detailed += "4. The package is in a different namespace"
        
        fixes = []
        if suggestions:
            fixes.append(f"Try one of these alternatives: {', '.join(suggestions[:3])}")
        
        fixes.extend([
            f"Search for similar packages: ask-nix 'search {package_name}'",
            f"Update your channels: sudo nix-channel --update",
            f"Check the exact name: nix search nixpkgs#{package_name}"
        ])
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["search", "install"],
            learn_more_topics=["packages", "channels", "search"],
            confidence=0.9 if suggestions else 0.7
        )
    
    def _handle_syntax_error(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle Nix syntax errors"""
        unexpected = match.group(1)
        
        simple = f"Syntax error: unexpected '{unexpected}' in your configuration."
        
        detailed = "Nix has specific syntax rules. Common issues:\n"
        detailed += "• Missing semicolon at end of line\n"
        detailed += "• Unclosed brackets or quotes\n"
        detailed += "• Wrong bracket type (use {} for sets, [] for lists)\n"
        detailed += "• Missing comma between list items"
        
        fixes = [
            "Check for missing semicolons (;) at the end of assignments",
            "Ensure all brackets and quotes are properly closed",
            "Verify you're using the right brackets: {} for attribute sets, [] for lists",
            "Look at the line mentioned in the error for issues"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["validate", "check"],
            learn_more_topics=["nix-syntax", "configuration"],
            confidence=0.8
        )
    
    def _handle_collision(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle package collision errors"""
        simple = "Two packages are trying to install the same file."
        
        detailed = "Package collisions happen when multiple packages provide the same file. "
        detailed += "NixOS prevents this to maintain system consistency. "
        detailed += "You need to choose which package to keep or use override priorities."
        
        fixes = [
            "Choose one package and remove the other",
            "Use lib.hiPrio or lib.lowPrio to set priorities",
            "For development environments, use nix-shell instead",
            "Consider using overlays to resolve conflicts"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["remove", "override"],
            learn_more_topics=["collisions", "priorities", "overlays"],
            confidence=0.85
        )
    
    def _handle_disk_full(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle disk full errors"""
        simple = "Your disk is full - Nix needs space to build packages."
        
        detailed = "NixOS keeps old versions for rollback, which uses disk space. "
        detailed += "You can safely remove old generations and garbage collect."
        
        fixes = [
            "Free space now: sudo nix-collect-garbage -d",
            "Delete old generations: ask-nix 'clean old generations keep 5'",
            "Check disk usage: df -h",
            "Remove specific store paths: nix-store --delete <path>"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["clean", "garbage-collect"],
            learn_more_topics=["disk-management", "garbage-collection"],
            confidence=0.95
        )
    
    def _handle_undefined_variable(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle undefined variable errors"""
        variable = match.group(1)
        
        simple = f"Variable '{variable}' is not defined in your configuration."
        
        detailed = f"The variable '{variable}' is being used but hasn't been defined. "
        detailed += "This usually means:\n"
        detailed += "• Missing 'with pkgs;' statement\n"
        detailed += "• Typo in variable name\n"
        detailed += "• Missing import statement\n"
        detailed += "• Variable defined in wrong scope"
        
        fixes = [
            f"If '{variable}' is a package, add 'with pkgs;' at the top of the list",
            f"Check spelling - Nix is case-sensitive",
            f"Define the variable: let {variable} = ...; in ...",
            f"Import missing module that defines '{variable}'"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["validate", "check"],
            learn_more_topics=["variables", "scope", "imports"],
            confidence=0.85
        )
    
    def _handle_permission_error(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle permission denied errors"""
        simple = "Permission denied - you need elevated privileges for this operation."
        
        detailed = "This operation requires administrator access. "
        detailed += "System-wide changes need sudo, while user packages don't."
        
        fixes = self.common_fixes["permission_denied"]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["sudo", "user-install"],
            learn_more_topics=["permissions", "user-vs-system"],
            confidence=0.9
        )
    
    def _handle_network_error(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle network-related errors"""
        simple = "Network error - couldn't download required files."
        
        detailed = "NixOS needs to download packages from the internet. "
        detailed += "This error usually means connection issues or server problems."
        
        fixes = self.common_fixes["network_error"]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["retry", "check-network"],
            learn_more_topics=["networking", "channels"],
            confidence=0.8
        )
    
    def _handle_unknown_error(self, error_text: str) -> TranslatedError:
        """Handle unknown errors with generic help"""
        simple = "An error occurred that I don't recognize yet."
        
        detailed = "This error pattern isn't in my database yet. "
        detailed += "However, here are some general troubleshooting steps."
        
        fixes = [
            "Check the full error message for clues",
            "Try validating your configuration: nixos-rebuild test",
            "Search online for the specific error message",
            "Ask for help with: ask-nix 'explain error' and paste the error"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["help", "validate"],
            learn_more_topics=["debugging", "troubleshooting"],
            confidence=0.3
        )
    
    def _handle_ssl_error(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle SSL certificate errors"""
        simple = "SSL certificate error - secure connection failed."
        
        detailed = "The secure connection to download packages failed. "
        detailed += "This might be due to proxy settings, firewall, or certificate issues."
        
        fixes = [
            "Check your system time is correct",
            "If behind a proxy, configure Nix to use it",
            "Try: export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt",
            "Update ca-certificates package"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["check-network"],
            learn_more_topics=["ssl", "certificates", "proxy"],
            confidence=0.75
        )
    
    def _handle_flake_not_found(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle flake not found errors"""
        simple = "Flake not found - the flake.nix file or reference doesn't exist."
        
        detailed = "Nix couldn't find the flake you're trying to use. "
        detailed += "Make sure the path is correct and the flake.nix file exists."
        
        fixes = [
            "Check if flake.nix exists in the current directory",
            "For remote flakes, ensure the URL is correct",
            "Initialize a flake: ask-nix 'create flake'",
            "Verify the flake reference syntax"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["flake", "create"],
            learn_more_topics=["flakes", "flake-reference"],
            confidence=0.85
        )
    
    def _handle_option_not_exist(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle non-existent option errors"""
        # Extract option name from error
        option_match = re.search(r"The option `([^`]+)`", error_text)
        option = option_match.group(1) if option_match else "unknown"
        
        simple = f"Configuration option '{option}' doesn't exist."
        
        detailed = f"The option '{option}' is not a valid NixOS configuration option. "
        detailed += "This could be due to:\n"
        detailed += "• Typo in the option name\n"
        detailed += "• Missing module import\n"
        detailed += "• Option was removed or renamed"
        
        fixes = [
            f"Check spelling: options are case-sensitive",
            f"Search for similar options: nixos-option '{option.split('.')[0]}'",
            "Ensure required modules are imported",
            "Check NixOS manual for correct option names"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["options", "search-options"],
            learn_more_topics=["options", "modules"],
            confidence=0.8
        )
    
    def _handle_type_mismatch(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle type mismatch errors"""
        simple = "Type mismatch - the value has the wrong type for this option."
        
        detailed = "Nix is strongly typed. Each option expects a specific type of value. "
        detailed += "Common type issues:\n"
        detailed += "• String vs boolean: 'true' vs true\n"
        detailed += "• List vs single value: ['pkg'] vs 'pkg'\n"
        detailed += "• Number vs string: 80 vs '80'"
        
        fixes = [
            "Check the expected type in the option documentation",
            "Remove quotes from booleans and numbers",
            "Use [ ] for lists, even with one item",
            "Use '' for strings, not for other types"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["validate", "check-type"],
            learn_more_topics=["types", "nix-types"],
            confidence=0.85
        )
    
    def _handle_build_failure(self, error_text: str, match: re.Match) -> TranslatedError:
        """Handle package build failures"""
        package = match.group(1) if match.groups() else "unknown"
        
        simple = f"Package '{package}' failed to build."
        
        detailed = "Build failures can happen for various reasons:\n"
        detailed += "• Missing dependencies\n"
        detailed += "• Compilation errors\n"
        detailed += "• Test failures\n"
        detailed += "• Network issues during fetch"
        
        fixes = [
            "Try again - it might be a temporary issue",
            "Check if the package is broken: nix-env -qa --json | grep broken",
            "Use an older version if available",
            "Report the issue if it persists"
        ]
        
        return TranslatedError(
            original_error=error_text,
            simple_explanation=simple,
            detailed_explanation=detailed,
            suggested_fixes=fixes,
            related_commands=["retry", "check-broken"],
            learn_more_topics=["building", "debugging-builds"],
            confidence=0.7
        )


def demonstrate_error_translation():
    """Demonstrate the error translator with common errors"""
    translator = ErrorTranslator()
    
    # Test errors
    test_errors = [
        "error: attribute 'nodejs_18' missing, at /etc/nixos/configuration.nix:42:15",
        "error: collision between `/nix/store/abc-firefox-1.0/bin/firefox' and `/nix/store/def-firefox-2.0/bin/firefox'",
        "error: undefined variable 'vscode' at /home/user/config.nix:10:5",
        "error: No space left on device",
        "error: syntax error, unexpected '}', expecting ';'",
        "error: The option `services.httpd.enable' does not exist",
        "error: value is a string while a Boolean was expected",
    ]
    
    print("🔍 NixOS Error Translation Demo")
    print("=" * 60)
    
    for error in test_errors:
        print(f"\n❌ Original Error:")
        print(f"   {error}")
        
        translated = translator.translate_error(error)
        
        print(f"\n✨ Translation (friendly persona):")
        print(translated.format_for_persona("friendly"))
        print("-" * 40)


if __name__ == "__main__":
    demonstrate_error_translation()