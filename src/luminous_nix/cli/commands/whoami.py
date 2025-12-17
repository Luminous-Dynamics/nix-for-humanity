"""
`whoami` command - Show current user identity and trust status
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional

from luminous_nix.mycelix.identity import get_did_manager
from luminous_nix.core.user_profile import get_profile_manager


def cmd_whoami(storage_path: Optional[str] = None):
    """Show current user identity and status"""
    console = Console()

    # Get user profile and DID manager
    if storage_path:
        from pathlib import Path
        from luminous_nix.core.user_profile import UserProfileManager
        from luminous_nix.mycelix.identity import DIDManager

        profile_mgr = UserProfileManager(storage_path=Path(storage_path))
        did_mgr = DIDManager(storage_path=Path(storage_path) / "identity")
    else:
        profile_mgr = get_profile_manager()
        did_mgr = get_did_manager()

    # Check if DID exists
    current_did = did_mgr.get_current_did()

    if not current_did:
        console.print(Panel.fit(
            "[yellow]No identity found.[/yellow]\n\n"
            "Run [cyan]ask-nix did setup[/cyan] to create your decentralized identity.",
            title="Luminous Nix Identity",
            border_style="yellow"
        ))
        return

    # Load full profile
    profile = profile_mgr.get_profile()

    if not profile:
        # Fallback to just DID info
        profile_mgr.load_or_create()
        profile = profile_mgr.get_profile()

    # Create display table
    table = Table(title="🌟 Your Luminous Nix Identity", show_header=True, title_style="bold cyan")
    table.add_column("Property", style="cyan", width=20)
    table.add_column("Value", style="green")

    # Identity
    table.add_row("DID", current_did.did)
    table.add_row("Created", current_did.created_at[:19])  # Remove microseconds

    # Assurance level with description
    assurance_desc = {
        "E0": "Basic (local only)",
        "E1": "Device verified",
        "E2": "Social recovery enabled",
        "E3": "Multi-device synced",
        "E4": "Fully distributed"
    }.get(current_did.assurance_level, "Unknown")
    table.add_row("Assurance Level", f"{current_did.assurance_level} ({assurance_desc})")

    # Trust (placeholder for Week 3)
    if profile.matl_score > 0:
        table.add_row("Trust Score", f"{profile.matl_score:.2f}/1.00")
    else:
        table.add_row("Trust Score", "[dim]Building...[/dim]")

    # Usage stats
    table.add_row("Total Operations", str(profile.total_operations))

    if profile.total_operations > 0:
        success_rate = profile.get_success_rate()
        success_color = "green" if success_rate >= 0.8 else "yellow" if success_rate >= 0.6 else "red"
        table.add_row(
            "Success Rate",
            f"[{success_color}]{profile.successful_operations}/{profile.total_operations} ({success_rate:.1%})[/{success_color}]"
        )

    if profile.last_active:
        table.add_row("Last Active", profile.last_active[:19])

    console.print(table)
    console.print("\n[dim]💡 Your DID is your sovereign identity across all devices.[/dim]")


if __name__ == "__main__":
    cmd_whoami()
