#!/usr/bin/env python3
"""
Configuration management commands for Nix for Humanity
"""

import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from nix_for_humanity.core.config_generator import NixConfigGenerator

console = Console()


@click.group()
def config():
    """Manage NixOS configuration files"""
    pass


@config.command()
@click.argument("description", nargs=-1, required=True)
@click.option("--output", "-o", help="Output file path")
@click.option("--preview", "-p", is_flag=True, help="Preview without saving")
def generate(description, output, preview):
    """Generate NixOS configuration from natural language

    Examples:
        ask-nix config generate "web server with nginx and postgresql"
        ask-nix config generate "desktop with KDE" -o /tmp/config.nix
    """
    # Join description parts
    natural_language = " ".join(description)

    console.print(
        f"[bold blue]🔧 Generating configuration for:[/bold blue] {natural_language}"
    )

    # Generate configuration
    generator = NixConfigGenerator()
    intent = generator.parse_intent(natural_language)

    # Show what we understood
    console.print("\n[bold]Understanding:[/bold]")
    if intent["modules"]:
        console.print(f"  • Modules: {', '.join(intent['modules'])}")
    if intent["packages"]:
        console.print(f"  • Packages: {', '.join(intent['packages'])}")
    if intent["users"]:
        console.print(f"  • Users: {', '.join([u['name'] for u in intent['users']])}")

    # Check for conflicts
    conflicts = generator.check_conflicts(intent["modules"])
    if conflicts:
        console.print("\n[bold red]⚠️  Conflicts detected:[/bold red]")
        for m1, m2 in conflicts:
            console.print(f"  • {m1} conflicts with {m2}")

        # Ask user to resolve
        choices = list(set([m for conflict in conflicts for m in conflict]))
        choice = Prompt.ask("\nWhich module would you like to use?", choices=choices)

        # Remove conflicting modules
        intent["modules"] = [
            m
            for m in intent["modules"]
            if m == choice or m not in [c for conflict in conflicts for c in conflict]
        ]

    # Generate config
    config_content = generator.generate_config(intent)

    # Show preview
    console.print("\n[bold]Generated Configuration:[/bold]")
    syntax = Syntax(config_content, "nix", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="configuration.nix", border_style="blue"))

    # Save if requested
    if not preview:
        if output:
            save_path = output
        else:
            save_path = Prompt.ask(
                "\nWhere should I save this?", default="/tmp/configuration.nix"
            )

        # Check if file exists
        if os.path.exists(save_path):
            if not Confirm.ask(
                f"\n{save_path} already exists. Create backup?", default=True
            ):
                return

        success, message = generator.save_config(config_content, save_path, backup=True)
        if success:
            console.print(f"\n[bold green]✅ {message}[/bold green]")
            console.print("\n[yellow]To apply this configuration:[/yellow]")
            console.print(f"  sudo cp {save_path} /etc/nixos/configuration.nix")
            console.print("  sudo nixos-rebuild switch")
        else:
            console.print(f"\n[bold red]❌ {message}[/bold red]")


@config.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate(config_file):
    """Validate a NixOS configuration file"""
    console.print(f"[bold blue]🔍 Validating:[/bold blue] {config_file}")

    generator = NixConfigGenerator()
    valid, message = generator.validate_config(config_file)

    if valid:
        console.print(f"\n[bold green]✅ {message}[/bold green]")
    else:
        console.print(f"\n[bold red]❌ {message}[/bold red]")


@config.command()
@click.argument("config_file", type=click.Path(exists=True))
def explain(config_file):
    """Explain what a configuration does in plain language"""
    console.print(f"[bold blue]📖 Explaining:[/bold blue] {config_file}")

    generator = NixConfigGenerator()
    explanation = generator.explain_config(config_file)

    console.print(
        Panel(explanation, title="Configuration Explanation", border_style="green")
    )


@config.command()
@click.argument("old_config", type=click.Path(exists=True))
@click.argument("new_config", type=click.Path(exists=True))
def diff(old_config, new_config):
    """Show differences between two configurations"""
    console.print("[bold blue]📊 Comparing configurations:[/bold blue]")
    console.print(f"  • Old: {old_config}")
    console.print(f"  • New: {new_config}")

    generator = NixConfigGenerator()
    diff_output = generator.diff_configs(old_config, new_config)

    if diff_output:
        syntax = Syntax(diff_output, "diff", theme="monokai")
        console.print(
            Panel(syntax, title="Configuration Differences", border_style="yellow")
        )
    else:
        console.print("\n[green]No differences found![/green]")


@config.command()
def templates():
    """Show available configuration templates"""
    console.print("[bold blue]📋 Available Configuration Templates:[/bold blue]\n")

    generator = NixConfigGenerator()

    # Group modules by category
    categories = {
        "Boot Loaders": [],
        "Desktop Environments": [],
        "Web Servers": [],
        "Databases": [],
        "Development Tools": [],
        "Security": [],
    }

    for name, module in generator.modules_db.items():
        if name.startswith("boot."):
            categories["Boot Loaders"].append((name, module))
        elif name.startswith("desktop."):
            categories["Desktop Environments"].append((name, module))
        elif name.startswith("web."):
            categories["Web Servers"].append((name, module))
        elif name.startswith("db."):
            categories["Databases"].append((name, module))
        elif name.startswith("dev."):
            categories["Development Tools"].append((name, module))
        elif name.startswith("security."):
            categories["Security"].append((name, module))

    for category, modules in categories.items():
        if modules:
            table = Table(title=category, show_header=True, header_style="bold magenta")
            table.add_column("Module", style="cyan", no_wrap=True)
            table.add_column("Description", style="white")
            table.add_column("Conflicts", style="yellow")

            for name, module in modules:
                conflicts = ", ".join(module.conflicts) if module.conflicts else "None"
                table.add_row(name, module.description, conflicts)

            console.print(table)
            console.print()


@config.command()
def wizard():
    """Interactive configuration wizard"""
    console.print("[bold blue]🧙 NixOS Configuration Wizard[/bold blue]\n")
    console.print("Let's create your perfect NixOS configuration!\n")

    generator = NixConfigGenerator()
    intent = {
        "modules": [],
        "packages": [],
        "users": [],
        "settings": {},
        "action": "generate",
    }

    # Ask about system type
    system_type = Prompt.ask(
        "What kind of system are you building?",
        choices=["desktop", "server", "development", "minimal"],
        default="desktop",
    )

    # Desktop configuration
    if system_type == "desktop":
        de = Prompt.ask(
            "\nWhich desktop environment?",
            choices=["gnome", "kde", "xfce", "none"],
            default="gnome",
        )
        if de == "gnome":
            intent["modules"].append("desktop.gnome")
        elif de == "kde":
            intent["modules"].append("desktop.kde")

        # Common desktop packages
        if Confirm.ask("\nInclude common desktop applications?", default=True):
            intent["packages"].extend(["firefox", "vlc", "libreoffice"])

    # Server configuration
    elif system_type == "server":
        if Confirm.ask("\nInclude web server?", default=True):
            web = Prompt.ask(
                "Which web server?", choices=["nginx", "apache"], default="nginx"
            )
            intent["modules"].append(f"web.{web}")

        if Confirm.ask("\nInclude database?", default=False):
            db = Prompt.ask(
                "Which database?", choices=["postgresql", "mysql"], default="postgresql"
            )
            intent["modules"].append(f"db.{db}")

        intent["modules"].append("security.firewall")
        intent["modules"].append("security.ssh")

    # Development configuration
    elif system_type == "development":
        if Confirm.ask("\nInclude Docker?", default=True):
            intent["modules"].append("dev.docker")
        if Confirm.ask("\nInclude VS Code?", default=True):
            intent["modules"].append("dev.vscode")

        intent["packages"].extend(["git", "vim", "tmux", "htop"])

    # Common questions
    hostname = Prompt.ask("\nWhat should we call this system?", default="nixos")
    intent["settings"]["hostname"] = hostname

    # Users
    if Confirm.ask("\nAdd a user account?", default=True):
        username = Prompt.ask("Username")
        admin = Confirm.ask("Give admin (sudo) access?", default=True)
        intent["users"].append({"name": username, "admin": admin})

    # Additional packages
    if Confirm.ask("\nAdd additional packages?", default=False):
        packages = Prompt.ask("List packages (space-separated)")
        intent["packages"].extend(packages.split())

    # Generate configuration
    console.print("\n[bold]Generating your configuration...[/bold]")
    config_content = generator.generate_config(intent)

    # Show result
    syntax = Syntax(config_content, "nix", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Your Configuration", border_style="green"))

    # Save
    if Confirm.ask("\nSave this configuration?", default=True):
        save_path = Prompt.ask("Save to", default="/tmp/configuration.nix")
        success, message = generator.save_config(config_content, save_path, backup=True)

        if success:
            console.print(f"\n[bold green]✅ {message}[/bold green]")
            console.print("\n[yellow]Next steps:[/yellow]")
            console.print(f"1. Review: cat {save_path}")
            console.print(
                f"2. Test: sudo nixos-rebuild test -I nixos-config={save_path}"
            )
            console.print(
                f"3. Apply: sudo cp {save_path} /etc/nixos/configuration.nix && sudo nixos-rebuild switch"
            )
        else:
            console.print(f"\n[bold red]❌ {message}[/bold red]")


if __name__ == "__main__":
    config()
