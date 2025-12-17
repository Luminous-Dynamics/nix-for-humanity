"""
Dependency Predictor - Predicts what packages/tools you'll need

Uses context to predict dependencies before you even ask for them.

Examples:
- Detects you're editing Python → Predicts you'll need python dev tools
- Sees you're working with Docker → Predicts you'll need docker-compose
- Notices Rust project → Predicts you'll need rust-analyzer
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

from ..context import get_context_engine, ProjectType, IntentType
from .types import DependencyPrediction, PredictionType, PredictionBatch

logger = logging.getLogger(__name__)


class DependencyPredictor:
    """
    Predicts package dependencies based on context

    Strategies:
    1. Project type → common dependencies
    2. File patterns → required tools
    3. Command history → missing dependencies
    4. Common pairings (e.g., docker + docker-compose)
    """

    def __init__(self):
        """Initialize the dependency predictor"""
        self.context_engine = get_context_engine()

        # Project type → common dependencies mapping
        self.project_dependencies = {
            ProjectType.PYTHON: [
                ("python3", "Python interpreter", 0.9),
                ("python3Packages.pip", "Package manager", 0.8),
                ("python3Packages.virtualenv", "Virtual environments", 0.7),
                ("black", "Code formatter", 0.6),
                ("ruff", "Fast linter", 0.6),
            ],
            ProjectType.RUST: [
                ("rustc", "Rust compiler", 0.95),
                ("cargo", "Rust package manager", 0.95),
                ("rust-analyzer", "IDE support", 0.8),
                ("clippy", "Linter", 0.7),
            ],
            ProjectType.WEB_DEV: [
                ("nodejs", "Node.js runtime", 0.85),
                ("nodePackages.npm", "Package manager", 0.85),
                ("nodePackages.typescript", "TypeScript", 0.7),
                ("nodePackages.eslint", "Linter", 0.6),
            ],
            ProjectType.SYSTEM_CONFIG: [
                ("nixfmt", "Nix formatter", 0.7),
                ("nix-tree", "Dependency visualization", 0.5),
                ("nil", "Nix LSP", 0.6),
            ],
            ProjectType.NIX: [
                ("nixfmt", "Nix formatter", 0.8),
                ("nix-tree", "Dependency visualization", 0.6),
                ("nil", "Nix LSP", 0.7),
            ],
        }

        # Common dependency pairings
        self.dependency_pairs = {
            "docker": ["docker-compose"],
            "postgresql": ["pgcli", "postgresql-client"],
            "nginx": ["certbot"],  # For SSL certificates
            "git": ["git-lfs"],  # For large files
            "python3": ["python3Packages.pip"],
            "nodejs": ["nodePackages.npm", "nodePackages.yarn"],
        }

        # File extension → required tools
        self.file_dependencies = {
            ".rs": [("rust-analyzer", "Rust IDE support", 0.8)],
            ".py": [("python3", "Python interpreter", 0.9)],
            ".ts": [("nodePackages.typescript", "TypeScript", 0.85)],
            ".nix": [("nil", "Nix LSP", 0.6)],
            ".sql": [("postgresql", "Database", 0.7)],
            ".md": [("glow", "Markdown viewer", 0.4)],
        }

    def predict(self, context=None) -> PredictionBatch:
        """
        Predict dependencies based on current context

        Args:
            context: Optional context (uses current if None)

        Returns:
            PredictionBatch with dependency predictions
        """
        if context is None:
            context = self.context_engine.get_current_context()

        batch = PredictionBatch(
            context_summary=f"Project: {context.primary_project}, Intent: {context.current_intent}"
        )

        # Predict from project type
        if context.primary_project:
            batch = self._predict_from_project_type(context, batch)

        # Predict from active files
        batch = self._predict_from_files(context, batch)

        # Predict from command history
        batch = self._predict_from_commands(context, batch)

        return batch

    def _predict_from_project_type(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Predict dependencies based on project type"""
        if not context.primary_project:
            return batch

        project_deps = self.project_dependencies.get(context.primary_project, [])

        for pkg_name, reason, confidence in project_deps:
            prediction = DependencyPrediction(
                prediction_type=PredictionType.DEPENDENCY,
                confidence=confidence,
                confidence_level=None,  # Will be set by __post_init__
                title=f"You'll likely need '{pkg_name}'",
                description=f"{reason} for {context.primary_project.value} projects",
                evidence=[
                    f"Project type: {context.primary_project.value}",
                    f"Common dependency for this project type"
                ],
                package_name=pkg_name,
                reason=reason,
                install_command=f"nix-shell -p {pkg_name}"
            )
            batch.add(prediction)

        return batch

    def _predict_from_files(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Predict dependencies based on active files"""
        # Get file extensions from active files
        extensions = set()
        for file_activity in context.active_files:
            ext = self._get_extension(file_activity.path)
            if ext:
                extensions.add(ext)

        # Predict dependencies for each extension
        for ext in extensions:
            if ext in self.file_dependencies:
                for pkg_name, reason, confidence in self.file_dependencies[ext]:
                    prediction = DependencyPrediction(
                        prediction_type=PredictionType.DEPENDENCY,
                        confidence=confidence,
                        confidence_level=None,
                        title=f"Consider '{pkg_name}' for {ext} files",
                        description=reason,
                        evidence=[
                            f"Working with {ext} files",
                            f"Common tool for this file type"
                        ],
                        package_name=pkg_name,
                        reason=reason,
                        install_command=f"nix-shell -p {pkg_name}"
                    )
                    batch.add(prediction)

        return batch

    def _predict_from_commands(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Predict dependencies based on command history"""
        # Look for commands that suggest missing dependencies
        recent = context.recent_commands[:10] if context.recent_commands else []

        for cmd_activity in recent:
            cmd = cmd_activity.command

            # Check for dependency pairs
            for base_pkg, related_pkgs in self.dependency_pairs.items():
                if base_pkg in cmd:
                    for related_pkg in related_pkgs:
                        prediction = DependencyPrediction(
                            prediction_type=PredictionType.DEPENDENCY,
                            confidence=0.75,
                            confidence_level=None,
                            title=f"'{related_pkg}' often used with '{base_pkg}'",
                            description=f"Common companion package",
                            evidence=[
                                f"You're using {base_pkg}",
                                f"{related_pkg} is commonly used together"
                            ],
                            package_name=related_pkg,
                            reason=f"Companion to {base_pkg}",
                            related_packages=[base_pkg],
                            install_command=f"nix-shell -p {related_pkg}"
                        )
                        batch.add(prediction)

        return batch

    @staticmethod
    def _get_extension(filepath) -> Optional[str]:
        """Extract file extension from path"""
        # Convert Path to string if needed
        filepath_str = str(filepath)
        if '.' not in filepath_str:
            return None
        return '.' + filepath_str.rsplit('.', 1)[-1]


# Global instance
_dependency_predictor: Optional[DependencyPredictor] = None


def get_dependency_predictor() -> DependencyPredictor:
    """Get or create global dependency predictor"""
    global _dependency_predictor

    if _dependency_predictor is None:
        _dependency_predictor = DependencyPredictor()

    return _dependency_predictor
