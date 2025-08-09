#!/usr/bin/env python3
"""
Demo script for Enhanced Error Intelligence TUI Integration

Shows how educational errors, preventive suggestions, and XAI explanations
work together to help users understand and fix issues.
"""

import asyncio
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from src.nix_for_humanity.tui.enhanced_app import EnhancedNixForHumanityTUI
from src.nix_for_humanity.core.types import PersonalityStyle
from src.nix_for_humanity.ai.xai_engine import ExplanationLevel
from src.nix_for_humanity.tui.persona_styles import PersonaType


console = Console()


def print_demo_header():
    """Print demo header"""
    console.print(Panel.fit(
        "[bold cyan]Nix for Humanity - Enhanced Error Intelligence Demo[/bold cyan]\n\n"
        "[yellow]Showcasing educational errors, preventive suggestions, and XAI integration[/yellow]",
        border_style="cyan"
    ))
    console.print()


def show_demo_scenarios():
    """Show available demo scenarios"""
    scenarios = """
## Demo Scenarios

1. **Permission Error** - Try to install system-wide without sudo
2. **Package Not Found** - Misspell a package name  
3. **Disk Space Warning** - Preventive suggestion demo
4. **Network Error** - Connection issues with solutions
5. **Build Failure** - Complex error with XAI explanation
6. **Interactive Mode** - Try your own commands

Each scenario demonstrates:
- 🎓 Educational error explanations
- 💡 Contextual solutions
- 🔍 XAI "why did this fail?" analysis
- 🎯 Persona-adaptive formatting
"""
    
    console.print(Markdown(scenarios))
    console.print()


def run_demo_scenario(scenario: int):
    """Run a specific demo scenario"""
    
    scenarios = {
        1: {
            'name': 'Permission Error Demo',
            'commands': [
                'install firefox system-wide',
                'show me why it failed',
                'try the first solution'
            ],
            'persona': PersonaType.GRANDMA_ROSE,
            'description': 'Shows how permission errors are explained educationally'
        },
        2: {
            'name': 'Package Not Found Demo',
            'commands': [
                'install fierfix',  # Typo
                'install pythoon',  # Another typo
                'search for browsers'
            ],
            'persona': PersonaType.MAYA,
            'description': 'Demonstrates typo detection and helpful suggestions'
        },
        3: {
            'name': 'Disk Space Warning Demo',
            'commands': [
                'install large-package',
                'check disk space',
                'clean up old generations'
            ],
            'persona': PersonaType.DAVID,
            'description': 'Shows preventive suggestions before errors occur'
        },
        4: {
            'name': 'Network Error Demo',
            'commands': [
                'update system',
                'check network status',
                'try offline mode'
            ],
            'persona': PersonaType.CARLOS,
            'description': 'Network troubleshooting with educational context'
        },
        5: {
            'name': 'Build Failure Demo',
            'commands': [
                'build custom-package',
                'explain why build failed',
                'show technical details'
            ],
            'persona': PersonaType.DR_SARAH,
            'description': 'Complex error with full XAI causal analysis'
        }
    }
    
    if scenario not in scenarios:
        console.print("[red]Invalid scenario number[/red]")
        return
        
    scenario_info = scenarios[scenario]
    
    console.print(Panel(
        f"[bold]{scenario_info['name']}[/bold]\n\n"
        f"{scenario_info['description']}\n\n"
        f"Persona: [cyan]{scenario_info['persona'].value}[/cyan]\n"
        f"Commands to try:\n" + 
        "\n".join(f"  • {cmd}" for cmd in scenario_info['commands']),
        title="Demo Scenario",
        border_style="green"
    ))
    
    console.print("\n[yellow]Press Enter to launch the TUI...[/yellow]")
    input()
    
    # Launch TUI with appropriate settings
    app = EnhancedNixForHumanityTUI()
    app.persona_manager.set_persona(scenario_info['persona'])
    app.show_explanations = True
    app.explanation_level = ExplanationLevel.DETAILED
    
    console.print("\n[dim]Launching Enhanced TUI with Error Intelligence...[/dim]\n")
    console.print("[yellow]Try the suggested commands to see error intelligence in action![/yellow]")
    console.print("[dim]Press Ctrl+Q to exit the TUI[/dim]\n")
    
    # Run the app
    app.run()


def interactive_demo():
    """Run interactive demo"""
    console.print(Panel(
        "[bold]Interactive Demo Mode[/bold]\n\n"
        "The Enhanced TUI will launch with all error intelligence features enabled.\n"
        "Try any command to see how errors are handled educationally!\n\n"
        "Features to try:\n"
        "• Misspell package names to see corrections\n"
        "• Try operations without permissions\n"
        "• Ask 'why did that fail?' after any error\n"
        "• Press Ctrl+E to cycle explanation detail levels\n"
        "• Press Ctrl+U to switch personas",
        title="Interactive Mode",
        border_style="cyan"
    ))
    
    console.print("\n[yellow]Press Enter to launch...[/yellow]")
    input()
    
    app = EnhancedNixForHumanityTUI()
    app.run()


def main():
    """Main demo function"""
    print_demo_header()
    show_demo_scenarios()
    
    while True:
        choice = console.input("\n[cyan]Select scenario (1-6) or 'q' to quit:[/cyan] ")
        
        if choice.lower() == 'q':
            console.print("\n[yellow]Thanks for trying the Error Intelligence demo![/yellow]")
            break
            
        try:
            scenario_num = int(choice)
            if scenario_num == 6:
                interactive_demo()
            else:
                run_demo_scenario(scenario_num)
                
            console.print("\n[green]Demo completed![/green]")
            
        except ValueError:
            console.print("[red]Please enter a number 1-6 or 'q' to quit[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo interrupted[/yellow]")
            break


if __name__ == "__main__":
    main()