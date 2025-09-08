"""
Luminous Nix CLI Commands

This module provides the main CLI entry point and command registration.
"""

import click

from .config_command import config
from .discover_command import discover_group as discover
from .error_command import error
from .flake_command import flake
from .generation_command import generation
from .home_command import home
from .settings_command import settings

# Import Phase 1 advanced features
try:
    from .rollback_command import rollback
    from .storage_command import storage
    from .security_command import security
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False
    rollback = None
    storage = None
    security = None

# Import Phase 2 advanced features
try:
    from .devenv_command import devenv
    from .performance_command import performance
    PHASE2_FEATURES_AVAILABLE = True
except ImportError:
    PHASE2_FEATURES_AVAILABLE = False
    devenv = None
    performance = None

# Import Phase 3 advanced features
try:
    from .dna_command import dna
    from .modes_command import modes
    from .health_command import health
    PHASE3_FEATURES_AVAILABLE = True
except ImportError:
    PHASE3_FEATURES_AVAILABLE = False
    dna = None
    modes = None
    health = None

# Import UI generation commands
try:
    from .ui_command import ui

    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False
    ui = None

# Import cache command
try:
    from .cache_command import cache

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    cache = None

# Import onboarding wizard
try:
    from ..onboarding.wizard import OnboardingWizard

    ONBOARDING_AVAILABLE = True
except ImportError:
    ONBOARDING_AVAILABLE = False
    OnboardingWizard = None


@click.group()
@click.version_option(version="0.6.0", prog_name="Luminous Nix")
@click.pass_context
def cli(ctx):
    """Luminous Nix - Natural language interface for NixOS

    Transform NixOS from command-line complexity into natural conversation.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)


# Register all subcommands
cli.add_command(config)
cli.add_command(settings)
cli.add_command(home)
cli.add_command(error)
cli.add_command(generation)
cli.add_command(flake)
cli.add_command(discover)

# Add cache command if available
if CACHE_AVAILABLE and cache:
    cli.add_command(cache)

# Add UI generation command if available
if UI_AVAILABLE and ui:
    cli.add_command(ui)

# Add Phase 1 advanced features if available
if ADVANCED_FEATURES_AVAILABLE:
    if rollback:
        cli.add_command(rollback)
    if storage:
        cli.add_command(storage)
    if security:
        cli.add_command(security)

# Add Phase 2 advanced features if available
if PHASE2_FEATURES_AVAILABLE:
    if devenv:
        cli.add_command(devenv)
    if performance:
        cli.add_command(performance)

# Add Phase 3 advanced features if available
if PHASE3_FEATURES_AVAILABLE:
    if dna:
        cli.add_command(dna)
    if modes:
        cli.add_command(modes)
    if health:
        cli.add_command(health)


# Setup/Onboarding command
@cli.command()
@click.option("--reset", is_flag=True, help="Reset preferences and run setup again")
@click.pass_context
def setup(ctx, reset):
    """Run the interactive setup wizard

    Guides you through:
    • System checks
    • Preference configuration
    • First successful command
    • Celebration!
    """
    if not ONBOARDING_AVAILABLE:
        click.echo("⚠️ Onboarding wizard not available in this installation")
        return

    import json
    from pathlib import Path

    config_file = Path.home() / ".config" / "luminous-nix" / "config.json"

    # Check if already completed (unless reset)
    if not reset and config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
                if config.get("onboarding_complete"):
                    click.echo("✅ Setup already complete! Use --reset to run again.")
                    click.echo("\n💡 Quick commands:")
                    click.echo("  • luminous-nix help")
                    click.echo('  • luminous-nix "install firefox"')
                    click.echo("  • luminous-nix settings wizard")
                    return
        except:
            pass  # Continue with setup if config is corrupted

    # Run the wizard
    wizard = OnboardingWizard()
    wizard.run()


# Natural language command (default when no subcommand)
@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option(
    "--personality",
    "-p",
    type=click.Choice(
        ["minimal", "friendly", "encouraging", "technical", "accessible"]
    ),
    help="Set response personality",
)
@click.option(
    "--dry-run", "-d", is_flag=True, help="Show what would be done without executing"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmations")
@click.option("--no-visual", is_flag=True, help="Disable visual elements")
@click.option("--execute", "-e", is_flag=True, help="Execute commands immediately")
@click.option("--profile", help="Use a specific configuration profile")
@click.pass_context
def ask(ctx, query, personality, dry_run, yes, no_visual, execute, profile):
    """Ask Luminous Nix anything in natural language

    Examples:
        ask-nix ask "install firefox"
        ask-nix ask "update my system"
        ask-nix ask "why is my wifi not working?"
    """
    import os

    from luminous_nix.config import get_config_manager
    from luminous_nix.frontends.cli import UnifiedNixAssistant

    # Apply profile if specified
    if profile:
        manager = get_config_manager()
        manager.apply_profile(profile)

    # Create assistant with config
    config = get_config_manager().config
    assistant = UnifiedNixAssistant()

    # Apply settings from config
    if personality:
        assistant.set_personality(personality)
    elif config.ui.default_personality:
        assistant.set_personality(config.ui.default_personality.value)

    # Handle execution mode - execute flag overrides dry_run
    # Also check environment variables for compatibility with bin/ask-nix
    if execute or os.environ.get("LUMINOUS_EXECUTE", "").lower() == "true":
        assistant.dry_run = False  # Execute commands when -e is passed
    else:
        # Check environment variable first (from bin/ask-nix), then use CLI flag
        env_dry_run = os.environ.get("LUMINOUS_DRY_RUN", "").lower() == "true"
        assistant.dry_run = env_dry_run or dry_run  # Use env var or CLI flag

    # Check environment variable for skip confirmation (from bin/ask-nix)
    env_skip_confirm = os.environ.get("LUMINOUS_SKIP_CONFIRM", "").lower() == "true"
    assistant.skip_confirmation = (
        env_skip_confirm or yes or not config.ui.confirm_actions
    )
    assistant.visual_mode = not no_visual and config.ui.use_colors
    assistant.show_progress = config.ui.progress_indicators

    # Process the query
    query_text = " ".join(query)
    assistant.answer(query_text)


def main():
    """Main entry point for the CLI"""
    import json
    import os
    import sys
    from pathlib import Path

    # Check for first run (unless specific command is being run)
    if len(sys.argv) == 1 or (
        len(sys.argv) > 1 and sys.argv[1] not in ["setup", "--help", "-h", "--version"]
    ):
        config_file = Path.home() / ".config" / "luminous-nix" / "config.json"

        # Check if this is first run
        if not config_file.exists() and ONBOARDING_AVAILABLE:
            # Check if running in non-interactive mode (CI, testing, etc)
            if not os.environ.get("LUMINOUS_SKIP_ONBOARDING") and sys.stdin.isatty():
                from rich.console import Console
                from rich.panel import Panel

                console = Console()

                console.print("\n")
                console.print(
                    Panel.fit(
                        "[bold cyan]🎉 Welcome to Luminous Nix![/bold cyan]\n\n"
                        "I see this is your first time! Let's set things up\n"
                        "to make NixOS simple and joyful for you.\n\n"
                        "[yellow]This will only take 2 minutes.[/yellow]",
                        border_style="cyan",
                    )
                )
                console.print("\n")

                response = (
                    input("Would you like to run the setup wizard? [Y/n]: ")
                    .strip()
                    .lower()
                )
                if response != "n":
                    wizard = OnboardingWizard()
                    wizard.run()
                    console.print(
                        "\n[green]Setup complete! Now running your command...[/green]\n"
                    )
                else:
                    console.print(
                        "\n[yellow]Skipping setup. You can run 'luminous-nix setup' anytime.[/yellow]\n"
                    )
                    # Create minimal config to not ask again
                    config_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(config_file, "w") as f:
                        json.dump({"onboarding_skipped": True}, f)

    # Check if voice mode is enabled
    if os.environ.get("LUMINOUS_VOICE_ENABLED", "").lower() == "true":
        # Run in voice mode
        from luminous_nix.frontends.cli import UnifiedNixAssistant
        from luminous_nix.voice.voice_interface import VoiceInterface

        assistant = UnifiedNixAssistant()
        voice = VoiceInterface(verbose=assistant.verbose_level > 0)

        # Run voice conversation loop
        def process_voice_command(text):
            """Process voice command and return response"""
            # Use the assistant to process the command
            import io
            import sys

            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()

            try:
                assistant.answer(text)
                response = buffer.getvalue()
            finally:
                sys.stdout = old_stdout

            # Also print to console
            print(response)
            return response

        # Start voice conversation
        voice.conversation_loop(process_voice_command)
        return

    # Normal CLI mode
    # If no arguments, show help
    if len(sys.argv) == 1:
        cli.main(["--help"])
    # If first argument doesn't start with dash and isn't a known command,
    # treat it as a natural language query
    elif (
        len(sys.argv) > 1
        and not sys.argv[1].startswith("-")
        and sys.argv[1] not in cli.commands
    ):
        # Convert "ask-nix install firefox" to "ask-nix ask install firefox"
        sys.argv.insert(1, "ask")
        cli()
    else:
        cli()


__all__ = ["cli", "main"]
