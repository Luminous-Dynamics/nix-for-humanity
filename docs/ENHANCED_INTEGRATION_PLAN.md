# 🚀 Enhanced Conversational AI Integration Plan

**Date**: December 3, 2025
**Approach**: Option A + Complete Context Awareness + Model Testing
**Timeline**: 2-4 hours for POC, then iterative enhancement

---

## 🎯 Enhanced Requirements

### Core Requirements (from audit):
- ✅ Multi-turn conversations
- ✅ User skill adaptation
- ✅ Unified chat interface

### NEW Requirements (from user):
1. **Comprehensive Model Testing**
   - Test all existing trained models
   - Benchmark accuracy on diverse queries
   - Identify gaps → train specialized models

2. **Complete System Context Awareness**
   - System information (hardware, packages, services)
   - User information (skill level, preferences, history)
   - Screen capture capability (see what user sees)
   - Configuration state (current config.nix, hardware-configuration.nix)
   - Generation history (rollback points)

3. **Flake-First Recommendations**
   - AI should recommend flakes as default approach
   - Guide users toward modern Nix practices
   - Explain benefits of flakes over channels

---

## 🏗️ Architecture Enhancement

### Complete Context System

```
┌─────────────────────────────────────────────────────┐
│                   User Query                         │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  Context Gatherer      │
         │  - System Info         │
         │  - User State          │
         │  - Screen Capture      │
         │  - Config Files        │
         │  - History             │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │  AI Orchestrator       │
         │  + Full Context        │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼───┐      ┌────▼────┐     ┌────▼────┐
│ HRM   │      │Gemma3+  │     │ Ollama  │
│       │      │  HRM    │     │         │
└───┬───┘      └────┬────┘     └────┬────┘
    │               │               │
    └───────────────┼───────────────┘
                    │
         ┌──────────▼──────────┐
         │  Smart Response      │
         │  - Context-aware     │
         │  - Flake-first       │
         │  - Skill-adaptive    │
         └─────────────────────┘
```

---

## 📋 Implementation Plan

### Phase 1A: Proof of Concept (TODAY - 2-4 hours) 🔥

#### Step 1: Create Basic Context Gatherer (30 min)

**File**: `src/luminous_nix/ai/context/system_context.py`

```python
"""
System Context Gatherer - Provides AI with complete understanding
"""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class SystemContext:
    """Complete system context for AI"""
    # Hardware info
    hostname: str
    cpu_info: str
    memory_total: str
    disk_usage: Dict[str, Any]

    # NixOS info
    nixos_version: str
    current_generation: int
    channel_or_flake: str  # "channels" or "flakes"

    # Configuration
    has_configuration_nix: bool
    has_flake_nix: bool
    configuration_path: Optional[Path]

    # Installed packages
    installed_packages: List[str]

    # Current state
    running_services: List[str]
    failed_services: List[str]

    def to_context_string(self) -> str:
        """Convert to natural language context for AI"""
        context = f"""
System Context:
- Hostname: {self.hostname}
- NixOS: {self.nixos_version}
- Generation: {self.current_generation}
- Using: {self.channel_or_flake}
- Configuration: {'flake.nix' if self.has_flake_nix else 'configuration.nix'}

Hardware:
- CPU: {self.cpu_info}
- RAM: {self.memory_total}
- Disk: {self.disk_usage}

Status:
- {len(self.installed_packages)} packages installed
- {len(self.running_services)} services running
- {len(self.failed_services)} failed services
"""
        return context


class SystemContextGatherer:
    """Gathers comprehensive system information"""

    def gather(self) -> SystemContext:
        """Gather all system context"""
        return SystemContext(
            hostname=self._get_hostname(),
            cpu_info=self._get_cpu_info(),
            memory_total=self._get_memory(),
            disk_usage=self._get_disk_usage(),
            nixos_version=self._get_nixos_version(),
            current_generation=self._get_current_generation(),
            channel_or_flake=self._detect_config_type(),
            has_configuration_nix=Path("/etc/nixos/configuration.nix").exists(),
            has_flake_nix=Path("/etc/nixos/flake.nix").exists(),
            configuration_path=self._find_config_path(),
            installed_packages=self._get_installed_packages(),
            running_services=self._get_running_services(),
            failed_services=self._get_failed_services()
        )

    def _get_hostname(self) -> str:
        return subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip()

    def _get_cpu_info(self) -> str:
        try:
            result = subprocess.run(['lscpu'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'Model name:' in line:
                    return line.split(':')[1].strip()
        except:
            pass
        return "Unknown"

    def _get_memory(self) -> str:
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                mem_line = lines[1].split()
                return mem_line[1]  # Total memory
        except:
            pass
        return "Unknown"

    def _get_disk_usage(self) -> Dict[str, Any]:
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                return {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "percent": parts[4]
                }
        except:
            pass
        return {}

    def _get_nixos_version(self) -> str:
        try:
            result = subprocess.run(['nixos-version'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "Unknown"

    def _get_current_generation(self) -> int:
        try:
            result = subprocess.run(
                ['nix-env', '--list-generations', '-p', '/nix/var/nix/profiles/system'],
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                if '(current)' in line:
                    return int(line.split()[0])
        except:
            pass
        return 0

    def _detect_config_type(self) -> str:
        """Detect if system uses flakes or channels"""
        if Path("/etc/nixos/flake.nix").exists():
            return "flakes"
        return "channels"

    def _find_config_path(self) -> Optional[Path]:
        """Find the main configuration file"""
        if Path("/etc/nixos/flake.nix").exists():
            return Path("/etc/nixos/flake.nix")
        if Path("/etc/nixos/configuration.nix").exists():
            return Path("/etc/nixos/configuration.nix")
        return None

    def _get_installed_packages(self) -> List[str]:
        """Get list of installed packages (first 50 for context)"""
        try:
            result = subprocess.run(
                ['nix-env', '-q'],
                capture_output=True, text=True
            )
            packages = result.stdout.strip().split('\n')
            return packages[:50]  # Limit for context
        except:
            return []

    def _get_running_services(self) -> List[str]:
        """Get running systemd services"""
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager'],
                capture_output=True, text=True
            )
            lines = result.stdout.split('\n')[1:]  # Skip header
            services = []
            for line in lines[:20]:  # First 20 services
                if '.service' in line:
                    service = line.split()[0]
                    services.append(service)
            return services
        except:
            return []

    def _get_failed_services(self) -> List[str]:
        """Get failed systemd services"""
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--state=failed', '--no-pager'],
                capture_output=True, text=True
            )
            lines = result.stdout.split('\n')[1:]
            services = []
            for line in lines:
                if '.service' in line:
                    service = line.split()[0]
                    services.append(service)
            return services
        except:
            return []
```

#### Step 2: Create User Context Manager (20 min)

**File**: `src/luminous_nix/ai/context/user_context.py`

```python
"""
User Context Manager - Tracks user skill level, preferences, history
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from enum import Enum

class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class UserContext:
    """User profile and preferences"""
    skill_level: SkillLevel
    prefers_flakes: bool
    command_history: List[str]
    successful_actions: int
    failed_actions: int
    preferences: Dict[str, Any]

    def to_context_string(self) -> str:
        """Convert to natural language for AI"""
        context = f"""
User Profile:
- Skill Level: {self.skill_level.value}
- Prefers: {'Flakes' if self.prefers_flakes else 'Traditional Nix'}
- Success Rate: {self._calculate_success_rate():.1%}
- Commands Used: {len(self.command_history)}
"""
        return context

    def _calculate_success_rate(self) -> float:
        total = self.successful_actions + self.failed_actions
        if total == 0:
            return 0.0
        return self.successful_actions / total


class UserContextManager:
    """Manages user profile and context"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "luminous-nix"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.profile_path = self.config_dir / "user_profile.json"
        self.context = self._load_or_create_profile()

    def _load_or_create_profile(self) -> UserContext:
        """Load existing profile or create new one"""
        if self.profile_path.exists():
            try:
                with open(self.profile_path) as f:
                    data = json.load(f)
                    return UserContext(
                        skill_level=SkillLevel(data.get('skill_level', 'beginner')),
                        prefers_flakes=data.get('prefers_flakes', True),
                        command_history=data.get('command_history', []),
                        successful_actions=data.get('successful_actions', 0),
                        failed_actions=data.get('failed_actions', 0),
                        preferences=data.get('preferences', {})
                    )
            except Exception as e:
                print(f"Warning: Could not load profile: {e}")

        # Create new profile with smart defaults
        return UserContext(
            skill_level=SkillLevel.BEGINNER,
            prefers_flakes=True,  # Recommend flakes by default!
            command_history=[],
            successful_actions=0,
            failed_actions=0,
            preferences={}
        )

    def save(self):
        """Persist profile to disk"""
        data = {
            'skill_level': self.context.skill_level.value,
            'prefers_flakes': self.context.prefers_flakes,
            'command_history': self.context.command_history[-100:],  # Keep last 100
            'successful_actions': self.context.successful_actions,
            'failed_actions': self.context.failed_actions,
            'preferences': self.context.preferences
        }
        with open(self.profile_path, 'w') as f:
            json.dump(data, f, indent=2)

    def record_command(self, command: str):
        """Record a command in history"""
        self.context.command_history.append(command)
        self.save()

    def record_success(self):
        """Record a successful action"""
        self.context.successful_actions += 1
        self._update_skill_level()
        self.save()

    def record_failure(self):
        """Record a failed action"""
        self.context.failed_actions += 1
        self.save()

    def _update_skill_level(self):
        """Automatically detect skill level based on usage"""
        total = self.context.successful_actions + self.context.failed_actions

        if total < 10:
            self.context.skill_level = SkillLevel.BEGINNER
        elif total < 50:
            success_rate = self.context.successful_actions / total
            if success_rate > 0.8:
                self.context.skill_level = SkillLevel.INTERMEDIATE
        elif total < 200:
            success_rate = self.context.successful_actions / total
            if success_rate > 0.85:
                self.context.skill_level = SkillLevel.ADVANCED
        else:
            success_rate = self.context.successful_actions / total
            if success_rate > 0.9:
                self.context.skill_level = SkillLevel.EXPERT

    def get_context(self) -> UserContext:
        """Get current user context"""
        return self.context
```

#### Step 3: Create Simple Chat with Full Context (45 min)

**File**: `src/luminous_nix/ai/conversation/simple_chat.py`

```python
"""
Simple Conversational AI - Proof of Concept
Integrates all existing AI components with full context awareness
"""

import sys
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Import our AI components
from ..orchestrator import AIOrchestrator
from ..error_resolver import ErrorResolver
from ..config_generator import AIConfigGenerator
from ..package_recommender import PackageRecommender
from ..command_explainer import CommandExplainer

# Import context managers
from ..context.system_context import SystemContextGatherer
from ..context.user_context import UserContextManager, SkillLevel

console = Console()


class FlakeRecommender:
    """Recommends flakes and explains benefits"""

    def should_recommend_flake(self, query: str, user_context, system_context) -> bool:
        """Determine if we should recommend flakes"""
        # If user already uses flakes, no need to recommend
        if system_context.has_flake_nix:
            return False

        # Recommend flakes for:
        # - Dev environments
        # - New projects
        # - Modern setup requests
        flake_triggers = [
            'dev environment', 'development', 'project setup',
            'new project', 'create', 'setup', 'configure'
        ]

        return any(trigger in query.lower() for trigger in flake_triggers)

    def get_flake_recommendation(self, query: str, skill_level: SkillLevel) -> str:
        """Get flake recommendation based on skill level"""
        if skill_level == SkillLevel.BEGINNER:
            return """
💡 **Flake Recommendation**: I notice you're not using flakes yet.
Flakes are the modern way to manage NixOS configurations with these benefits:
- Reproducible: Lock exact versions of all dependencies
- Portable: Share configs easily with others
- Faster: Better caching and evaluation
- Cleaner: Self-contained, no channel management

Would you like me to help you migrate to flakes?
"""
        elif skill_level == SkillLevel.INTERMEDIATE:
            return """
💡 **Tip**: Consider using flakes for this! Flakes provide:
- Reproducible builds with flake.lock
- Better dev environments with nix develop
- Easier sharing and composition
- Modern Nix CLI (nix build, nix run, etc.)

I can generate a flake.nix for you. Interested?
"""
        else:  # Advanced/Expert
            return """
💡 Flakes would be ideal here - `flake.nix` with inputs/outputs, locked deps, and `nix develop` support. Want a template?
"""


class SimpleChat:
    """
    Simple conversational AI that ties everything together.

    Features:
    - Full context awareness (system + user)
    - Multi-turn conversation memory
    - Flake-first recommendations
    - Skill-adaptive responses
    - All existing AI features integrated
    """

    def __init__(self):
        console.print("[bold cyan]🚀 Initializing Luminous Nix AI...[/bold cyan]")

        # Initialize context gatherers
        self.system_context = SystemContextGatherer().gather()
        self.user_manager = UserContextManager()
        self.user_context = self.user_manager.get_context()

        # Initialize AI components
        self.orchestrator = AIOrchestrator()
        self.error_resolver = ErrorResolver()
        self.config_gen = AIConfigGenerator()
        self.recommender = PackageRecommender()
        self.explainer = CommandExplainer()
        self.flake_recommender = FlakeRecommender()

        # Conversation history (for multi-turn context)
        self.history: List[Dict[str, str]] = []

        console.print("[green]✅ AI System Ready[/green]\n")

    def chat_loop(self):
        """Main interactive chat loop"""
        # Show welcome message with context
        self._show_welcome()

        while True:
            try:
                # Get user input
                user_input = console.input("[bold green]You:[/bold green] ").strip()

                if not user_input:
                    continue

                # Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    console.print("\n[bold cyan]AI:[/bold cyan] Happy hacking! 🌊\n")
                    break

                # Handle special commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue

                # Record command
                self.user_manager.record_command(user_input)

                # Add to history
                self.history.append({"role": "user", "content": user_input})

                # Process query with full context
                response = self._handle_query(user_input)

                # Display response
                console.print(f"\n[bold cyan]AI:[/bold cyan] {response}\n")

                # Add response to history
                self.history.append({"role": "assistant", "content": response})

                # Record success (for now, we'll add failure detection later)
                self.user_manager.record_success()

            except KeyboardInterrupt:
                console.print("\n\n[bold cyan]AI:[/bold cyan] Happy hacking! 🌊\n")
                break
            except Exception as e:
                console.print(f"\n[bold red]Error:[/bold red] {e}\n")
                self.user_manager.record_failure()

    def _show_welcome(self):
        """Show welcome message with system context"""
        welcome = f"""
[bold cyan]🤖 Luminous Nix AI Assistant[/bold cyan]

[dim]System: {self.system_context.nixos_version} | Using: {self.system_context.channel_or_flake}[/dim]
[dim]Skill Level: {self.user_context.skill_level.value}[/dim]

I have complete understanding of your system and I'm here to help!

[bold]What I can do:[/bold]
- Resolve errors and explain problems
- Generate NixOS configurations
- Recommend packages and alternatives
- Explain commands and concepts
- Guide you through NixOS tasks

[dim]Type 'exit' to quit, '/help' for commands[/dim]
"""
        console.print(Panel(welcome, border_style="cyan"))

    def _handle_command(self, command: str):
        """Handle special /commands"""
        if command == '/help':
            help_text = """
**Available Commands:**
- `/help` - Show this help
- `/context` - Show system & user context
- `/clear` - Clear conversation history
- `/skill [level]` - Set skill level (beginner/intermediate/advanced/expert)
- `/flakes on|off` - Toggle flake preference
- `/history` - Show conversation history
- `exit` - Exit chat
"""
            console.print(Markdown(help_text))

        elif command == '/context':
            context_info = f"""
**System Context:**
{self.system_context.to_context_string()}

**User Context:**
{self.user_context.to_context_string()}
"""
            console.print(Markdown(context_info))

        elif command == '/clear':
            self.history = []
            console.print("[green]✅ Conversation history cleared[/green]")

        elif command.startswith('/skill'):
            parts = command.split()
            if len(parts) > 1:
                level = parts[1].lower()
                if level in ['beginner', 'intermediate', 'advanced', 'expert']:
                    self.user_context.skill_level = SkillLevel(level)
                    self.user_manager.save()
                    console.print(f"[green]✅ Skill level set to: {level}[/green]")
                else:
                    console.print("[red]Invalid skill level. Use: beginner, intermediate, advanced, or expert[/red]")

        elif command.startswith('/flakes'):
            parts = command.split()
            if len(parts) > 1:
                preference = parts[1].lower()
                if preference == 'on':
                    self.user_context.prefers_flakes = True
                    self.user_manager.save()
                    console.print("[green]✅ Flake recommendations enabled[/green]")
                elif preference == 'off':
                    self.user_context.prefers_flakes = False
                    self.user_manager.save()
                    console.print("[yellow]Flake recommendations disabled[/yellow]")

        elif command == '/history':
            console.print("\n[bold]Conversation History:[/bold]")
            for msg in self.history:
                role = msg['role'].title()
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                console.print(f"[cyan]{role}:[/cyan] {content}")

    def _handle_query(self, query: str) -> str:
        """
        Route query to appropriate AI component with full context.
        This is where all the magic happens!
        """

        # Check if we should recommend flakes
        if self.user_context.prefers_flakes:
            if self.flake_recommender.should_recommend_flake(
                query, self.user_context, self.system_context
            ):
                flake_rec = self.flake_recommender.get_flake_recommendation(
                    query, self.user_context.skill_level
                )
                # We'll append this to the response
        else:
            flake_rec = None

        # Route to appropriate handler based on query patterns

        # 1. Error Resolution
        if any(word in query.lower() for word in ['error', 'failed', 'broken', 'issue']):
            response = self._resolve_error(query)

        # 2. Configuration Generation
        elif any(word in query.lower() for word in ['setup', 'configure', 'create', 'generate', 'enable']):
            response = self._generate_config(query)

        # 3. Package Recommendations
        elif any(word in query.lower() for word in ['recommend', 'alternative', 'similar', 'suggest', 'find']):
            response = self._recommend_packages(query)

        # 4. Command Explanation
        elif any(word in query.lower() for word in ['what does', 'explain', 'how does', 'what is']):
            response = self._explain_command(query)

        # 5. General query - use orchestrator with full context
        else:
            response = self._general_query(query)

        # Add flake recommendation if applicable
        if flake_rec:
            response = f"{response}\n\n{flake_rec}"

        return response

    def _resolve_error(self, query: str) -> str:
        """Resolve error with context awareness"""
        result = self.error_resolver.resolve(query)

        # Adapt response based on skill level
        if self.user_context.skill_level == SkillLevel.BEGINNER:
            # Add extra explanation for beginners
            result = f"📍 **Error Analysis**\n\n{result}\n\n💡 **Tip**: I can walk you through this step-by-step. Just ask!"

        return result

    def _generate_config(self, query: str) -> str:
        """Generate configuration with flake preference"""
        # Check if user prefers flakes
        if self.user_context.prefers_flakes and not self.system_context.has_flake_nix:
            # Generate flake-based config
            return self._generate_flake_config(query)
        else:
            # Use existing config generator
            return self.config_gen.generate(query)

    def _generate_flake_config(self, query: str) -> str:
        """Generate flake-based configuration"""
        # This would call a flake-specific config generator
        # For now, we'll add a note about flakes
        traditional_config = self.config_gen.generate(query)

        flake_note = """

💡 **Flake Version**: To use this with flakes, I can generate a `flake.nix` instead.
This would give you reproducible builds and better dependency management. Would you like that?
"""

        return traditional_config + flake_note

    def _recommend_packages(self, query: str) -> str:
        """Recommend packages"""
        return self.recommender.recommend(query)

    def _explain_command(self, query: str) -> str:
        """Explain command"""
        return self.explainer.explain(query)

    def _general_query(self, query: str) -> str:
        """Handle general query with orchestrator"""
        # Build context string for AI
        context = f"""
{self.system_context.to_context_string()}
{self.user_context.to_context_string()}

Recent conversation:
{self._format_recent_history()}
"""

        # Call orchestrator with context
        try:
            result = self.orchestrator.process_query(query, context=context)
            return result.response
        except Exception as e:
            return f"I encountered an issue processing your query: {e}\n\nCould you rephrase that?"

    def _format_recent_history(self, n=3) -> str:
        """Format recent conversation history"""
        if not self.history:
            return "(No previous conversation)"

        recent = self.history[-n:]
        formatted = []
        for msg in recent:
            role = msg['role'].title()
            content = msg['content'][:200]  # Truncate long messages
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)


# Entry point
def main():
    """Main entry point for chat mode"""
    chat = SimpleChat()
    chat.chat_loop()


if __name__ == "__main__":
    main()
```

#### Step 4: Add CLI Command (10 min)

**File**: `src/luminous_nix/cli/chat_command.py`

```python
"""
Chat command - Interactive AI assistant
"""

import click
from ..ai.conversation.simple_chat import SimpleChat


@click.command()
def chat():
    """
    Start an interactive chat session with the Luminous Nix AI assistant.

    The AI has complete context awareness including:
    - Your NixOS configuration and system state
    - Your skill level and preferences
    - Conversation history
    - System information

    Use natural language to:
    - Ask questions
    - Get help with errors
    - Generate configurations
    - Find packages
    - Learn NixOS concepts

    Special commands:
    - /help - Show available commands
    - /context - View system and user context
    - /skill [level] - Set your skill level
    - exit - Quit chat mode
    """
    chat = SimpleChat()
    chat.chat_loop()


if __name__ == '__main__':
    chat()
```

#### Step 5: Integrate with Main CLI (10 min)

Add to `src/luminous_nix/cli/main.py`:

```python
from .chat_command import chat

# In your CLI group:
cli.add_command(chat)
```

#### Step 6: Test (30 min)

```bash
# Test the POC
cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix
poetry install

# Run chat
poetry run ask-nix chat

# Test various scenarios:
# 1. Error resolution: "error: attribute 'vim' missing"
# 2. Config generation: "setup nginx with SSL"
# 3. Package search: "recommend text editors"
# 4. Command explanation: "what does nixos-rebuild switch do"
# 5. Multi-turn: "install firefox" then "what else do I need for web browsing?"
# 6. Context awareness: "/context" to see what AI knows
```

---

### Phase 1B: Model Testing Framework (NEXT - 1-2 hours)

#### Create Comprehensive Model Tester

**File**: `tests/ai/test_model_comprehensive.py`

```python
"""
Comprehensive HRM Model Testing Suite
Tests all trained models across diverse query types
"""

import pytest
import time
from pathlib import Path
from typing import List, Dict, Tuple

# Model paths
MODEL_DIR = Path(__file__).parent.parent.parent / "models"

MODELS_TO_TEST = [
    MODEL_DIR / "hrm_neural_best.pt",
    MODEL_DIR / "hrm_neural_demo.pt",
    MODEL_DIR / "hrm_simple_best.pt",
    # Add more as we discover them
]

# Test query categories
TEST_QUERIES = {
    "package_management": [
        "install firefox",
        "remove vim",
        "update my system",
        "search for text editor",
        "upgrade all packages"
    ],
    "configuration": [
        "setup nginx web server",
        "configure postgresql database",
        "enable docker service",
        "create systemd service for my app",
        "configure firewall rules"
    ],
    "errors": [
        "error: attribute 'neovim' missing",
        "collision between firefox packages",
        "build failed out of memory",
        "permission denied /etc/nixos",
        "command not found: nix-shell"
    ],
    "flakes": [
        "create a flake for python project",
        "migrate to flakes",
        "update flake inputs",
        "generate flake.nix",
        "use flake for dev environment"
    ],
    "system_management": [
        "check system health",
        "find safe rollback point",
        "optimize disk space",
        "audit security vulnerabilities",
        "list all generations"
    ],
    "development": [
        "setup rust development environment",
        "create python shell with poetry",
        "configure nodejs project",
        "install docker for development",
        "setup vscode with nix"
    ]
}

class ModelTester:
    """Test harness for HRM models"""

    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.model_name = model_path.stem
        # Load model (implementation depends on your HRM loading code)
        # self.model = load_hrm_model(model_path)

    def test_query(self, query: str) -> Tuple[str, float, float]:
        """
        Test a single query.
        Returns: (predicted_intent, confidence, response_time_ms)
        """
        start = time.time()
        # result = self.model.predict(query)
        elapsed = (time.time() - start) * 1000

        # For now, return dummy data
        # Replace with actual model prediction
        return ("install", 0.95, elapsed)

    def test_category(self, category: str, queries: List[str]) -> Dict:
        """Test all queries in a category"""
        results = []
        for query in queries:
            intent, confidence, response_time = self.test_query(query)
            results.append({
                "query": query,
                "intent": intent,
                "confidence": confidence,
                "response_time_ms": response_time
            })

        # Calculate category statistics
        avg_confidence = sum(r["confidence"] for r in results) / len(results)
        avg_response_time = sum(r["response_time_ms"] for r in results) / len(results)

        return {
            "category": category,
            "results": results,
            "avg_confidence": avg_confidence,
            "avg_response_time_ms": avg_response_time,
            "num_queries": len(results)
        }

    def test_all(self) -> Dict:
        """Test model across all categories"""
        model_results = {
            "model": self.model_name,
            "categories": {}
        }

        for category, queries in TEST_QUERIES.items():
            category_results = self.test_category(category, queries)
            model_results["categories"][category] = category_results

        # Calculate overall statistics
        all_confidences = []
        all_response_times = []
        for cat_results in model_results["categories"].values():
            for result in cat_results["results"]:
                all_confidences.append(result["confidence"])
                all_response_times.append(result["response_time_ms"])

        model_results["overall"] = {
            "avg_confidence": sum(all_confidences) / len(all_confidences),
            "avg_response_time_ms": sum(all_response_times) / len(all_response_times),
            "total_queries": len(all_confidences)
        }

        return model_results


def test_all_models():
    """Test all available models"""
    results = []

    for model_path in MODELS_TO_TEST:
        if not model_path.exists():
            print(f"⚠️  Model not found: {model_path}")
            continue

        print(f"\n🧪 Testing model: {model_path.name}")
        tester = ModelTester(model_path)
        model_results = tester.test_all()
        results.append(model_results)

        # Print summary
        overall = model_results["overall"]
        print(f"   Confidence: {overall['avg_confidence']:.2%}")
        print(f"   Response Time: {overall['avg_response_time_ms']:.2f}ms")
        print(f"   Queries Tested: {overall['total_queries']}")

    return results


def identify_gaps(results: List[Dict]) -> Dict:
    """Identify areas where models perform poorly"""
    gaps = {
        "low_confidence_categories": [],
        "slow_categories": [],
        "missing_capabilities": []
    }

    for model_result in results:
        for category, cat_results in model_result["categories"].items():
            # Check for low confidence
            if cat_results["avg_confidence"] < 0.80:
                gaps["low_confidence_categories"].append({
                    "model": model_result["model"],
                    "category": category,
                    "confidence": cat_results["avg_confidence"]
                })

            # Check for slow response
            if cat_results["avg_response_time_ms"] > 100:
                gaps["slow_categories"].append({
                    "model": model_result["model"],
                    "category": category,
                    "response_time": cat_results["avg_response_time_ms"]
                })

    return gaps


def recommend_new_models(gaps: Dict) -> List[str]:
    """Recommend specialized models to train based on gaps"""
    recommendations = []

    # Group by category
    weak_categories = {}
    for gap in gaps["low_confidence_categories"]:
        category = gap["category"]
        if category not in weak_categories:
            weak_categories[category] = []
        weak_categories[category].append(gap)

    # Recommend specialized models
    for category, gap_list in weak_categories.items():
        if len(gap_list) >= 2:  # Multiple models struggle
            recommendations.append(f"hrm_{category}_specialist")

    return recommendations


if __name__ == "__main__":
    print("🧪 Starting Comprehensive Model Testing\n")
    print("=" * 60)

    # Test all models
    results = test_all_models()

    # Identify gaps
    print("\n" + "=" * 60)
    print("📊 Gap Analysis")
    gaps = identify_gaps(results)

    if gaps["low_confidence_categories"]:
        print("\n⚠️  Low Confidence Areas:")
        for gap in gaps["low_confidence_categories"]:
            print(f"   {gap['model']} - {gap['category']}: {gap['confidence']:.2%}")

    # Recommend new models
    print("\n" + "=" * 60)
    print("💡 Recommended Specialized Models:")
    recommendations = recommend_new_models(gaps)
    for rec in recommendations:
        print(f"   - {rec}")

    if not recommendations:
        print("   ✅ No gaps detected - existing models cover all areas well!")
```

---

### Phase 1C: Screen Capture Integration (FUTURE)

**Note**: Screen capture added to roadmap but not implemented in POC.

**Future Implementation**:
- Use `pyautogui.screenshot()` or similar
- OCR for text extraction (`pytesseract`)
- Allow AI to "see" what user sees
- Useful for debugging visual issues

---

## 📊 Testing Plan

### Model Testing (Phase 1B)

1. **Run comprehensive tests**:
   ```bash
   pytest tests/ai/test_model_comprehensive.py -v
   ```

2. **Analyze results**:
   - Identify low-confidence categories
   - Find slow response areas
   - Detect missing capabilities

3. **Train specialized models** (if gaps found):
   ```bash
   python src/luminous_nix/ai/train_hrm_nixos.py \
     --category flakes \
     --output models/hrm_flakes_specialist.pt
   ```

### Integration Testing (Phase 1A)

1. **Test context gathering**:
   - Verify system info collected correctly
   - Check user profile persists
   - Confirm flake detection works

2. **Test conversation flow**:
   - Multi-turn conversations maintain context
   - References resolved correctly ("it", "that")
   - History tracked properly

3. **Test skill adaptation**:
   - Beginner gets detailed explanations
   - Expert gets concise responses
   - Automatic skill level detection works

4. **Test flake recommendations**:
   - Recommends flakes for dev envs
   - Explains benefits appropriately
   - Respects user preference

---

## 🎯 Success Criteria

### POC Success (Today):
- [ ] Chat mode launches and runs
- [ ] System context gathered correctly
- [ ] User profile created and persists
- [ ] AI responds to queries
- [ ] Flake recommendations appear
- [ ] Conversation history works
- [ ] Special commands work (/help, /context, etc.)

### Model Testing Success:
- [ ] All trained models tested
- [ ] Performance metrics collected
- [ ] Gaps identified
- [ ] Recommendations for specialized models

### Integration Success (Ongoing):
- [ ] Multi-turn conversations feel natural
- [ ] Context maintained across turns
- [ ] Skill adaptation works
- [ ] Flake-first approach evident
- [ ] Users report positive experience

---

## 📝 Next Steps After POC

1. **Refine based on testing** (1-2 days)
   - Fix bugs found during POC testing
   - Improve context gathering
   - Enhance response quality

2. **Train specialized models** (as needed)
   - Focus on gaps identified in testing
   - E.g., `hrm_flakes_specialist.pt` if flake queries underperform

3. **Add advanced features** (1-2 weeks)
   - Screen capture integration
   - Proactive monitoring
   - Learning from feedback

4. **Documentation** (1 week)
   - User guide for chat mode
   - Developer guide for extending
   - Model training guide

---

*Enhanced Integration Plan - December 3, 2025*
*Let's build the best FOSS AI for NixOS!* 🚀
