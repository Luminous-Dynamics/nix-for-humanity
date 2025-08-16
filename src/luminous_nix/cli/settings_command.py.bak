#!/usr/bin/env python3
"""
Settings management commands for Nix for Humanity

Provides CLI interface for managing user settings and configuration.
"""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.syntax import Syntax
from rich.table import Table

from nix_for_humanity.config import ConfigSchema, get_config_manager
from nix_for_humanity.config.schema import Personality

console = Console()


@click.group()
def settings():
    """Manage Nix for Humanity settings and configuration"""
    pass


@settings.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json", "toml"]),
    default="yaml",
    help="Output format",
)
@click.option("--show-defaults", is_flag=True, help="Show default values")
def show(format, show_defaults):
    """Show current configuration"""
    manager = get_config_manager()

    if show_defaults:
        config = ConfigSchema()  # Default config
        console.print("[dim]Showing default configuration[/dim]")
    else:
        config = manager.config
        console.print(
            f"[dim]Configuration from: {manager.config_path or 'defaults'}[/dim]"
        )

    # Export as string
    config_str = manager.export(format)

    if config_str:
        syntax = Syntax(config_str, format, theme="monokai", line_numbers=True)
        console.print(
            Panel(syntax, title=f"Configuration ({format})", border_style="blue")
        )
    else:
        console.print("[red]Error exporting configuration[/red]")


@settings.command()
@click.argument("path")
@click.argument("value", required=False)
def get(path, value):
    """Get a configuration value

    Examples:
        ask-nix settings get ui.default_personality
        ask-nix settings get performance.timeout
    """
    manager = get_config_manager()

    if value:
        # This is actually a set command
        console.print("[yellow]Did you mean 'ask-nix settings set'?[/yellow]")
        return

    result = manager.get(path)

    if result is None:
        console.print(f"[red]Configuration key not found: {path}[/red]")
    else:
        console.print(f"[bold]{path}:[/bold] {result}")


@settings.command()
@click.argument("path")
@click.argument("value")
def set(path, value):
    """Set a configuration value

    Examples:
        ask-nix settings set ui.default_personality friendly
        ask-nix settings set performance.timeout 60
    """
    manager = get_config_manager()

    # Try to parse value to appropriate type
    try:
        # Try boolean
        if value.lower() in ["true", "false"]:
            parsed_value = value.lower() == "true"
        # Try integer
        elif value.isdigit():
            parsed_value = int(value)
        # Try float
        elif "." in value and value.replace(".", "").isdigit():
            parsed_value = float(value)
        else:
            parsed_value = value
    except Exception:
        parsed_value = value

    if manager.set(path, parsed_value):
        console.print(f"[green]✅ Set {path} = {parsed_value}[/green]")

        # Auto-save
        if manager.save():
            console.print("[dim]Configuration saved[/dim]")
    else:
        console.print(f"[red]❌ Failed to set {path}[/red]")


@settings.command()
@click.option("--profile", "-p", help="Apply a profile first")
def wizard(profile):
    """Interactive configuration wizard"""
    console.print("[bold blue]🧙 Nix for Humanity Configuration Wizard[/bold blue]\n")

    manager = get_config_manager()
    config = manager.config

    # Apply profile if specified
    if profile:
        if manager.apply_profile(profile):
            console.print(f"[green]Applied profile: {profile}[/green]\n")
        else:
            console.print(f"[red]Profile not found: {profile}[/red]\n")

    # UI Settings
    console.print("[bold]User Interface Settings[/bold]")

    personalities = [p.value for p in Personality]
    current_personality = config.ui.default_personality.value
    personality = Prompt.ask(
        "Default personality", choices=personalities, default=current_personality
    )
    config.ui.default_personality = Personality(personality)

    config.ui.show_commands = Confirm.ask(
        "Show underlying Nix commands?", default=config.ui.show_commands
    )

    config.ui.use_colors = Confirm.ask(
        "Use colored output?", default=config.ui.use_colors
    )

    # Performance Settings
    console.print("\n[bold]Performance Settings[/bold]")

    config.performance.fast_mode = Confirm.ask(
        "Enable fast mode (speed over accuracy)?", default=config.performance.fast_mode
    )

    config.performance.timeout = IntPrompt.ask(
        "Command timeout (seconds)",
        default=config.performance.timeout,
        show_default=True,
    )

    # Privacy Settings
    console.print("\n[bold]Privacy Settings[/bold]")

    config.privacy.local_only = Confirm.ask(
        "Keep all data local only?", default=config.privacy.local_only
    )

    config.privacy.share_anonymous_stats = Confirm.ask(
        "Share anonymous usage statistics to improve the system?",
        default=config.privacy.share_anonymous_stats,
    )

    # Learning Settings
    console.print("\n[bold]Learning Settings[/bold]")

    config.learning.enabled = Confirm.ask(
        "Enable learning from your interactions?", default=config.learning.enabled
    )

    if config.learning.enabled:
        config.learning.personal_preferences = Confirm.ask(
            "Learn your personal preferences?",
            default=config.learning.personal_preferences,
        )

    # Voice Settings
    console.print("\n[bold]Voice Interface[/bold]")

    config.voice.enabled = Confirm.ask(
        "Enable voice interface?", default=config.voice.enabled
    )

    if config.voice.enabled:
        config.voice.wake_word = Prompt.ask("Wake word", default=config.voice.wake_word)

    # Save configuration
    console.print("\n[bold]Save Configuration[/bold]")

    # Show summary
    changes = [
        f"Personality: {config.ui.default_personality.value}",
        f"Show commands: {config.ui.show_commands}",
        f"Fast mode: {config.performance.fast_mode}",
        f"Learning enabled: {config.learning.enabled}",
        f"Voice enabled: {config.voice.enabled}",
    ]

    console.print(
        Panel("\n".join(changes), title="Configuration Summary", border_style="green")
    )

    if Confirm.ask("\nSave this configuration?", default=True):
        if manager.save():
            console.print("[bold green]✅ Configuration saved![/bold green]")

            # Offer to save as profile
            if Confirm.ask("\nSave as a reusable profile?", default=False):
                profile_name = Prompt.ask("Profile name")
                description = Prompt.ask("Profile description", default="")

                if manager.save_as_profile(profile_name, description):
                    console.print(f"[green]✅ Saved profile: {profile_name}[/green]")
                else:
                    console.print("[red]❌ Failed to save profile[/red]")
        else:
            console.print("[red]❌ Failed to save configuration[/red]")


@settings.command()
def profiles():
    """List available profiles"""
    manager = get_config_manager()
    profiles = manager.list_profiles()

    console.print("[bold blue]📋 Available Profiles[/bold blue]\n")

    # Group profiles
    built_in = []
    custom = []

    for profile_name in profiles:
        profile = manager.get_profile(profile_name)
        if profile_name in manager.profile_manager.BUILT_IN_PROFILES:
            built_in.append((profile_name, profile))
        else:
            custom.append((profile_name, profile))

    # Show built-in profiles
    if built_in:
        table = Table(
            title="Built-in Profiles", show_header=True, header_style="bold magenta"
        )
        table.add_column("Profile", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Key Features", style="yellow")

        for name, profile in built_in:
            features = []
            overrides = profile.config_overrides

            if "ui" in overrides:
                if "default_personality" in overrides["ui"]:
                    features.append(
                        f"Personality: {overrides['ui']['default_personality']}"
                    )

            if "performance" in overrides:
                if overrides["performance"].get("fast_mode"):
                    features.append("Fast mode")

            if "voice" in overrides:
                if overrides["voice"].get("enabled"):
                    features.append("Voice enabled")

            if "accessibility" in overrides:
                if overrides["accessibility"].get("screen_reader"):
                    features.append("Screen reader")

            table.add_row(name, profile.description, ", ".join(features[:3]))

        console.print(table)
        console.print()

    # Show custom profiles
    if custom:
        table = Table(
            title="Custom Profiles", show_header=True, header_style="bold magenta"
        )
        table.add_column("Profile", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Created", style="dim")

        for name, profile in custom:
            created = profile.created_at[:10] if profile.created_at else "Unknown"
            table.add_row(name, profile.description or "No description", created)

        console.print(table)
        console.print()

    console.print(f"[dim]Total profiles: {len(profiles)}[/dim]")


@settings.command()
@click.argument("profile_name")
def use(profile_name):
    """Apply a profile to current configuration"""
    manager = get_config_manager()

    if manager.apply_profile(profile_name):
        console.print(f"[green]✅ Applied profile: {profile_name}[/green]")

        # Show some key settings
        config = manager.config
        console.print("\n[bold]Active Settings:[/bold]")
        console.print(f"  • Personality: {config.ui.default_personality.value}")
        console.print(f"  • Fast mode: {config.performance.fast_mode}")
        console.print(f"  • Learning: {config.learning.enabled}")
        console.print(f"  • Voice: {config.voice.enabled}")

        # Auto-save
        if manager.save():
            console.print("\n[dim]Configuration saved[/dim]")
    else:
        console.print(f"[red]❌ Profile not found: {profile_name}[/red]")
        console.print("\nAvailable profiles:")
        for p in manager.list_profiles():
            console.print(f"  • {p}")


@settings.command()
@click.argument("name")
@click.option("--description", "-d", help="Profile description")
def save_profile(name, description):
    """Save current configuration as a profile"""
    manager = get_config_manager()

    if manager.save_as_profile(name, description or ""):
        console.print(f"[green]✅ Saved profile: {name}[/green]")
    else:
        console.print("[red]❌ Failed to save profile[/red]")


@settings.command()
@click.argument("name")
def delete_profile(name):
    """Delete a custom profile"""
    manager = get_config_manager()

    # Confirm deletion
    if not Confirm.ask(f"Delete profile '{name}'?", default=False):
        return

    if manager.profile_manager.delete_profile(name):
        console.print(f"[green]✅ Deleted profile: {name}[/green]")
    else:
        console.print("[red]❌ Failed to delete profile (may be built-in)[/red]")


@settings.command()
def validate():
    """Validate current configuration"""
    manager = get_config_manager()
    errors = manager.validate()

    if errors:
        console.print("[red]❌ Configuration validation errors:[/red]")
        for error in errors:
            console.print(f"  • {error}")
    else:
        console.print("[green]✅ Configuration is valid![/green]")


@settings.command()
@click.option("--force", is_flag=True, help="Reset without confirmation")
def reset(force):
    """Reset configuration to defaults"""
    if not force:
        if not Confirm.ask("Reset all settings to defaults?", default=False):
            return

    manager = get_config_manager()
    if manager.reset():
        console.print("[green]✅ Configuration reset to defaults[/green]")

        if manager.save():
            console.print("[dim]Configuration saved[/dim]")
    else:
        console.print("[red]❌ Failed to reset configuration[/red]")


@settings.command()
def aliases():
    """Show command aliases and shortcuts"""
    manager = get_config_manager()

    console.print("[bold blue]🔤 Command Aliases & Shortcuts[/bold blue]\n")

    # Show aliases
    aliases = manager.get_aliases()
    if aliases:
        table = Table(title="Aliases", show_header=True, header_style="bold magenta")
        table.add_column("Alias", style="cyan", no_wrap=True)
        table.add_column("Command", style="white")

        for alias, command in sorted(aliases.items()):
            table.add_row(alias, command)

        console.print(table)
        console.print()

    # Show shortcuts
    shortcuts = manager.get_shortcuts()
    if shortcuts:
        table = Table(title="Shortcuts", show_header=True, header_style="bold magenta")
        table.add_column("Shortcut", style="cyan", no_wrap=True)
        table.add_column("Commands", style="white")

        for name, commands in sorted(shortcuts.items()):
            commands_str = "\n".join(f"→ {cmd}" for cmd in commands)
            table.add_row(name, commands_str)

        console.print(table)


@settings.command()
@click.argument("alias")
@click.argument("command")
def add_alias(alias, command):
    """Add a command alias

    Examples:
        ask-nix settings add-alias up "update system"
        ask-nix settings add-alias gc "collect garbage"
    """
    manager = get_config_manager()

    if manager.add_alias(alias, command):
        console.print(f"[green]✅ Added alias: {alias} → {command}[/green]")

        if manager.save():
            console.print("[dim]Configuration saved[/dim]")
    else:
        console.print("[red]❌ Failed to add alias[/red]")


@settings.command()
@click.argument("name")
@click.argument("commands", nargs=-1, required=True)
def add_shortcut(name, commands):
    """Add a command shortcut

    Examples:
        ask-nix settings add-shortcut dev-setup "install git" "install vim" "install docker"
    """
    manager = get_config_manager()

    if manager.add_shortcut(name, list(commands)):
        console.print(f"[green]✅ Added shortcut: {name}[/green]")
        for cmd in commands:
            console.print(f"  → {cmd}")

        if manager.save():
            console.print("\n[dim]Configuration saved[/dim]")
    else:
        console.print("[red]❌ Failed to add shortcut[/red]")


@settings.command()
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json", "toml"]),
    default="yaml",
    help="Export format",
)
def export(output, format):
    """Export configuration to file"""
    manager = get_config_manager()

    config_str = manager.export(format)
    if not config_str:
        console.print("[red]Error exporting configuration[/red]")
        return

    if output:
        try:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            with open(output, "w") as f:
                f.write(config_str)
            console.print(f"[green]✅ Exported configuration to {output}[/green]")
        except Exception as e:
            console.print(f"[red]Error writing file: {e}[/red]")
    else:
        # Print to console
        syntax = Syntax(config_str, format, theme="monokai", line_numbers=True)
        console.print(
            Panel(syntax, title=f"Configuration ({format})", border_style="blue")
        )


@settings.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json", "toml"]),
    help="File format (auto-detected if not specified)",
)
def import_config(file, format):
    """Import configuration from file"""
    manager = get_config_manager()

    try:
        with open(file) as f:
            content = f.read()

        # Auto-detect format if not specified
        if not format:
            if file.endswith(".yaml") or file.endswith(".yml"):
                format = "yaml"
            elif file.endswith(".json"):
                format = "json"
            elif file.endswith(".toml"):
                format = "toml"
            else:
                console.print("[yellow]Could not detect format, assuming YAML[/yellow]")
                format = "yaml"

        if manager.import_config(content, format):
            console.print(f"[green]✅ Imported configuration from {file}[/green]")

            # Show summary
            config = manager.config
            console.print("\n[bold]Imported Settings:[/bold]")
            console.print(f"  • Personality: {config.ui.default_personality.value}")
            console.print(f"  • Fast mode: {config.performance.fast_mode}")
            console.print(f"  • Learning: {config.learning.enabled}")

            if Confirm.ask("\nSave imported configuration?", default=True):
                if manager.save():
                    console.print("[green]✅ Configuration saved[/green]")
        else:
            console.print("[red]❌ Failed to import configuration[/red]")

    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")


if __name__ == "__main__":
    settings()
