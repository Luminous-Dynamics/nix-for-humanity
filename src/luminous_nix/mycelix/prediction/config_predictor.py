"""
Configuration Predictor - Suggests configuration improvements

Analyzes your workflow and suggests config changes to improve experience.

Examples:
- "Enable cachix for 10x faster builds"
- "Add this package to your shell.nix"
- "Consider auto-formatting on save"
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from ..context import get_context_engine, ProjectType, IntentType
from .types import ConfigPrediction, PredictionType, PredictionBatch

logger = logging.getLogger(__name__)


class ConfigurationPredictor:
    """
    Suggests configuration improvements based on usage patterns

    Strategies:
    1. Performance optimizations (caching, parallel builds)
    2. Quality of life improvements (aliases, shortcuts)
    3. Project-specific configurations
    4. Development workflow improvements
    """

    def __init__(self):
        """Initialize the configuration predictor"""
        self.context_engine = get_context_engine()

        # Configuration suggestions database
        self.config_suggestions = {
            # Performance improvements
            "enable_cachix": {
                "config_file": "/etc/nixos/configuration.nix",
                "config_key": "nix.settings.substituters",
                "current_value": None,
                "suggested_value": '["https://cache.nixos.org" "https://cachix.org"]',
                "benefit": "10x faster builds with binary cache",
                "risk_level": "low",
                "triggers": ["slow_builds"],
                "confidence": 0.85,
            },
            "enable_parallel_builds": {
                "config_file": "/etc/nixos/configuration.nix",
                "config_key": "nix.settings.max-jobs",
                "current_value": "auto",
                "suggested_value": "auto",
                "benefit": "utilize all CPU cores for faster builds",
                "risk_level": "low",
                "triggers": ["build_commands"],
                "confidence": 0.8,
            },
            "enable_flakes": {
                "config_file": "/etc/nixos/configuration.nix",
                "config_key": "nix.settings.experimental-features",
                "current_value": None,
                "suggested_value": '["nix-command" "flakes"]',
                "benefit": "use modern Nix with reproducible builds",
                "risk_level": "low",
                "triggers": ["nix_usage"],
                "confidence": 0.9,
            },

            # Development tools
            "add_direnv": {
                "config_file": "~/.bashrc or ~/.zshrc",
                "config_key": "programs.direnv.enable",
                "current_value": False,
                "suggested_value": True,
                "benefit": "automatically load project environments",
                "risk_level": "low",
                "triggers": ["frequent_nix_shell"],
                "confidence": 0.75,
            },
            "enable_git_lfs": {
                "config_file": "~/.gitconfig",
                "config_key": "filter.lfs",
                "current_value": None,
                "suggested_value": "enabled",
                "benefit": "handle large files in git repositories",
                "risk_level": "low",
                "triggers": ["large_files"],
                "confidence": 0.7,
            },

            # Project-specific
            "rust_analyzer_config": {
                "config_file": ".vscode/settings.json",
                "config_key": "rust-analyzer.checkOnSave.command",
                "current_value": "check",
                "suggested_value": "clippy",
                "benefit": "get linting suggestions while coding",
                "risk_level": "low",
                "triggers": ["rust_development"],
                "confidence": 0.8,
            },
            "python_formatting": {
                "config_file": "pyproject.toml",
                "config_key": "tool.black",
                "current_value": None,
                "suggested_value": '{"line-length": 88}',
                "benefit": "consistent code formatting",
                "risk_level": "low",
                "triggers": ["python_development"],
                "confidence": 0.75,
            },

            # Aliases and shortcuts
            "add_nix_aliases": {
                "config_file": "~/.bashrc",
                "config_key": "alias",
                "current_value": None,
                "suggested_value": {
                    "ns": "nix-shell",
                    "nb": "nix-build",
                    "nr": "sudo nixos-rebuild switch",
                },
                "benefit": "faster common commands",
                "risk_level": "low",
                "triggers": ["frequent_nix_commands"],
                "confidence": 0.7,
            },
        }

        # Project type → recommended configs
        self.project_configs = {
            ProjectType.PYTHON: [
                "python_formatting",
                "add_direnv",
            ],
            ProjectType.RUST: [
                "rust_analyzer_config",
                "add_direnv",
            ],
            ProjectType.WEB_DEV: [
                "add_direnv",
                "enable_git_lfs",
            ],
            ProjectType.SYSTEM_CONFIG: [
                "enable_flakes",
                "enable_cachix",
                "add_nix_aliases",
            ],
            ProjectType.NIX: [
                "enable_flakes",
                "enable_cachix",
                "add_nix_aliases",
            ],
        }

    def predict(self, context=None) -> PredictionBatch:
        """
        Suggest configuration improvements

        Args:
            context: Optional context (uses current if None)

        Returns:
            PredictionBatch with config suggestions
        """
        if context is None:
            context = self.context_engine.get_current_context()

        batch = PredictionBatch(
            context_summary="Analyzing configuration opportunities"
        )

        # Suggest project-specific configs
        batch = self._suggest_project_configs(context, batch)

        # Suggest performance improvements
        batch = self._suggest_performance_configs(context, batch)

        # Suggest workflow improvements
        batch = self._suggest_workflow_configs(context, batch)

        return batch

    def _suggest_project_configs(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Suggest configurations for current project type"""
        if not context.primary_project:
            return batch

        recommended = self.project_configs.get(context.primary_project, [])

        for config_name in recommended[:2]:  # Limit to top 2
            if config_name in self.config_suggestions:
                config = self.config_suggestions[config_name]

                prediction = ConfigPrediction(
                    prediction_type=PredictionType.CONFIGURATION,
                    confidence=config["confidence"],
                    confidence_level=None,
                    title=f"Recommended for {context.primary_project.value} projects",
                    description=config["benefit"],
                    evidence=[
                        f"Project type: {context.primary_project.value}",
                        "Common configuration for this project type",
                    ],
                    config_file=config["config_file"],
                    config_key=config["config_key"],
                    current_value=config["current_value"],
                    suggested_value=config["suggested_value"],
                    benefit=config["benefit"],
                    risk_level=config["risk_level"],
                    suggested_action=self._generate_config_action(config),
                )
                batch.add(prediction)

        return batch

    def _suggest_performance_configs(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Suggest performance-related configurations"""
        # Check if user runs many Nix commands
        recent_cmds = context.recent_commands[:20] if context.recent_commands else []
        nix_cmds = [cmd for cmd in recent_cmds if "nix" in cmd.command.lower()]

        if len(nix_cmds) >= 5:
            # Suggest Nix performance configs
            for config_name in ["enable_cachix", "enable_parallel_builds"]:
                config = self.config_suggestions[config_name]

                prediction = ConfigPrediction(
                    prediction_type=PredictionType.CONFIGURATION,
                    confidence=config["confidence"],
                    confidence_level=None,
                    title=f"Speed up Nix operations",
                    description=config["benefit"],
                    evidence=[
                        f"You've run {len(nix_cmds)} Nix commands recently",
                        "These settings will improve performance",
                    ],
                    config_file=config["config_file"],
                    config_key=config["config_key"],
                    current_value=config["current_value"],
                    suggested_value=config["suggested_value"],
                    benefit=config["benefit"],
                    risk_level=config["risk_level"],
                    suggested_action=self._generate_config_action(config),
                )
                batch.add(prediction)

        return batch

    def _suggest_workflow_configs(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Suggest workflow improvement configurations"""
        # Check if user frequently enters nix-shell
        recent_cmds = context.recent_commands[:20] if context.recent_commands else []
        nix_shell_cmds = [
            cmd for cmd in recent_cmds
            if "nix-shell" in cmd.command or "nix develop" in cmd.command
        ]

        if len(nix_shell_cmds) >= 3:
            # Suggest direnv
            config = self.config_suggestions["add_direnv"]

            prediction = ConfigPrediction(
                prediction_type=PredictionType.CONFIGURATION,
                confidence=config["confidence"] * 1.1,  # Boost confidence
                confidence_level=None,
                title="Automate nix-shell with direnv",
                description=config["benefit"],
                evidence=[
                    f"You've entered nix-shell {len(nix_shell_cmds)} times",
                    "direnv can automate this",
                ],
                config_file=config["config_file"],
                config_key=config["config_key"],
                current_value=config["current_value"],
                suggested_value=config["suggested_value"],
                benefit=config["benefit"],
                risk_level=config["risk_level"],
                suggested_action=self._generate_config_action(config),
            )
            batch.add(prediction)

        return batch

    @staticmethod
    def _generate_config_action(config: Dict) -> str:
        """Generate action instruction for config"""
        config_file = config["config_file"]
        config_key = config["config_key"]
        suggested_value = config["suggested_value"]

        if "configuration.nix" in config_file:
            return f"Add to {config_file}:\n  {config_key} = {suggested_value};"
        elif "bashrc" in config_file or "zshrc" in config_file:
            return f"Add to {config_file}:\n  {config_key}={suggested_value}"
        elif "pyproject.toml" in config_file:
            return f"Add to {config_file}:\n  [{config_key}]\n  {suggested_value}"
        else:
            return f"Set {config_key} = {suggested_value} in {config_file}"


# Global instance
_config_predictor: Optional[ConfigurationPredictor] = None


def get_config_predictor() -> ConfigurationPredictor:
    """Get or create global configuration predictor"""
    global _config_predictor

    if _config_predictor is None:
        _config_predictor = ConfigurationPredictor()

    return _config_predictor
