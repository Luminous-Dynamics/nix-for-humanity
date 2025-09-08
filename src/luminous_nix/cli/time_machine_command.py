#!/usr/bin/env python3
"""
Time Machine Command - Browse and restore configuration history

This module provides CLI commands for the Configuration Time Machine,
allowing users to navigate through their configuration history and
restore to any point in time.
"""

import click
import json
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.columns import Columns

from ..ai.advanced_features.config_time_machine import (
    ConfigTimeMachine, RestoreStrategy, ChangeType
)


@click.group(name='time-machine')
def time_machine():
    """
    Configuration Time Machine - Browse and restore past configurations
    
    Navigate through your NixOS configuration history with ease:
    
    • View timeline of all configurations
    
    • Compare changes between any two points
    
    • Restore to any previous state
    
    • Find similar configurations
    
    • Track evolution patterns
    """
    pass


@time_machine.command(name='timeline')
@click.option('--limit', type=int, default=20, help='Number of events to show')
@click.option('--format', type=click.Choice(['tree', 'table', 'json']), 
              default='tree', help='Output format')
@click.option('--filter', type=str, help='Filter by change type (package/service/kernel)')
def timeline(limit: int, format: str, filter: str):
    """View configuration timeline"""
    
    console = Console()
    machine = ConfigTimeMachine()
    
    try:
        events = machine.browse_timeline(limit)
        
        if not events:
            console.print("[yellow]No configuration history found[/yellow]")
            return
        
        if format == 'json':
            # JSON output
            output = []
            for event in events:
                output.append({
                    'generation': event.generation,
                    'timestamp': event.timestamp.isoformat(),
                    'type': event.event_type,
                    'description': event.description,
                    'details': event.details
                })
            click.echo(json.dumps(output, indent=2))
            
        elif format == 'table':
            # Table output
            table = Table(title="Configuration Timeline", show_header=True)
            table.add_column("Gen", style="cyan", width=6)
            table.add_column("Date", style="white")
            table.add_column("Time", style="white")
            table.add_column("Changes", style="yellow")
            table.add_column("Description", style="white")
            
            for event in events:
                date_str = event.timestamp.strftime("%Y-%m-%d")
                time_str = event.timestamp.strftime("%H:%M")
                changes_str = str(event.details.get('changes', 0)) if event.details else "0"
                
                # Add icon for current
                gen_str = f"{event.icon} {event.generation}"
                
                table.add_row(
                    gen_str,
                    date_str,
                    time_str,
                    changes_str,
                    event.description[:50] + "..." if len(event.description) > 50 else event.description
                )
            
            console.print(table)
            
        else:
            # Tree format (default)
            timeline_panel = machine.visualize_timeline()
            console.print(timeline_panel)
        
        # Show summary
        if format != 'json':
            console.print()
            console.print(f"[dim]Showing {len(events)} most recent configurations[/dim]")
            
            # Find current generation
            current = next((e for e in events if e.event_type == "current"), None)
            if current:
                console.print(f"[green]Current generation: {current.generation}[/green]")
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@time_machine.command(name='show')
@click.argument('generation', type=int)
@click.option('--details', is_flag=True, help='Show detailed information')
def show(generation: int, details: bool):
    """Show details of a specific generation"""
    
    console = Console()
    machine = ConfigTimeMachine()
    
    try:
        snapshot = machine.get_snapshot(generation)
        
        if not snapshot:
            console.print(f"[red]Generation {generation} not found[/red]")
            return
        
        # Basic info panel
        info_lines = [
            f"[bold]Generation:[/bold] {snapshot.generation}",
            f"[bold]Date:[/bold] {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"[bold]Hash:[/bold] {snapshot.hash}",
            f"[bold]Size:[/bold] {snapshot.size / 1e9:.2f} GB"
        ]
        
        if snapshot.description:
            info_lines.append(f"[bold]Description:[/bold] {snapshot.description}")
        
        if snapshot.tags:
            info_lines.append(f"[bold]Tags:[/bold] {', '.join(snapshot.tags)}")
        
        if snapshot.is_milestone:
            info_lines.append("[yellow]⭐ Milestone Configuration[/yellow]")
        
        if snapshot.metadata.get("is_current"):
            info_lines.append("[green]✓ Current Configuration[/green]")
        
        console.print(Panel("\n".join(info_lines), title=f"[cyan]Generation {generation}[/cyan]"))
        
        # Changes from previous
        if snapshot.changes_from_previous:
            console.print("\n[bold]Changes from Previous Generation:[/bold]\n")
            
            for change in snapshot.changes_from_previous:
                icon = {
                    ChangeType.PACKAGE_ADD: "📦+",
                    ChangeType.PACKAGE_REMOVE: "📦-",
                    ChangeType.SERVICE_ENABLE: "🔧+",
                    ChangeType.SERVICE_DISABLE: "🔧-",
                    ChangeType.KERNEL_UPDATE: "🐧",
                    ChangeType.BOOT_CONFIG: "🥾"
                }.get(change.type, "•")
                
                console.print(f"  {icon} {change.description}")
                
                if details and change.details:
                    if change.added:
                        console.print(f"    [green]Added: {', '.join(change.added[:5])}[/green]")
                    if change.removed:
                        console.print(f"    [red]Removed: {', '.join(change.removed[:5])}[/red]")
        
        # Risk and stability scores
        if details:
            console.print("\n[bold]Analysis:[/bold]\n")
            console.print(f"  Risk Score: {snapshot.risk_score:.1f}/100")
            console.print(f"  Stability Score: {snapshot.stability_score:.1f}/100")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@time_machine.command(name='diff')
@click.argument('gen1', type=int)
@click.argument('gen2', type=int)
@click.option('--unified', is_flag=True, help='Show unified diff format')
@click.option('--summary', is_flag=True, help='Show only summary of changes')
def diff(gen1: int, gen2: int, unified: bool, summary: bool):
    """Compare two configurations"""
    
    console = Console()
    machine = ConfigTimeMachine()
    
    try:
        if summary:
            # Show change summary
            snapshot1 = machine.get_snapshot(gen1)
            snapshot2 = machine.get_snapshot(gen2)
            
            if not snapshot1 or not snapshot2:
                console.print("[red]One or both generations not found[/red]")
                return
            
            console.print(f"\n[bold]Comparing Generation {gen1} → {gen2}[/bold]\n")
            
            # Time difference
            time_diff = snapshot2.timestamp - snapshot1.timestamp
            console.print(f"Time difference: {time_diff.days} days, {time_diff.seconds // 3600} hours")
            
            # Analyze all changes between them
            all_changes = []
            for gen in range(gen1 + 1, gen2 + 1):
                snap = machine.get_snapshot(gen)
                if snap and snap.changes_from_previous:
                    all_changes.extend(snap.changes_from_previous)
            
            if all_changes:
                console.print(f"\nTotal changes: {len(all_changes)}")
                
                # Summarize by type
                by_type = {}
                for change in all_changes:
                    by_type[change.type] = by_type.get(change.type, 0) + 1
                
                console.print("\nChanges by type:")
                for change_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                    console.print(f"  • {change_type.value}: {count}")
            else:
                console.print("\n[green]No changes detected[/green]")
                
        else:
            # Show actual diff
            diff_lines = machine.diff_configurations(gen1, gen2)
            
            if not diff_lines:
                console.print("[yellow]No differences found[/yellow]")
                return
            
            if unified:
                # Show as unified diff
                console.print(Panel(
                    "".join(diff_lines),
                    title=f"[cyan]Diff: Generation {gen1} → {gen2}[/cyan]",
                    border_style="blue"
                ))
            else:
                # Show with syntax highlighting
                syntax = Syntax(
                    "".join(diff_lines),
                    "diff",
                    theme="monokai",
                    line_numbers=True
                )
                console.print(syntax)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@time_machine.command(name='restore')
@click.argument('generation', type=int)
@click.option('--strategy', type=click.Choice(['full', 'selective', 'merge', 'cherry_pick']),
              default='full', help='Restoration strategy')
@click.option('--dry-run', is_flag=True, help='Preview without applying')
@click.option('--force', is_flag=True, help='Skip confirmation')
def restore(generation: int, strategy: str, dry_run: bool, force: bool):
    """Restore to a previous configuration"""
    
    console = Console()
    machine = ConfigTimeMachine()
    
    try:
        snapshot = machine.get_snapshot(generation)
        
        if not snapshot:
            console.print(f"[red]Generation {generation} not found[/red]")
            return
        
        # Show what we're restoring to
        console.print(f"\n[bold]Restore Target:[/bold] Generation {generation}")
        console.print(f"Date: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if snapshot.description:
            console.print(f"Description: {snapshot.description}")
        
        # Confirm unless forced
        if not force and not dry_run:
            if not click.confirm("\nAre you sure you want to restore to this configuration?"):
                console.print("[yellow]Restore cancelled[/yellow]")
                return
        
        # Perform restoration
        restore_strategy = RestoreStrategy(strategy)
        result = machine.restore_configuration(generation, restore_strategy, dry_run)
        
        if result['success']:
            if dry_run:
                console.print("\n[yellow]DRY RUN - No changes made[/yellow]")
                console.print(f"\nWould execute: [cyan]{result.get('command', 'N/A')}[/cyan]")
                
                if result.get('changes'):
                    console.print(f"Expected changes: {result['changes']}")
            else:
                console.print("\n[green]✅ Configuration restored successfully![/green]")
                
                if result.get('output'):
                    console.print("\nOutput:")
                    console.print(Panel(result['output'], border_style="green"))
        else:
            console.print(f"\n[red]❌ Restore failed: {result.get('error', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@time_machine.command(name='find-similar')
@click.argument('generation', type=int)
@click.option('--threshold', type=float, default=0.8, help='Similarity threshold (0.0-1.0)')
@click.option('--limit', type=int, default=5, help='Maximum results to show')
def find_similar(generation: int, threshold: float, limit: int):
    """Find configurations similar to a target"""
    
    console = Console()
    machine = ConfigTimeMachine()
    
    try:
        similar = machine.find_similar_configurations(generation, threshold)
        
        if not similar:
            console.print(f"[yellow]No similar configurations found (threshold: {threshold:.0%})[/yellow]")
            return
        
        console.print(f"\n[bold]Configurations Similar to Generation {generation}:[/bold]\n")
        
        table = Table(show_header=True)
        table.add_column("Generation", style="cyan")
        table.add_column("Similarity", style="yellow")
        table.add_column("Date", style="white")
        table.add_column("Age", style="dim")
        
        for gen_num, similarity in similar[:limit]:
            snapshot = machine.get_snapshot(gen_num)
            if snapshot:
                age = datetime.now() - snapshot.timestamp
                age_str = f"{age.days}d ago" if age.days > 0 else "Today"
                
                table.add_row(
                    str(gen_num),
                    f"{similarity:.1%}",
                    snapshot.timestamp.strftime("%Y-%m-%d"),
                    age_str
                )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@time_machine.command(name='recommend')
@click.option('--stable', is_flag=True, help='Prefer stable configurations')
@click.option('--minimal', is_flag=True, help='Prefer minimal configurations')
@click.option('--recent', is_flag=True, help='Prefer recent configurations')
def recommend(stable: bool, minimal: bool, recent: bool):
    """Get restore point recommendations"""
    
    console = Console()
    machine = ConfigTimeMachine()
    
    try:
        # Build criteria
        criteria = {}
        if stable:
            criteria['stable'] = True
        if minimal:
            criteria['minimal'] = True
        if recent:
            criteria['recent'] = True
        
        recommendations = machine.recommend_restore_points(criteria)
        
        if not recommendations:
            console.print("[yellow]No recommendations available[/yellow]")
            return
        
        console.print("\n[bold cyan]💡 Recommended Restore Points[/bold cyan]\n")
        
        for i, rec in enumerate(recommendations, 1):
            snapshot = rec.snapshot
            
            # Create recommendation panel
            content = [
                f"[bold]Generation {snapshot.generation}[/bold]",
                f"Date: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M')}",
                f"Confidence: [yellow]{rec.confidence:.0%}[/yellow]",
                f"Reason: {rec.reason}"
            ]
            
            if rec.benefits:
                content.append(f"\n[green]Benefits:[/green]")
                for benefit in rec.benefits:
                    content.append(f"  ✓ {benefit}")
            
            if rec.risks:
                content.append(f"\n[yellow]Risks:[/yellow]")
                for risk in rec.risks:
                    content.append(f"  ⚠ {risk}")
            
            panel = Panel(
                "\n".join(content),
                title=f"[cyan]#{i} Recommendation[/cyan]",
                border_style="blue"
            )
            
            console.print(panel)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@time_machine.command(name='snapshot')
@click.option('--description', required=True, help='Description of this snapshot')
@click.option('--tags', multiple=True, help='Tags for this snapshot')
@click.option('--milestone', is_flag=True, help='Mark as milestone')
def snapshot(description: str, tags: tuple, milestone: bool):
    """Create a snapshot with annotations"""
    
    console = Console()
    machine = ConfigTimeMachine()
    
    try:
        snapshot = machine.create_snapshot(
            description=description,
            tags=list(tags) if tags else [],
            is_milestone=milestone
        )
        
        console.print(f"\n[green]✅ Snapshot created for generation {snapshot.generation}[/green]")
        console.print(f"Description: {snapshot.description}")
        
        if snapshot.tags:
            console.print(f"Tags: {', '.join(snapshot.tags)}")
        
        if milestone:
            console.print("[yellow]⭐ Marked as milestone[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@time_machine.command(name='analyze')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def analyze(output_json: bool):
    """Analyze configuration evolution patterns"""
    
    console = Console()
    machine = ConfigTimeMachine()
    
    try:
        patterns = machine.analyze_evolution_patterns()
        
        if output_json:
            click.echo(json.dumps(patterns, indent=2, default=str))
        else:
            console.print("\n[bold cyan]📊 Configuration Evolution Analysis[/bold cyan]\n")
            
            if patterns.get('total_generations'):
                console.print(f"[bold]Total Generations:[/bold] {patterns['total_generations']}")
            
            if patterns.get('time_span') is not None:
                console.print(f"[bold]Time Span:[/bold] {patterns['time_span']} days")
            
            if patterns.get('change_frequency') is not None:
                console.print(f"[bold]Average Changes/Week:[/bold] {patterns['change_frequency']:.1f}")
            
            if patterns.get('growth_rate') is not None:
                growth_mb_day = patterns['growth_rate'] / 1e6
                console.print(f"[bold]Growth Rate:[/bold] {growth_mb_day:.2f} MB/day")
            
            if patterns.get('most_changed'):
                console.print("\n[bold]Most Changed Categories:[/bold]")
                for category, count in patterns['most_changed'].items():
                    console.print(f"  • {category}: {count} changes")
            
            if patterns.get('stability_periods'):
                console.print("\n[bold]Stability Periods:[/bold]")
                for period in patterns['stability_periods'][:3]:
                    console.print(f"  • {period['duration_days']} days ({period['start'].strftime('%Y-%m-%d')} - {period['end'].strftime('%Y-%m-%d')})")
                    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    time_machine()