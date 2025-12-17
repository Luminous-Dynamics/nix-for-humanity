"""
Project Detector - Infers project type and goals

Combines evidence from files and commands to determine:
- What type of project user is working on
- Confidence level in detection
- Project-specific needs and suggestions
"""

import logging
from typing import Optional, Dict, List, Tuple
from collections import Counter

from .types import ProjectType
from .file_monitor import FileMonitor
from .command_tracker import CommandTracker

logger = logging.getLogger(__name__)


class ProjectDetector:
    """
    Detect current project type from multiple sources

    Combines evidence from:
    - File activity
    - Command history
    - Working directory
    - File patterns
    """

    def __init__(
        self,
        file_monitor: FileMonitor,
        command_tracker: CommandTracker
    ):
        """
        Initialize project detector

        Args:
            file_monitor: FileMonitor instance for file context
            command_tracker: CommandTracker instance for command context
        """
        self.file_monitor = file_monitor
        self.command_tracker = command_tracker

    def detect_project(self) -> Tuple[Optional[ProjectType], float]:
        """
        Detect current project type with confidence

        Returns:
            Tuple of (project_type, confidence)
            confidence is 0.0-1.0
        """
        # Gather evidence from multiple sources
        evidence: Counter[ProjectType] = Counter()

        # Evidence from files (weight: 3)
        file_project = self.file_monitor.infer_project_type()
        if file_project and file_project != ProjectType.UNKNOWN:
            evidence[file_project] += 3
            logger.debug(f"File evidence: {file_project.value}")

        # Evidence from commands (weight: 2)
        command_project = self.command_tracker.get_project_context_from_commands()
        if command_project and command_project != ProjectType.UNKNOWN:
            evidence[command_project] += 2
            logger.debug(f"Command evidence: {command_project.value}")

        # Evidence from language distribution (weight: 1)
        lang_dist = self.file_monitor.get_language_distribution()
        if lang_dist:
            # Map languages to project types
            for lang, count in lang_dist.items():
                project = self._language_to_project(lang)
                if project:
                    evidence[project] += min(count, 3)  # Cap contribution

        if not evidence:
            return (ProjectType.UNKNOWN, 0.0)

        # Get project with most evidence
        project, score = evidence.most_common(1)[0]

        # Calculate confidence (0.0-1.0)
        # Based on:
        # - How much evidence (score)
        # - How concentrated (ratio of top to second)
        max_possible_score = 10  # 3 (files) + 2 (commands) + 3 (languages) + 2 (bonus)
        confidence = min(score / max_possible_score, 1.0)

        # Boost confidence if evidence is concentrated
        if len(evidence) > 1:
            second_score = evidence.most_common(2)[1][1]
            if score > second_score * 2:  # Clear winner
                confidence = min(confidence * 1.2, 1.0)

        logger.info(f"Detected project: {project.value} (confidence: {confidence:.1%})")

        return (project, confidence)

    def get_project_needs(self, project_type: ProjectType) -> List[str]:
        """
        Get likely needs for a project type

        Args:
            project_type: The detected project type

        Returns:
            List of likely package/tool needs
        """
        needs_map = {
            ProjectType.PYTHON: [
                "python3",
                "python3Packages.pip",
                "python3Packages.virtualenv",
                "poetry",
                "black",
                "ruff"
            ],
            ProjectType.RUST: [
                "rustc",
                "cargo",
                "rust-analyzer",
                "clippy",
                "rustfmt"
            ],
            ProjectType.JAVASCRIPT: [
                "nodejs",
                "nodePackages.npm",
                "nodePackages.yarn",
                "nodePackages.typescript"
            ],
            ProjectType.TYPESCRIPT: [
                "nodejs",
                "nodePackages.typescript",
                "nodePackages.ts-node",
                "nodePackages.eslint"
            ],
            ProjectType.WEB_DEV: [
                "nodejs",
                "firefox",
                "chromium",
                "nodePackages.live-server"
            ],
            ProjectType.NIX: [
                "nil",  # Nix LSP
                "nixpkgs-fmt",
                "nix-tree"
            ],
            ProjectType.SYSTEM_CONFIG: [
                "nixos-rebuild",
                "home-manager",
                "git"
            ],
            ProjectType.DOCUMENTATION: [
                "pandoc",
                "hugo",
                "mdbook",
                "python3Packages.mkdocs"
            ]
        }

        return needs_map.get(project_type, [])

    def get_project_suggestions(self, project_type: ProjectType) -> List[str]:
        """
        Get helpful suggestions for a project type

        Args:
            project_type: The detected project type

        Returns:
            List of helpful suggestions
        """
        suggestions_map = {
            ProjectType.PYTHON: [
                "Consider using 'nix develop' for reproducible environments",
                "Poetry can manage dependencies in pyproject.toml",
                "Black and ruff can auto-format your code"
            ],
            ProjectType.RUST: [
                "Use 'cargo build' for debug builds, 'cargo build --release' for optimized",
                "rust-analyzer provides excellent IDE support",
                "Consider 'cargo clippy' for linting"
            ],
            ProjectType.JAVASCRIPT: [
                "Use 'npm install' to install dependencies from package.json",
                "Consider TypeScript for better type safety",
                "ESLint can catch common errors"
            ],
            ProjectType.WEB_DEV: [
                "Firefox Developer Edition has great debugging tools",
                "Consider using live-server for auto-reload during development",
                "Chrome DevTools can help debug rendering issues"
            ],
            ProjectType.NIX: [
                "Use 'nix flake check' to validate your flake",
                "nil LSP provides autocomplete in editors",
                "nix-tree visualizes dependency graphs"
            ],
            ProjectType.SYSTEM_CONFIG: [
                "Always test changes with 'nixos-rebuild test' before 'switch'",
                "Use 'nixos-option <option>' to see current values",
                "Keep backups - each generation is automatically saved"
            ]
        }

        return suggestions_map.get(project_type, [])

    def _language_to_project(self, language: str) -> Optional[ProjectType]:
        """Map programming language to project type"""
        mapping = {
            "python": ProjectType.PYTHON,
            "rust": ProjectType.RUST,
            "javascript": ProjectType.JAVASCRIPT,
            "typescript": ProjectType.TYPESCRIPT,
            "nix": ProjectType.NIX,
            "html": ProjectType.WEB_DEV,
            "css": ProjectType.WEB_DEV,
            "markdown": ProjectType.DOCUMENTATION,
        }
        return mapping.get(language)
