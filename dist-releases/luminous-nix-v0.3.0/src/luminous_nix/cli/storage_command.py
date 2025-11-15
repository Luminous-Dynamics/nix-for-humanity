#!/usr/bin/env python3
"""
Storage Optimizer CLI Commands
Intelligent storage management using HRM
"""

import click
import json
import os
from typing import Optional
from luminous_nix.ai.advanced_features.storage_optimizer import StorageOptimizer


def format_size(size_gb: float) -> str:
    """Format size in GB to human readable"""
    if size_gb >= 1:
        return f"{size_gb:.1f}GB"
    else:
        return f"{size_gb*1024:.0f}MB"


@click.group()
@click.pass_context
def storage(ctx):
    """💾 Smart storage optimization and cleanup

    Uses AI to identify safe cleanup opportunities without breaking your system.
    Knows what's critical and what's safe to remove.
    """
    ctx.ensure_object(dict)
    ctx.obj["storage"] = StorageOptimizer()


@storage.command()
@click.option("--aggressive", is_flag=True, help="Use aggressive cleanup mode")
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
@click.pass_context
def analyze(ctx, aggressive, json_output):
    """Analyze storage usage and find safe cleanup opportunities

    Examples:
        luminous-nix storage analyze
        luminous-nix storage analyze --aggressive
    """
    storage_opt = ctx.obj["storage"]

    mode = "aggressive" if aggressive else "safe"
    if not json_output:
        click.secho(f"💾 Analyzing Storage ({mode} mode)...", fg="cyan", bold=True)

    analysis = storage_opt.analyze_storage(aggressive)

    if json_output:
        output = {
            "total_size_gb": analysis.total_store_size_gb,
            "reclaimable_gb": analysis.reclaimable_gb,
            "safe_gb": analysis.safe_to_remove_gb,
            "risky_gb": analysis.risky_to_remove_gb,
            "confidence": analysis.confidence,
            "estimated_time": analysis.estimated_time_minutes,
            "breakdown": analysis.breakdown,
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo()
        click.echo(f"Nix Store Size: {format_size(analysis.total_store_size_gb)}")
        click.echo(f"Reclaimable Space: {format_size(analysis.reclaimable_gb)}")
        click.echo(f"  • Safe to remove: {format_size(analysis.safe_to_remove_gb)}")
        click.echo(f"  • Risky to remove: {format_size(analysis.risky_to_remove_gb)}")
        click.echo(f"Confidence: {analysis.confidence:.0%}")
        click.echo(f"Estimated Time: {analysis.estimated_time_minutes:.0f} minutes")

        if analysis.breakdown:
            click.echo()
            click.secho("Breakdown by Category:", bold=True)
            for category, size in analysis.breakdown.items():
                if size > 0 and category != "error":
                    click.echo(f"  • {category}: {format_size(size)}")

        if analysis.old_generations:
            click.echo()
            click.secho(
                f"Old Generations ({len(analysis.old_generations)}):", bold=True
            )
            for gen in analysis.old_generations[:5]:
                click.echo(f"  • Generation {gen['number']} ({gen['date']})")

        if analysis.cleanup_commands:
            click.echo()
            click.secho("Cleanup Commands:", fg="green", bold=True)
            for cmd in analysis.cleanup_commands:
                if cmd.startswith("#"):
                    click.echo(f"  {cmd}")
                else:
                    click.echo(f"  $ {cmd}")


@storage.command()
@click.option("--aggressive", is_flag=True, help="Use aggressive cleanup mode")
@click.option("--dry-run", is_flag=True, help="Show commands without executing")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def cleanup(ctx, aggressive, dry_run, yes):
    """Perform safe storage cleanup

    Examples:
        luminous-nix storage cleanup --dry-run
        luminous-nix storage cleanup --yes
        luminous-nix storage cleanup --aggressive --yes
    """
    storage_opt = ctx.obj["storage"]

    if dry_run:
        click.secho("DRY RUN - Commands will be shown but not executed", fg="yellow")

    analysis = storage_opt.analyze_storage(aggressive)

    click.echo()
    click.secho(f"Ready to free {format_size(analysis.reclaimable_gb)}", bold=True)

    if not dry_run and not yes:
        response = click.confirm(
            click.style("Proceed with cleanup?", fg="yellow"), default=False
        )
        if not response:
            click.echo("Cleanup cancelled")
            return

    # Execute or show commands
    for cmd in analysis.cleanup_commands:
        if cmd.startswith("#"):
            click.echo(f"\n{cmd}")
        else:
            if dry_run:
                click.echo(f"$ {cmd}")
            else:
                click.echo(f"$ {cmd}")
                result = os.system(cmd)
                if result != 0:
                    click.secho(
                        f"⚠️ Command failed with exit code {result}", fg="yellow"
                    )

    if not dry_run:
        click.echo()
        click.secho("✅ Cleanup complete!", fg="green", bold=True)


@storage.command()
@click.argument("target_gb", type=float)
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
@click.pass_context
def optimize(ctx, target_gb, json_output):
    """Optimize storage to free specific amount of space

    Examples:
        luminous-nix storage optimize 10    # Free 10GB
        luminous-nix storage optimize 5.5   # Free 5.5GB
    """
    storage_opt = ctx.obj["storage"]

    if not json_output:
        click.secho(
            f"💾 Optimizing to Free {format_size(target_gb)}...", fg="cyan", bold=True
        )

    plan = storage_opt.optimize_store(target_gb)

    if json_output:
        click.echo(json.dumps(plan, indent=2))
    else:
        click.echo()

        can_achieve = plan.get("can_achieve", False)
        available = plan.get("available_gb", 0)

        if can_achieve:
            click.secho(f"✅ Can free {format_size(target_gb)}", fg="green", bold=True)
        else:
            click.secho(f"⚠️ Can only free {format_size(available)}", fg="yellow")

        if plan.get("steps"):
            click.echo()
            click.secho("Optimization Steps:", bold=True)
            for step in plan["steps"]:
                risk = step.get("risk", "unknown")
                risk_color = (
                    "green" if risk == "none" else "yellow" if risk == "low" else "red"
                )
                click.echo(
                    f"  • {step['action']}: {format_size(step['space_gb'])} (", nl=False
                )
                click.secho(f"{risk} risk", fg=risk_color, nl=False)
                click.echo(")")
                click.echo(f"    Command: {step['command']}")


@storage.command(name="large")
@click.option("--min-size", type=int, default=100, help="Minimum package size in MB")
@click.option("--json", "json_output", is_flag=True, help="Output in JSON format")
@click.pass_context
def find_large(ctx, min_size, json_output):
    """Find large packages in the store

    Examples:
        luminous-nix storage large              # Find packages > 100MB
        luminous-nix storage large --min-size 500  # Find packages > 500MB
    """
    storage_opt = ctx.obj["storage"]

    if not json_output:
        click.secho(
            f"🔍 Finding Packages Larger Than {min_size}MB...", fg="cyan", bold=True
        )

    packages = storage_opt.find_large_packages(min_size)

    if json_output:
        click.echo(json.dumps(packages, indent=2))
    else:
        if packages:
            click.echo()
            click.secho(f"Found {len(packages)} Large Packages:", bold=True)
            for pkg in packages:
                click.echo(f"  • {pkg['name']}: {pkg['size_mb']}MB")
        else:
            click.echo()
            click.secho(f"No packages larger than {min_size}MB found", fg="yellow")
