"""Input validation and sanitization."""

# === Merged from migration ===

#!/usr/bin/env python3
"""
from typing import List, Dict, Optional, Tuple
Security Input Validator for Nix for Humanity
Provides comprehensive input validation and sanitization for all user inputs
"""

import logging
import os
import re
import shlex
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Comprehensive input validation for security

    Features:
    - Command injection prevention
    - Path traversal protection
    - Package name validation
    - NLP input sanitization
    - Educational error messages
    """

    # Dangerous patterns that should never appear in inputs
    DANGEROUS_PATTERNS = [
        # Command injection attempts
        r"[;&|]",  # Command chaining
        r"`.*`",  # Command substitution
        r"\$\(.*\)",  # Command substitution
        r"\${.*}",  # Variable expansion that could be dangerous
        # Path traversal
        r"\.\./",  # Parent directory access
        r"\.\.\\",  # Windows-style parent directory
        # Dangerous commands
        r"\brm\s+-rf\s+/",  # Recursive force remove from root
        r"\bdd\s+if=/dev/(zero|random)",  # Disk destroyer
        r"\bmkfs\.",  # Filesystem formatting
        r":\(\)\{\s*:\|:\&\s*\};:",  # Fork bomb
        # SQL injection (for future database features)
        r"';|--",  # SQL injection attempts
        r"union\s+select",  # SQL union attacks
        # Shell metacharacters in wrong context
        r"[<>]",  # Redirection when not expected
        r"\*\s*\*",  # Glob bombs
    ]

    # Valid package name pattern (alphanumeric, dash, underscore, dot)
    VALID_PACKAGE_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\-_.]*$")

    # Valid file path pattern
    VALID_PATH = re.compile(r"^[a-zA-Z0-9/\-_.]+$")

    # Maximum lengths to prevent DoS
    MAX_INPUT_LENGTH = 1000
    MAX_PACKAGE_NAME_LENGTH = 100
    MAX_PATH_LENGTH = 256

    @classmethod
    def validate_input(
        cls, user_input: str, input_type: str = "general"
    ) -> dict[str, Any]:
        """
        Validate and sanitize user input based on type

        Args:
            user_input: The raw user input
            input_type: Type of input ('nlp', 'package', 'path', 'general')

        Returns:
            Dict with:
                - valid: bool
                - sanitized_input: str (if valid)
                - reason: str (if invalid)
                - suggestions: List[str] (if invalid)
        """
        if not user_input:
            return {
                "valid": False,
                "reason": "Empty input provided",
                "suggestions": ["Please provide a command or question"],
            }

        # Length check
        if len(user_input) > cls.MAX_INPUT_LENGTH:
            return {
                "valid": False,
                "reason": f"Input too long (max {cls.MAX_INPUT_LENGTH} characters)",
                "suggestions": [
                    "Please shorten your request",
                    "Break it into smaller parts",
                ],
            }

        # Type-specific validation
        if input_type == "nlp":
            return cls._validate_nlp_input(user_input)
        if input_type == "package":
            return cls._validate_package_name(user_input)
        if input_type == "path":
            return cls._validate_path(user_input)
        return cls._validate_general_input(user_input)

    @classmethod
    def _validate_nlp_input(cls, user_input: str) -> dict[str, Any]:
        """Validate natural language input"""
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return {
                    "valid": False,
                    "reason": "Potentially dangerous pattern detected",
                    "suggestions": [
                        "Please rephrase without special characters",
                        "Use simple natural language",
                        "Avoid command-line syntax",
                    ],
                }

        # Basic sanitization - remove excessive whitespace
        sanitized = " ".join(user_input.split())

        # Remove any Unicode control characters
        sanitized = "".join(
            char for char in sanitized if not ord(char) < 32 or char == "\n"
        )

        # Escape any quotes for safety
        sanitized = sanitized.replace('"', '\\"').replace("'", "\\'")

        return {"valid": True, "sanitized_input": sanitized}

    @classmethod
    def _validate_package_name(cls, package_name: str) -> dict[str, Any]:
        """Validate package name"""
        # Length check
        if len(package_name) > cls.MAX_PACKAGE_NAME_LENGTH:
            return {
                "valid": False,
                "reason": f"Package name too long (max {cls.MAX_PACKAGE_NAME_LENGTH} characters)",
                "suggestions": ["Check the package name spelling"],
            }

        # Format check
        if not cls.VALID_PACKAGE_NAME.match(package_name):
            return {
                "valid": False,
                "reason": "Invalid package name format",
                "suggestions": [
                    "Package names should contain only letters, numbers, dash, underscore, and dot",
                    "Examples: firefox, python3, git-lfs",
                ],
            }

        # Check for suspicious patterns
        suspicious_packages = ["rm", "dd", "mkfs", "fork-bomb"]
        if any(sus in package_name.lower() for sus in suspicious_packages):
            return {
                "valid": False,
                "reason": "Suspicious package name",
                "suggestions": [
                    "Please verify the package name",
                    "Check nixpkgs for valid packages",
                ],
            }

        return {"valid": True, "sanitized_input": package_name}

    @classmethod
    def _validate_path(cls, file_path: str) -> dict[str, Any]:
        """Validate file path"""
        # Length check
        if len(file_path) > cls.MAX_PATH_LENGTH:
            return {
                "valid": False,
                "reason": f"Path too long (max {cls.MAX_PATH_LENGTH} characters)",
                "suggestions": ["Use a shorter path"],
            }

        # Path traversal check
        if ".." in file_path:
            return {
                "valid": False,
                "reason": "Path traversal detected",
                "suggestions": ["Use absolute paths", "Avoid .. in paths"],
            }

        # Check if path is within allowed directories
        allowed_dirs = ["/etc/nixos", "/home", "/tmp", "/var"]
        path_obj = Path(file_path).resolve()

        if not any(str(path_obj).startswith(allowed) for allowed in allowed_dirs):
            return {
                "valid": False,
                "reason": "Path outside allowed directories",
                "suggestions": [
                    f'Paths should be within: {", ".join(allowed_dirs)}',
                    "Use paths relative to your home directory",
                ],
            }

        return {"valid": True, "sanitized_input": str(path_obj)}

    @classmethod
    def _validate_general_input(cls, user_input: str) -> dict[str, Any]:
        """Validate general input"""
        # Check for obvious command injection
        dangerous_chars = ["&", "|", ";", "`", "$", "<", ">"]
        found_chars = [char for char in dangerous_chars if char in user_input]

        if found_chars:
            return {
                "valid": False,
                "reason": f'Dangerous characters detected: {", ".join(found_chars)}',
                "suggestions": [
                    "Remove special shell characters",
                    "Use natural language instead of commands",
                ],
            }

        # Basic sanitization
        try:
            # Try to safely quote the input
            sanitized = shlex.quote(user_input)

            return {"valid": True, "sanitized_input": sanitized}
        except Exception:
            return {
                "valid": False,
                "reason": "Input contains invalid characters",
                "suggestions": ["Simplify your input", "Remove special characters"],
            }

    @classmethod
    def validate_command(cls, command: list[str]) -> tuple[bool, str | None]:
        """
        Validate a command that will be executed

        Args:
            command: List of command parts (e.g., ['nix-env', '-iA', 'nixpkgs.firefox'])

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not command:
            return False, "Empty command"

        # Whitelist of allowed base commands
        allowed_commands = [
            "nix",
            "nix-env",
            "nix-channel",
            "nix-store",
            "nix-build",
            "nixos-rebuild",
            "nix-shell",
            "nix-instantiate",
            "nix-collect-garbage",
            "systemctl",
            "journalctl",
            "ip",
            "ping",
            "df",
            "free",
            "ps",
            "which",
            "whereis",
            "ls",
            "cat",
            "echo",
            "true",
            "false",
        ]

        base_command = os.path.basename(command[0])

        if base_command not in allowed_commands:
            return False, f"Command '{base_command}' not in allowed list"

        # Check for dangerous flags
        dangerous_flags = [
            "--run",  # Can execute arbitrary commands
            "--command",  # Can execute arbitrary commands
            "-c",  # Shell command execution
            "--expr",  # Nix expressions could be dangerous
        ]

        for arg in command[1:]:
            if arg in dangerous_flags:
                return False, f"Dangerous flag '{arg}' not allowed"

        # Validate each argument
        for arg in command:
            # Check for command substitution
            if "`" in arg or "$(" in arg or "${" in arg:
                return False, "Command substitution not allowed"

            # Check for redirections
            if any(char in arg for char in ["<", ">", "|", "&", ";"]):
                return False, "Shell metacharacters not allowed in arguments"

        return True, None

    @classmethod
    def sanitize_for_display(cls, text: str) -> str:
        """
        Sanitize text for safe display to user

        Args:
            text: Text that will be displayed

        Returns:
            Sanitized text safe for display
        """
        # Remove ANSI escape codes
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        text = ansi_escape.sub("", text)

        # Remove other control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")

        # Limit length for display
        max_display_length = 5000
        if len(text) > max_display_length:
            text = text[:max_display_length] + "\n... (truncated)"

        return text

    @classmethod
    def validate_nix_expression(cls, expr: str) -> tuple[bool, str | None]:
        """
        Validate a Nix expression for safety

        Args:
            expr: Nix expression string

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for import of suspicious paths
        if "import" in expr:
            suspicious_imports = ["/etc/passwd", "/etc/shadow", "~/.ssh"]
            for path in suspicious_imports:
                if path in expr:
                    return False, f"Suspicious import of {path}"

        # Check for builtins that could be dangerous
        dangerous_builtins = ["exec", "getEnv", "readFile", "readDir"]
        for builtin in dangerous_builtins:
            if f"builtins.{builtin}" in expr:
                return False, f"Dangerous builtin '{builtin}' not allowed"

        # Check for network operations
        if any(proto in expr for proto in ["http://", "https://", "ftp://", "ssh://"]):
            return False, "Network operations not allowed in expressions"

        return True, None


class SecurityContext:
    """
    Security context manager for operations
    """

    def __init__(self, operation_type: str, user: str | None = None):
        self.operation_type = operation_type
        self.user = user or os.getenv("USER", "unknown")
        self.start_time = None

    def __enter__(self):
        self.start_time = os.times()
        logger.info(f"Security context started: {self.operation_type} by {self.user}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = os.times()
        if self.start_time:
            elapsed = end_time.elapsed - self.start_time.elapsed
            logger.info(
                f"Security context ended: {self.operation_type} took {elapsed:.2f}s"
            )

        if exc_type:
            logger.error(f"Security context error: {exc_type.__name__}: {exc_val}")

        return False  # Don't suppress exceptions


# Demo and testing
def demo():
    """Demonstrate input validation"""
    print("🔒 Security Input Validator Demo\n")

    test_inputs = [
        # Valid inputs
        ("install firefox", "nlp", True),
        ("what is my disk usage?", "nlp", True),
        ("firefox", "package", True),
        ("python3-numpy", "package", True),
        ("/etc/nixos/configuration.nix", "path", True),
        # Invalid inputs
        ("rm -rf /", "nlp", False),
        ("install firefox; rm -rf /", "nlp", False),
        ("../../etc/passwd", "path", False),
        ("firefox`echo bad`", "package", False),
        (":(){ :|:& };:", "nlp", False),
    ]

    for user_input, input_type, expected_valid in test_inputs:
        print(f"\n{'='*50}")
        print(f"Input: '{user_input}' (type: {input_type})")
        print(f"Expected: {'✅ Valid' if expected_valid else '❌ Invalid'}")

        result = InputValidator.validate_input(user_input, input_type)

        print(f"Result: {'✅ Valid' if result['valid'] else '❌ Invalid'}")
        if result["valid"]:
            print(f"Sanitized: '{result['sanitized_input']}'")
        else:
            print(f"Reason: {result['reason']}")
            print(f"Suggestions: {', '.join(result.get('suggestions', []))}")

    # Test command validation
    print(f"\n{'='*50}")
    print("Command Validation Tests:")

    test_commands = [
        (["nix-env", "-iA", "nixpkgs.firefox"], True),
        (["nixos-rebuild", "switch"], True),
        (["rm", "-rf", "/"], False),
        (["nix-shell", "--run", "malicious"], False),
        (["ls", "|", "grep", "test"], False),
    ]

    for command, expected_valid in test_commands:
        valid, error = InputValidator.validate_command(command)
        print(f"\nCommand: {' '.join(command)}")
        print(f"Expected: {'✅ Valid' if expected_valid else '❌ Invalid'}")
        print(f"Result: {'✅ Valid' if valid else f'❌ Invalid: {error}'}")


if __name__ == "__main__":
    demo()
