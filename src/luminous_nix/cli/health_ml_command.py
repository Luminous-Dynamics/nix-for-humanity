#!/usr/bin/env python3
"""
Health ML Command - CLI integration for ML-powered health predictions

This module provides CLI commands for the ML health prediction system.
"""

import click
import json
from pathlib import Path
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich.syntax import Syntax

from ..ai.advanced_features.ml_health_predictor import (
    MLHealthPredictor,
    HealthMetric,
    PredictionType,
    HealthTrend
)


console = Console()


@click.group(name='health-ml')
def health_ml():
    """Machine learning powered health monitoring and prediction"""
    pass


@health_ml.command()
@click.option('--collect-live', is_flag=True, help='Collect live system metrics')
@click.option('--duration', default=60, help='Collection duration in seconds')
def monitor(collect_live: bool, duration: int):
    """Monitor system health with ML predictions"""
    
    predictor = MLHealthPredictor()
    
    if collect_live:
        console.print("[cyan]Starting live metrics collection...[/cyan]")
        _collect_live_metrics(predictor, duration)
    
    # Analyze health
    with console.status("[bold green]Analyzing system health with ML..."):
        profile = predictor.analyze_current_health()
    
    # Display results
    _display_health_profile(profile)
    
    # Show predictions
    if profile.predictions:
        _display_predictions(profile.predictions)
    
    # Show optimization opportunities
    if profile.optimization_opportunities:
        console.print("\n[yellow]💡 Optimization Opportunities:[/yellow]")
        for opp in profile.optimization_opportunities:
            console.print(f"  • {opp}")


@health_ml.command()
@click.argument('metric', type=click.Choice([m.value for m in HealthMetric]))
@click.option('--horizon', default=24, help='Prediction horizon in hours')
@click.option('--detailed', is_flag=True, help='Show detailed analysis')
def predict(metric: str, horizon: int, detailed: bool):
    """Predict health issues for a specific metric"""
    
    predictor = MLHealthPredictor()
    
    # Load historical data if available
    _load_historical_data(predictor)
    
    # Get prediction
    metric_enum = HealthMetric(metric)
    prob, explanation = predictor.predict_failure_probability(metric_enum, horizon)
    
    # Display result
    console.print(f"\n[bold]Health Prediction for {metric}[/bold]")
    console.print(f"Time Horizon: {horizon} hours")
    console.print(f"Failure Probability: {prob:.1%}")
    console.print(f"Analysis: {explanation}")
    
    if detailed:
        # Show trend analysis
        history = list(predictor.metric_history[metric_enum])
        if history:
            _display_metric_trend(metric_enum, history)


@health_ml.command()
@click.option('--format', type=click.Choice(['text', 'json', 'html']), default='text')
@click.option('--output', type=click.Path(), help='Output file')
def report(format: str, output: str):
    """Generate comprehensive health report"""
    
    predictor = MLHealthPredictor()
    
    # Load historical data
    _load_historical_data(predictor)
    
    # Generate report
    if format == 'text':
        report_content = predictor.generate_health_report()
    elif format == 'json':
        profile = predictor.analyze_current_health()
        report_content = _profile_to_json(profile)
    else:  # html
        profile = predictor.analyze_current_health()
        report_content = _generate_html_report(profile)
    
    # Output
    if output:
        Path(output).write_text(report_content)
        console.print(f"[green]✅ Report saved to {output}[/green]")
    else:
        if format == 'text':
            console.print(report_content)
        else:
            console.print(Syntax(report_content, format))


@health_ml.command()
@click.option('--data-file', type=click.Path(exists=True), help='Historical data file')
@click.option('--from-system', is_flag=True, help='Train from system logs')
def train(data_file: str, from_system: bool):
    """Train ML models on historical data"""
    
    predictor = MLHealthPredictor()
    
    with console.status("[bold green]Training ML models..."):
        if data_file:
            # Load from file
            data = json.loads(Path(data_file).read_text())
            success = predictor.train_on_historical_data(data)
        elif from_system:
            # Extract from system
            data = _extract_system_history()
            success = predictor.train_on_historical_data(data)
        else:
            console.print("[red]Please specify --data-file or --from-system[/red]")
            return
    
    if success:
        predictor.save_models()
        console.print("[green]✅ Models trained and saved successfully[/green]")
    else:
        console.print("[red]❌ Training failed[/red]")


@health_ml.command()
def insights():
    """Show correlation insights and patterns"""
    
    predictor = MLHealthPredictor()
    _load_historical_data(predictor)
    
    insights = predictor.get_correlation_insights()
    
    if not insights:
        console.print("[yellow]No insights available - need more data[/yellow]")
        return
    
    console.print("[bold cyan]System Health Insights[/bold cyan]\n")
    
    for category, items in insights.items():
        console.print(f"[bold]{category.upper()}:[/bold]")
        for item in items:
            console.print(f"  • {item}")
        console.print()


@health_ml.command()
@click.option('--interval', default=5, help='Update interval in seconds')
def dashboard(interval: int):
    """Live health monitoring dashboard"""
    
    predictor = MLHealthPredictor()
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    layout["body"].split_row(
        Layout(name="metrics"),
        Layout(name="predictions")
    )
    
    with Live(layout, refresh_per_second=1, screen=True):
        import time
        
        while True:
            try:
                # Collect current metrics
                _collect_current_metrics(predictor)
                
                # Update dashboard
                profile = predictor.analyze_current_health()
                
                # Update header
                layout["header"].update(
                    Panel(
                        f"[bold cyan]ML Health Monitor[/bold cyan] | Risk: {profile.risk_score:.1f}/100",
                        border_style="cyan"
                    )
                )
                
                # Update metrics
                metrics_table = _create_metrics_table(profile)
                layout["metrics"].update(Panel(metrics_table, title="Current Metrics"))
                
                # Update predictions
                pred_content = _format_predictions(profile.predictions)
                layout["predictions"].update(Panel(pred_content, title="ML Predictions"))
                
                # Update footer
                layout["footer"].update(
                    Panel(
                        f"Updated: {datetime.now().strftime('%H:%M:%S')} | Press Ctrl+C to exit",
                        border_style="dim"
                    )
                )
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                break
    
    console.print("\n[cyan]Dashboard closed[/cyan]")


def _collect_live_metrics(predictor: MLHealthPredictor, duration: int):
    """Collect live system metrics"""
    
    import psutil
    import time
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task(f"Collecting metrics for {duration}s...", total=duration)
        
        for _ in range(duration):
            # Collect CPU
            predictor.collect_metric(
                HealthMetric.CPU_USAGE,
                psutil.cpu_percent(interval=1)
            )
            
            # Collect Memory
            predictor.collect_metric(
                HealthMetric.MEMORY_USAGE,
                psutil.virtual_memory().percent
            )
            
            # Collect Disk
            predictor.collect_metric(
                HealthMetric.DISK_USAGE,
                psutil.disk_usage('/').percent
            )
            
            progress.update(task, advance=1)
            time.sleep(1)


def _collect_current_metrics(predictor: MLHealthPredictor):
    """Collect current system metrics"""
    
    import psutil
    
    # CPU
    predictor.collect_metric(
        HealthMetric.CPU_USAGE,
        psutil.cpu_percent(interval=0.1)
    )
    
    # Memory
    predictor.collect_metric(
        HealthMetric.MEMORY_USAGE,
        psutil.virtual_memory().percent
    )
    
    # Disk
    predictor.collect_metric(
        HealthMetric.DISK_USAGE,
        psutil.disk_usage('/').percent
    )


def _load_historical_data(predictor: MLHealthPredictor):
    """Load historical data if available"""
    
    history_file = Path.home() / ".luminous_nix" / "health_history.json"
    
    if history_file.exists():
        try:
            data = json.loads(history_file.read_text())
            predictor.train_on_historical_data(data)
        except Exception:
            pass  # Ignore errors


def _extract_system_history() -> list:
    """Extract historical data from system logs"""
    
    # This would parse system logs, journalctl, etc.
    # For now, return simulated data
    
    import random
    
    history = []
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(100):
        timestamp = base_time + timedelta(minutes=i * 15)
        
        history.append({
            'metric': 'cpu_usage',
            'value': 30 + random.gauss(20, 10),
            'timestamp': timestamp.isoformat()
        })
        
        history.append({
            'metric': 'memory_usage',
            'value': 40 + random.gauss(15, 5),
            'timestamp': timestamp.isoformat()
        })
    
    return history


def _display_health_profile(profile):
    """Display health profile in a table"""
    
    table = Table(title="System Health Profile", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Trend", justify="center")
    table.add_column("Status", justify="center")
    
    for metric, value in profile.current_health.items():
        trend = profile.trends.get(metric, HealthTrend.STABLE)
        
        # Determine status color
        if trend == HealthTrend.CRITICAL:
            status = "[red]⚠ Critical[/red]"
        elif trend == HealthTrend.DEGRADING:
            status = "[yellow]↓ Degrading[/yellow]"
        elif trend == HealthTrend.IMPROVING:
            status = "[green]↑ Improving[/green]"
        else:
            status = "[cyan]→ Stable[/cyan]"
        
        # Trend symbol
        trend_symbol = {
            HealthTrend.IMPROVING: "[green]↑[/green]",
            HealthTrend.STABLE: "[cyan]→[/cyan]",
            HealthTrend.DEGRADING: "[yellow]↓[/yellow]",
            HealthTrend.CRITICAL: "[red]⚠[/red]"
        }.get(trend, "?")
        
        table.add_row(
            metric.value,
            f"{value:.2f}",
            trend_symbol,
            status
        )
    
    # Add risk score
    table.add_row(
        "[bold]Risk Score[/bold]",
        f"[bold]{profile.risk_score:.1f}/100[/bold]",
        "",
        _get_risk_status(profile.risk_score)
    )
    
    console.print(table)


def _display_predictions(predictions):
    """Display predictions in a formatted way"""
    
    console.print("\n[bold yellow]⚡ ML Predictions:[/bold yellow]")
    
    for pred in predictions:
        # Determine severity color
        if pred.probability > 0.7:
            color = "red"
        elif pred.probability > 0.4:
            color = "yellow"
        else:
            color = "cyan"
        
        console.print(f"\n[{color}]• {pred.type.value}[/{color}]")
        console.print(f"  Probability: {pred.probability:.1%}")
        console.print(f"  Time Horizon: {pred.time_horizon}")
        console.print(f"  Confidence: {pred.confidence:.1%}")
        console.print(f"  Explanation: {pred.explanation}")
        
        if pred.recommended_actions:
            console.print("  Recommended Actions:")
            for action in pred.recommended_actions:
                console.print(f"    - {action}")


def _display_metric_trend(metric: HealthMetric, history):
    """Display trend for a metric"""
    
    if len(history) < 2:
        console.print("[yellow]Insufficient data for trend analysis[/yellow]")
        return
    
    # Simple ASCII chart
    values = [dp.value for dp in history[-20:]]
    
    console.print(f"\n[bold]Trend for {metric.value}:[/bold]")
    
    # Normalize to 0-10 scale for display
    if values:
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val if max_val > min_val else 1
        
        for i, val in enumerate(values):
            normalized = int((val - min_val) / range_val * 10)
            bar = "█" * normalized + "░" * (10 - normalized)
            console.print(f"{i:2d}: {bar} {val:.2f}")


def _profile_to_json(profile) -> str:
    """Convert profile to JSON"""
    
    data = {
        'timestamp': profile.last_updated.isoformat(),
        'risk_score': profile.risk_score,
        'current_health': {
            m.value: v for m, v in profile.current_health.items()
        },
        'trends': {
            m.value: t.value for m, t in profile.trends.items()
        },
        'predictions': [
            {
                'type': p.type.value,
                'probability': p.probability,
                'time_horizon': str(p.time_horizon),
                'confidence': p.confidence,
                'explanation': p.explanation,
                'actions': p.recommended_actions
            }
            for p in profile.predictions
        ],
        'optimizations': profile.optimization_opportunities
    }
    
    return json.dumps(data, indent=2)


def _generate_html_report(profile) -> str:
    """Generate HTML report"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ML Health Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; }}
            .metric {{ display: inline-block; margin: 10px; padding: 15px; 
                       border: 1px solid #ddd; border-radius: 5px; }}
            .critical {{ background: #e74c3c; color: white; }}
            .warning {{ background: #f39c12; color: white; }}
            .good {{ background: #27ae60; color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ML Health Report</h1>
            <p>Generated: {profile.last_updated}</p>
            <p>Risk Score: {profile.risk_score:.1f}/100</p>
        </div>
        
        <h2>Current Metrics</h2>
        <div class="metrics">
    """
    
    for metric, value in profile.current_health.items():
        trend = profile.trends.get(metric, HealthTrend.STABLE)
        css_class = "metric"
        
        if trend == HealthTrend.CRITICAL:
            css_class += " critical"
        elif trend == HealthTrend.DEGRADING:
            css_class += " warning"
        else:
            css_class += " good"
        
        html += f"""
            <div class="{css_class}">
                <h3>{metric.value}</h3>
                <p>{value:.2f}</p>
                <p>{trend.value}</p>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html


def _create_metrics_table(profile):
    """Create metrics table for dashboard"""
    
    table = Table(show_header=True, expand=True)
    table.add_column("Metric")
    table.add_column("Value")
    table.add_column("Trend")
    
    for metric, value in profile.current_health.items():
        trend = profile.trends.get(metric, HealthTrend.STABLE)
        
        trend_symbol = {
            HealthTrend.IMPROVING: "[green]↑[/green]",
            HealthTrend.STABLE: "[cyan]→[/cyan]",
            HealthTrend.DEGRADING: "[yellow]↓[/yellow]",
            HealthTrend.CRITICAL: "[red]⚠[/red]"
        }.get(trend, "?")
        
        table.add_row(
            metric.value[:15],
            f"{value:.1f}",
            trend_symbol
        )
    
    return table


def _format_predictions(predictions):
    """Format predictions for dashboard"""
    
    if not predictions:
        return "No predictions at this time"
    
    lines = []
    for pred in predictions[:3]:  # Show top 3
        color = "red" if pred.probability > 0.7 else "yellow"
        lines.append(f"[{color}]{pred.type.value[:20]}[/{color}]")
        lines.append(f"  Prob: {pred.probability:.0%} | {pred.time_horizon}")
    
    return "\n".join(lines)


def _get_risk_status(risk_score: float) -> str:
    """Get risk status string"""
    
    if risk_score < 30:
        return "[green]✅ Low Risk[/green]"
    elif risk_score < 60:
        return "[yellow]⚠ Medium Risk[/yellow]"
    elif risk_score < 80:
        return "[orange1]⚠ High Risk[/orange1]"
    else:
        return "[red]🚨 Critical Risk[/red]"


if __name__ == "__main__":
    health_ml()