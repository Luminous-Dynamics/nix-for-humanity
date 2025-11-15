"""
Advanced AI features for Luminous Nix.
Multi-step planning, learning from corrections, and AI-powered troubleshooting.
"""

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class Plan:
    """Multi-step execution plan."""

    goal: str
    steps: list[dict[str, Any]]
    estimated_time: float
    risk_level: str
    dependencies: list[str]
    rollback_plan: Optional[list[str]] = None


@dataclass
class Correction:
    """User correction for learning."""

    original_query: str
    original_response: str
    user_correction: str
    correct_response: str
    timestamp: datetime
    category: str


class MultiStepPlanner:
    """AI planner for complex multi-step configurations."""

    def __init__(self):
        self.plans_db = {}
        self._load_plan_templates()

    def _load_plan_templates(self):
        """Load pre-defined plan templates."""
        self.plans_db = {
            "python_dev_environment": Plan(
                goal="Set up complete Python development environment",
                steps=[
                    {
                        "action": "install",
                        "packages": ["python312", "python312Packages.pip"],
                    },
                    {
                        "action": "install",
                        "packages": [
                            "python312Packages.virtualenv",
                            "python312Packages.poetry",
                        ],
                    },
                    {
                        "action": "install",
                        "packages": [
                            "python312Packages.black",
                            "python312Packages.ruff",
                            "python312Packages.mypy",
                        ],
                    },
                    {
                        "action": "configure",
                        "file": "shell.nix",
                        "template": "python_dev",
                    },
                    {"action": "create", "file": ".envrc", "content": "use nix"},
                    {"action": "install", "packages": ["direnv"]},
                    {"action": "execute", "command": "direnv allow"},
                ],
                estimated_time=120.0,
                risk_level="low",
                dependencies=["nix", "git"],
                rollback_plan=["nix-env --rollback", "rm shell.nix .envrc"],
            ),
            "web_server_ssl": Plan(
                goal="Configure web server with automatic SSL",
                steps=[
                    {"action": "install", "packages": ["nginx", "certbot"]},
                    {"action": "configure", "service": "nginx", "enable": True},
                    {
                        "action": "create",
                        "file": "/etc/nginx/sites-available/default",
                        "template": "nginx_ssl",
                    },
                    {"action": "execute", "command": "certbot --nginx -d example.com"},
                    {"action": "configure", "firewall": {"ports": [80, 443]}},
                    {"action": "restart", "service": "nginx"},
                    {"action": "verify", "url": "https://example.com", "expected": 200},
                ],
                estimated_time=300.0,
                risk_level="medium",
                dependencies=["systemd", "networkmanager"],
                rollback_plan=["systemctl stop nginx", "nix-env --rollback"],
            ),
            "gaming_setup": Plan(
                goal="Complete gaming setup with Steam and Discord",
                steps=[
                    {
                        "action": "configure",
                        "hardware": {"opengl": True, "pulseaudio": True},
                    },
                    {
                        "action": "install",
                        "packages": ["steam", "steam-run", "steamcmd"],
                    },
                    {"action": "install", "packages": ["discord", "obs-studio"]},
                    {"action": "configure", "kernel_params": ["nvidia-drm.modeset=1"]},
                    {"action": "install", "packages": ["mangohud", "gamemode"]},
                    {"action": "create_user_group", "group": "gamemode"},
                    {
                        "action": "restart",
                        "required": True,
                        "reason": "Graphics driver changes",
                    },
                ],
                estimated_time=600.0,
                risk_level="low",
                dependencies=["X11", "graphics_driver"],
                rollback_plan=["nix-env --rollback", "remove kernel params"],
            ),
        }

    def create_plan(self, goal: str) -> Plan:
        """Create execution plan for a goal."""
        # Check templates first
        for key, plan in self.plans_db.items():
            if key in goal.lower() or any(
                word in goal.lower() for word in key.split("_")
            ):
                return plan

        # Generate dynamic plan
        return self._generate_dynamic_plan(goal)

    def _generate_dynamic_plan(self, goal: str) -> Plan:
        """Generate plan dynamically based on goal analysis."""
        steps = []
        risk = "low"

        # Analyze goal for keywords
        if "install" in goal:
            packages = self._extract_packages(goal)
            for pkg in packages:
                steps.append({"action": "install", "package": pkg})

        if "configure" in goal or "setup" in goal:
            if "server" in goal:
                steps.append({"action": "configure", "type": "server"})
                risk = "medium"
            if "development" in goal or "dev" in goal:
                steps.append({"action": "configure", "type": "development"})

        if "secure" in goal or "security" in goal:
            steps.append({"action": "harden", "level": "standard"})
            risk = "medium"

        return Plan(
            goal=goal,
            steps=steps if steps else [{"action": "analyze", "query": goal}],
            estimated_time=len(steps) * 30.0,
            risk_level=risk,
            dependencies=[],
            rollback_plan=["nix-env --rollback"],
        )

    def _extract_packages(self, text: str) -> list[str]:
        """Extract package names from text."""
        # Common package patterns
        packages = []
        words = text.lower().split()

        # Known package keywords
        known_packages = [
            "firefox",
            "chrome",
            "vim",
            "emacs",
            "git",
            "docker",
            "python",
            "nodejs",
            "rust",
            "go",
            "java",
            "vscode",
        ]

        for word in words:
            if word in known_packages:
                packages.append(word)

        return packages

    def validate_plan(self, plan: Plan) -> tuple[bool, list[str]]:
        """Validate a plan before execution."""
        issues = []

        # Check dependencies
        for dep in plan.dependencies:
            if not self._check_dependency(dep):
                issues.append(f"Missing dependency: {dep}")

        # Check risk level
        if plan.risk_level in ["high", "critical"]:
            issues.append(f"High risk operation: {plan.risk_level}")

        # Validate steps
        for i, step in enumerate(plan.steps):
            if "action" not in step:
                issues.append(f"Step {i} missing action")

        return len(issues) == 0, issues

    def _check_dependency(self, dep: str) -> bool:
        """Check if dependency is available."""
        # Simplified check - in reality would check system
        return True


class LearningSystem:
    """System that learns from user corrections."""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path.home() / ".local/share/luminous-nix/learning.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize learning database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_query TEXT,
                original_response TEXT,
                user_correction TEXT,
                correct_response TEXT,
                category TEXT,
                timestamp DATETIME,
                applied_count INTEGER DEFAULT 0
            )
        """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT UNIQUE,
                replacement TEXT,
                confidence REAL,
                usage_count INTEGER DEFAULT 0
            )
        """
        )
        conn.commit()
        conn.close()

    def record_correction(self, correction: Correction):
        """Record a user correction for learning."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO corrections
            (original_query, original_response, user_correction, correct_response, category, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                correction.original_query,
                correction.original_response,
                correction.user_correction,
                correction.correct_response,
                correction.category,
                correction.timestamp,
            ),
        )
        conn.commit()

        # Extract and learn pattern
        self._learn_pattern(correction, conn)
        conn.close()

    def _learn_pattern(self, correction: Correction, conn):
        """Learn patterns from corrections."""
        # Simple pattern extraction
        pattern = self._extract_pattern(
            correction.original_query, correction.correct_response
        )
        if pattern:
            conn.execute(
                """
                INSERT OR REPLACE INTO patterns (pattern, replacement, confidence, usage_count)
                VALUES (?, ?, ?, COALESCE((SELECT usage_count FROM patterns WHERE pattern = ?), 0) + 1)
            """,
                (pattern[0], pattern[1], 0.5, pattern[0]),
            )

    def _extract_pattern(self, query: str, correct: str) -> Optional[tuple[str, str]]:
        """Extract reusable pattern from correction."""
        # Simple word replacement pattern
        query_words = set(query.lower().split())
        correct_words = set(correct.lower().split())

        diff = query_words - correct_words
        if len(diff) == 1:
            wrong_word = diff.pop()
            for word in correct_words - query_words:
                return (wrong_word, word)

        return None

    def apply_learning(self, query: str) -> Optional[str]:
        """Apply learned patterns to improve response."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            SELECT pattern, replacement, confidence
            FROM patterns
            WHERE confidence > 0.3
            ORDER BY confidence DESC, usage_count DESC
        """
        )

        improved_query = query
        for pattern, replacement, confidence in cursor:
            if pattern in query.lower():
                improved_query = improved_query.replace(pattern, replacement)
                # Update usage count
                conn.execute(
                    "UPDATE patterns SET usage_count = usage_count + 1 WHERE pattern = ?",
                    (pattern,),
                )

        conn.commit()
        conn.close()

        return improved_query if improved_query != query else None

    def get_suggestions(self, query: str) -> list[str]:
        """Get suggestions based on past corrections."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            SELECT DISTINCT correct_response
            FROM corrections
            WHERE original_query LIKE ?
            ORDER BY timestamp DESC
            LIMIT 5
        """,
            (f"%{query}%",),
        )

        suggestions = [row[0] for row in cursor]
        conn.close()
        return suggestions


class AITroubleshooter:
    """AI-powered troubleshooting system."""

    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load troubleshooting knowledge base."""
        return {
            "permission_denied": {
                "patterns": ["permission denied", "access denied", "not permitted"],
                "diagnosis": "Insufficient permissions for operation",
                "solutions": [
                    "Run with sudo if system-level change",
                    "Check file ownership with ls -la",
                    "Ensure user is in necessary groups (wheel, users)",
                    "Use nix-shell for development environments",
                ],
                "preventions": [
                    "Always use nix-shell for development",
                    "Avoid sudo for package installation",
                ],
            },
            "command_not_found": {
                "patterns": ["command not found", "not found", "no such file"],
                "diagnosis": "Package not installed or not in PATH",
                "solutions": [
                    "Install package: nix-env -iA nixpkgs.<package>",
                    "Use nix-shell -p <package> for temporary access",
                    "Check PATH: echo $PATH",
                    "Use full path to binary",
                ],
                "preventions": [
                    "Use nix-shell for project dependencies",
                    "Add to configuration.nix",
                ],
            },
            "build_failure": {
                "patterns": ["build failed", "compilation error", "make error"],
                "diagnosis": "Missing build dependencies or configuration issues",
                "solutions": [
                    "Check build dependencies in default.nix",
                    "Use nix-shell with all buildInputs",
                    "Clear build cache: nix-collect-garbage",
                    "Check for conflicting versions",
                ],
                "preventions": [
                    "Use flakes for reproducible builds",
                    "Pin nixpkgs version",
                ],
            },
            "disk_space": {
                "patterns": ["no space left", "disk full", "out of space"],
                "diagnosis": "Insufficient disk space, likely from Nix store",
                "solutions": [
                    "Run: nix-collect-garbage -d",
                    "Remove old generations: nix-env --delete-generations old",
                    "Check disk usage: df -h",
                    "Clean /tmp directory",
                ],
                "preventions": [
                    "Regular garbage collection",
                    "Set up automatic GC in configuration.nix",
                ],
            },
        }

    def diagnose(self, error_message: str) -> dict[str, Any]:
        """Diagnose an error and provide solutions."""
        error_lower = error_message.lower()

        for issue_type, knowledge in self.knowledge_base.items():
            if any(pattern in error_lower for pattern in knowledge["patterns"]):
                return {
                    "issue_type": issue_type,
                    "diagnosis": knowledge["diagnosis"],
                    "solutions": knowledge["solutions"],
                    "preventions": knowledge["preventions"],
                    "confidence": 0.9,
                }

        # Fallback to general diagnosis
        return self._general_diagnosis(error_message)

    def _general_diagnosis(self, error: str) -> dict[str, Any]:
        """Provide general diagnosis for unknown errors."""
        return {
            "issue_type": "unknown",
            "diagnosis": "Unrecognized error pattern",
            "solutions": [
                "Check system logs: journalctl -xe",
                "Search NixOS discourse for similar issues",
                "Try operation with --verbose flag",
                "Check nixpkgs GitHub issues",
            ],
            "preventions": ["Keep system updated", "Use stable nixpkgs channel"],
            "confidence": 0.3,
        }

    def suggest_fix_command(self, diagnosis: dict[str, Any]) -> Optional[str]:
        """Suggest a specific command to fix the issue."""
        fixes = {
            "permission_denied": "sudo chown -R $USER:users .",
            "command_not_found": "nix-env -iA nixpkgs.{package}",
            "build_failure": "nix-shell --pure",
            "disk_space": "nix-collect-garbage -d",
        }

        issue_type = diagnosis.get("issue_type")
        return fixes.get(issue_type)

    def learn_from_resolution(self, error: str, solution: str, successful: bool):
        """Learn from successful problem resolutions."""
        if successful:
            # This would update the knowledge base
            # In a real implementation, this would persist to a database
            pass


# Integration with main system
class AdvancedAI:
    """Main class integrating all advanced AI features."""

    def __init__(self):
        self.planner = MultiStepPlanner()
        self.learning = LearningSystem()
        self.troubleshooter = AITroubleshooter()

    def process_complex_request(self, request: str) -> dict[str, Any]:
        """Process a complex request with all AI capabilities."""
        # Apply learning from past corrections
        improved_request = self.learning.apply_learning(request)
        if improved_request:
            request = improved_request

        # Create execution plan
        plan = self.planner.create_plan(request)

        # Validate plan
        valid, issues = self.planner.validate_plan(plan)

        return {
            "request": request,
            "improved": improved_request is not None,
            "plan": asdict(plan),
            "valid": valid,
            "issues": issues,
            "suggestions": self.learning.get_suggestions(request),
        }

    def handle_error(self, error: str) -> dict[str, Any]:
        """Handle an error with AI troubleshooting."""
        diagnosis = self.troubleshooter.diagnose(error)
        fix_command = self.troubleshooter.suggest_fix_command(diagnosis)

        return {"error": error, "diagnosis": diagnosis, "fix_command": fix_command}

    def record_feedback(self, query: str, response: str, correction: str):
        """Record user feedback for learning."""
        self.learning.record_correction(
            Correction(
                original_query=query,
                original_response=response,
                user_correction=correction,
                correct_response=correction,
                timestamp=datetime.now(),
                category="user_feedback",
            )
        )


# Example usage
def example_advanced_ai():
    """Example of advanced AI features."""
    ai = AdvancedAI()

    # Complex request with planning
    result = ai.process_complex_request(
        "Set up complete Python development environment with testing tools"
    )
    print(f"Execution plan: {json.dumps(result, indent=2)}")

    # Error troubleshooting
    error_result = ai.handle_error("Error: permission denied when running nix-env")
    print(f"Troubleshooting: {json.dumps(error_result, indent=2)}")

    # Learning from correction
    ai.record_feedback(
        query="install vscode",
        response="nix-env -iA nixpkgs.vscode",
        correction="nix-env -iA nixpkgs.vscode-fhs",
    )
