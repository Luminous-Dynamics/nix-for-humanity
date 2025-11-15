"""
Development Environment Specialist for Luminous Nix
Handles shell and development environment queries with pattern-based fallbacks
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DevEnvironmentSpecialist:
    """Specialized handler for development environment queries (fixing 0% accuracy)"""

    def __init__(self):
        # Pattern-based rules for immediate fix
        self.dev_patterns = {
            # Python development
            r"python.*(dev|environment|shell)": {
                "command": "nix-shell -p python3 python3Packages.pip python3Packages.virtualenv",
                "description": "Python development environment",
                "confidence": 0.95,
            },
            r"(create|setup|make).*(python|py).*env": {
                "command": "nix-shell -p python3 python3Packages.pip",
                "description": "Python development shell",
                "confidence": 0.90,
            },
            # Rust development
            r"rust.*(dev|environment|shell)": {
                "command": "nix-shell -p rustc cargo rustfmt clippy",
                "description": "Rust development environment",
                "confidence": 0.95,
            },
            r"(create|setup).*(rust|cargo)": {
                "command": "nix-shell -p rustc cargo",
                "description": "Rust development shell",
                "confidence": 0.90,
            },
            # Node.js development
            r"(node|nodejs|npm).*(dev|environment|shell)": {
                "command": "nix-shell -p nodejs nodePackages.npm nodePackages.yarn",
                "description": "Node.js development environment",
                "confidence": 0.95,
            },
            r"javascript.*(dev|environment)": {
                "command": "nix-shell -p nodejs nodePackages.npm",
                "description": "JavaScript development shell",
                "confidence": 0.90,
            },
            # Go development
            r"go(lang)?.*(dev|environment|shell)": {
                "command": "nix-shell -p go gopls gotools",
                "description": "Go development environment",
                "confidence": 0.95,
            },
            # C/C++ development
            r"(c\+\+|cpp|gcc).*(dev|environment)": {
                "command": "nix-shell -p gcc cmake gnumake pkg-config",
                "description": "C++ development environment",
                "confidence": 0.90,
            },
            r"c.*(dev|environment|compiler)": {
                "command": "nix-shell -p gcc gnumake pkg-config",
                "description": "C development environment",
                "confidence": 0.85,
            },
            # Java development
            r"java.*(dev|environment|jdk)": {
                "command": "nix-shell -p jdk maven gradle",
                "description": "Java development environment",
                "confidence": 0.90,
            },
            # Ruby development
            r"ruby.*(dev|environment|shell)": {
                "command": "nix-shell -p ruby bundler",
                "description": "Ruby development environment",
                "confidence": 0.90,
            },
            # Haskell development
            r"haskell.*(dev|environment|ghc)": {
                "command": "nix-shell -p ghc cabal-install stack",
                "description": "Haskell development environment",
                "confidence": 0.90,
            },
            # Web development
            r"web.*(dev|environment|full.?stack)": {
                "command": "nix-shell -p nodejs python3 postgresql redis",
                "description": "Full-stack web development",
                "confidence": 0.85,
            },
            # Database development
            r"(database|sql|postgres|mysql).*(dev|environment)": {
                "command": "nix-shell -p postgresql mysql sqlite",
                "description": "Database development tools",
                "confidence": 0.85,
            },
            # Generic development shell
            r"(dev|development).*(shell|environment)": {
                "command": "nix-shell -p git vim tmux",
                "description": "Basic development shell",
                "confidence": 0.70,
            },
            # Shell.nix file creation
            r"(create|generate|make).*shell\.nix": {
                "command": 'echo "{ pkgs ? import <nixpkgs> {} }:\\npkgs.mkShell {\\n  buildInputs = with pkgs; [ ];\\n}" > shell.nix',
                "description": "Create shell.nix template",
                "confidence": 0.95,
            },
            # Flake.nix creation
            r"(create|generate|make).*flake": {
                "command": "nix flake init",
                "description": "Initialize Nix flake",
                "confidence": 0.95,
            },
        }

        # Extended patterns for common variations
        self.variation_map = {
            "python": ["python", "py", "python3", "pip"],
            "rust": ["rust", "cargo", "rustc"],
            "node": ["node", "nodejs", "npm", "js", "javascript"],
            "go": ["go", "golang"],
            "cpp": ["c++", "cpp", "cxx"],
            "java": ["java", "jdk", "jvm"],
            "ruby": ["ruby", "rb", "rails"],
            "haskell": ["haskell", "ghc", "cabal"],
        }

        # Common dev tool packages
        self.dev_tools = {
            "editor": "neovim vim emacs",
            "version_control": "git gh",
            "terminal": "tmux screen alacritty",
            "build": "gnumake cmake ninja meson",
            "debug": "gdb valgrind strace",
            "container": "docker podman",
            "network": "curl wget httpie",
            "json": "jq yq",
            "search": "ripgrep fd fzf",
        }

    def handle_query(self, query: str) -> Optional[Dict]:
        """
        Handle development environment queries
        Returns command, description, and confidence
        """
        query_lower = query.lower().strip()

        # First, try exact pattern matching
        for pattern, result in self.dev_patterns.items():
            if re.search(pattern, query_lower):
                logger.info(f"Matched dev pattern: {pattern}")
                return {
                    "command": result["command"],
                    "description": result["description"],
                    "confidence": result["confidence"],
                    "type": "shell_command",
                }

        # Second, try to identify language and build command
        identified_lang = self._identify_language(query_lower)
        if identified_lang:
            return self._build_dev_command(identified_lang, query_lower)

        # Third, check for dev tool requests
        tool_command = self._check_dev_tools(query_lower)
        if tool_command:
            return tool_command

        return None

    def _identify_language(self, query: str) -> Optional[str]:
        """Identify programming language from query"""
        for lang, variations in self.variation_map.items():
            for variation in variations:
                if variation in query:
                    return lang
        return None

    def _build_dev_command(self, language: str, query: str) -> Dict:
        """Build development command for identified language"""
        commands = {
            "python": "nix-shell -p python3 python3Packages.pip python3Packages.virtualenv",
            "rust": "nix-shell -p rustc cargo rustfmt",
            "node": "nix-shell -p nodejs nodePackages.npm",
            "go": "nix-shell -p go gopls",
            "cpp": "nix-shell -p gcc cmake gnumake",
            "java": "nix-shell -p jdk maven",
            "ruby": "nix-shell -p ruby bundler",
            "haskell": "nix-shell -p ghc cabal-install",
        }

        base_command = commands.get(language, "nix-shell")

        # Add common dev tools if requested
        if any(word in query for word in ["full", "complete", "all"]):
            base_command += " git vim tmux"

        return {
            "command": base_command,
            "description": f"{language.capitalize()} development environment",
            "confidence": 0.85,
            "type": "shell_command",
        }

    def _check_dev_tools(self, query: str) -> Optional[Dict]:
        """Check for development tool requests"""
        for category, packages in self.dev_tools.items():
            if category in query:
                return {
                    "command": f"nix-shell -p {packages}",
                    "description": f"Development {category} tools",
                    "confidence": 0.80,
                    "type": "shell_command",
                }
        return None

    def get_training_examples(self) -> List[Tuple[str, str]]:
        """Generate training examples for the neural network"""
        examples = []

        # Generate variations for each language
        templates = [
            "create {lang} development environment",
            "setup {lang} dev shell",
            "I need a {lang} environment",
            "{lang} development",
            "give me {lang} tools",
            "install {lang} dev environment",
        ]

        for lang in self.variation_map.keys():
            for template in templates:
                query = template.format(lang=lang)
                result = self.handle_query(query)
                if result:
                    examples.append((query, result["command"]))

        return examples

    def validate_command(self, command: str) -> bool:
        """Validate that the generated command is safe"""
        # Basic safety checks
        dangerous_patterns = [
            r"rm\s+-rf",
            r"sudo\s+rm",
            r">\s*/dev/.*",
            r"mkfs",
            r"dd\s+if=",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False

        return True
