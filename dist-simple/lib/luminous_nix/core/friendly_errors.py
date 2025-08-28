#!/usr/bin/env python3
"""
😊 Friendly Error Messages - Making Errors Educational, Not Frustrating
Transforms cryptic errors into helpful guidance.
"""

import re
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors we handle"""
    TIMEOUT = "timeout"
    MODEL_NOT_FOUND = "model_not_found"
    OLLAMA_NOT_RUNNING = "ollama_not_running"
    SYNTAX_ERROR = "syntax_error"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    PACKAGE_NOT_FOUND = "package_not_found"
    CONFIGURATION_ERROR = "configuration_error"
    BUILD_FAILED = "build_failed"
    UNKNOWN = "unknown"


@dataclass
class FriendlyError:
    """A user-friendly error message"""
    type: ErrorType
    title: str
    explanation: str
    suggestions: List[str]
    commands: Optional[List[str]] = None
    learn_more: Optional[str] = None


class FriendlyErrorHandler:
    """
    Transforms technical errors into friendly, educational messages.
    """
    
    def __init__(self):
        """Initialize error handler with patterns"""
        self.error_patterns = {
            ErrorType.TIMEOUT: [
                r"timeout|timed out|took too long|exceeded.*time",
                r"TimeoutExpired|TimeoutError"
            ],
            ErrorType.MODEL_NOT_FOUND: [
                r"model.*not found|no such model|unknown model",
                r"pull.*model.*first"
            ],
            ErrorType.OLLAMA_NOT_RUNNING: [
                r"connection refused.*11434|ollama.*not running",
                r"failed to connect to ollama"
            ],
            ErrorType.SYNTAX_ERROR: [
                r"syntax error|unexpected.*token|parse error",
                r"error:.*at.*line.*column"
            ],
            ErrorType.PERMISSION_DENIED: [
                r"permission denied|access denied|operation not permitted",
                r"sudo.*required|must be root"
            ],
            ErrorType.NETWORK_ERROR: [
                r"network.*error|connection.*failed|could not resolve",
                r"unable to download|fetch.*failed"
            ],
            ErrorType.PACKAGE_NOT_FOUND: [
                r"package.*not found|attribute.*missing",
                r"undefined variable.*pkgs"
            ],
            ErrorType.CONFIGURATION_ERROR: [
                r"configuration.*error|config.*invalid",
                r"option.*does not exist|cannot coerce"
            ],
            ErrorType.BUILD_FAILED: [
                r"build.*failed|builder.*failed|derivation.*failed",
                r"error:.*while evaluating"
            ]
        }
        
        # Friendly messages for each error type
        self.error_messages = {
            ErrorType.TIMEOUT: FriendlyError(
                type=ErrorType.TIMEOUT,
                title="⏱️ This is taking longer than expected",
                explanation="The AI model is taking too long to respond. This usually happens with large models or complex queries.",
                suggestions=[
                    "Try a simpler question",
                    "Install a faster model for quicker responses",
                    "Check if your system is under heavy load"
                ],
                commands=[
                    "ask-nix 'install qwen:0.5b'  # Ultra-fast model",
                    "ask-nix 'install tinyllama'  # Fast and capable"
                ],
                learn_more="Large models like llama3:13b can take 30+ seconds. Smaller models respond in 1-5 seconds."
            ),
            
            ErrorType.MODEL_NOT_FOUND: FriendlyError(
                type=ErrorType.MODEL_NOT_FOUND,
                title="🤖 AI Model Not Found",
                explanation="The requested AI model isn't installed on your system yet.",
                suggestions=[
                    "Download the model first",
                    "Check available models",
                    "Use a different model"
                ],
                commands=[
                    "ollama list                # See installed models",
                    "ollama pull gemma:2b       # Download a fast model",
                    "ask-nix setup              # Run setup wizard"
                ],
                learn_more="Models need to be downloaded once (300MB-4GB). After that, they work offline."
            ),
            
            ErrorType.OLLAMA_NOT_RUNNING: FriendlyError(
                type=ErrorType.OLLAMA_NOT_RUNNING,
                title="🔌 AI Service Not Running",
                explanation="The Ollama AI service needs to be running for AI features to work.",
                suggestions=[
                    "Start the Ollama service",
                    "Check if Ollama is installed",
                    "Enable automatic startup"
                ],
                commands=[
                    "ollama serve               # Start Ollama",
                    "systemctl --user enable ollama  # Auto-start",
                    "ask-nix setup              # Install if needed"
                ],
                learn_more="Ollama runs AI models locally on your machine for privacy and offline use."
            ),
            
            ErrorType.SYNTAX_ERROR: FriendlyError(
                type=ErrorType.SYNTAX_ERROR,
                title="📝 Configuration Syntax Error",
                explanation="There's a syntax error in your NixOS configuration.",
                suggestions=[
                    "Check for missing semicolons",
                    "Verify bracket matching",
                    "Look for typos in attribute names"
                ],
                commands=[
                    "ask-nix fix                # Auto-diagnose issues",
                    "nixos-rebuild test         # Test without applying"
                ],
                learn_more="NixOS uses a functional language. Every statement needs a semicolon, and brackets must match."
            ),
            
            ErrorType.PERMISSION_DENIED: FriendlyError(
                type=ErrorType.PERMISSION_DENIED,
                title="🔒 Permission Required",
                explanation="This operation requires administrator privileges.",
                suggestions=[
                    "Run with sudo",
                    "Check file ownership",
                    "Verify you're in the right groups"
                ],
                commands=[
                    "sudo nixos-rebuild switch  # System changes need sudo",
                    "groups                     # Check your groups"
                ],
                learn_more="System-wide changes need sudo. User packages don't."
            ),
            
            ErrorType.NETWORK_ERROR: FriendlyError(
                type=ErrorType.NETWORK_ERROR,
                title="🌐 Network Connection Issue",
                explanation="Can't connect to download packages or models.",
                suggestions=[
                    "Check internet connection",
                    "Verify DNS settings",
                    "Check proxy configuration"
                ],
                commands=[
                    "ping 8.8.8.8              # Test connectivity",
                    "nslookup cache.nixos.org  # Test DNS"
                ],
                learn_more="NixOS downloads packages from cache.nixos.org. Models come from ollama.ai."
            ),
            
            ErrorType.PACKAGE_NOT_FOUND: FriendlyError(
                type=ErrorType.PACKAGE_NOT_FOUND,
                title="📦 Package Not Found",
                explanation="The package name might be different in NixOS.",
                suggestions=[
                    "Search for the correct name",
                    "Check if it's in nixpkgs",
                    "Try alternative packages"
                ],
                commands=[
                    "nix search firefox         # Find exact name",
                    "ask-nix 'search browser'   # Natural search"
                ],
                learn_more="NixOS packages sometimes have different names. 'google-chrome' is 'google-chrome-stable'."
            ),
            
            ErrorType.CONFIGURATION_ERROR: FriendlyError(
                type=ErrorType.CONFIGURATION_ERROR,
                title="⚙️ Configuration Issue",
                explanation="There's a problem with your NixOS configuration.",
                suggestions=[
                    "Check option names",
                    "Verify value types",
                    "Look for deprecated options"
                ],
                commands=[
                    "ask-nix fix                # Diagnose automatically",
                    "man configuration.nix      # See all options"
                ],
                learn_more="NixOS options are strongly typed. Booleans need 'true' not 'yes'."
            ),
            
            ErrorType.BUILD_FAILED: FriendlyError(
                type=ErrorType.BUILD_FAILED,
                title="🔨 Build Failed",
                explanation="NixOS couldn't build your configuration.",
                suggestions=[
                    "Check the error details",
                    "Try a simpler change first",
                    "Rollback if needed"
                ],
                commands=[
                    "nixos-rebuild test         # Test without applying",
                    "nixos-rebuild switch --rollback  # Revert"
                ],
                learn_more="NixOS keeps old configurations. You can always rollback if something breaks."
            )
        }
    
    def identify_error_type(self, error_message: str) -> ErrorType:
        """Identify the type of error from the message"""
        error_lower = error_message.lower()
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_lower, re.IGNORECASE):
                    return error_type
        
        return ErrorType.UNKNOWN
    
    def get_friendly_message(self, error: Exception) -> FriendlyError:
        """Convert an exception to a friendly error message"""
        error_str = str(error)
        error_type = self.identify_error_type(error_str)
        
        if error_type in self.error_messages:
            return self.error_messages[error_type]
        
        # Default unknown error
        return FriendlyError(
            type=ErrorType.UNKNOWN,
            title="❓ Unexpected Issue",
            explanation=f"Something unexpected happened: {error_str[:100]}",
            suggestions=[
                "Try the command again",
                "Check the full error message",
                "Ask for help with the error"
            ],
            commands=[
                "ask-nix help               # Get help",
                "ask-nix fix                # Try auto-diagnosis"
            ]
        )
    
    def extract_line_number(self, error_message: str) -> Optional[Tuple[str, int]]:
        """Extract file and line number from error message"""
        # Pattern: file.nix:123:45
        match = re.search(r'([^:]+\.nix):(\d+):(\d+)', error_message)
        if match:
            return match.group(1), int(match.group(2))
        
        # Pattern: at line 123
        match = re.search(r'at line (\d+)', error_message)
        if match:
            return 'configuration.nix', int(match.group(1))
        
        return None
    
    def format_for_terminal(self, friendly_error: FriendlyError, 
                           use_color: bool = True) -> str:
        """Format error for terminal display"""
        if use_color:
            # Use ANSI color codes
            RESET = "\033[0m"
            BOLD = "\033[1m"
            RED = "\033[91m"
            YELLOW = "\033[93m"
            CYAN = "\033[96m"
            GREEN = "\033[92m"
            DIM = "\033[2m"
        else:
            RESET = BOLD = RED = YELLOW = CYAN = GREEN = DIM = ""
        
        output = []
        output.append(f"\n{RED}{BOLD}{friendly_error.title}{RESET}")
        output.append(f"{friendly_error.explanation}\n")
        
        if friendly_error.suggestions:
            output.append(f"{YELLOW}💡 Suggestions:{RESET}")
            for suggestion in friendly_error.suggestions:
                output.append(f"  • {suggestion}")
            output.append("")
        
        if friendly_error.commands:
            output.append(f"{GREEN}🔧 Try these commands:{RESET}")
            for command in friendly_error.commands:
                output.append(f"  {CYAN}{command}{RESET}")
            output.append("")
        
        if friendly_error.learn_more:
            output.append(f"{DIM}ℹ️  {friendly_error.learn_more}{RESET}")
        
        return "\n".join(output)
    
    def suggest_model_for_timeout(self, current_model: str = None) -> List[str]:
        """Suggest faster models when timeout occurs"""
        fast_models = [
            ("qwen:0.5b", "300MB", "< 2s"),
            ("tinyllama", "637MB", "< 3s"),
            ("gemma:2b", "1.4GB", "< 5s"),
            ("phi3:mini", "2.2GB", "< 5s")
        ]
        
        suggestions = []
        for model, size, speed in fast_models:
            if model != current_model:
                suggestions.append(f"ollama pull {model:12} # {size:>6}, {speed}")
        
        return suggestions
    
    def diagnose_configuration_file(self, file_path: str = "/etc/nixos/configuration.nix") -> List[str]:
        """Quick diagnosis of common configuration issues"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for common issues
            if content.count('{') != content.count('}'):
                issues.append("Mismatched brackets: {} count doesn't match")
            
            if content.count('[') != content.count(']'):
                issues.append("Mismatched square brackets: [] count doesn't match")
            
            if content.count('(') != content.count(')'):
                issues.append("Mismatched parentheses: () count doesn't match")
            
            # Check for missing semicolons
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.endswith(('=', '+', '-')) and not line.endswith(';'):
                        issues.append(f"Line {i}: Might be missing semicolon")
            
            # Check for common typos
            typos = {
                'enviroment': 'environment',
                'systenPackages': 'systemPackages',
                'configuraiton': 'configuration'
            }
            
            for typo, correct in typos.items():
                if typo in content:
                    issues.append(f"Typo found: '{typo}' should be '{correct}'")
            
        except Exception as e:
            issues.append(f"Could not read configuration: {e}")
        
        return issues


def test_friendly_errors():
    """Test the friendly error handler"""
    print("Testing Friendly Error Handler")
    print("="*50)
    
    handler = FriendlyErrorHandler()
    
    # Test different error types
    test_errors = [
        "TimeoutExpired: Command timed out after 30 seconds",
        "Error: model 'llama3:70b' not found, try pulling it first",
        "Connection refused: localhost:11434",
        "error: syntax error, unexpected ':', expecting ';' at line 42",
        "Permission denied: /etc/nixos/configuration.nix",
        "Network error: Could not resolve host cache.nixos.org",
        "error: attribute 'emacs' missing",
        "error: while evaluating the configuration",
        "Some random error message"
    ]
    
    for error_msg in test_errors:
        print(f"\nOriginal: {error_msg[:50]}...")
        error_type = handler.identify_error_type(error_msg)
        print(f"Type: {error_type.value}")
        
        # Create exception and get friendly message
        error = Exception(error_msg)
        friendly = handler.get_friendly_message(error)
        
        # Format and display
        formatted = handler.format_for_terminal(friendly)
        print(formatted)
        print("-"*50)


if __name__ == "__main__":
    test_friendly_errors()