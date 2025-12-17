"""
Anticipatory Intelligence - AI That Thinks Ahead

Revolutionary capability: Predict what users will need next and offer
proactive help BEFORE they ask.

This transforms AI from reactive to genuinely intelligent.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    """Types of tasks users perform"""
    INSTALL = "install"
    CONFIGURE = "configure"
    DEBUG = "debug"
    LEARN = "learn"
    BUILD = "build"
    DEPLOY = "deploy"


class Domain(Enum):
    """Technical domains"""
    DATABASE = "database"
    WEB_SERVER = "web_server"
    PROGRAMMING = "programming"
    DEVOPS = "devops"
    SECURITY = "security"
    NETWORKING = "networking"


@dataclass
class NextStep:
    """Represents a predicted next step"""
    description: str
    rationale: str
    priority: int  # 1 = most likely, 2 = likely, 3 = possible
    action: str  # What the user should ask for
    auto_doable: bool  # Can we do this automatically?


@dataclass
class Anticipation:
    """AI's prediction of what user needs next"""
    context: str  # What user just did
    next_steps: List[NextStep]
    confidence: float  # 0.0-1.0
    domain: Domain


class AnticipatoryIntelligence:
    """
    Predicts what users will need next based on what they just did.

    Philosophy: The best AI anticipates needs before they're expressed.
    Don't just react - predict and proactively help.
    """

    def __init__(self):
        """Initialize with common workflow patterns"""

        # Database setup patterns
        self.database_workflows = {
            'postgresql': {
                'after_install': [
                    NextStep(
                        description="Create a database user",
                        rationale="You'll need users to access the database",
                        priority=1,
                        action="help me create a postgresql user",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Create your first database",
                        rationale="PostgreSQL is installed but no databases exist yet",
                        priority=1,
                        action="help me create a database",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Configure remote connections",
                        rationale="By default, PostgreSQL only accepts local connections",
                        priority=2,
                        action="help me configure postgresql for remote access",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Set up automatic backups",
                        rationale="Always backup your data!",
                        priority=2,
                        action="help me set up postgresql backups",
                        auto_doable=True
                    )
                ]
            },
            'mysql': {
                'after_install': [
                    NextStep(
                        description="Secure MySQL installation",
                        rationale="MySQL needs initial security setup",
                        priority=1,
                        action="help me secure mysql",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Create database and user",
                        rationale="You'll need a database and user to get started",
                        priority=1,
                        action="help me create mysql database",
                        auto_doable=True
                    )
                ]
            }
        }

        # Web server patterns
        self.webserver_workflows = {
            'nginx': {
                'after_install': [
                    NextStep(
                        description="Configure a virtual host",
                        rationale="Nginx is running but serving default page",
                        priority=1,
                        action="help me configure nginx virtual host",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Set up SSL/HTTPS",
                        rationale="Always use HTTPS in production",
                        priority=2,
                        action="help me set up nginx ssl",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Configure firewall",
                        rationale="You'll need to allow HTTP/HTTPS traffic",
                        priority=1,
                        action="help me configure firewall for nginx",
                        auto_doable=True
                    )
                ]
            },
            'apache': {
                'after_install': [
                    NextStep(
                        description="Enable common modules",
                        rationale="Apache needs modules for most functionality",
                        priority=1,
                        action="help me enable apache modules",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Configure virtual hosts",
                        rationale="Set up your first website",
                        priority=1,
                        action="help me set up apache virtual host",
                        auto_doable=True
                    )
                ]
            }
        }

        # Development environment patterns
        self.dev_workflows = {
            'python': {
                'after_install': [
                    NextStep(
                        description="Set up a development environment",
                        rationale="Python projects need isolated environments",
                        priority=1,
                        action="help me create python dev environment",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Install pip packages",
                        rationale="You'll need libraries for your project",
                        priority=2,
                        action="help me manage python packages",
                        auto_doable=False
                    ),
                    NextStep(
                        description="Set up VSCode/editor",
                        rationale="Proper editor setup improves productivity",
                        priority=3,
                        action="help me set up python editor",
                        auto_doable=True
                    )
                ]
            },
            'nodejs': {
                'after_install': [
                    NextStep(
                        description="Initialize a Node project",
                        rationale="Create package.json and project structure",
                        priority=1,
                        action="help me start a node project",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Install common dependencies",
                        rationale="Most projects need express, etc.",
                        priority=2,
                        action="help me with node dependencies",
                        auto_doable=False
                    )
                ]
            }
        }

        # DevOps patterns
        self.devops_workflows = {
            'docker': {
                'after_install': [
                    NextStep(
                        description="Pull common images",
                        rationale="Get started with popular containers",
                        priority=1,
                        action="help me with docker images",
                        auto_doable=False
                    ),
                    NextStep(
                        description="Create a Dockerfile",
                        rationale="Containerize your application",
                        priority=2,
                        action="help me create a dockerfile",
                        auto_doable=True
                    ),
                    NextStep(
                        description="Set up docker-compose",
                        rationale="Manage multi-container apps easily",
                        priority=2,
                        action="help me with docker compose",
                        auto_doable=True
                    )
                ]
            }
        }

    def anticipate_next_steps(self, user_query: str, action_taken: str) -> Optional[Anticipation]:
        """
        Predict what user will need next based on their query and action.

        Args:
            user_query: What the user asked
            action_taken: What we just did for them

        Returns:
            Anticipation with predicted next steps, or None
        """
        query_lower = user_query.lower()

        # Detect what was just done
        detection = self._detect_action_type(query_lower, action_taken)

        if not detection:
            return None

        action_type, tool, domain = detection

        # Get relevant workflow
        next_steps = self._get_workflow_next_steps(action_type, tool, domain)

        if not next_steps:
            return None

        # Build anticipation
        return Anticipation(
            context=f"You just {action_taken}",
            next_steps=next_steps[:3],  # Top 3 most relevant
            confidence=0.8,  # High confidence for known patterns
            domain=domain
        )

    def _detect_action_type(self, query: str, action: str) -> Optional[Tuple[TaskType, str, Domain]]:
        """
        Detect what type of action was just performed.

        Returns:
            (TaskType, tool_name, Domain) or None
        """
        # Database installs
        if 'postgresql' in query or 'postgres' in query:
            if 'install' in query or 'setup' in query:
                return (TaskType.INSTALL, 'postgresql', Domain.DATABASE)

        if 'mysql' in query or 'mariadb' in query:
            if 'install' in query or 'setup' in query:
                return (TaskType.INSTALL, 'mysql', Domain.DATABASE)

        # Web servers
        if 'nginx' in query:
            if 'install' in query or 'setup' in query:
                return (TaskType.INSTALL, 'nginx', Domain.WEB_SERVER)

        if 'apache' in query:
            if 'install' in query or 'setup' in query:
                return (TaskType.INSTALL, 'apache', Domain.WEB_SERVER)

        # Programming languages
        if 'python' in query:
            if 'install' in query or 'setup' in query or 'get' in query:
                return (TaskType.INSTALL, 'python', Domain.PROGRAMMING)

        if 'node' in query or 'nodejs' in query:
            if 'install' in query or 'setup' in query:
                return (TaskType.INSTALL, 'nodejs', Domain.PROGRAMMING)

        # DevOps tools
        if 'docker' in query:
            if 'install' in query or 'setup' in query:
                return (TaskType.INSTALL, 'docker', Domain.DEVOPS)

        return None

    def _get_workflow_next_steps(self, action_type: TaskType, tool: str, domain: Domain) -> List[NextStep]:
        """Get predicted next steps for a workflow"""

        if action_type != TaskType.INSTALL:
            return []

        # Look up workflow based on domain and tool
        if domain == Domain.DATABASE:
            workflow = self.database_workflows.get(tool)
            if workflow:
                return workflow.get('after_install', [])

        elif domain == Domain.WEB_SERVER:
            workflow = self.webserver_workflows.get(tool)
            if workflow:
                return workflow.get('after_install', [])

        elif domain == Domain.PROGRAMMING:
            workflow = self.dev_workflows.get(tool)
            if workflow:
                return workflow.get('after_install', [])

        elif domain == Domain.DEVOPS:
            workflow = self.devops_workflows.get(tool)
            if workflow:
                return workflow.get('after_install', [])

        return []

    def format_anticipation(self, anticipation: Anticipation) -> str:
        """
        Format anticipation as a user-friendly message.

        Args:
            anticipation: The predicted next steps

        Returns:
            Formatted string to show user
        """
        if not anticipation.next_steps:
            return ""

        message = f"\n💡 **I noticed you just {anticipation.context.lower()}.**\n\n"
        message += "Here's what you'll probably want next:\n\n"

        for i, step in enumerate(anticipation.next_steps, 1):
            message += f"{i}. **{step.description}**\n"
            message += f"   ↳ {step.rationale}\n"

            if step.auto_doable:
                message += f"   💬 Just say: \"{step.action}\"\n"

            message += "\n"

        message += "Or ask me anything else! I'm here to help. 😊"

        return message


def get_anticipatory_intelligence() -> AnticipatoryIntelligence:
    """Get singleton instance of anticipatory intelligence"""
    global _anticipatory_intelligence

    if _anticipatory_intelligence is None:
        _anticipatory_intelligence = AnticipatoryIntelligence()

    return _anticipatory_intelligence


# Singleton
_anticipatory_intelligence: Optional[AnticipatoryIntelligence] = None
