#!/usr/bin/env python3
"""
FlakeSpecialist - Handles Nix flake operations
Part of v0.3.1 critical fixes based on user feedback
"""

from typing import Dict, List, Optional
import re


class FlakeSpecialist:
    """Specialist for Nix flake operations"""

    def __init__(self):
        self.patterns = {
            "init": [
                r"nix\s+flake\s+init",
                r"initialize\s+flake",
                r"create\s+flake",
                r"new\s+flake",
                r"start\s+flake\s+project",
            ],
            "update": [
                r"nix\s+flake\s+update",
                r"update\s+flake(?:s)?",
                r"flake\s+update",
                r"refresh\s+flake\s+inputs",
                r"update\s+flake\s+lock",
            ],
            "check": [
                r"nix\s+flake\s+check",
                r"check\s+flake",
                r"validate\s+flake",
                r"test\s+flake",
                r"verify\s+flake",
            ],
            "show": [
                r"nix\s+flake\s+show",
                r"show\s+flake",
                r"display\s+flake",
                r"list\s+flake\s+outputs",
                r"flake\s+info",
            ],
            "metadata": [
                r"nix\s+flake\s+metadata",
                r"flake\s+metadata",
                r"flake\s+details",
                r"flake\s+information",
            ],
            "lock": [
                r"nix\s+flake\s+lock",
                r"lock\s+flake\s+inputs",
                r"update\s+flake\.lock",
                r"refresh\s+lock\s+file",
            ],
            "new": [
                r"nix\s+flake\s+new",
                r"create\s+new\s+flake\s+project",
                r"flake\s+template",
                r"generate\s+flake",
            ],
            "build": [
                r"nix\s+build.*flake",
                r"build\s+flake",
                r"compile\s+flake",
                r"flake\s+build",
            ],
            "develop": [
                r"nix\s+develop",
                r"enter\s+flake\s+shell",
                r"flake\s+dev\s+shell",
                r"development\s+shell",
            ],
            "run": [
                r"nix\s+run",
                r"run\s+flake\s+app",
                r"execute\s+flake",
                r"flake\s+run",
            ],
        }

        self.commands = {
            "init": "nix flake init",
            "update": "nix flake update",
            "check": "nix flake check",
            "show": "nix flake show",
            "metadata": "nix flake metadata",
            "lock": "nix flake lock",
            "new": "nix flake new -t templates#basic .",
            "build": "nix build",
            "develop": "nix develop",
            "run": "nix run",
        }

        self.explanations = {
            "init": "Initialize a new flake in the current directory",
            "update": "Update all flake inputs to their latest versions",
            "check": "Check flake outputs and run tests",
            "show": "Show flake outputs and structure",
            "metadata": "Show detailed flake metadata and inputs",
            "lock": "Update the flake.lock file without updating inputs",
            "new": "Create a new project from a flake template",
            "build": "Build the default package from the flake",
            "develop": "Enter a development shell defined by the flake",
            "run": "Run the default app from the flake",
        }

        # Common template shortcuts
        self.templates = {
            "rust": "nix flake new -t templates#rust-project .",
            "python": "nix flake new -t templates#python-project .",
            "nodejs": "nix flake new -t templates#nodejs-project .",
            "go": "nix flake new -t templates#go-project .",
            "haskell": "nix flake new -t templates#haskell-project .",
        }

    def can_handle(self, query: str) -> bool:
        """Check if this specialist can handle the query"""
        query_lower = query.lower()

        # Check for flake keywords
        if "flake" in query_lower:
            return True

        # Check for nix develop/run (commonly flake-related)
        if re.search(r"nix\s+(develop|run|build)", query_lower):
            return True

        # Check specific patterns
        for patterns in self.patterns.values():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return True

        return False

    def handle_query(self, query: str) -> Dict:
        """Process a flake-related query"""
        query_lower = query.lower()

        # Check for language-specific templates
        for lang, template_cmd in self.templates.items():
            if lang in query_lower and any(
                word in query_lower for word in ["new", "create", "template", "project"]
            ):
                return {
                    "command": template_cmd,
                    "explanation": f"Create a new {lang.title()} project with flake template",
                    "category": "flake",
                    "confidence": 0.9,
                    "specialist": "FlakeSpecialist",
                    "alternatives": [
                        "nix flake init",
                        f"nix flake new -t github:some/{lang}-template .",
                    ],
                }

        # Find the best matching operation
        best_match = None
        best_score = 0

        for operation, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    # Calculate match score based on pattern specificity
                    score = len(pattern)
                    if score > best_score:
                        best_score = score
                        best_match = operation

        if best_match:
            command = self.commands[best_match]

            # Add context-specific modifications
            if best_match == "update" and "single" in query_lower:
                # Update single input
                command = "nix flake lock --update-input <input-name>"
            elif best_match == "build" and "#" in query:
                # Build specific output
                match = re.search(r"#(\w+)", query)
                if match:
                    command = f"nix build .#{match.group(1)}"
            elif best_match == "develop" and any(
                word in query_lower for word in ["shell", "env"]
            ):
                # Develop with specific shell
                if "ci" in query_lower:
                    command = "nix develop .#ci"
                elif "test" in query_lower:
                    command = "nix develop .#test"

            return {
                "command": command,
                "explanation": self.explanations[best_match],
                "category": "flake",
                "confidence": min(
                    0.95, 0.85 + (best_score / 100)
                ),  # Increased base confidence
                "specialist": "FlakeSpecialist",
                "alternatives": self._get_alternatives(best_match),
            }

        # Default fallback for unrecognized flake queries
        return {
            "command": "nix flake --help",
            "explanation": "Show flake help to find the right command",
            "category": "flake",
            "confidence": 0.5,
            "specialist": "FlakeSpecialist",
            "alternatives": [
                "nix flake show",
                "nix flake check",
                "nix flake metadata",
            ],
        }

    def _get_alternatives(self, operation: str) -> List[str]:
        """Get alternative commands for an operation"""
        alternatives = []

        if operation == "update":
            alternatives = [
                "nix flake update --commit-lock-file",  # Auto-commit
                "nix flake lock --update-input nixpkgs",  # Update specific
                "nix flake update && git diff flake.lock",  # Show changes
            ]
        elif operation == "init":
            alternatives = [
                "nix flake init -t templates#minimal",
                "nix flake init -t nixpkgs#templates.defaultTemplate",
                "nix flake new -t templates#full .",
            ]
        elif operation == "develop":
            alternatives = [
                "nix develop -c $SHELL",  # Enter with shell
                "nix develop --profile dev-profile",  # Create profile
                "nix develop --command code .",  # Launch VSCode
            ]
        elif operation == "build":
            alternatives = [
                "nix build --print-build-logs",  # Verbose
                "nix build --no-link",  # Don't create result symlink
                "nix build .#packages.x86_64-linux.default",  # Explicit
            ]

        return alternatives

    def get_common_tasks(self) -> List[Dict]:
        """Return common flake tasks for help/suggestions"""
        return [
            {
                "task": "Initialize a new flake",
                "command": "nix flake init",
                "frequency": "common",
            },
            {
                "task": "Update all inputs",
                "command": "nix flake update",
                "frequency": "very_common",
            },
            {
                "task": "Check flake validity",
                "command": "nix flake check",
                "frequency": "common",
            },
            {
                "task": "Enter development shell",
                "command": "nix develop",
                "frequency": "very_common",
            },
            {
                "task": "Build default package",
                "command": "nix build",
                "frequency": "very_common",
            },
            {
                "task": "Show flake outputs",
                "command": "nix flake show",
                "frequency": "common",
            },
            {
                "task": "Create Python project",
                "command": "nix flake new -t templates#python-project .",
                "frequency": "occasional",
            },
            {
                "task": "Update single input",
                "command": "nix flake lock --update-input nixpkgs",
                "frequency": "occasional",
            },
        ]
