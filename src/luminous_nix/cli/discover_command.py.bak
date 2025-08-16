#!/usr/bin/env python3
"""
from typing import Optional
CLI commands for smart package discovery
"""


import click
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nix_for_humanity.nlp.personas import PersonaManager
from nix_for_humanity.utils.logger import get_logger

from ..core.package_discovery import PackageDiscovery

console = Console()
logger = get_logger(__name__)


@click.group(name="discover")
def discover_group():
    """Smart package discovery commands"""
    pass


@discover_group.command(name="search")
@click.argument("query", nargs=-1, required=True)
@click.option("--limit", "-l", default=10, help="Maximum results to show")
@click.option("--persona", "-p", help="Use specific persona style")
def search_packages(query: tuple, limit: int, persona: str | None):
    """Search for packages using natural language

    Examples:
        ask-nix discover search i need a web browser
        ask-nix discover search tool for editing photos
        ask-nix discover search something to play music
    """
    query_str = " ".join(query)
    discovery = PackageDiscovery()
    persona_mgr = PersonaManager()

    # Set persona if specified
    if persona:
        persona_mgr.set_persona(persona)

    console.print(f"\n🔍 Searching for: [cyan]{query_str}[/cyan]\n")

    # Search for packages
    results = discovery.search_packages(query_str, limit=limit)

    if not results:
        console.print(f"[yellow]No packages found matching '{query_str}'[/yellow]")
        console.print("\nTry:")
        console.print("  • Using different keywords")
        console.print("  • Browsing categories with 'discover browse'")
        console.print("  • Searching by command with 'discover command'")
        return

    # Create results table
    table = Table(
        title=f"Package Matches for '{query_str}'", box=box.ROUNDED, show_lines=True
    )

    table.add_column("Package", style="cyan", width=20)
    table.add_column("Description", style="white", width=40)
    table.add_column("Match Score", style="green", width=12)
    table.add_column("Reason", style="yellow", width=25)

    for match in results:
        score_bar = "▰" * int(match.score * 10) + "▱" * (10 - int(match.score * 10))
        table.add_row(
            match.name,
            match.description,
            f"{score_bar} {match.score:.1f}",
            match.reason,
        )

    console.print(table)

    # Show installation commands
    console.print("\n📦 To install a package:")
    console.print(f"   [green]ask-nix install {results[0].name}[/green]")
    console.print(
        f"   [dim]or[/dim] [green]nix-env -iA nixpkgs.{results[0].name}[/green]"
    )

    # Show alternatives for top result
    if results:
        alternatives = discovery.find_alternatives(results[0].name)
        if alternatives:
            console.print(
                f"\n🔄 Similar to {results[0].name}: {', '.join(alternatives[:3])}"
            )

    # Persona-styled response
    response = persona_mgr.format_response(
        f"Found {len(results)} packages matching your search.",
        {
            "action": "search",
            "query": query_str,
            "results": len(results),
            "top_match": results[0].name if results else None,
        },
    )

    console.print(f"\n{response}")


@discover_group.command(name="info")
@click.argument("package")
@click.option("--persona", "-p", help="Use specific persona style")
def package_info(package: str, persona: str | None):
    """Get detailed information about a package"""
    discovery = PackageDiscovery()
    persona_mgr = PersonaManager()

    if persona:
        persona_mgr.set_persona(persona)

    info = discovery.get_package_info(package)

    if not info:
        console.print(f"[red]Package '{package}' not found[/red]")
        return

    # Create info panel
    content = f"""[cyan]Package:[/cyan] {info.name}
[cyan]Description:[/cyan] {info.description}
[cyan]Version:[/cyan] {info.version or 'Latest'}
[cyan]Homepage:[/cyan] {info.homepage or 'Not available'}
[cyan]License:[/cyan] {info.license or 'Check package'}
[cyan]Platforms:[/cyan] {', '.join(info.platforms)}"""

    panel = Panel(
        content, title=f"📦 {info.name}", border_style="blue", box=box.ROUNDED
    )

    console.print(panel)

    # Show common commands
    if info.common_commands:
        console.print("\n🔧 Common commands:")
        for cmd in info.common_commands[:5]:
            console.print(f"   • [green]{cmd}[/green]")

    # Show similar packages
    if info.similar_packages:
        console.print("\n🔄 Similar packages:")
        similar_table = Table(show_header=False, box=None)
        similar_table.add_column("Package", style="cyan")

        for pkg in info.similar_packages[:5]:
            similar_table.add_row(f"• {pkg}")

        console.print(similar_table)

    # Installation command
    console.print("\n📥 To install:")
    console.print(f"   [green]ask-nix install {package}[/green]")

    # Persona response
    response = persona_mgr.format_response(
        f"Package information for {package}", {"action": "info", "package": package}
    )

    console.print(f"\n{response}")


@discover_group.command(name="command")
@click.argument("command")
@click.option("--persona", "-p", help="Use specific persona style")
def find_by_command(command: str, persona: str | None):
    """Find packages that provide a specific command

    Example:
        ask-nix discover command python
        ask-nix discover command npm
        ask-nix discover command cargo
    """
    discovery = PackageDiscovery()
    persona_mgr = PersonaManager()

    if persona:
        persona_mgr.set_persona(persona)

    console.print(f"\n🔧 Command '{command}' not found\n")

    suggestions = discovery.suggest_by_command(command)

    if not suggestions:
        console.print(f"[yellow]No packages found that provide '{command}'[/yellow]")
        console.print("\nThe command might be:")
        console.print("  • Part of a different package")
        console.print("  • Available under a different name")
        console.print("  • Not yet packaged for NixOS")
        return

    console.print("📦 These packages provide this command:\n")

    for i, match in enumerate(suggestions, 1):
        console.print(f"{i}. [cyan]{match.name}[/cyan]")
        console.print(f"   {match.description}")
        console.print(f"   Install: [green]nix-env -iA nixpkgs.{match.name}[/green]\n")

    # Quick install option
    if suggestions:
        console.print("💡 Quick install the most likely match:")
        console.print(f"   [green]ask-nix install {suggestions[0].name}[/green]")

    # Persona response
    response = persona_mgr.format_response(
        f"Found {len(suggestions)} packages that provide '{command}'",
        {
            "action": "command_search",
            "command": command,
            "suggestions": len(suggestions),
        },
    )

    console.print(f"\n{response}")


@discover_group.command(name="browse")
@click.option("--category", "-c", help="Browse specific category")
@click.option("--persona", "-p", help="Use specific persona style")
def browse_packages(category: str | None, persona: str | None):
    """Browse packages by category"""
    discovery = PackageDiscovery()
    persona_mgr = PersonaManager()

    if persona:
        persona_mgr.set_persona(persona)

    categories = discovery.browse_categories()

    if category:
        # Show specific category
        if category not in categories:
            console.print(f"[red]Category '{category}' not found[/red]")
            console.print(f"\nAvailable categories: {', '.join(categories.keys())}")
            return

        cat_info = categories[category]

        # Category panel
        panel = Panel(
            f"[cyan]Keywords:[/cyan] {', '.join(cat_info['keywords'])}\n"
            f"[cyan]Description:[/cyan] {cat_info['description']}",
            title=f"📁 {category.title()} Packages",
            border_style="blue",
        )

        console.print(panel)

        # Packages table
        table = Table(title="Top Packages", box=box.SIMPLE, show_lines=False)

        table.add_column("Package", style="cyan", width=20)
        table.add_column("Install Command", style="green", width=50)

        for pkg in cat_info["top_packages"]:
            table.add_row(pkg, f"ask-nix install {pkg}")

        console.print(table)

    else:
        # Show all categories
        console.print("\n📚 [bold]Package Categories[/bold]\n")

        cards = []
        for cat_name, cat_info in categories.items():
            card = Panel(
                f"[yellow]{', '.join(cat_info['keywords'][:3])}...[/yellow]\n\n"
                f"[cyan]Top packages:[/cyan]\n"
                + "\n".join(f"• {pkg}" for pkg in cat_info["top_packages"][:3]),
                title=f"📁 {cat_name.title()}",
                width=40,
                height=10,
            )
            cards.append(card)

        # Display in columns
        console.print(Columns(cards[:6], equal=True, expand=True))

        console.print("\n💡 To browse a specific category:")
        console.print(
            "   [green]ask-nix discover browse --category development[/green]"
        )

    # Persona response
    action = f"browse_{category}" if category else "browse_all"
    response = persona_mgr.format_response(
        f"Browsing {'packages in ' + category if category else 'all categories'}",
        {"action": action},
    )

    console.print(f"\n{response}")


@discover_group.command(name="popular")
@click.option("--category", "-c", help="Show popular packages in category")
@click.option("--persona", "-p", help="Use specific persona style")
def popular_packages(category: str | None, persona: str | None):
    """Show popular packages"""
    discovery = PackageDiscovery()
    persona_mgr = PersonaManager()

    if persona:
        persona_mgr.set_persona(persona)

    title = f"Popular {category.title()} Packages" if category else "Popular Packages"
    console.print(f"\n⭐ [bold]{title}[/bold]\n")

    popular = discovery.get_popular_packages(category)

    if not popular:
        console.print(
            f"[yellow]No popular packages found{' in ' + category if category else ''}[/yellow]"
        )
        return

    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("Package", style="cyan", width=15)
    table.add_column("Description", style="white", width=40)
    table.add_column("Quick Install", style="green", width=30)

    for pkg_name, pkg_desc in popular:
        table.add_row(pkg_name, pkg_desc, f"ask-nix install {pkg_name}")

    console.print(table)

    # Persona response
    response = persona_mgr.format_response(
        f"Showing {len(popular)} popular packages",
        {"action": "popular", "category": category, "count": len(popular)},
    )

    console.print(f"\n{response}")


# Register with main CLI
def register_commands(cli):
    """Register discover commands with main CLI"""
    cli.add_command(discover_group)
