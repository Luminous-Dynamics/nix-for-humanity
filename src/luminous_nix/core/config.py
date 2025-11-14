"""
Unified configuration system for Luminous Nix

This replaces the fragmented environment variable approach with a clean,
explicit configuration object that flows through the application.
"""

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """
    Central configuration for all Luminous Nix operations.

    Principles:
    - Safe by default (preview mode)
    - Explicit over implicit
    - Clear precedence rules
    - No conflicting states
    """

    # Core behavior
    preview: bool = True  # Safe by default - preview changes
    force: bool = False  # Skip all confirmations
    verbose: int = 0  # Verbosity level (0=normal, 1=verbose, 2=debug)
    quiet: bool = False  # Minimal output

    # Operation settings
    timeout: int = 30  # Command timeout in seconds
    cache_enabled: bool = True  # Use package cache

    # Persona/UI settings
    persona: Optional[str] = None  # User persona (grandma, developer, etc.)
    color: bool = True  # Colored output
    icons: bool = True  # Use unicode icons

    # Advanced features
    ai_enabled: bool = False  # Use AI assistance
    voice_enabled: bool = False  # Voice interface

    @classmethod
    def from_args(cls, args: list[str]) -> "Config":
        """Parse configuration from command-line arguments"""
        parser = cls._create_parser()
        parsed = parser.parse_args(args)

        # Create config with parsed values
        config = cls()

        # Handle preview/apply logic clearly
        if hasattr(parsed, "apply") and parsed.apply:
            config.preview = False
        elif hasattr(parsed, "preview") and parsed.preview:
            config.preview = True
        # Otherwise keep default (True = safe)

        # Handle force/confirmation
        if hasattr(parsed, "yes") and parsed.yes:
            config.force = True
        elif hasattr(parsed, "force") and parsed.force:
            config.force = True

        # Verbosity
        if hasattr(parsed, "verbose"):
            config.verbose = parsed.verbose or 0
        if hasattr(parsed, "quiet") and parsed.quiet:
            config.quiet = True
            config.verbose = 0  # Quiet overrides verbose

        # Other settings
        if hasattr(parsed, "persona"):
            config.persona = parsed.persona
        if hasattr(parsed, "no_color") and parsed.no_color:
            config.color = False
        if hasattr(parsed, "no_icons") and parsed.no_icons:
            config.icons = False
        if hasattr(parsed, "ai") and parsed.ai:
            config.ai_enabled = True
        if hasattr(parsed, "voice") and parsed.voice:
            config.voice_enabled = True

        # Store the command for later use
        if hasattr(parsed, "command"):
            config._command = parsed.command
        else:
            config._command = []

        return config

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        config = cls()

        # Map environment variables to config
        if os.getenv("LUMINOUS_PREVIEW", "").lower() == "false":
            config.preview = False
        if os.getenv("LUMINOUS_APPLY", "").lower() == "true":
            config.preview = False
        if os.getenv("LUMINOUS_FORCE", "").lower() == "true":
            config.force = True
        if os.getenv("LUMINOUS_VERBOSE"):
            try:
                config.verbose = int(os.getenv("LUMINOUS_VERBOSE", "0"))
            except ValueError:
                config.verbose = 1
        if os.getenv("LUMINOUS_QUIET", "").lower() == "true":
            config.quiet = True
        if os.getenv("LUMINOUS_PERSONA"):
            config.persona = os.getenv("LUMINOUS_PERSONA")
        if os.getenv("LUMINOUS_NO_COLOR", "").lower() == "true":
            config.color = False
        if os.getenv("LUMINOUS_AI_ENABLED", "").lower() == "true":
            config.ai_enabled = True

        return config

    @classmethod
    def from_file(cls, path: Optional[Path] = None) -> "Config":
        """Load configuration from a file"""
        if path is None:
            # Default config locations
            config_paths = [
                Path.home() / ".config/luminous-nix/config.json",
                Path.home() / ".luminous-nix.json",
                Path("/etc/luminous-nix/config.json"),
            ]
        else:
            config_paths = [path]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        data = json.load(f)
                    return cls(**data)
                except Exception:
                    # Invalid config file, use defaults
                    pass

        return cls()

    def merge(self, other: "Config") -> "Config":
        """
        Merge another config into this one.
        Other config takes precedence.
        """
        # Only override if the other value is not the default
        if not other.preview and self.preview:
            self.preview = other.preview
        if other.force and not self.force:
            self.force = other.force
        if other.verbose > self.verbose:
            self.verbose = other.verbose
        if other.quiet and not self.quiet:
            self.quiet = other.quiet
        if other.persona and not self.persona:
            self.persona = other.persona
        if not other.color and self.color:
            self.color = other.color
        if not other.icons and self.icons:
            self.icons = other.icons
        if other.ai_enabled and not self.ai_enabled:
            self.ai_enabled = other.ai_enabled
        if other.voice_enabled and not self.voice_enabled:
            self.voice_enabled = other.voice_enabled

        return self

    def validate(self) -> list[str]:
        """
        Validate configuration for conflicts.
        Returns list of warnings/errors.
        """
        issues = []

        # Check for conflicting flags
        if self.verbose > 0 and self.quiet:
            issues.append(
                "Warning: Both --verbose and --quiet specified. Using --quiet."
            )
            self.verbose = 0

        # Preview mode should be safe
        if not self.preview and not self.force:
            issues.append(
                "Info: Running in apply mode. Changes will be made to the system."
            )

        return issues

    @staticmethod
    def _create_parser() -> argparse.ArgumentParser:
        """Create the argument parser with all flags"""
        parser = argparse.ArgumentParser(
            prog="ask-nix",
            description="Luminous Nix - Natural Language NixOS Interface",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Main command (rest of arguments)
        parser.add_argument("command", nargs="*", help="Command to execute")

        # Mode flags (mutually exclusive)
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument(
            "--preview",
            "-p",
            action="store_true",
            help="Preview changes without applying (default)",
        )
        mode_group.add_argument(
            "--apply", "-a", action="store_true", help="Apply changes to the system"
        )

        # Legacy support (will show deprecation warning)
        mode_group.add_argument(
            "--execute",
            "-e",
            action="store_true",
            dest="apply",  # Map to apply
            help="(Deprecated) Use --apply instead",
        )
        mode_group.add_argument(
            "--dry-run",
            "-n",
            action="store_true",
            dest="preview",  # Map to preview
            help="(Deprecated) Use --preview instead",
        )

        # Confirmation
        parser.add_argument(
            "--yes",
            "-y",
            action="store_true",
            dest="force",
            help="Skip all confirmation prompts",
        )
        parser.add_argument(
            "--force", "-f", action="store_true", help="Force operation (same as --yes)"
        )

        # Output control
        output_group = parser.add_mutually_exclusive_group()
        output_group.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="Increase verbosity (-vv for debug)",
        )
        output_group.add_argument(
            "--quiet", "-q", action="store_true", help="Minimal output"
        )

        # UI options
        parser.add_argument(
            "--no-color", action="store_true", help="Disable colored output"
        )
        parser.add_argument(
            "--no-icons", action="store_true", help="Disable unicode icons"
        )
        parser.add_argument(
            "--persona",
            type=str,
            help="Use specific persona (grandma, developer, etc.)",
        )

        # Advanced features
        parser.add_argument("--ai", action="store_true", help="Enable AI assistance")
        parser.add_argument(
            "--voice", action="store_true", help="Enable voice interface"
        )

        # Version
        parser.add_argument(
            "--version", action="version", version="Luminous Nix v0.1.0-alpha"
        )

        return parser

    def to_dict(self) -> dict:
        """Convert config to dictionary for serialization"""
        return {
            "preview": self.preview,
            "force": self.force,
            "verbose": self.verbose,
            "quiet": self.quiet,
            "timeout": self.timeout,
            "cache_enabled": self.cache_enabled,
            "persona": self.persona,
            "color": self.color,
            "icons": self.icons,
            "ai_enabled": self.ai_enabled,
            "voice_enabled": self.voice_enabled,
        }

    def get_display_mode(self) -> str:
        """Get human-readable mode description"""
        if self.preview:
            return "🔍 Preview Mode"
        else:
            return "⚡ Apply Mode"

    def get_verbosity_level(self) -> str:
        """Get human-readable verbosity level"""
        if self.quiet:
            return "Quiet"
        elif self.verbose == 0:
            return "Normal"
        elif self.verbose == 1:
            return "Verbose"
        else:
            return "Debug"


def load_config(args: Optional[list[str]] = None) -> Config:
    """
    Load configuration with proper precedence:
    1. Command-line arguments (highest priority)
    2. Config file
    3. Environment variables
    4. Defaults (lowest priority)
    """
    # Start with defaults
    config = Config()

    # Layer in environment variables
    env_config = Config.from_env()
    config.merge(env_config)

    # Layer in config file
    file_config = Config.from_file()
    config.merge(file_config)

    # Layer in command-line arguments (highest priority)
    if args is not None:
        arg_config = Config.from_args(args)
        config.merge(arg_config)
        # Store the command
        if hasattr(arg_config, "_command"):
            config._command = arg_config._command

    # Validate for conflicts
    issues = config.validate()
    if issues and config.verbose > 0:
        for issue in issues:
            print(f"Config: {issue}")

    return config
