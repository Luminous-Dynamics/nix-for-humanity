#!/usr/bin/env python3
"""
🌊 Luminous Setup Ceremony - Natural Language CLI
Integrates with ask-nix for conversational setup
"""

import sys
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .profile_system import (
    SetupCeremony, ProfileManager, PackageIntelligence,
    ConflictResolver, ProfileType
)
from ..consciousness import POMLConsciousness
from ..cli.ask_nix import AskNix

console = Console()


class CeremonyCLI:
    """
    Natural language setup ceremony via CLI
    Extends ask-nix with setup capabilities
    """
    
    def __init__(self):
        self.ceremony = SetupCeremony()
        self.ask_nix = AskNix()
        self.consciousness = POMLConsciousness()
        self.console = console
        
    def welcome(self) -> Dict[str, Any]:
        """Interactive welcome with detection"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Detecting installed packages...", total=None)
            result = self.ceremony.begin_ceremony()
            progress.update(task, completed=True)
        
        # Display welcome
        self.console.print(Panel(
            f"""
[bold cyan]🌟 Welcome to Luminous System Setup Ceremony[/]

I've detected [bold]{result.get('installed_summary', {}).get('count', 0)}[/] packages already installed.

Based on what I see, you look like a [bold yellow]{result.get('suggested_profile', 'Developer')}[/].

Let's complete your system together through natural conversation!
            """.strip(),
            title="Sacred Welcome",
            border_style="cyan"
        ))
        
        return result
    
    def select_profile_natural(self) -> ProfileType:
        """Natural language profile selection"""
        self.console.print("\n[bold]Let's understand your needs:[/]\n")
        
        # Ask natural questions
        response = Prompt.ask(
            "[cyan]What will you primarily use this computer for?[/]",
            choices=None  # Free text
        )
        
        # Use consciousness to interpret
        result = self.consciousness.process_intent(
            intent="determine user profile",
            context={"user_response": response}
        )
        
        suggested = result.get('profile', 'developer')
        
        # Confirm with user
        profiles_table = Table(title="Available Profiles")
        profiles_table.add_column("Profile", style="cyan")
        profiles_table.add_column("Description")
        profiles_table.add_column("Best For")
        
        for key, profile in self.ceremony.profile_manager.profiles.items():
            profiles_table.add_row(
                f"{profile.emoji} {profile.name}",
                profile.description,
                ", ".join(profile.optimizations)
            )
        
        self.console.print(profiles_table)
        
        if Confirm.ask(f"\nI suggest [bold]{suggested}[/]. Is this right?"):
            return ProfileType(suggested)
        else:
            # Let them choose
            choice = Prompt.ask(
                "Which profile would you prefer?",
                choices=list(self.ceremony.profile_manager.profiles.keys())
            )
            return ProfileType(choice)
    
    def package_selection_round(self, round_num: int, 
                               recommendations: Dict[str, List]) -> List[str]:
        """Interactive package selection"""
        selected = []
        
        for category, packages in recommendations.items():
            if not packages:
                continue
                
            self.console.print(f"\n[bold]{category}:[/]")
            
            # Show packages
            for pkg in packages:
                if Confirm.ask(
                    f"  Install [cyan]{pkg['package']}[/]? "
                    f"([dim]{pkg.get('reason', 'Recommended')}[/])",
                    default=True
                ):
                    selected.append(pkg['package'])
        
        # Natural language additions
        self.console.print("\n[bold]Need anything else?[/]")
        while True:
            additional = Prompt.ask(
                "[cyan]Describe what you need (or 'done')[/]"
            )
            
            if additional.lower() in ['done', 'no', 'nothing']:
                break
                
            # Use ask-nix to find packages
            suggestions = self.ask_nix.search_packages(additional)
            
            if suggestions:
                self.console.print("[dim]I found these:[/]")
                for i, pkg in enumerate(suggestions[:5], 1):
                    self.console.print(f"  {i}. {pkg['name']} - {pkg.get('description', '')}")
                
                choice = Prompt.ask(
                    "Which one? (number or 'none')",
                    default="none"
                )
                
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(suggestions):
                        selected.append(suggestions[idx]['name'])
        
        return selected
    
    def handle_conflicts_interactive(self, conflicts: List[Dict]) -> Dict[str, str]:
        """Interactive conflict resolution"""
        resolutions = {}
        
        for conflict in conflicts:
            pkg1, pkg2 = conflict['conflict']
            
            self.console.print(Panel(
                f"""
[bold red]Conflict Detected![/]

{pkg1} ↔ {pkg2}

[dim]{conflict.get('explanation', 'These packages conflict')}[/]

Resolution: {conflict.get('resolution', 'Choose one')}
                """.strip(),
                title="⚠️ Package Conflict",
                border_style="red"
            ))
            
            if conflict.get('auto_apply'):
                self.console.print(
                    f"[green]Auto-resolving: {conflict['resolution']}[/]"
                )
                resolutions[f"{pkg1}_{pkg2}"] = conflict['resolution']
            else:
                choice = Prompt.ask(
                    "Your choice",
                    choices=[pkg1, pkg2, "both", "neither"],
                    default=pkg1
                )
                resolutions[f"{pkg1}_{pkg2}"] = choice
        
        return resolutions
    
    def run_ceremony(self) -> None:
        """Run the complete ceremony"""
        # Welcome
        initial_state = self.welcome()
        
        # Profile selection
        profile = self.select_profile_natural()
        self.ceremony.selected_profile = profile.value
        
        # Get profile object
        profile_obj = self.ceremony.profile_manager.profiles[profile.value]
        
        # Round 1: Essentials
        self.console.print(Panel(
            "[bold]Round 1: Essential Packages[/]",
            border_style="cyan"
        ))
        
        installed = self.ceremony.package_intel.detect_installed()
        recommendations = self.ceremony.profile_manager.recommend_packages(
            profile_obj,
            list(installed.values())
        )
        
        round1_packages = self.package_selection_round(1, {
            "Essential Missing": recommendations.get("essential_missing", [])
        })
        
        # Check conflicts
        conflicts = self.ceremony.package_intel.find_conflicts(round1_packages)
        if conflicts:
            resolutions = self.handle_conflicts_interactive(
                self.ceremony.conflict_resolver.resolve_conflicts(
                    conflicts, profile_obj
                )
            )
        
        self.ceremony.selected_packages.extend(round1_packages)
        
        # Round 2: Specialized
        if Confirm.ask("\n[cyan]Continue with specialized tools?[/]", default=True):
            self.console.print(Panel(
                "[bold]Round 2: Professional Tools[/]",
                border_style="cyan"
            ))
            
            round2_packages = self.package_selection_round(2, {
                "Highly Recommended": recommendations.get("highly_recommended", []),
                "Companion Apps": recommendations.get("companion_apps", [])
            })
            
            self.ceremony.selected_packages.extend(round2_packages)
        
        # Final summary
        self.show_summary()
        
        # Apply if confirmed
        if Confirm.ask("\n[bold green]Ready to install?[/]", default=True):
            self.apply_setup()
    
    def show_summary(self) -> None:
        """Show installation summary"""
        total = len(self.ceremony.selected_packages)
        
        # Estimate
        download_mb = total * 50
        time_min = total * 0.5
        
        self.console.print(Panel(
            f"""
[bold]Installation Summary[/]

Profile: [cyan]{self.ceremony.selected_profile}[/]
Packages: [yellow]{total}[/] packages selected
Download: ~[blue]{download_mb}MB[/]
Time: ~[green]{time_min:.0f} minutes[/]

Selected packages:
{', '.join(self.ceremony.selected_packages[:10])}
{f'... and {total-10} more' if total > 10 else ''}
            """.strip(),
            title="📦 Ready to Install",
            border_style="green"
        ))
    
    def apply_setup(self) -> None:
        """Apply the configuration"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Applying configuration...", total=100)
            
            # Finalize setup
            result = self.ceremony.finalize_setup()
            
            progress.update(task, completed=100)
        
        if result.get('success'):
            self.console.print(Panel(
                """
[bold green]✅ Setup Complete![/]

Your system has been configured successfully.

[cyan]Next steps:[/]
• Restart your system for all changes to take effect
• Run [bold]ask-nix "help"[/] to explore your new capabilities
• Your configuration is saved and can be rolled back if needed

[dim]Thank you for participating in the setup ceremony![/]
                """.strip(),
                title="🎉 Success!",
                border_style="green"
            ))
        else:
            self.console.print(
                f"[red]Setup failed: {result.get('error', 'Unknown error')}[/]"
            )


@click.command()
@click.option('--profile', help='Skip interactive and use profile')
@click.option('--packages', help='Comma-separated list of packages')
@click.option('--natural', is_flag=True, help='Use natural language mode')
def setup_ceremony(profile: Optional[str], packages: Optional[str], natural: bool):
    """
    Run the Luminous Setup Ceremony
    
    Examples:
        ask-nix setup                    # Interactive ceremony
        ask-nix setup --profile developer  # Quick developer setup
        ask-nix setup --natural          # Natural language only
    """
    cli = CeremonyCLI()
    
    if profile and packages:
        # Quick mode
        cli.ceremony.selected_profile = profile
        cli.ceremony.selected_packages = packages.split(',')
        cli.show_summary()
        if Confirm.ask("Apply this configuration?"):
            cli.apply_setup()
    else:
        # Full ceremony
        cli.run_ceremony()


# Integration with ask-nix
def register_setup_command(ask_nix_cli):
    """Register setup ceremony with ask-nix"""
    ask_nix_cli.add_command(setup_ceremony, name='setup')


if __name__ == "__main__":
    setup_ceremony()