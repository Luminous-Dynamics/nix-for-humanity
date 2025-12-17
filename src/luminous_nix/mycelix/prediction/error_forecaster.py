"""
Error Forecaster - Predicts what will fail and why

Anticipates failures before they happen by analyzing context patterns.

Examples:
- Detects missing dependencies before build attempt
- Predicts configuration conflicts
- Warns about common mistakes
- Suggests preventive actions
"""

from typing import List, Dict, Optional, Set
from datetime import datetime
import logging

from ..context import get_context_engine, ProjectType, IntentType
from .types import ErrorPrediction, PredictionType, PredictionBatch

logger = logging.getLogger(__name__)


class ErrorForecaster:
    """
    Predicts errors before they occur

    Strategies:
    1. Missing dependency detection
    2. Configuration conflict detection
    3. Common mistake patterns
    4. Version incompatibility detection
    """

    def __init__(self):
        """Initialize the error forecaster"""
        self.context_engine = get_context_engine()

        # Common error patterns
        self.error_patterns = {
            "missing_rust_std": {
                "triggers": ["cargo build", "cargo run"],
                "conditions": lambda ctx: self._is_rust_project(ctx),
                "error_type": "missing_dependency",
                "affected_operation": "Rust compilation",
                "root_cause": "Rust standard library not found - rustup needs updating",
                "prevention": [
                    "Run: rustup update",
                    "Or: nix-shell -p rustc cargo",
                ],
                "confidence": 0.85,
            },
            "python_missing_deps": {
                "triggers": ["python", "python3", "pip"],
                "conditions": lambda ctx: self._has_python_imports(ctx),
                "error_type": "missing_dependency",
                "affected_operation": "Python script execution",
                "root_cause": "Python packages not installed",
                "prevention": [
                    "Create a shell.nix with required packages",
                    "Or: pip install -r requirements.txt",
                ],
                "confidence": 0.75,
            },
            "docker_not_running": {
                "triggers": ["docker run", "docker-compose"],
                "conditions": lambda ctx: True,
                "error_type": "service_unavailable",
                "affected_operation": "Docker commands",
                "root_cause": "Docker daemon not running",
                "prevention": [
                    "Enable Docker: systemctl start docker",
                    "Or add to configuration.nix: virtualisation.docker.enable = true",
                ],
                "confidence": 0.7,
            },
            "port_already_in_use": {
                "triggers": ["npm start", "serve", "python -m http.server"],
                "conditions": lambda ctx: self._has_recent_server_start(ctx),
                "error_type": "port_conflict",
                "affected_operation": "Server startup",
                "root_cause": "Port already in use by another process",
                "prevention": [
                    "Check running processes: lsof -i :PORT",
                    "Kill the process or use a different port",
                ],
                "confidence": 0.65,
            },
            "nix_build_failure": {
                "triggers": ["nix-build", "nix develop"],
                "conditions": lambda ctx: self._has_recent_nix_errors(ctx),
                "error_type": "build_failure",
                "affected_operation": "Nix build",
                "root_cause": "Previous Nix build failures detected",
                "prevention": [
                    "Clean build cache: nix-collect-garbage",
                    "Update flake.lock: nix flake update",
                ],
                "confidence": 0.8,
            },
        }

        # Project-specific error patterns
        self.project_errors = {
            ProjectType.RUST: [
                "Rust toolchain might need updating (rustup update)",
                "Cargo.lock conflicts might occur",
                "Build.rs scripts might fail without system dependencies",
            ],
            ProjectType.PYTHON: [
                "Virtual environment might not be activated",
                "Missing system libraries for compiled packages",
                "Version conflicts in requirements.txt",
            ],
            ProjectType.WEB_DEV: [
                "node_modules might be outdated (npm install)",
                "Port conflicts if dev server already running",
                "Missing environment variables",
            ],
            ProjectType.SYSTEM_CONFIG: [
                "Syntax errors in configuration.nix",
                "Conflicting package versions",
                "Module import errors",
            ],
            ProjectType.NIX: [
                "Syntax errors in Nix expressions",
                "Conflicting package versions",
                "Missing dependencies in flake.nix",
            ],
        }

    def predict(self, context=None) -> PredictionBatch:
        """
        Predict potential errors based on context

        Args:
            context: Optional context (uses current if None)

        Returns:
            PredictionBatch with error predictions
        """
        if context is None:
            context = self.context_engine.get_current_context()

        batch = PredictionBatch(
            context_summary=f"Analyzing for potential errors in {context.primary_project} project"
        )

        # Check for pattern-based errors
        batch = self._check_error_patterns(context, batch)

        # Check for project-specific risks
        batch = self._check_project_risks(context, batch)

        # Check for configuration issues
        batch = self._check_configuration_issues(context, batch)

        return batch

    def _check_error_patterns(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Check for known error patterns"""
        # Get recent commands
        recent_cmds = context.recent_commands[:5] if context.recent_commands else []

        for cmd_activity in recent_cmds:
            cmd = cmd_activity.command

            # Check each error pattern
            for pattern_name, pattern in self.error_patterns.items():
                # Check if command triggers this pattern
                triggered = any(trigger in cmd for trigger in pattern["triggers"])

                if triggered and pattern["conditions"](context):
                    prediction = ErrorPrediction(
                        prediction_type=PredictionType.ERROR,
                        confidence=pattern["confidence"],
                        confidence_level=None,
                        title=f"{pattern['affected_operation']} might fail",
                        description=pattern["root_cause"],
                        evidence=[
                            f"Command: {cmd}",
                            f"Pattern: {pattern_name}",
                        ],
                        error_type=pattern["error_type"],
                        affected_operation=pattern["affected_operation"],
                        root_cause=pattern["root_cause"],
                        prevention_steps=pattern["prevention"],
                    )
                    batch.add(prediction)

        return batch

    def _check_project_risks(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Check for project-specific risks"""
        if not context.primary_project:
            return batch

        project_risks = self.project_errors.get(context.primary_project, [])

        # Only show risks if there's relevant activity
        if len(context.recent_commands) > 0 or len(context.active_files) > 0:
            for risk in project_risks[:2]:  # Limit to top 2 risks
                prediction = ErrorPrediction(
                    prediction_type=PredictionType.ERROR,
                    confidence=0.5,  # Lower confidence for general risks
                    confidence_level=None,
                    title=f"Common {context.primary_project.value} issue",
                    description=risk,
                    evidence=[
                        f"Project type: {context.primary_project.value}",
                        "Common issue for this project type",
                    ],
                    error_type="general_risk",
                    affected_operation=context.primary_project.value,
                    root_cause=risk,
                    prevention_steps=["Be aware of this common issue"],
                )
                batch.add(prediction)

        return batch

    def _check_configuration_issues(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Check for configuration-related issues"""
        # Check if editing configuration files
        config_files = [
            fa for fa in context.active_files
            if any(name in fa.path.lower() for name in [
                "config", ".nix", "flake", "configuration.nix"
            ])
        ]

        if config_files and context.recent_commands:
            # User is editing config and running commands - might forget to rebuild
            rebuild_cmds = [
                cmd for cmd in context.recent_commands[:5]
                if "nixos-rebuild" in cmd.command or "nix develop" in cmd.command
            ]

            if not rebuild_cmds:
                prediction = ErrorPrediction(
                    prediction_type=PredictionType.MISSING_STEP,
                    confidence=0.75,
                    confidence_level=None,
                    title="Configuration changes not applied",
                    description="You edited config files but haven't rebuilt",
                    evidence=[
                        f"Editing: {config_files[0].path}",
                        "No rebuild command detected",
                    ],
                    error_type="missing_step",
                    affected_operation="System configuration",
                    root_cause="Configuration changes require rebuild to take effect",
                    prevention_steps=[
                        "Run: sudo nixos-rebuild switch",
                        "Or: nix develop (for flake.nix changes)",
                    ],
                )
                batch.add(prediction)

        return batch

    # Helper methods for pattern conditions

    def _is_rust_project(self, context) -> bool:
        """Check if current project is Rust"""
        return context.primary_project == ProjectType.RUST

    def _has_python_imports(self, context) -> bool:
        """Check if there are Python files with imports"""
        python_files = [
            fa for fa in context.active_files
            if fa.path.endswith('.py')
        ]
        return len(python_files) > 0

    def _has_recent_server_start(self, context) -> bool:
        """Check if a server was recently started"""
        recent_cmds = context.recent_commands[:10] if context.recent_commands else []
        server_keywords = ["serve", "start", "run", "dev"]

        return any(
            any(keyword in cmd.command for keyword in server_keywords)
            for cmd in recent_cmds
        )

    def _has_recent_nix_errors(self, context) -> bool:
        """Check if there were recent Nix errors"""
        recent_cmds = context.recent_commands[:10] if context.recent_commands else []

        # Check for failed Nix commands
        nix_failures = [
            cmd for cmd in recent_cmds
            if ("nix" in cmd.command.lower()) and (not cmd.success)
        ]

        return len(nix_failures) > 0


# Global instance
_error_forecaster: Optional[ErrorForecaster] = None


def get_error_forecaster() -> ErrorForecaster:
    """Get or create global error forecaster"""
    global _error_forecaster

    if _error_forecaster is None:
        _error_forecaster = ErrorForecaster()

    return _error_forecaster
