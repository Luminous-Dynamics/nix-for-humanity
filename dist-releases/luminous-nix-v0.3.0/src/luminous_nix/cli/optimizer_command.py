#!/usr/bin/env python3
"""
Optimizer Command - AI-powered configuration optimization

This module provides CLI commands for the Configuration Optimizer,
allowing users to analyze and optimize their NixOS configurations
with AI assistance.
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from ..ai.advanced_features.config_optimizer import (
    ConfigOptimizer, OptimizationLevel, OptimizationType
)


@click.group(name='optimize')
def optimize():
    """
    AI-powered configuration optimization
    
    Analyze and optimize your NixOS configuration with:
    
    • Performance improvements
    
    • Security hardening
    
    • Resource efficiency
    
    • Dependency cleanup
    
    • Best practice enforcement
    """
    pass


@optimize.command(name='analyze')
@click.option('--config', default='/etc/nixos/configuration.nix', 
              help='Path to configuration file')
@click.option('--level', type=click.Choice(['safe', 'balanced', 'aggressive', 'custom']),
              default='balanced', help='Optimization aggressiveness level')
@click.option('--type', 'opt_type', type=click.Choice([
    'performance', 'security', 'resources', 'dependencies', 
    'best_practices', 'boot_time', 'network', 'storage'
]), help='Focus on specific optimization type')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def analyze(config: str, level: str, opt_type: str, output_json: bool):
    """Analyze configuration for optimization opportunities"""
    
    console = Console()
    optimizer = ConfigOptimizer()
    
    try:
        # Analyze configuration
        optimization_level = OptimizationLevel(level)
        plan = optimizer.analyze_configuration(config, optimization_level)
        
        if output_json:
            # JSON output
            output = {
                'total_suggestions': len(plan.suggestions),
                'risk_assessment': plan.risk_assessment,
                'estimated_improvement': plan.estimated_improvement,
                'suggestions': []
            }
            
            for suggestion in plan.suggestions:
                output['suggestions'].append({
                    'type': suggestion.rule.type.value,
                    'name': suggestion.rule.name,
                    'description': suggestion.rule.description,
                    'location': suggestion.location,
                    'impact': suggestion.rule.impact,
                    'risk': suggestion.rule.risk,
                    'confidence': suggestion.confidence
                })
            
            click.echo(json.dumps(output, indent=2))
            
        else:
            # Generate and display report
            report = optimizer.generate_report(plan)
            console.print(report)
            
            # Filter by type if specified
            if opt_type:
                opt_type_enum = OptimizationType(opt_type)
                filtered = plan.filter_by_type(opt_type_enum)
                
                if filtered:
                    console.print(f"\n[bold]Suggestions for {opt_type}:[/bold]\n")
                    
                    for i, suggestion in enumerate(filtered[:10], 1):
                        console.print(f"{i}. [cyan]{suggestion.rule.name}[/cyan]")
                        console.print(f"   {suggestion.explanation}")
                        console.print(f"   Impact: {suggestion.rule.impact} | Risk: {suggestion.rule.risk}")
                        console.print()
                else:
                    console.print(f"\n[yellow]No {opt_type} optimizations found[/yellow]")
            else:
                # Show top suggestions
                if plan.suggestions:
                    console.print("\n[bold]Top Suggestions:[/bold]\n")
                    
                    for i, suggestion in enumerate(plan.suggestions[:5], 1):
                        risk_color = {
                            'low': 'green',
                            'medium': 'yellow',
                            'high': 'red'
                        }.get(suggestion.rule.risk, 'white')
                        
                        console.print(f"{i}. [cyan]{suggestion.rule.name}[/cyan]")
                        console.print(f"   {suggestion.explanation}")
                        console.print(f"   Location: {suggestion.location}")
                        console.print(f"   Impact: {suggestion.rule.impact} | Risk: [{risk_color}]{suggestion.rule.risk}[/{risk_color}]")
                        console.print(f"   Confidence: {suggestion.confidence:.0%}")
                        console.print()
            
            # Show summary
            console.print(f"\n[dim]Found {len(plan.suggestions)} optimization opportunities[/dim]")
            
            if plan.suggestions:
                low_risk = plan.filter_by_risk('low')
                console.print(f"[green]Safe optimizations: {len(low_risk)}[/green]")
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@optimize.command(name='apply')
@click.option('--config', default='/etc/nixos/configuration.nix',
              help='Path to configuration file')
@click.option('--selections', multiple=True, type=int,
              help='Specific suggestion numbers to apply')
@click.option('--risk', type=click.Choice(['low', 'medium', 'high']),
              default='low', help='Maximum risk level to apply')
@click.option('--backup/--no-backup', default=True,
              help='Create backup before applying')
@click.option('--dry-run', is_flag=True, help='Preview changes without applying')
@click.option('--force', is_flag=True, help='Skip confirmation')
def apply(config: str, selections: tuple, risk: str, backup: bool, 
          dry_run: bool, force: bool):
    """Apply optimization suggestions"""
    
    console = Console()
    optimizer = ConfigOptimizer()
    
    try:
        # First analyze to get suggestions
        plan = optimizer.analyze_configuration(config)
        
        if not plan.suggestions:
            console.print("[yellow]No optimizations to apply[/yellow]")
            return
        
        # Filter by risk if no specific selections
        if not selections:
            suggestions_to_apply = plan.filter_by_risk(risk)
            console.print(f"\n[bold]Applying {risk}-risk optimizations:[/bold]\n")
        else:
            # Convert tuple to list
            selections_list = list(selections)
            # Adjust for 0-based indexing
            selections_list = [s - 1 for s in selections_list]
            suggestions_to_apply = [plan.suggestions[i] for i in selections_list 
                                   if 0 <= i < len(plan.suggestions)]
            console.print(f"\n[bold]Applying selected optimizations:[/bold]\n")
        
        # Show what will be applied
        for suggestion in suggestions_to_apply:
            console.print(f"• {suggestion.rule.name}")
        
        if not suggestions_to_apply:
            console.print("\n[yellow]No optimizations match criteria[/yellow]")
            return
        
        # Confirm unless forced or dry-run
        if not force and not dry_run:
            if not click.confirm(f"\nApply {len(suggestions_to_apply)} optimizations?"):
                console.print("[yellow]Cancelled[/yellow]")
                return
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - No changes will be made[/yellow]")
            
            # Show what would be done
            for suggestion in suggestions_to_apply:
                console.print(f"\nWould apply: [cyan]{suggestion.rule.name}[/cyan]")
                console.print(f"Current: {suggestion.current_value[:50]}...")
                console.print(f"New: {suggestion.suggested_value[:50]}...")
        else:
            # Apply optimizations
            result = optimizer.apply_optimizations(
                config, 
                plan,
                [plan.suggestions.index(s) for s in suggestions_to_apply],
                backup
            )
            
            if result['success']:
                console.print("\n[green]✅ Optimizations applied successfully![/green]")
                
                if result.get('applied'):
                    console.print("\nApplied:")
                    for item in result['applied']:
                        console.print(f"  • {item}")
                
                if result.get('backup'):
                    console.print(f"\nBackup saved: {result['backup']}")
            else:
                console.print(f"\n[red]❌ Failed: {result.get('error', 'Unknown error')}[/red]")
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@optimize.command(name='benchmark')
@click.option('--config', default='/etc/nixos/configuration.nix',
              help='Path to configuration file')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def benchmark(config: str, output_json: bool):
    """Benchmark current configuration performance"""
    
    console = Console()
    optimizer = ConfigOptimizer()
    
    try:
        benchmarks = optimizer.benchmark_configuration(config)
        
        if output_json:
            click.echo(json.dumps(benchmarks, indent=2))
        else:
            # Create benchmark table
            table = Table(title="Configuration Benchmarks", show_header=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", justify="right")
            table.add_column("Status", justify="center")
            
            # Boot time
            if 'boot_time' in benchmarks:
                boot_time = benchmarks['boot_time']
                status = "[green]Good[/green]" if boot_time < 30 else "[yellow]Could improve[/yellow]" if boot_time < 60 else "[red]Slow[/red]"
                table.add_row("Boot Time", f"{boot_time:.1f}s", status)
            
            # Memory usage
            if 'memory_used_mb' in benchmarks:
                mem_used = benchmarks['memory_used_mb']
                status = "[green]Good[/green]" if mem_used < 2048 else "[yellow]High[/yellow]" if mem_used < 4096 else "[red]Very High[/red]"
                table.add_row("Memory Used", f"{mem_used:.0f} MB", status)
            
            # Package count
            if 'package_count' in benchmarks:
                pkg_count = benchmarks['package_count']
                status = "[green]Minimal[/green]" if pkg_count < 300 else "[yellow]Normal[/yellow]" if pkg_count < 600 else "[red]Bloated[/red]"
                table.add_row("Packages", str(pkg_count), status)
            
            # Service count
            if 'service_count' in benchmarks:
                svc_count = benchmarks['service_count']
                status = "[green]Minimal[/green]" if svc_count < 30 else "[yellow]Normal[/yellow]" if svc_count < 60 else "[red]Many[/red]"
                table.add_row("Services", str(svc_count), status)
            
            console.print(table)
            
            # Optimization hint
            console.print("\n[dim]Run 'ask-nix optimize analyze' to find improvements[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@optimize.command(name='compare')
@click.argument('config1')
@click.argument('config2')
@click.option('--verbose', is_flag=True, help='Show detailed comparison')
def compare(config1: str, config2: str, verbose: bool):
    """Compare optimization levels of two configurations"""
    
    console = Console()
    optimizer = ConfigOptimizer()
    
    try:
        # Analyze both configurations
        console.print("[cyan]Analyzing first configuration...[/cyan]")
        plan1 = optimizer.analyze_configuration(config1)
        
        console.print("[cyan]Analyzing second configuration...[/cyan]")
        plan2 = optimizer.analyze_configuration(config2)
        
        # Create comparison table
        table = Table(title="Configuration Comparison", show_header=True)
        table.add_column("Aspect", style="cyan")
        table.add_column(Path(config1).name, justify="center")
        table.add_column(Path(config2).name, justify="center")
        table.add_column("Winner", justify="center")
        
        # Total suggestions (fewer is better)
        winner = "First" if len(plan1.suggestions) < len(plan2.suggestions) else "Second" if len(plan2.suggestions) < len(plan1.suggestions) else "Tie"
        table.add_row(
            "Optimization Needed",
            str(len(plan1.suggestions)),
            str(len(plan2.suggestions)),
            f"[{'green' if winner == 'First' else 'yellow' if winner == 'Tie' else 'red'}]{winner}[/]"
        )
        
        # Risk assessment
        risk_colors = {'low': 'green', 'medium': 'yellow', 'high': 'red'}
        table.add_row(
            "Risk Level",
            f"[{risk_colors.get(plan1.risk_assessment, 'white')}]{plan1.risk_assessment}[/]",
            f"[{risk_colors.get(plan2.risk_assessment, 'white')}]{plan2.risk_assessment}[/]",
            ""
        )
        
        # By optimization type
        if verbose:
            for opt_type in OptimizationType:
                count1 = len(plan1.filter_by_type(opt_type))
                count2 = len(plan2.filter_by_type(opt_type))
                
                if count1 > 0 or count2 > 0:
                    winner = "First" if count1 < count2 else "Second" if count2 < count1 else "Tie"
                    table.add_row(
                        f"  {opt_type.value.replace('_', ' ').title()}",
                        str(count1),
                        str(count2),
                        winner if count1 != count2 else ""
                    )
        
        console.print(table)
        
        # Summary
        console.print("\n[bold]Summary:[/bold]")
        
        if len(plan1.suggestions) < len(plan2.suggestions):
            console.print(f"[green]✅ {Path(config1).name} is more optimized[/green]")
        elif len(plan2.suggestions) < len(plan1.suggestions):
            console.print(f"[green]✅ {Path(config2).name} is more optimized[/green]")
        else:
            console.print("[yellow]Both configurations have similar optimization levels[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    optimize()