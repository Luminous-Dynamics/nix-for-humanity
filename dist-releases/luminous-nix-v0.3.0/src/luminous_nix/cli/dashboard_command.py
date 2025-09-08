#!/usr/bin/env python3
"""
Dashboard Command - Launch the interactive TUI dashboard

This module provides the CLI command to launch the comprehensive
interactive dashboard for Luminous Nix.
"""

import click
import asyncio
from rich.console import Console

from ..ui.interactive_dashboard import InteractiveDashboard, DashboardView


@click.command(name='dashboard')
@click.option('--view', type=click.Choice([v.value for v in DashboardView]),
              default='overview', help='Initial view to display')
@click.option('--refresh', type=int, default=2, help='Refresh rate in seconds')
@click.option('--no-animations', is_flag=True, help='Disable animations')
@click.option('--no-predictions', is_flag=True, help='Disable ML predictions')
def dashboard(view: str, refresh: int, no_animations: bool, no_predictions: bool):
    """
    Launch the interactive TUI dashboard
    
    This provides a comprehensive real-time view of your NixOS system with:
    
    • System health monitoring with ML predictions
    
    • Configuration DNA visualization
    
    • System mode management
    
    • Storage optimization insights
    
    • Rollback timeline
    
    • AI/LLM status monitoring
    
    • Performance metrics
    
    Navigation:
    
    • Number keys (1-8): Switch between views
    
    • r: Force refresh
    
    • a: Toggle animations
    
    • p: Toggle predictions
    
    • q: Quit dashboard
    """
    
    console = Console()
    
    try:
        # Initialize dashboard
        dashboard = InteractiveDashboard(console)
        
        # Set initial state
        dashboard.state.current_view = DashboardView(view)
        dashboard.state.refresh_rate = refresh
        dashboard.state.show_animations = not no_animations
        dashboard.state.show_predictions = not no_predictions
        
        # Show startup message
        console.print("""
[bold cyan]🚀 Luminous Nix Interactive Dashboard[/bold cyan]

[dim]Starting dashboard with:[/dim]
• View: {view}
• Refresh: {refresh}s
• Animations: {animations}
• Predictions: {predictions}

[dim]Press Ctrl+C to exit[/dim]
        """.format(
            view=view,
            refresh=refresh,
            animations="enabled" if not no_animations else "disabled",
            predictions="enabled" if not no_predictions else "disabled"
        ))
        
        # Run the dashboard
        asyncio.run(dashboard.run())
        
    except KeyboardInterrupt:
        console.print("\n[cyan]Dashboard closed gracefully[/cyan]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@click.command(name='monitor')
@click.option('--metric', type=click.Choice(['cpu', 'memory', 'disk', 'network', 'all']),
              default='all', help='Specific metric to monitor')
@click.option('--duration', type=int, default=60, help='Monitoring duration in seconds')
@click.option('--interval', type=int, default=1, help='Update interval in seconds')
def monitor(metric: str, duration: int, interval: int):
    """
    Simple real-time monitoring (lightweight alternative to full dashboard)
    
    Provides focused monitoring of specific metrics without the full dashboard.
    """
    
    import time
    import psutil
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    def create_monitor_table():
        """Create monitoring table"""
        table = Table(show_header=True, title=f"System Monitor - {metric.upper()}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        table.add_column("Status", justify="center")
        
        if metric == 'all' or metric == 'cpu':
            cpu = psutil.cpu_percent(interval=0.1)
            status = "[red]HIGH[/red]" if cpu > 80 else "[yellow]MED[/yellow]" if cpu > 50 else "[green]LOW[/green]"
            table.add_row("CPU Usage", f"{cpu:.1f}%", status)
        
        if metric == 'all' or metric == 'memory':
            mem = psutil.virtual_memory()
            status = "[red]HIGH[/red]" if mem.percent > 80 else "[yellow]MED[/yellow]" if mem.percent > 50 else "[green]LOW[/green]"
            table.add_row("Memory Usage", f"{mem.percent:.1f}%", status)
            table.add_row("Memory Free", f"{mem.available / 1e9:.1f} GB", "")
        
        if metric == 'all' or metric == 'disk':
            disk = psutil.disk_usage('/')
            status = "[red]HIGH[/red]" if disk.percent > 80 else "[yellow]MED[/yellow]" if disk.percent > 50 else "[green]LOW[/green]"
            table.add_row("Disk Usage", f"{disk.percent:.1f}%", status)
            table.add_row("Disk Free", f"{disk.free / 1e9:.1f} GB", "")
        
        if metric == 'all' or metric == 'network':
            net = psutil.net_io_counters()
            table.add_row("Net Sent", f"{net.bytes_sent / 1e9:.2f} GB", "")
            table.add_row("Net Recv", f"{net.bytes_recv / 1e9:.2f} GB", "")
        
        return table
    
    try:
        with Live(console=console, refresh_per_second=1) as live:
            start_time = time.time()
            
            while time.time() - start_time < duration:
                table = create_monitor_table()
                
                remaining = duration - int(time.time() - start_time)
                panel = Panel(
                    table,
                    title=f"[bold]Monitoring for {remaining}s[/bold]",
                    border_style="cyan"
                )
                
                live.update(panel)
                time.sleep(interval)
        
        console.print("[green]✅ Monitoring complete[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[cyan]Monitoring stopped[/cyan]")


# Create command group
@click.group()
def ui():
    """User interface commands"""
    pass

ui.add_command(dashboard)
ui.add_command(monitor)


if __name__ == "__main__":
    ui()