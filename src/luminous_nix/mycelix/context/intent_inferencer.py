"""
Intent Inferencer - Predicts user intent from context

Combines all context signals to infer what the user is trying to accomplish:
- Developing new features
- Debugging issues
- Configuring environment
- Learning/exploring
- Maintaining code
"""

import logging
from typing import Optional, List

from .types import Intent, IntentType, ProjectType, SessionState
from .file_monitor import FileMonitor
from .command_tracker import CommandTracker
from .project_detector import ProjectDetector
from .session_tracker import SessionTracker

logger = logging.getLogger(__name__)


class IntentInferencer:
    """
    Infer user intent from all available context

    Combines:
    - File activity patterns
    - Command history
    - Project type
    - Session state
    """

    def __init__(
        self,
        file_monitor: FileMonitor,
        command_tracker: CommandTracker,
        project_detector: ProjectDetector,
        session_tracker: SessionTracker
    ):
        """
        Initialize intent inferencer

        Args:
            file_monitor: FileMonitor instance
            command_tracker: CommandTracker instance
            project_detector: ProjectDetector instance
            session_tracker: SessionTracker instance
        """
        self.file_monitor = file_monitor
        self.command_tracker = command_tracker
        self.project_detector = project_detector
        self.session_tracker = session_tracker

    def infer_intent(self) -> Intent:
        """
        Infer current user intent

        Returns:
            Intent object with type, confidence, and evidence
        """
        evidence: List[str] = []
        intent_scores = {
            IntentType.DEVELOPING: 0.0,
            IntentType.DEBUGGING: 0.0,
            IntentType.CONFIGURING: 0.0,
            IntentType.LEARNING: 0.0,
            IntentType.MAINTAINING: 0.0,
        }

        # Get context
        recent_files = self.file_monitor.get_recent_files(limit=10)
        recent_commands = self.command_tracker.get_recent_commands(limit=10)
        session_state = self.session_tracker.detect_session_state()
        project, project_confidence = self.project_detector.detect_project()

        # Analyze file activity
        if recent_files:
            active_files = self.file_monitor.get_active_files(threshold_minutes=5)

            if active_files:
                intent_scores[IntentType.DEVELOPING] += 2.0
                evidence.append(f"{len(active_files)} files actively being edited")

            # Check for test files
            test_files = [f for f in recent_files if "test" in str(f.path).lower()]
            if test_files:
                intent_scores[IntentType.DEBUGGING] += 1.5
                evidence.append("Test files being edited")

            # Check for config files
            config_files = [
                f for f in recent_files
                if any(pattern in str(f.path).lower() for pattern in ["config", ".nix", "toml", "json", "yml"])
            ]
            if config_files:
                intent_scores[IntentType.CONFIGURING] += 2.0
                evidence.append("Configuration files being edited")

        # Analyze command patterns
        if recent_commands:
            # Debugging indicators
            failures = [cmd for cmd in recent_commands if not cmd.success]
            if failures:
                failure_rate = len(failures) / len(recent_commands)
                intent_scores[IntentType.DEBUGGING] += failure_rate * 3.0
                evidence.append(f"{len(failures)} failed commands (debugging)")

            # Build/run commands = developing
            build_commands = [
                cmd for cmd in recent_commands
                if any(keyword in cmd.command.lower() for keyword in ["build", "compile", "run", "cargo", "npm run"])
            ]
            if build_commands:
                intent_scores[IntentType.DEVELOPING] += len(build_commands) * 0.5
                evidence.append("Build/run commands executed")

            # Install/setup commands = configuring
            setup_commands = [
                cmd for cmd in recent_commands
                if any(keyword in cmd.command.lower() for keyword in ["install", "setup", "init", "nix develop"])
            ]
            if setup_commands:
                intent_scores[IntentType.CONFIGURING] += len(setup_commands) * 0.5
                evidence.append("Setup/install commands executed")

            # Update/clean commands = maintaining
            maintain_commands = [
                cmd for cmd in recent_commands
                if any(keyword in cmd.command.lower() for keyword in ["update", "upgrade", "clean", "gc", "prune"])
            ]
            if maintain_commands:
                intent_scores[IntentType.MAINTAINING] += len(maintain_commands) * 0.5
                evidence.append("Maintenance commands executed")

            # Help/man/search commands = learning
            learning_commands = [
                cmd for cmd in recent_commands
                if any(keyword in cmd.command.lower() for keyword in ["help", "man", "search", "info", "--help"])
            ]
            if learning_commands:
                intent_scores[IntentType.LEARNING] += len(learning_commands) * 0.5
                evidence.append("Looking up documentation")

        # Session state influences
        if session_state == SessionState.EXPLORING:
            intent_scores[IntentType.LEARNING] += 1.0
            evidence.append("Exploratory session state")
        elif session_state == SessionState.FRUSTRATED:
            intent_scores[IntentType.DEBUGGING] += 2.0
            evidence.append("Frustration detected")
        elif session_state == SessionState.HIGH_FOCUS:
            intent_scores[IntentType.DEVELOPING] += 1.0
            evidence.append("High focus session")

        # Project type influences
        if project == ProjectType.SYSTEM_CONFIG:
            intent_scores[IntentType.CONFIGURING] += 1.0
            evidence.append("System configuration project")
        elif project == ProjectType.DOCUMENTATION:
            intent_scores[IntentType.LEARNING] += 1.0

        # Determine intent
        if not any(score > 0 for score in intent_scores.values()):
            return Intent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                evidence=["No recent activity to analyze"],
                primary_project=project
            )

        # Get highest scoring intent
        intent_type = max(intent_scores.items(), key=lambda x: x[1])[0]
        raw_score = intent_scores[intent_type]

        # Calculate confidence (0.0-1.0)
        # Normalize score and apply project confidence
        confidence = min(raw_score / 5.0, 1.0)  # Cap at 5 points = 100%
        if project_confidence:
            confidence = (confidence + project_confidence) / 2  # Blend with project confidence

        logger.info(f"Inferred intent: {intent_type.value} (confidence: {confidence:.1%})")

        return Intent(
            intent_type=intent_type,
            confidence=confidence,
            evidence=evidence,
            primary_project=project
        )

    def get_next_likely_need(self, intent: Intent) -> Optional[str]:
        """
        Predict next likely need based on intent

        Args:
            intent: Current inferred intent

        Returns:
            Predicted next need/action
        """
        if intent.intent_type == IntentType.DEVELOPING:
            # Predict common development needs
            recent_failures = self.command_tracker.get_recent_failures(limit=3)
            if recent_failures:
                return "Debug recent build/run failures"

            predicted_cmd = self.command_tracker.predict_next_command()
            if predicted_cmd:
                return f"Run '{predicted_cmd}'"

            return "Test or build project"

        elif intent.intent_type == IntentType.DEBUGGING:
            return "Check logs or error messages"

        elif intent.intent_type == IntentType.CONFIGURING:
            if intent.primary_project:
                needs = self.project_detector.get_project_needs(intent.primary_project)
                if needs:
                    return f"May need: {', '.join(needs[:3])}"

            return "Validate configuration"

        elif intent.intent_type == IntentType.LEARNING:
            workflow = self.command_tracker.infer_workflow()
            if workflow:
                return f"Learning about: {workflow}"

            return "Explore documentation"

        elif intent.intent_type == IntentType.MAINTAINING:
            return "Clean up and update dependencies"

        return None
