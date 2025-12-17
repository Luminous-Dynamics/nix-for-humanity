"""
Mycelix CLI Commands for Luminous Nix

Commands:
- did: Show/manage your Decentralized Identity
- identity: Alias for 'did'
- matl: Show your MATL trust score (coming in Week 3)
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@click.group()
def mycelix():
    """Mycelix Protocol integration commands (Layer 7)."""
    pass


@mycelix.command()
@click.option('--create', is_flag=True, help='Create new DID')
@click.option('--passphrase', help='Passphrase for DID encryption')
@click.option('--show', is_flag=True, default=True, help='Show current DID (default)')
def did(create, passphrase, show):
    """
    Manage your Decentralized Identity (DID).

    Your DID is your sovereign identity in the Mycelix network.
    It works across devices and is controlled only by you.

    Examples:
        luminous-nix mycelix did                    # Show current DID
        luminous-nix mycelix did --create          # Create new DID
    """
    from luminous_nix.mycelix import get_did_manager

    manager = get_did_manager()

    if create:
        # Create new DID
        console.print("\n[bold cyan]Creating new Mycelix DID...[/bold cyan]\n")

        # Get passphrase if not provided
        if not passphrase:
            import getpass
            passphrase = getpass.getpass("Enter passphrase (or press Enter for auto-generated): ")
            if not passphrase:
                passphrase = None  # Will auto-generate

        try:
            user_did = manager.create_did(passphrase)
            _display_did(user_did, is_new=True)

        except Exception as e:
            console.print(f"[bold red]Error creating DID:[/bold red] {e}")
            return 1

    elif show:
        # Show existing DID
        try:
            user_did = manager.get_current_did()

            if user_did:
                _display_did(user_did, is_new=False)
            else:
                console.print("\n[yellow]No DID found.[/yellow]")
                console.print("Create one with: [cyan]luminous-nix mycelix did --create[/cyan]\n")
                return 1

        except Exception as e:
            console.print(f"[bold red]Error loading DID:[/bold red] {e}")
            return 1

    return 0


def _display_did(did, is_new=False):
    """Display DID information in a beautiful format."""
    from datetime import datetime

    # Header
    if is_new:
        console.print(Panel(
            "[bold green]✅ DID Created Successfully![/bold green]",
            style="green"
        ))
    else:
        console.print(Panel(
            "[bold cyan]Your Mycelix Identity[/bold cyan]",
            style="cyan"
        ))

    # Create info table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Property", style="cyan", width=20)
    table.add_column("Value", style="white")

    # DID
    table.add_row(
        "DID",
        f"[bold]{did.did}[/bold]"
    )

    # Created
    try:
        created = datetime.fromisoformat(did.created_at)
        created_str = created.strftime("%B %d, %Y at %I:%M %p")
    except:
        created_str = did.created_at

    table.add_row("Created", created_str)

    # Assurance Level
    assurance_info = {
        "E0": ("Basic", "No verification"),
        "E1": ("Email", "Email verified"),
        "E2": ("Social", "OAuth + Email"),
        "E3": ("Strong", "2+ factors + Passkey"),
        "E4": ("Maximum", "Government ID")
    }

    level, desc = assurance_info.get(did.assurance_level, ("Unknown", ""))
    table.add_row(
        "Assurance Level",
        f"{did.assurance_level} - {level} ({desc})"
    )

    # Recovery
    if did.recovery_guardians:
        recovery_str = f"{len(did.recovery_guardians)} guardians ({did.recovery_threshold} required)"
    else:
        recovery_str = "[yellow]Not configured[/yellow]"

    table.add_row("Social Recovery", recovery_str)

    console.print(table)

    # Capabilities
    console.print("\n[bold]What your DID enables:[/bold]")
    console.print("  • Sovereign identity (you own it, not any company)")
    console.print("  • Cross-device synchronization")
    console.print("  • Social recovery (never lose access)")
    console.print("  • MATL trust scoring (Byzantine resistance)")
    console.print("  • Future: Federated learning, DKG, Credits")

    # Storage location
    console.print(f"\n[dim]Stored at: {manager.did_file}[/dim]\n")


@mycelix.command()
def identity():
    """Alias for 'did' command."""
    import sys
    sys.argv = [sys.argv[0], 'did'] + sys.argv[2:]
    return did.main(standalone_mode=False)


@mycelix.command()
def matl():
    """
    Show your MATL trust score.

    MATL (Mycelix Adaptive Trust Layer) provides Byzantine-resistant
    trust scoring based on your interaction patterns.

    Coming in Week 3-4!
    """
    console.print("\n[bold cyan]MATL Trust Scoring[/bold cyan]\n")
    console.print("[yellow]Coming in Week 3-4![/yellow]")
    console.print("\nMATL will calculate your trust score based on:")
    console.print("  • PoGQ (Proof of Genuine Query) - Are you human or bot?")
    console.print("  • TCDM (Temporal Consistency) - Behavioral consistency")
    console.print("  • Entropy (Diversity) - Variety of commands used")
    console.print("\nComposite Score = (PoGQ × 0.4) + (TCDM × 0.3) + (Entropy × 0.3)\n")
    return 0


@mycelix.command()
def status():
    """
    Show Mycelix integration status.

    Displays what's implemented and what's coming.
    """
    console.print("\n[bold cyan]Mycelix Protocol Integration Status[/bold cyan]\n")

    # Layer 7 Phase 1 Status
    components = [
        ("Identity (DID)", "✅ Implemented", "Week 1", "green"),
        ("MATL Trust", "🔄 Coming", "Week 3-4", "yellow"),
        ("Epistemic Cube", "🔄 Coming", "Week 5-6", "yellow"),
        ("Credits System", "🔄 Coming", "Week 7-8", "yellow"),
        ("Cross-Device Sync", "🔮 Planned", "Week 9-10", "blue"),
        ("Social Recovery", "🔮 Planned", "Week 9-10", "blue"),
    ]

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Component", style="white", width=20)
    table.add_column("Status", width=15)
    table.add_column("Timeline", width=12)

    for name, status, timeline, color in components:
        table.add_row(name, f"[{color}]{status}[/{color}]", timeline)

    console.print(table)

    # Check current DID status
    from luminous_nix.mycelix import get_did_manager
    manager = get_did_manager()
    current_did = manager.get_current_did()

    if current_did:
        console.print(f"\n[green]✅ Your DID:[/green] {current_did.did}")
    else:
        console.print("\n[yellow]⚠️  No DID created yet.[/yellow]")
        console.print("   Create one: [cyan]luminous-nix mycelix did --create[/cyan]")

    console.print("\n[dim]Layer 7 Phase 1: 12-week implementation plan[/dim]\n")

    return 0


# Add to main CLI
def register_mycelix_commands(cli):
    """Register Mycelix commands with main CLI."""
    cli.add_command(mycelix)
