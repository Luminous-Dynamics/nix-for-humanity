#!/usr/bin/env python3
"""
Secret Redactor - Prevent TTS from reading credentials aloud
Critical security component for voice interface

SECURITY: Never speak passwords, API keys, SSH keys, tokens aloud
"""

import re
import unicodedata
from typing import Tuple
from dataclasses import dataclass


@dataclass
class RedactionResult:
    """Result of secret redaction"""

    text: str
    was_redacted: bool
    secret_types: list[str]


class SecretRedactor:
    """
    Redact secrets before Text-to-Speech

    Prevents voice interface from reading sensitive data aloud:
    - API keys and tokens
    - Passwords and passphrases
    - SSH private keys
    - JWT tokens
    - Cryptocurrency addresses
    - Age encryption keys
    """

    # Regex patterns for common secret formats
    PATTERNS = {
        # Original patterns
        "jwt": r"eyJ[^\s.]{20,500}\.[^\s.]{20,500}\.[^\s.]{20,500}",
        "api_key": r"\b[a-zA-Z0-9]{32,64}\b",
        "ssh_key": r"-----BEGIN .* PRIVATE KEY-----",
        "hex_64": r"\b[0-9a-f]{64}\b",
        "age_key": r"AGE-SECRET-KEY-[0-9A-Z]+",
        "password_field": r"password[=:\s]+[^\s]+",
        "password_multilingual": r"(?:mot de passe|passwort|contraseña|senha|parola|пароль)[=:\s]+[^\s]+",
        "token": r"token[=:\s]+[a-zA-Z0-9_-]{20,}",
        "email_token": r"[\w\.-]+@[\w\.-]+\.[a-z]{2,}[:\s]+\S+",
        "bearer": r"Bearer\s+[a-zA-Z0-9_-]+",
        "secret": r"secret[=:\s]+[^\s]+",
        # Enhanced patterns (from security audit)
        "env_var": r"(?:^|\s)[A-Z0-9_]{3,32}=[^\s]+",  # .env style (with optional leading whitespace)
        "base64_secret": r"[A-Za-z0-9+/]{32,}={0,2}",  # Base64-encoded secrets
        "url_token": r"[?&](?:token|key|sig|api_key|access_token)=[^&\s]+",  # URL tokens
        "aws_access_key": r"AKIA[0-9A-Z]{16}",  # AWS Access Key ID
        "aws_secret_key": r"[A-Za-z0-9/+=]{40}",  # AWS Secret Access Key format
        "gcp_api_key": r"AIza[0-9A-Za-z_-]{35}",  # Google Cloud API key
        "github_token": r"gh[pousr]_[A-Za-z0-9]{36,}",  # GitHub tokens
        "ssh_path": r"\.ssh/[^\s]*",  # Paths under ~/.ssh
        "credentials_path": r"\.(?:config|aws)/[^\s]*credential[^\s]*",  # Credential files
    }

    # Generic refusal message
    REFUSAL_MESSAGE = "I won't read secrets aloud. Check the terminal for details."

    def __init__(self, enabled: bool = True):
        """
        Initialize redactor

        Args:
            enabled: Whether redaction is active (default: True)
        """
        self.enabled = enabled
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance"""
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for name, pattern in self.PATTERNS.items()
        }

    @staticmethod
    def _normalize_homoglyphs(text: str) -> str:
        """Convert common homoglyphs to ASCII equivalents"""
        # Map Cyrillic and other confusables to Latin
        confusables = {
            "а": "a",
            "е": "e",
            "о": "o",
            "р": "p",
            "с": "c",
            "у": "y",
            "х": "x",  # Cyrillic lowercase
            "А": "A",
            "В": "B",
            "Е": "E",
            "К": "K",
            "М": "M",
            "Н": "H",
            "О": "O",  # Cyrillic uppercase
            "Р": "P",
            "С": "C",
            "Т": "T",
            "Х": "X",
        }
        result = []
        for char in text:
            result.append(confusables.get(char, char))
        return "".join(result)

    def redact(self, text: str) -> RedactionResult:
        """
        Redact secrets from text before TTS

        Args:
            text: Original text that might contain secrets

        Returns:
            RedactionResult with redacted text and metadata
        """
        if not self.enabled:
            return RedactionResult(text=text, was_redacted=False, secret_types=[])

        # Normalize Unicode and convert homoglyphs
        normalized_text = unicodedata.normalize("NFKC", text)
        normalized_text = self._normalize_homoglyphs(normalized_text)

        redacted_text = text
        found_secrets = []

        # Check each pattern against normalized text
        for secret_type, pattern in self.compiled_patterns.items():
            if pattern.search(normalized_text):
                found_secrets.append(secret_type)
                # Replace with generic placeholder
                redacted_text = pattern.sub("•••", redacted_text)

        # If any secrets found, return generic message
        if found_secrets:
            return RedactionResult(
                text=self.REFUSAL_MESSAGE, was_redacted=True, secret_types=found_secrets
            )

        # No secrets found, return original
        return RedactionResult(text=text, was_redacted=False, secret_types=[])

    def check_for_secrets(self, text: str) -> bool:
        """
        Check if text contains secrets without redacting

        Args:
            text: Text to check

        Returns:
            True if secrets detected, False otherwise
        """
        if not self.enabled:
            return False

        for pattern in self.compiled_patterns.values():
            if pattern.search(text):
                return True

        return False

    def add_pattern(self, name: str, pattern: str):
        """
        Add custom secret pattern

        Args:
            name: Pattern identifier (e.g., 'custom_token')
            pattern: Regex pattern to match
        """
        self.PATTERNS[name] = pattern
        self.compiled_patterns[name] = re.compile(pattern, re.IGNORECASE)


# Example usage and testing
if __name__ == "__main__":
    redactor = SecretRedactor()

    # Test cases
    test_cases = [
        "My password is secret123",
        "Here's an API key: abc123def456ghi789jkl012mno345pqr678",
        "JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
        "This is safe text with no secrets",
        "Bearer abc123def456ghi789",
        "AGE-SECRET-KEY-1234567890ABCDEF",
    ]

    print("🔒 Secret Redactor Test\n")

    for i, test in enumerate(test_cases, 1):
        result = redactor.redact(test)

        print(f"Test {i}:")
        print(f"  Input:    {test[:50]}...")
        print(f"  Output:   {result.text}")
        print(f"  Redacted: {result.was_redacted}")
        if result.secret_types:
            print(f"  Types:    {', '.join(result.secret_types)}")
        print()

    print("✅ Secret redactor initialized and tested")
