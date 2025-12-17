"""
`did setup` command - Interactive DID setup wizard
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from typing import Optional

from luminous_nix.mycelix.identity import get_did_manager
from luminous_nix.core.user_profile import get_profile_manager


def cmd_did_setup(storage_path: Optional[str] = None, auto_passphrase: Optional[str] = None, force: bool = False):
    """Interactive DID setup wizard

    Args:
        storage_path: Optional storage path for testing
        auto_passphrase: Automatically use this passphrase (for testing)
        force: Skip confirmation if DID already exists (for testing)
    """
    console = Console()

    # Welcome
    console.print(Panel.fit(
        "[bold cyan]🌟 Luminous Nix Identity Setup[/bold cyan]\n\n"
        "Create your decentralized identity (DID) to:\n"
        "• Track your trust and reputation\n"
        "• Sync across devices (coming soon)\n"
        "• Recover your account with guardians (coming soon)\n",
        border_style="cyan"
    ))

    # Check if DID already exists
    if storage_path:
        from pathlib import Path
        from luminous_nix.mycelix.identity import DIDManager
        did_mgr = DIDManager(storage_path=Path(storage_path) / "identity")
    else:
        did_mgr = get_did_manager()

    existing_did = did_mgr.get_current_did()

    if existing_did and not force:
        console.print(f"\n[yellow]⚠️  You already have a DID:[/yellow] {existing_did.did}")
        if not Confirm.ask("Create a new one? (This will replace your current DID)"):
            console.print("[dim]Setup cancelled.[/dim]")
            return

    # Get passphrase
    console.print("\n[bold]Step 1: Secure Your Identity[/bold]")
    console.print("Choose a passphrase to encrypt your private key.")
    console.print("[dim]Tip: Use a passphrase you'll remember, or use a password manager.[/dim]")

    if auto_passphrase:
        # For testing - use auto passphrase
        passphrase = auto_passphrase
        console.print(f"\n[dim]Using auto-passphrase for testing...[/dim]")
    else:
        passphrase = Prompt.ask("\nEnter passphrase", password=True)
        passphrase_confirm = Prompt.ask("Confirm passphrase", password=True)

        if passphrase != passphrase_confirm:
            console.print("[red]❌ Passphrases don't match! Please try again.[/red]")
            return

    # Create DID
    console.print("\n[bold]Creating your DID...[/bold]")

    if storage_path:
        from pathlib import Path
        from luminous_nix.mycelix.identity import DIDManager
        did_mgr = DIDManager(storage_path=Path(storage_path) / "identity")

    user_did = did_mgr.create_did(passphrase=passphrase)

    # Initialize profile
    if storage_path:
        from pathlib import Path
        from luminous_nix.core.user_profile import UserProfileManager
        profile_mgr = UserProfileManager(storage_path=Path(storage_path))
    else:
        profile_mgr = get_profile_manager()

    profile_mgr.load_or_create(passphrase=passphrase)

    # Success
    console.print(Panel.fit(
        f"[bold green]✅ Identity Created Successfully![/bold green]\n\n"
        f"Your DID: [cyan]{user_did.did}[/cyan]\n"
        f"Assurance Level: [yellow]{user_did.assurance_level}[/yellow] (Basic)\n\n"
        f"[dim]Run 'ask-nix whoami' to view your identity anytime.[/dim]",
        border_style="green"
    ))


if __name__ == "__main__":
    cmd_did_setup()
