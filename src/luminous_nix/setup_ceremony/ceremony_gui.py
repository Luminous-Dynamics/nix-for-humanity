#!/usr/bin/env python3
"""
🎨 Luminous Setup Ceremony - Beautiful GUI Interface
Progressive, intelligent, consciousness-first setup experience
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, Label, Checkbox, ProgressBar
from textual.widgets import Input, RadioButton, RadioSet, ListView, ListItem
from textual.reactive import reactive
from textual.message import Message
from textual import events
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

from .profile_system import (
    SetupCeremony, ProfileManager, PackageIntelligence,
    UserProfile, ProfileType
)


class ProfileCard(Static):
    """Beautiful profile selection card"""
    
    def __init__(self, profile: UserProfile, selected: bool = False):
        super().__init__()
        self.profile = profile
        self.selected = selected
        
    def render(self) -> RenderableType:
        """Render a beautiful profile card"""
        style = "bold cyan" if self.selected else "dim"
        
        content = f"""
{self.profile.emoji} {self.profile.name}

{self.profile.description}

📦 {len(self.profile.packages)} essential packages
⚡ Optimized for: {', '.join(self.profile.optimizations)}
🤖 Guided by: {self.profile.ai_persona}
        """
        
        return Panel(
            content.strip(),
            title=f"[{style}]{self.profile.name}[/]",
            border_style=style,
            expand=False
        )


class PackageSelector(Container):
    """Intelligent package selection widget"""
    
    def __init__(self, packages: List[Dict[str, Any]], category: str):
        super().__init__()
        self.packages = packages
        self.category = category
        self.selected = set()
        
    def compose(self) -> ComposeResult:
        """Create package selection UI"""
        yield Static(f"[bold]{self.category}[/bold]")
        
        with ScrollableContainer():
            for pkg in self.packages:
                with Horizontal(classes="package-row"):
                    yield Checkbox(
                        value=pkg.get('selected', False),
                        label=pkg['package'],
                        id=f"pkg_{pkg['package']}"
                    )
                    yield Static(
                        pkg.get('reason', ''),
                        classes="package-reason"
                    )


class ConflictResolutionModal(Container):
    """Modal for resolving package conflicts"""
    
    def __init__(self, conflicts: List[Dict[str, Any]]):
        super().__init__()
        self.conflicts = conflicts
        self.resolutions = {}
        
    def compose(self) -> ComposeResult:
        """Create conflict resolution UI"""
        yield Static("[bold red]⚠️ Package Conflicts Detected[/]")
        
        for conflict in self.conflicts:
            pkg1, pkg2 = conflict['conflict']
            
            with Container(classes="conflict-item"):
                yield Static(f"Conflict: {pkg1} ↔ {pkg2}")
                yield Static(f"Reason: {conflict.get('explanation', 'Unknown')}")
                
                with RadioSet(id=f"resolve_{pkg1}_{pkg2}"):
                    yield RadioButton(f"Keep {pkg1}", value=pkg1)
                    yield RadioButton(f"Keep {pkg2}", value=pkg2)
                    yield RadioButton("Keep both (advanced)", value="both")
                    yield RadioButton("Skip both", value="none")
        
        yield Button("Resolve Conflicts", variant="primary", id="resolve_btn")


class SetupCeremonyApp(App):
    """
    The main ceremony application - beautiful, progressive, intelligent
    """
    
    CSS = """
    Screen {
        background: $background;
    }
    
    .profile-grid {
        layout: grid;
        grid-size: 3 2;
        grid-gutter: 1 2;
        margin: 1 2;
    }
    
    ProfileCard {
        height: 12;
        width: 40;
    }
    
    ProfileCard.selected {
        border: thick $primary;
    }
    
    .package-row {
        height: 3;
        margin: 0 1;
    }
    
    .package-reason {
        color: $text-muted;
        margin-left: 2;
    }
    
    .round-indicator {
        dock: top;
        height: 3;
        background: $primary 20%;
        border: solid $primary;
        content-align: center middle;
    }
    
    .estimation-panel {
        dock: right;
        width: 30;
        border: solid $accent;
        padding: 1;
    }
    
    .conflict-item {
        border: solid $error;
        margin: 1;
        padding: 1;
    }
    
    #progress {
        margin: 2;
    }
    """
    
    TITLE = "🌟 Luminous System Setup Ceremony"
    
    current_round = reactive(0)
    selected_profile = reactive(None)
    selected_packages = reactive(set())
    
    def __init__(self):
        super().__init__()
        self.ceremony = SetupCeremony()
        self.profile_manager = ProfileManager()
        self.package_intel = PackageIntelligence()
        self.rounds_data = []
        
    def compose(self) -> ComposeResult:
        """Create the main UI"""
        yield Header()
        
        # Round indicator
        with Container(classes="round-indicator"):
            yield Static("", id="round_label")
        
        # Main content area
        with Container(id="main_content"):
            yield Static("Loading ceremony...", id="content")
        
        # Estimation panel
        with Container(classes="estimation-panel", id="estimation"):
            yield Static("[bold]Installation Estimate[/]")
            yield Static("", id="estimate_details")
        
        # Progress bar
        yield ProgressBar(id="progress", total=100, show_eta=True)
        
        # Navigation buttons
        with Horizontal(id="navigation"):
            yield Button("Back", id="back_btn", disabled=True)
            yield Button("Continue", id="continue_btn", variant="primary")
            yield Button("Skip", id="skip_btn")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the ceremony when app starts"""
        await self.start_ceremony()
    
    async def start_ceremony(self) -> None:
        """Begin the setup ceremony"""
        # Get initial state
        result = self.ceremony.begin_ceremony()
        
        # Update UI with welcome screen
        await self.show_welcome(result)
    
    async def show_welcome(self, data: Dict[str, Any]) -> None:
        """Show the welcome screen with detected packages"""
        self.current_round = 0
        
        content = self.query_one("#content")
        content.update(
            Panel(
                f"""
[bold cyan]Welcome to Your System's Setup Ceremony![/]

I've detected {data.get('installed_summary', {}).get('count', 0)} packages already installed.

Based on what I see, you look like a [bold]{data.get('suggested_profile', 'Developer')}[/].

Let's complete your system setup together!

[dim]This ceremony will guide you through:
• Selecting your user profile
• Installing essential packages
• Adding specialized tools
• Personal customization[/]
                """.strip(),
                title="🌟 Sacred Welcome",
                border_style="cyan"
            )
        )
        
        # Update round indicator
        self.query_one("#round_label").update(
            "[bold]Welcome - Let's Begin Your Journey[/]"
        )
    
    async def show_profile_selection(self) -> None:
        """Show profile selection screen"""
        self.current_round = 1
        
        # Update round indicator
        self.query_one("#round_label").update(
            "[bold]Round 1: Choose Your Digital Personality[/]"
        )
        
        # Create profile grid
        content = self.query_one("#content")
        content.remove_children()
        
        with content:
            profile_grid = Container(classes="profile-grid")
            
            for profile_key, profile in self.profile_manager.profiles.items():
                card = ProfileCard(profile)
                card.on_click = lambda p=profile_key: self.select_profile(p)
                profile_grid.mount(card)
            
            content.mount(profile_grid)
    
    async def show_package_selection(self, round_num: int) -> None:
        """Show package selection for current round"""
        self.current_round = round_num
        
        # Get recommendations based on profile
        if not self.selected_profile:
            return
            
        profile = self.profile_manager.profiles[self.selected_profile]
        installed = self.package_intel.detect_installed()
        recommendations = self.profile_manager.recommend_packages(
            profile, 
            list(installed.values())
        )
        
        # Update UI
        content = self.query_one("#content")
        content.remove_children()
        
        # Create package selectors by category
        for category, packages in recommendations.items():
            if packages:
                selector = PackageSelector(packages, category)
                content.mount(selector)
        
        # Update estimation
        await self.update_estimation()
    
    async def show_natural_language(self) -> None:
        """Show natural language input for final additions"""
        self.current_round = 99  # Final round
        
        self.query_one("#round_label").update(
            "[bold]Final Round: Anything Else You Need?[/]"
        )
        
        content = self.query_one("#content")
        content.update(
            Panel(
                """
[bold]Your system is almost ready![/]

Selected:
• Profile: {self.selected_profile}
• Packages: {len(self.selected_packages)} items

Is there anything specific you need that we haven't covered?

[dim]Type naturally, like:
"I need something for video editing"
"Tools for Python development"
"Gaming software"[/]
                """.strip(),
                title="🎯 Final Additions"
            )
        )
        
        # Add natural language input
        nl_input = Input(
            placeholder="Describe what you need...",
            id="natural_input"
        )
        content.mount(nl_input)
    
    async def handle_conflicts(self, conflicts: List[Dict[str, Any]]) -> None:
        """Show conflict resolution modal"""
        modal = ConflictResolutionModal(conflicts)
        await self.mount(modal)
    
    async def update_estimation(self) -> None:
        """Update installation estimation panel"""
        estimate = self.query_one("#estimate_details")
        
        # Calculate estimates
        package_count = len(self.selected_packages)
        download_size = package_count * 50  # MB average
        install_time = package_count * 0.5  # minutes average
        
        estimate.update(
            f"""
📦 {package_count} packages
💾 ~{download_size} MB download
💿 ~{download_size * 3} MB disk space
⏱️  ~{install_time:.0f} minutes

[dim]Your connection: Fast
Best mirror: cache.nixos.org[/]
            """.strip()
        )
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "continue_btn":
            await self.next_round()
        elif event.button.id == "back_btn":
            await self.previous_round()
        elif event.button.id == "skip_btn":
            await self.skip_round()
        elif event.button.id == "resolve_btn":
            await self.apply_conflict_resolution()
    
    async def next_round(self) -> None:
        """Progress to next round"""
        if self.current_round == 0:
            await self.show_profile_selection()
        elif self.current_round == 1:
            await self.show_package_selection(2)
        elif self.current_round == 2:
            await self.show_package_selection(3)
        elif self.current_round == 3:
            await self.show_natural_language()
        elif self.current_round == 99:
            await self.finalize_setup()
    
    async def finalize_setup(self) -> None:
        """Apply all selections and complete setup"""
        # Show progress
        progress = self.query_one("#progress")
        progress.total = len(self.selected_packages)
        
        content = self.query_one("#content")
        content.update(
            Panel(
                "[bold green]✨ Manifesting Your Perfect System...[/]",
                title="Installation in Progress",
                border_style="green"
            )
        )
        
        # Apply configuration
        result = self.ceremony.finalize_setup()
        
        # Show completion
        content.update(
            Panel(
                f"""
[bold green]✅ System Setup Complete![/]

Your {self.selected_profile} environment is ready.

Installed: {len(self.selected_packages)} packages
Time taken: {result.get('duration', 'unknown')}

[bold cyan]Restart your system to enjoy your new environment![/]

[dim]All changes have been recorded and can be rolled back if needed.[/]
                """.strip(),
                title="🎉 Ceremony Complete!",
                border_style="green"
            )
        )


def run_ceremony():
    """Launch the setup ceremony"""
    app = SetupCeremonyApp()
    app.run()


if __name__ == "__main__":
    run_ceremony()