"""
🎨 UI Generation Commands for Luminous Nix
Natural language interface generation integrated with NixOS operations
"""

import sys
from pathlib import Path

import click

# Import with fallback
UI_IMPORT_ERROR = None
try:
    from ..gui import UIGeneratorCLI, UserContext

    UI_AVAILABLE = True
except ImportError as e:
    UI_AVAILABLE = False
    UI_IMPORT_ERROR = str(e)
    UIGeneratorCLI = None
    UserContext = None


@click.group()
@click.pass_context
def ui(ctx):
    """AI-driven interface generation for NixOS

    Create beautiful, functional interfaces using natural language:

    \b
    Examples:
      ask-nix ui create "dashboard for system monitoring"
      ask-nix ui create "package installer with search"
      ask-nix ui refine "make it darker with bigger charts"
      ask-nix ui show --last

    The system learns from your preferences and improves over time.
    """
    if not UI_AVAILABLE:
        click.echo("❌ UI generation module not installed", err=True)
        if UI_IMPORT_ERROR:
            click.echo(f"   Import error: {UI_IMPORT_ERROR}", err=True)
        click.echo("   Install with: poetry install --with tui", err=True)
        ctx.exit(1)

    # Initialize CLI in context
    ctx.ensure_object(dict)
    ctx.obj["ui_cli"] = UIGeneratorCLI()


@ui.command()
@click.argument("request", nargs=-1, required=True)
@click.option(
    "--preview/--no-preview", default=True, help="Show preview after creation"
)
@click.option("--user", help="User profile for preferences")
@click.option("--save-as", help="Save with custom name")
@click.option("--for-command", help="Generate UI for specific NixOS command")
@click.pass_context
def create(ctx, request, preview, user, save_as, for_command):
    """Create interface from natural language

    \b
    Examples:
      ask-nix ui create dashboard for monitoring
      ask-nix ui create "package search interface" --no-preview
      ask-nix ui create "config editor" --for-command "edit configuration.nix"
    """
    cli = ctx.obj["ui_cli"]
    request_str = " ".join(request)

    # Add NixOS context if for specific command
    if for_command:
        request_str = f"{request_str} for NixOS command: {for_command}"

    click.echo(f"🎨 Creating interface: {request_str}")

    result = cli.create_interface(request=request_str, user_id=user, preview=preview)

    if result["success"]:
        click.echo("✅ Interface created successfully!")
        click.echo(f"   Components: {result['components']}")
        click.echo(f"   Confidence: {result['confidence']:.0%}")
        click.echo(f"   Time: {result['generation_time']:.2f}ms")

        if save_as:
            click.echo(f"   💾 Saved as: {save_as}")
    else:
        click.echo("❌ Failed to create interface", err=True)


@ui.command()
@click.argument("refinement", nargs=-1, required=True)
@click.option("--id", "interface_id", help="Interface ID to refine")
@click.option("--preview", is_flag=True, help="Show preview after refinement")
@click.pass_context
def refine(ctx, refinement, interface_id, preview):
    """Refine existing interface

    \b
    Examples:
      ask-nix ui refine make it darker
      ask-nix ui refine "add more charts" --preview
      ask-nix ui refine "remove sidebar" --id dashboard_123
    """
    cli = ctx.obj["ui_cli"]
    refinement_str = " ".join(refinement)

    click.echo(f"✏️ Refining: {refinement_str}")

    result = cli.refine_interface(refinement=refinement_str, interface_id=interface_id)

    if result["success"]:
        click.echo("✅ Interface refined!")
        click.echo(f"   Components: {result['components']}")

        if preview:
            interface = cli._load_interface(result["interface_id"])
            if interface:
                cli.renderer.preview(interface)
    else:
        click.echo(f"❌ {result.get('error', 'Refinement failed')}", err=True)


@ui.command()
@click.option("--last", is_flag=True, default=True, help="Show last created")
@click.option("--id", "interface_id", help="Show specific interface")
@click.option("--list", "list_all", is_flag=True, help="List all interfaces")
@click.pass_context
def show(ctx, last, interface_id, list_all):
    """Display saved interfaces

    \b
    Examples:
      ask-nix ui show              # Show last created
      ask-nix ui show --list       # List all interfaces
      ask-nix ui show --id dash_123  # Show specific
    """
    cli = ctx.obj["ui_cli"]

    if list_all:
        interfaces = cli.list_interfaces()
        if interfaces:
            click.echo("📋 Saved Interfaces")
            click.echo("=" * 60)
            for i, intf in enumerate(interfaces, 1):
                click.echo(f"\n{i}. ID: {intf['id']}")
                click.echo(f"   Created: {intf['created']}")
                click.echo(f"   Request: {intf['request'][:50]}...")
                click.echo(f"   Components: {intf['components']}")
        else:
            click.echo("No interfaces saved yet")
    elif interface_id:
        interface = cli._load_interface(interface_id)
        if interface:
            cli.renderer.preview(interface)
        else:
            click.echo(f"❌ Interface {interface_id} not found", err=True)
    else:
        cli.show_last_interface()


@ui.command()
@click.option("--id", "interface_id", help="Interface to export")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "html", "python", "nix"]),
    default="json",
    help="Export format",
)
@click.option("--output", "output_path", help="Output file path")
@click.pass_context
def export(ctx, interface_id, fmt, output_path):
    """Export interface to file

    \b
    Examples:
      ask-nix ui export --format html --output dashboard.html
      ask-nix ui export --format python > app.py
      ask-nix ui export --format nix  # Generate NixOS module
    """
    cli = ctx.obj["ui_cli"]

    # Special handling for NixOS module generation
    if fmt == "nix":
        click.echo("🔧 Generating NixOS module...")
        # TODO: Implement NixOS module generation
        click.echo("   (NixOS module generation coming soon)")
        return

    result = cli.export_interface(
        interface_id=interface_id, format=fmt, output_path=output_path
    )

    if result["success"]:
        click.echo(f"✅ Exported to: {result['path']}")
    else:
        click.echo(f"❌ {result.get('error', 'Export failed')}", err=True)


@ui.command()
@click.option("--detailed", is_flag=True, help="Show detailed statistics")
@click.option("--report", is_flag=True, help="Generate full report")
@click.pass_context
def stats(ctx, detailed, report):
    """Show UI generation statistics

    Track your usage patterns and system learning progress.
    """
    cli = ctx.obj["ui_cli"]

    if report:
        report_text = cli.monitor.generate_report()
        click.echo(report_text)
    else:
        stats = cli.get_statistics()

        click.echo("📊 UI Generation Statistics")
        click.echo("=" * 60)

        if "builder" in stats:
            click.echo("\n🔨 Builder:")
            click.echo(f"   Interfaces created: {stats.get('interfaces_created', 0)}")
            click.echo(f"   Patterns learned: {stats.get('patterns_learned', 0)}")

        if "performance" in stats and stats["performance"]:
            click.echo("\n⚡ Performance:")
            perf = stats["performance"]
            if "avg_generation_time" in perf:
                click.echo(f"   Avg generation: {perf['avg_generation_time']:.2f}ms")
            if "success_rate" in perf:
                click.echo(f"   Success rate: {perf['success_rate']:.0%}")

        if detailed:
            import json

            click.echo("\n📝 Detailed Stats:")
            click.echo(json.dumps(stats, indent=2))


@ui.command()
@click.argument("feedback_text", nargs=-1)
@click.option("--id", "interface_id", help="Interface to rate")
@click.option("--rating", type=click.IntRange(1, 10), help="Rating 1-10")
@click.option("--comment", help="Additional feedback")
@click.pass_context
def feedback(ctx, feedback_text, interface_id, rating, comment):
    """Provide feedback on generated interfaces

    \b
    Examples:
      ask-nix ui feedback "Great dashboard!" --rating 9
      ask-nix ui feedback --rating 7 --comment "Needs more colors"
    """
    cli = ctx.obj["ui_cli"]

    feedback_str = " ".join(feedback_text) if feedback_text else ""

    # Record feedback
    if rating:
        click.echo(f"⭐ Rating recorded: {rating}/10")

    if feedback_str:
        click.echo(f"💬 Feedback: {feedback_str}")

    if comment:
        click.echo(f"📝 Comment: {comment}")

    # Save to learning system
    cli.learning.save_interface_metrics(
        {
            "interface_id": interface_id or "last",
            "user_satisfaction": rating / 10 if rating else 0.5,
            "feedback": comment or feedback_str,
        }
    )

    click.echo("✅ Thank you for your feedback!")


# Special NixOS integration commands
@ui.group()
def nixos():
    """Generate interfaces for NixOS operations

    Create specialized UIs for common NixOS tasks.
    """
    pass


@nixos.command()
@click.option("--preview", is_flag=True, default=True)
@click.pass_context
def packages(ctx, preview):
    """Create package management interface

    Search, install, and manage NixOS packages visually.
    """
    cli = ctx.obj["ui_cli"]

    request = """Create a package manager interface with:
    - Search bar at top
    - Package list with name, description, version
    - Install/Remove buttons for each package
    - Filter by installed/available
    - Dark theme for NixOS style"""

    click.echo("📦 Creating NixOS package manager interface...")

    result = cli.create_interface(request, preview=preview)

    if result["success"]:
        click.echo("✅ Package manager created!")
        # TODO: Connect to actual nix-env commands
        click.echo("   (Connection to nix-env coming soon)")


@nixos.command()
@click.option("--file", default="/etc/nixos/configuration.nix")
@click.pass_context
def config(ctx, file):
    """Create configuration editor interface

    Edit NixOS configuration files with syntax highlighting.
    """
    cli = ctx.obj["ui_cli"]

    request = f"""Create a configuration editor for {file} with:
    - Syntax highlighting for Nix language
    - File tree on the left
    - Editor in center
    - Options reference panel on right
    - Save and rebuild buttons"""

    click.echo(f"📝 Creating config editor for {file}...")

    result = cli.create_interface(request, preview=True)

    if result["success"]:
        click.echo("✅ Config editor created!")
        # TODO: Connect to actual file operations


@nixos.command()
@click.pass_context
def monitor(ctx):
    """Create system monitoring dashboard

    Monitor NixOS system resources and services.
    """
    cli = ctx.obj["ui_cli"]

    request = """Create a system monitoring dashboard with:
    - CPU, Memory, Disk usage gauges
    - Running services list with status indicators
    - Network activity graph
    - System logs viewer at bottom
    - Real-time updates every 5 seconds
    - Dark professional theme"""

    click.echo("📊 Creating system monitor...")

    result = cli.create_interface(request, preview=True)

    if result["success"]:
        click.echo("✅ System monitor created!")
        # TODO: Connect to actual system metrics


# Add to main CLI
def register_ui_commands(cli_group):
    """Register UI commands with main CLI"""
    cli_group.add_command(ui)
