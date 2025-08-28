"""
from typing import Dict, List, Optional
Error Intelligence for Nix for Humanity
Deep error analysis and helpful recovery suggestions
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ErrorType(Enum):
    """Types of errors we understand"""
    HASH_MISMATCH = "hash_mismatch"
    MISSING_PACKAGE = "missing_package"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    DISK_SPACE = "disk_space"
    RECURSION = "recursion"
    BUILD_FAILURE = "build_failure"
    CHANNEL_ERROR = "channel_error"
    SYNTAX_ERROR = "syntax_error"
    UNKNOWN = "unknown"

@dataclass
class ErrorPattern:
    """Pattern for matching and understanding errors"""
    pattern: str
    error_type: ErrorType
    explanation: str
    solutions: List[str]
    learn_more: Optional[str] = None

@dataclass
class ErrorAnalysis:
    """Complete analysis of an error"""
    error_type: ErrorType
    explanation: str
    solutions: List[str]
    confidence: float
    extracted_info: Dict[str, str]
    auto_fixable: bool = False
    fix_command: Optional[str] = None

class ErrorIntelligence:
    """Analyzes NixOS errors and provides intelligent solutions"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> List[ErrorPattern]:
        """Initialize our error understanding database"""
        return [
            # Hash mismatches
            ErrorPattern(
                pattern=r"hash mismatch in fixed-output derivation.*expected:?\s*(\S+).*got:?\s*(\S+)",
                error_type=ErrorType.HASH_MISMATCH,
                explanation="The package source has changed since it was last verified. This often happens when upstream updates their files.",
                solutions=[
                    "Update your channels to get the latest hash: sudo nix-channel --update",
                    "If you trust the source, use --impure flag temporarily",
                    "Report the issue to the package maintainer",
                    "Try using the package from nixpkgs-unstable channel"
                ],
                learn_more="https://nixos.wiki/wiki/FAQ#Why_do_I_get_hash_mismatch"
            ),
            
            # Missing packages
            ErrorPattern(
                pattern=r"attribute '([^']+)' (?:missing|not found)",
                error_type=ErrorType.MISSING_PACKAGE,
                explanation="The package '{package}' wasn't found in your current channels.",
                solutions=[
                    "Search for the correct name: nix search nixpkgs {package}",
                    "Check if it's in unstable: nix search nixpkgs-unstable {package}",
                    "The package might have been renamed - try variations",
                    "Add the channel containing this package"
                ]
            ),
            
            # Permission errors
            ErrorPattern(
                pattern=r"(?:permission denied|insufficient permissions|operation not permitted)",
                error_type=ErrorType.PERMISSION_DENIED,
                explanation="You don't have permission for this operation.",
                solutions=[
                    "Try with sudo if it's a system operation",
                    "Check file ownership: ls -la",
                    "For user packages, don't use sudo",
                    "Ensure you're in the right groups (wheel for sudo)"
                ]
            ),
            
            # Network errors
            ErrorPattern(
                pattern=r"(?:unable to download|curl.*failed|network.*unreachable|connection.*refused)",
                error_type=ErrorType.NETWORK_ERROR,
                explanation="Can't download required files due to network issues.",
                solutions=[
                    "Check your internet connection",
                    "Try again - might be temporary",
                    "Check if you're behind a proxy",
                    "The server might be down - try later"
                ]
            ),
            
            # Disk space
            ErrorPattern(
                pattern=r"(?:no space left|disk.*full|out of space)",
                error_type=ErrorType.DISK_SPACE,
                explanation="You're running out of disk space.",
                solutions=[
                    "Free space with: sudo nix-collect-garbage -d",
                    "Check disk usage: df -h",
                    "Remove old generations: sudo nix-env --delete-generations old",
                    "Clean build directory: rm -rf /tmp/nix-build-*"
                ]
            ),
            
            # Infinite recursion
            ErrorPattern(
                pattern=r"infinite recursion encountered",
                error_type=ErrorType.RECURSION,
                explanation="Your configuration has a circular dependency.",
                solutions=[
                    "Check for recursive imports in configuration.nix",
                    "Look for self-referencing variables",
                    "Use lib.mkForce to override recursion",
                    "Simplify your configuration structure"
                ]
            ),
            
            # Build failures
            ErrorPattern(
                pattern=r"build.*failed|compilation.*error|make.*error",
                error_type=ErrorType.BUILD_FAILURE,
                explanation="The package failed to build from source.",
                solutions=[
                    "Check if a binary cache has it: nix profile install nixpkgs#{package}",
                    "Try an older/newer version",
                    "Check the build log for specific errors",
                    "Report the issue upstream"
                ]
            ),
            
            # Channel errors
            ErrorPattern(
                pattern=r"channel.*error|unable to update channel",
                error_type=ErrorType.CHANNEL_ERROR,
                explanation="Problem with your Nix channels.",
                solutions=[
                    "List channels: sudo nix-channel --list",
                    "Re-add the channel: sudo nix-channel --add",
                    "Update with --refresh: sudo nix-channel --update",
                    "Check channel URL is correct"
                ]
            ),
            
            # Syntax errors
            ErrorPattern(
                pattern=r"syntax error|unexpected|expecting",
                error_type=ErrorType.SYNTAX_ERROR,
                explanation="There's a syntax error in your Nix expression.",
                solutions=[
                    "Check for missing semicolons (;)",
                    "Ensure all brackets/braces match",
                    "Look at the line number mentioned",
                    "Use 'nixfmt' to format your code"
                ]
            )
        ]
    
    def analyze_error(self, error_text: str) -> ErrorAnalysis:
        """Analyze an error and provide helpful solutions"""
        
        # Try each pattern
        for pattern in self.patterns:
            match = re.search(pattern.pattern, error_text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Extract information from the match
                extracted_info = {}
                if match.groups():
                    # For missing package, extract the package name
                    if pattern.error_type == ErrorType.MISSING_PACKAGE:
                        extracted_info['package'] = match.group(1)
                    # For hash mismatch, extract both hashes
                    elif pattern.error_type == ErrorType.HASH_MISMATCH:
                        if len(match.groups()) >= 2:
                            extracted_info['expected'] = match.group(1)
                            extracted_info['got'] = match.group(2)
                
                # Customize solutions based on extracted info
                solutions = []
                for solution in pattern.solutions:
                    # Replace placeholders
                    for key, value in extracted_info.items():
                        solution = solution.replace(f"{{{key}}}", value)
                    solutions.append(solution)
                
                # Customize explanation
                explanation = pattern.explanation
                for key, value in extracted_info.items():
                    explanation = explanation.replace(f"{{{key}}}", value)
                
                # Check if auto-fixable
                auto_fixable = False
                fix_command = None
                
                if pattern.error_type == ErrorType.CHANNEL_ERROR:
                    auto_fixable = True
                    fix_command = "sudo nix-channel --update"
                elif pattern.error_type == ErrorType.DISK_SPACE:
                    auto_fixable = True
                    fix_command = "sudo nix-collect-garbage -d"
                
                return ErrorAnalysis(
                    error_type=pattern.error_type,
                    explanation=explanation,
                    solutions=solutions,
                    confidence=0.9,
                    extracted_info=extracted_info,
                    auto_fixable=auto_fixable,
                    fix_command=fix_command
                )
        
        # No pattern matched - provide generic help
        return ErrorAnalysis(
            error_type=ErrorType.UNKNOWN,
            explanation="I couldn't identify the specific error, but here's general help.",
            solutions=[
                "Check the full error message for clues",
                "Try searching online for the error text",
                "Ask in NixOS forums or chat",
                "Try simpler operations to isolate the issue"
            ],
            confidence=0.3,
            extracted_info={}
        )
    
    def format_analysis(self, analysis: ErrorAnalysis) -> str:
        """Format error analysis for display"""
        output = []
        
        # Error type badge
        emoji_map = {
            ErrorType.HASH_MISMATCH: "🔐",
            ErrorType.MISSING_PACKAGE: "📦",
            ErrorType.PERMISSION_DENIED: "🚫",
            ErrorType.NETWORK_ERROR: "🌐",
            ErrorType.DISK_SPACE: "💾",
            ErrorType.RECURSION: "🔄",
            ErrorType.BUILD_FAILURE: "🔨",
            ErrorType.CHANNEL_ERROR: "📡",
            ErrorType.SYNTAX_ERROR: "📝",
            ErrorType.UNKNOWN: "❓"
        }
        
        emoji = emoji_map.get(analysis.error_type, "❌")
        output.append(f"{emoji} **Error Type**: {analysis.error_type.value.replace('_', ' ').title()}")
        output.append("")
        
        # Explanation
        output.append(f"**What happened**: {analysis.explanation}")
        output.append("")
        
        # Solutions
        output.append("**How to fix it**:")
        for i, solution in enumerate(analysis.solutions, 1):
            output.append(f"{i}. {solution}")
        output.append("")
        
        # Auto-fix option
        if analysis.auto_fixable and analysis.fix_command:
            output.append(f"🔧 **Quick fix available**: `{analysis.fix_command}`")
            output.append("")
        
        # Confidence
        if analysis.confidence < 0.5:
            output.append("⚠️ *Note: This is a best guess. The actual issue might be different.*")
        
        return "\n".join(output)
    
    def suggest_prevention(self, error_type: ErrorType) -> List[str]:
        """Suggest how to prevent this error in the future"""
        prevention_tips = {
            ErrorType.HASH_MISMATCH: [
                "Keep channels updated regularly",
                "Pin specific versions for reproducibility",
                "Use flakes for better dependency management"
            ],
            ErrorType.MISSING_PACKAGE: [
                "Search before installing: nix search",
                "Keep a list of your common packages",
                "Use shell.nix for project dependencies"
            ],
            ErrorType.DISK_SPACE: [
                "Run garbage collection weekly",
                "Set up automatic GC in configuration.nix",
                "Monitor disk usage regularly"
            ],
            ErrorType.PERMISSION_DENIED: [
                "Understand when sudo is needed",
                "Use home-manager for user packages",
                "Check file permissions before editing"
            ]
        }
        
        return prevention_tips.get(error_type, [
            "Read error messages carefully",
            "Keep your system updated",
            "Make small, incremental changes"
        ])