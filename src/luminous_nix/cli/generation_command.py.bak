#!/usr/bin/env python3
"""
from typing import Optional
CLI commands for NixOS generation management and system recovery
"""

import sys
from pathlib import Path

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from nix_for_humanity.core.generation_manager import GenerationManager


@click.group()
def generation():
    """Manage NixOS generations and system recovery"""
    pass


@generation.command()
@click.option("--limit", "-n", default=10, help="Number of generations to show")
@click.option("--detailed", "-d", is_flag=True, help="Show detailed information")
def list(limit: int, detailed: bool):
    """List system generations"""
    manager = GenerationManager()
    generations = manager.list_generations(limit)

    if not generations:
        click.echo("No generations found")
        return

    click.echo(f"System Generations (showing last {limit}):\n")

    for gen in generations:
        marker = (
            click.style(" [CURRENT]", fg="green", bold=True) if gen.is_current else ""
        )
        click.echo(
            f"Generation {click.style(str(gen.number), fg='cyan', bold=True)}{marker}"
        )
        click.echo(f"  Date: {gen.date.strftime('%Y-%m-%d %H:%M:%S')}")

        if detailed:
            click.echo(f"  Kernel: {gen.kernel}")
            click.echo(f"  NixOS: {gen.nixos_version}")
            if gen.description:
                click.echo(f"  Description: {gen.description}")
            if gen.packages_added:
                click.echo(f"  Packages added: {', '.join(gen.packages_added[:5])}")
            if gen.packages_removed:
                click.echo(f"  Packages removed: {', '.join(gen.packages_removed[:5])}")

        click.echo()


@generation.command()
@click.argument("generation", type=int, required=False)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def rollback(generation: int | None, yes: bool):
    """Rollback to a previous generation"""
    manager = GenerationManager()

    if generation is None:
        target = "previous generation"
    else:
        target = f"generation {generation}"

    if not yes:
        click.confirm(f"Are you sure you want to rollback to {target}?", abort=True)

    click.echo(f"Rolling back to {target}...")
    success, message = manager.rollback(generation)

    if success:
        click.echo(click.style(f"✅ {message}", fg="green"))
        click.echo("\nPlease reboot for all changes to take effect.")
    else:
        click.echo(click.style(f"❌ {message}", fg="red"))
        sys.exit(1)


@generation.command()
@click.argument("gen1", type=int)
@click.argument("gen2", type=int, required=False)
def diff(gen1: int, gen2: int | None):
    """Show differences between generations"""
    manager = GenerationManager()

    if gen2 is None:
        # Compare with current
        current = manager.current_generation
        if current is None:
            click.echo("Could not determine current generation")
            return
        gen2 = current

    click.echo(f"Comparing generation {gen1} with {gen2}:\n")

    diff_info = manager.get_generation_diff(gen1, gen2)

    if diff_info["kernel_changed"]:
        click.echo(click.style("  ⚠️  Kernel version changed", fg="yellow"))

    if diff_info["nixos_version_changed"]:
        click.echo(click.style("  ⚠️  NixOS version changed", fg="yellow"))

    if diff_info["packages_added"]:
        click.echo(
            click.style(
                f"\n  + Added {len(diff_info['packages_added'])} packages:", fg="green"
            )
        )
        for pkg in diff_info["packages_added"][:10]:
            click.echo(f"    + {pkg}")
        if len(diff_info["packages_added"]) > 10:
            click.echo(f"    ... and {len(diff_info['packages_added']) - 10} more")

    if diff_info["packages_removed"]:
        click.echo(
            click.style(
                f"\n  - Removed {len(diff_info['packages_removed'])} packages:",
                fg="red",
            )
        )
        for pkg in diff_info["packages_removed"][:10]:
            click.echo(f"    - {pkg}")
        if len(diff_info["packages_removed"]) > 10:
            click.echo(f"    ... and {len(diff_info['packages_removed']) - 10} more")

    if diff_info["config_changes"]:
        click.echo(
            click.style(
                f"\n  ~ {len(diff_info['config_changes'])} configuration changes",
                fg="yellow",
            )
        )


@generation.command()
@click.option("--keep", "-k", default=5, help="Number of generations to keep")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def clean(keep: int, yes: bool):
    """Delete old generations to free space"""
    manager = GenerationManager()

    # First show what would be deleted
    generations = manager.list_generations()
    if len(generations) <= keep:
        click.echo(f"Only {len(generations)} generations exist, nothing to delete")
        return

    to_delete = generations[keep:]
    click.echo(f"Will delete {len(to_delete)} old generations:")
    for gen in to_delete:
        if not gen.is_current:
            click.echo(f"  - Generation {gen.number} ({gen.date.strftime('%Y-%m-%d')})")

    if not yes:
        click.confirm("Continue with deletion?", abort=True)

    click.echo("\nDeleting old generations...")
    success, message = manager.delete_generations(keep)

    if success:
        click.echo(click.style(f"✅ {message}", fg="green"))
        click.echo("\nRun 'nix-collect-garbage' to reclaim disk space")
    else:
        click.echo(click.style(f"❌ {message}", fg="red"))


@generation.command()
def health():
    """Check system health and recovery status"""
    manager = GenerationManager()
    health = manager.check_system_health()

    click.echo("System Health Check:\n")

    # Disk usage
    disk_color = (
        "green"
        if health.disk_usage_percent < 80
        else "yellow" if health.disk_usage_percent < 90 else "red"
    )
    click.echo(
        f"  Disk Usage: {click.style(f'{health.disk_usage_percent:.1f}%', fg=disk_color)}"
    )

    # Memory usage
    mem_color = (
        "green"
        if health.memory_usage_percent < 80
        else "yellow" if health.memory_usage_percent < 90 else "red"
    )
    click.echo(
        f"  Memory Usage: {click.style(f'{health.memory_usage_percent:.1f}%', fg=mem_color)}"
    )

    # Failed services
    svc_color = "green" if len(health.failed_services) == 0 else "red"
    click.echo(
        f"  Failed Services: {click.style(str(len(health.failed_services)), fg=svc_color)}"
    )
    if health.failed_services:
        for svc in health.failed_services[:3]:
            click.echo(f"    - {svc}")
        if len(health.failed_services) > 3:
            click.echo(f"    ... and {len(health.failed_services) - 3} more")

    # Config errors
    cfg_color = "green" if len(health.config_errors) == 0 else "red"
    click.echo(
        f"  Config Errors: {click.style(str(len(health.config_errors)), fg=cfg_color)}"
    )
    if health.config_errors:
        for err in health.config_errors[:3]:
            click.echo(f"    - {err}")

    # Last boot
    if health.last_successful_boot:
        click.echo(
            f"  Last Boot: {health.last_successful_boot.strftime('%Y-%m-%d %H:%M')}"
        )

    # Overall status
    status_icon = "✅" if health.is_healthy else "⚠️"
    status_text = "Healthy" if health.is_healthy else "Issues Detected"
    status_color = "green" if health.is_healthy else "yellow"
    click.echo(
        f"\nOverall Status: {status_icon} {click.style(status_text, fg=status_color, bold=True)}"
    )

    # Warnings
    if health.warnings:
        click.echo("\nWarnings:")
        for warning in health.warnings:
            click.echo(f"  ⚠️  {warning}")

    # Suggestions
    suggestions = manager.suggest_recovery_actions(health)
    if suggestions:
        click.echo("\nRecommended Actions:")
        for i, suggestion in enumerate(suggestions, 1):
            click.echo(f"  {i}. {suggestion}")


@generation.command()
@click.argument("description")
def snapshot(description: str):
    """Create a recovery snapshot of current system"""
    manager = GenerationManager()

    click.echo("Creating recovery snapshot...")
    click.echo(f"Description: {description}")

    success, message = manager.create_recovery_snapshot(description)

    if success:
        click.echo(click.style(f"✅ {message}", fg="green"))
        click.echo("\nSnapshot created! You can rollback to this point if needed.")
    else:
        click.echo(click.style(f"❌ {message}", fg="red"))
        sys.exit(1)


@generation.command()
def guide():
    """Show generation management guide"""
    guide_text = """
NixOS Generation Management Guide
================================

What are Generations?
--------------------
Every time you rebuild your NixOS system, a new "generation" is created.
Each generation is a complete snapshot of your system configuration.

Common Tasks:
------------

1. View Recent Generations:
   ask-nix generation list

2. Rollback to Previous:
   ask-nix generation rollback

3. Rollback to Specific Generation:
   ask-nix generation rollback 42

4. Compare Generations:
   ask-nix generation diff 42 43

5. Clean Old Generations:
   ask-nix generation clean --keep 5

6. Check System Health:
   ask-nix generation health

7. Create Recovery Snapshot:
   ask-nix generation snapshot "Before major update"

Safety Tips:
-----------
• Always keep at least 3-5 recent generations
• Create a snapshot before major changes
• Test new configurations before making permanent
• Use 'nixos-rebuild test' to try without creating generation

Recovery Process:
----------------
If something goes wrong:
1. Boot into previous generation from GRUB menu
2. Or use: ask-nix generation rollback
3. Fix the configuration
4. Rebuild when ready

Disk Space Management:
---------------------
Old generations consume disk space. To clean up:
1. Delete old generations: ask-nix generation clean
2. Collect garbage: nix-collect-garbage -d
3. Optimize store: nix-store --optimize
"""
    click.echo(guide_text)


def register_commands(cli):
    """Register generation commands with main CLI"""
    cli.add_command(generation)
