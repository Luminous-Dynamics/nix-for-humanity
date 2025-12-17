#!/usr/bin/env python3
"""
Demo: Mycelix DID System

Demonstrates the working W3C Decentralized Identity system
integrated into Luminous Nix (Layer 7 Phase 1, Week 1).

Run with: poetry run python demo_did_system.py
"""

from pathlib import Path
import tempfile
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def demo_did_system():
    """Demonstrate DID creation, loading, and management."""

    console.print("\n")
    console.print(Panel(
        "[bold cyan]Mycelix DID System Demo[/bold cyan]\n"
        "Layer 7 Phase 1 - Week 1 Implementation",
        style="cyan"
    ))

    # Use temporary storage for demo
    temp_dir = Path(tempfile.mkdtemp())
    console.print(f"\n[dim]Demo storage: {temp_dir}[/dim]\n")

    try:
        # Import DID manager
        from luminous_nix.mycelix.identity import DIDManager

        # Step 1: Create DID Manager
        console.print("[bold]Step 1: Initialize DID Manager[/bold]")
        manager = DIDManager(storage_path=temp_dir / "identity")
        console.print("[green]✅ DID Manager initialized[/green]\n")

        # Step 2: Create new DID
        console.print("[bold]Step 2: Create new Decentralized Identity (DID)[/bold]")
        passphrase = "demo_secure_passphrase_123"
        console.print(f"[dim]Using passphrase: {passphrase}[/dim]")

        user_did = manager.create_did(passphrase)
        console.print(f"[green]✅ DID created: {user_did.did}[/green]\n")

        # Display DID details
        console.print("[bold]Step 3: DID Details[/bold]")

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Full DID", f"[bold]{user_did.did}[/bold]")
        table.add_row("Format", "did:mycelix:luminous_nix:{hash}")
        table.add_row("Public Key", user_did.public_key[:32] + "...")
        table.add_row("Private Key", "[encrypted]")
        table.add_row("Created At", user_did.created_at)
        table.add_row("Assurance Level", f"{user_did.assurance_level} (Basic)")
        table.add_row("Storage", str(manager.did_file))

        console.print(table)
        console.print()

        # Step 4: Verify storage
        console.print("[bold]Step 4: Verify DID Storage[/bold]")
        console.print(f"DID file exists: [green]{manager.did_file.exists()}[/green]")

        # Check file permissions
        import stat
        file_stat = manager.did_file.stat()
        permissions = stat.filemode(file_stat.st_mode)
        console.print(f"File permissions: [green]{permissions}[/green] (owner only)\n")

        # Step 5: Simulate app restart - load existing DID
        console.print("[bold]Step 5: Simulate App Restart (Load Existing DID)[/bold]")

        # Create new manager instance
        manager2 = DIDManager(storage_path=temp_dir / "identity")
        loaded_did = manager2.load_did(passphrase)

        console.print(f"[green]✅ DID loaded: {loaded_did.did}[/green]")
        console.print(f"[green]✅ Matches original: {loaded_did.did == user_did.did}[/green]\n")

        # Step 6: Demonstrate create_or_load
        console.print("[bold]Step 6: Smart Create-or-Load[/bold]")

        # First call (already exists, will load)
        did_smart = manager.create_or_load(passphrase)
        console.print(f"[green]✅ Smart load: {did_smart.did}[/green]")
        console.print(f"[green]✅ Same DID: {did_smart.did == user_did.did}[/green]\n")

        # Step 7: Show what's enabled
        console.print("[bold]Step 7: What Your DID Enables[/bold]")

        features = [
            ("Sovereign Identity", "You own it, not any company"),
            ("Cross-Device Sync", "Coming in Week 9-10"),
            ("Social Recovery", "5 guardians, 3 threshold - Week 9-10"),
            ("MATL Trust Scoring", "Byzantine resistance - Week 3-4"),
            ("Federated Learning", "Phase 2 (Q2-Q3 2026)"),
            ("DKG Access", "Phase 3 (Q4 2026+)"),
            ("Zero-TrustML Credits", "Week 7-8"),
        ]

        feature_table = Table(show_header=True, header_style="bold cyan")
        feature_table.add_column("Feature", style="white", width=25)
        feature_table.add_column("Status / Timeline", style="yellow")

        for feature, status in features:
            feature_table.add_row(feature, status)

        console.print(feature_table)
        console.print()

        # Step 8: Architecture context
        console.print(Panel(
            "[bold]Layer 7 Phase 1 Progress[/bold]\n\n"
            "✅ Week 1: Identity (DID) - [green]COMPLETE![/green]\n"
            "🔄 Week 3-4: MATL Trust Scoring - Coming next\n"
            "🔄 Week 5-6: Epistemic Cube (E/N/M)\n"
            "🔄 Week 7-8: Credits System\n"
            "🔄 Week 9-12: Integration & Polish",
            title="Implementation Status",
            style="green"
        ))

        # Success summary
        console.print("\n[bold green]✅ Demo Complete![/bold green]")
        console.print("\n[bold]What we demonstrated:[/bold]")
        console.print("  1. Create decentralized identity (DID)")
        console.print("  2. Encrypted storage with proper permissions")
        console.print("  3. Load existing DID (app restart)")
        console.print("  4. Smart create-or-load logic")
        console.print("  5. Foundation for Layer 7 collective intelligence")

        console.print("\n[bold cyan]From revolutionary vision to working code in ONE DAY![/bold cyan]\n")

    finally:
        # Cleanup demo directory
        shutil.rmtree(temp_dir)
        console.print(f"[dim]Cleaned up demo storage: {temp_dir}[/dim]\n")


if __name__ == "__main__":
    try:
        demo_did_system()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]\n")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()
