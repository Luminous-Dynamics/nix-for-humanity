#!/usr/bin/env python3
"""Test the onboarding wizard display without interaction."""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align

console = Console()

def show_welcome():
    """Show the welcome screen."""
    # Clear screen for fresh start
    console.clear()
    
    # Animated welcome
    welcome_text = Text()
    welcome_text.append("🌟 ", style="bold yellow")
    welcome_text.append("Welcome to ", style="bold white")
    welcome_text.append("Luminous Nix", style="bold cyan")
    welcome_text.append("! ", style="bold white")
    welcome_text.append("🌟", style="bold yellow")
    
    console.print("\n" * 2)
    console.print(Panel(
        "[bold cyan]The Natural Language NixOS Assistant[/bold cyan]\n\n"
        "[white]I'm here to make NixOS [bold]simple[/bold] and [bold]joyful[/bold] for you![/white]\n\n"
        "In the next [yellow]2 minutes[/yellow], we'll:\n\n"
        "  1. ✨ [green]Set up your preferences[/green]\n"
        "  2. 🔍 [blue]Test that everything works[/blue]\n"  
        "  3. 🎯 [magenta]Complete your first task[/magenta]\n"
        "  4. 🎉 [yellow]Celebrate your success![/yellow]\n\n"
        "[dim]No technical knowledge required![/dim]",
        title=welcome_text,
        border_style="cyan",
        padding=1
    ))

def show_celebration():
    """Show the celebration screen."""
    console.print()
    celebration = Panel(
        Align.center(
            "[bold yellow]🎆 🎉 🎆[/bold yellow]\n\n"
            "[bold cyan]Setup Complete![/bold cyan]\n\n"
            "[bold yellow]🎆 🎉 🎆[/bold yellow]",
            vertical="middle"
        ),
        border_style="yellow",
        padding=1
    )
    console.print(celebration)
    console.print()
    
    console.print("[bold green]You're ready to use Luminous Nix![/bold green]\n")
    
    # Quick reference table
    console.print("[bold cyan]📚 Quick Reference:[/bold cyan]")
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Command", style="yellow")
    table.add_column("Description", style="white")
    
    table.add_row('luminous-nix help', 'Show all commands')
    table.add_row('luminous-nix "install ..."', 'Install packages')
    table.add_row('luminous-nix "search ..."', 'Find packages')
    table.add_row('luminous-nix "update"', 'Update system')
    table.add_row('luminous-nix setup --reset', 'Run setup again')
    
    console.print(table)
    console.print()
    
    # Next steps with nice formatting
    console.print("[bold magenta]🚀 Your Next Adventure:[/bold magenta]")
    console.print('  [cyan]1.[/cyan] Try: [yellow]luminous-nix "install your-favorite-app"[/yellow]')
    console.print("  [cyan]2.[/cyan] Explore: [yellow]luminous-nix discover[/yellow]")
    console.print("  [cyan]3.[/cyan] Learn: [yellow]luminous-nix help[/yellow]")
    console.print()

def show_skill_selection():
    """Show skill level selection screen."""
    console.print(Panel(
        "[bold]How would you describe your NixOS experience?[/bold]\n\n"
        "[cyan]1.[/cyan] 🆕 Brand new [dim](help me with everything)[/dim]\n"
        "[cyan]2.[/cyan] 📦 Some basics [dim](I've installed packages)[/dim]\n"
        "[cyan]3.[/cyan] ⚙️  Comfortable [dim](I edit configuration.nix)[/dim]\n"
        "[cyan]4.[/cyan] 🚀 Expert [dim](I write Nix expressions)[/dim]",
        border_style="magenta"
    ))

if __name__ == "__main__":
    print("\n🎨 Onboarding Wizard Visual Test\n")
    print("=" * 50)
    
    print("\n1. Welcome Screen:")
    print("-" * 30)
    show_welcome()
    
    print("\n\n2. Skill Selection Screen:")
    print("-" * 30)
    show_skill_selection()
    
    print("\n\n3. Celebration Screen:")
    print("-" * 30)
    show_celebration()
    
    print("\n✨ Visual test complete!")