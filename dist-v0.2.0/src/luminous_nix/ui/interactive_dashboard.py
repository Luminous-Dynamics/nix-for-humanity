#!/usr/bin/env python3
"""
Interactive TUI Dashboard - Comprehensive real-time system overview

This module provides a beautiful, interactive terminal dashboard that
displays all system information, health metrics, and AI features in one place.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.syntax import Syntax
from rich.columns import Columns
from rich.tree import Tree
import psutil

# Import our features
from ..ai.advanced_features.config_dna import ConfigDNAAnalyzer, ConfigDNA
from ..ai.advanced_features.system_modes import SystemModeManager, SystemMode
from ..ai.advanced_features.predictive_health import PredictiveHealthAnalyzer
from ..ai.advanced_features.ml_health_predictor import MLHealthPredictor, HealthMetric
from ..ai.advanced_features.rollback_intelligence import RollbackIntelligence
from ..ai.advanced_features.storage_optimizer import StorageOptimizer


class DashboardView(Enum):
    """Available dashboard views"""
    OVERVIEW = "overview"
    HEALTH = "health"
    DNA = "dna"
    MODES = "modes"
    STORAGE = "storage"
    ROLLBACK = "rollback"
    AI_STATUS = "ai_status"
    PERFORMANCE = "performance"


@dataclass
class DashboardState:
    """Current dashboard state"""
    current_view: DashboardView
    refresh_rate: int  # seconds
    show_animations: bool
    show_predictions: bool
    selected_metric: Optional[HealthMetric]
    
    
class InteractiveDashboard:
    """
    Interactive TUI Dashboard for Luminous Nix
    
    Features:
    - Real-time system metrics
    - Health predictions with ML
    - Configuration DNA visualization
    - System mode status
    - Storage optimization insights
    - Rollback timeline
    - AI/LLM status
    - Performance monitoring
    """
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the dashboard"""
        self.console = console or Console()
        
        # Initialize all analyzers
        self.dna_analyzer = ConfigDNAAnalyzer()
        self.mode_manager = SystemModeManager()
        self.health_analyzer = PredictiveHealthAnalyzer()
        self.ml_predictor = MLHealthPredictor()
        self.rollback_intel = RollbackIntelligence()
        self.storage_optimizer = StorageOptimizer()
        
        # Dashboard state
        self.state = DashboardState(
            current_view=DashboardView.OVERVIEW,
            refresh_rate=2,
            show_animations=True,
            show_predictions=True,
            selected_metric=None
        )
        
        # Metrics cache
        self.metrics_cache = {}
        self.last_update = datetime.now()
        
    def create_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()
        
        # Main structure
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Body layout based on current view
        if self.state.current_view == DashboardView.OVERVIEW:
            layout["body"].split_row(
                Layout(name="left", ratio=1),
                Layout(name="center", ratio=2),
                Layout(name="right", ratio=1)
            )
            
            layout["left"].split_column(
                Layout(name="system_info"),
                Layout(name="mode_status")
            )
            
            layout["center"].split_column(
                Layout(name="health_overview"),
                Layout(name="predictions")
            )
            
            layout["right"].split_column(
                Layout(name="dna_mini"),
                Layout(name="storage_mini")
            )
            
        elif self.state.current_view == DashboardView.HEALTH:
            layout["body"].split_row(
                Layout(name="metrics", ratio=2),
                Layout(name="predictions", ratio=1)
            )
            
            layout["metrics"].split_column(
                Layout(name="health_charts"),
                Layout(name="health_table")
            )
            
        elif self.state.current_view == DashboardView.DNA:
            layout["body"].split_row(
                Layout(name="dna_visual", ratio=2),
                Layout(name="dna_details", ratio=1)
            )
            
        else:
            # Simple single panel for other views
            layout["body"] = Layout(name="main_content")
        
        return layout
    
    def update_header(self, layout: Layout):
        """Update the header section"""
        current_time = datetime.now().strftime("%H:%M:%S")
        view_name = self.state.current_view.value.replace("_", " ").title()
        
        header_text = f"""
[bold cyan]Luminous Nix Interactive Dashboard[/bold cyan]
[dim]View: {view_name} | Time: {current_time} | Refresh: {self.state.refresh_rate}s[/dim]
        """
        
        layout["header"].update(
            Panel(
                Align.center(header_text.strip()),
                border_style="cyan"
            )
        )
    
    def update_footer(self, layout: Layout):
        """Update the footer section"""
        
        # Create view shortcuts
        shortcuts = []
        for i, view in enumerate(DashboardView, 1):
            if view == self.state.current_view:
                shortcuts.append(f"[bold cyan]{i}:{view.value}[/bold cyan]")
            else:
                shortcuts.append(f"{i}:{view.value}")
        
        footer_text = " | ".join(shortcuts) + " | q:quit | r:refresh | a:animations"
        
        layout["footer"].update(
            Panel(
                Align.center(footer_text),
                border_style="dim"
            )
        )
    
    def update_system_info(self) -> Panel:
        """Update system information panel"""
        
        # Gather system info
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get NixOS info
        try:
            with open('/etc/os-release') as f:
                os_info = dict(line.strip().split('=', 1) for line in f if '=' in line)
                nixos_version = os_info.get('VERSION', 'Unknown').strip('"')
        except:
            nixos_version = "Unknown"
        
        info_table = Table(show_header=False, box=None, padding=0)
        info_table.add_column("Key", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("System", f"NixOS {nixos_version}")
        info_table.add_row("CPU", f"{cpu_percent:.1f}%")
        info_table.add_row("Memory", f"{memory.percent:.1f}%")
        info_table.add_row("Disk", f"{disk.percent:.1f}%")
        info_table.add_row("Uptime", self._format_uptime())
        
        return Panel(info_table, title="[bold]System Info[/bold]", border_style="blue")
    
    def update_mode_status(self) -> Panel:
        """Update current mode status"""
        
        current_mode = self.mode_manager.current_mode
        profile = self.mode_manager.profiles[current_mode]
        
        # Mode icon
        icon = {
            SystemMode.MINIMAL: '📦',
            SystemMode.GAMING: '🎮',
            SystemMode.PRIVACY: '🔒',
            SystemMode.DEVELOPER: '💻',
            SystemMode.CREATIVE: '🎨',
            SystemMode.SERVER: '🖥️'
        }.get(current_mode, '⚡')
        
        content = f"""
{icon} [bold cyan]{current_mode.value.upper()}[/bold cyan]

[dim]{profile.description}[/dim]

CPU: {profile.cpu_governor}
GPU: {profile.gpu_profile}
        """
        
        return Panel(content.strip(), title="[bold]Active Mode[/bold]", border_style="green")
    
    def update_health_overview(self) -> Panel:
        """Update health overview panel"""
        
        # Get current health
        profile = self.ml_predictor.analyze_current_health()
        
        # Create health bars
        health_display = []
        
        for metric, value in list(profile.current_health.items())[:5]:
            # Create visual bar
            bar_length = 20
            filled = int(value / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            # Determine color
            if value > 80:
                color = "red"
            elif value > 60:
                color = "yellow"
            else:
                color = "green"
            
            metric_name = metric.value.replace("_", " ").title()[:15]
            health_display.append(
                f"{metric_name:15} [{color}]{bar}[/{color}] {value:5.1f}%"
            )
        
        # Add risk score
        risk_color = "green" if profile.risk_score < 30 else "yellow" if profile.risk_score < 60 else "red"
        health_display.append("")
        health_display.append(f"[bold]Risk Score: [{risk_color}]{profile.risk_score:.1f}/100[/{risk_color}][/bold]")
        
        return Panel(
            "\n".join(health_display),
            title="[bold]System Health[/bold]",
            border_style="cyan"
        )
    
    def update_predictions(self) -> Panel:
        """Update predictions panel"""
        
        if not self.state.show_predictions:
            return Panel("Predictions disabled", title="[bold]ML Predictions[/bold]")
        
        profile = self.ml_predictor.analyze_current_health()
        
        if not profile.predictions:
            content = "[dim]No predictions at this time[/dim]"
        else:
            predictions_text = []
            for pred in profile.predictions[:3]:
                # Icon based on severity
                if pred.probability > 0.7:
                    icon = "🔴"
                    color = "red"
                elif pred.probability > 0.4:
                    icon = "🟡"
                    color = "yellow"
                else:
                    icon = "🟢"
                    color = "green"
                
                predictions_text.append(
                    f"{icon} [{color}]{pred.type.value}[/{color}]\n"
                    f"   Probability: {pred.probability:.0%}\n"
                    f"   Time: {pred.time_horizon}"
                )
            
            content = "\n\n".join(predictions_text)
        
        return Panel(content, title="[bold]ML Predictions[/bold]", border_style="yellow")
    
    def update_dna_mini(self) -> Panel:
        """Update DNA mini visualization"""
        
        try:
            dna = self.dna_analyzer.analyze_config('/etc/nixos/configuration.nix')
            
            # Mini DNA helix
            helix = []
            colors = ['red', 'green', 'blue', 'magenta', 'cyan']
            
            for i in range(5):
                color = colors[i % len(colors)]
                spaces = " " * abs(2 - i % 4)
                helix.append(f"{spaces}[{color}]◉──◉[/{color}]")
            
            content = "\n".join(helix)
            content += f"\n\n[dim]Complexity: {dna.complexity_score:.1f}[/dim]"
            content += f"\n[dim]Health: {dna.health_score:.1f}[/dim]"
            
        except:
            content = "[dim]DNA analysis unavailable[/dim]"
        
        return Panel(content, title="[bold]Config DNA[/bold]", border_style="magenta")
    
    def update_storage_mini(self) -> Panel:
        """Update storage mini panel"""
        
        analysis = self.storage_optimizer.analyze_usage()
        
        # Show top space usage
        content_lines = []
        
        content_lines.append(f"Used: {analysis.total_used / 1e9:.1f} GB")
        content_lines.append(f"Free: {analysis.total_free / 1e9:.1f} GB")
        content_lines.append("")
        
        # Optimization potential
        if analysis.optimization_potential > 1e9:
            content_lines.append(f"[yellow]Can free: {analysis.optimization_potential / 1e9:.1f} GB[/yellow]")
        
        return Panel(
            "\n".join(content_lines),
            title="[bold]Storage[/bold]",
            border_style="blue"
        )
    
    def update_main_view(self, layout: Layout):
        """Update the main view based on current state"""
        
        if self.state.current_view == DashboardView.OVERVIEW:
            # Update all overview panels
            layout["left"]["system_info"].update(self.update_system_info())
            layout["left"]["mode_status"].update(self.update_mode_status())
            layout["center"]["health_overview"].update(self.update_health_overview())
            layout["center"]["predictions"].update(self.update_predictions())
            layout["right"]["dna_mini"].update(self.update_dna_mini())
            layout["right"]["storage_mini"].update(self.update_storage_mini())
            
        elif self.state.current_view == DashboardView.HEALTH:
            self._update_health_view(layout)
            
        elif self.state.current_view == DashboardView.DNA:
            self._update_dna_view(layout)
            
        elif self.state.current_view == DashboardView.MODES:
            self._update_modes_view(layout)
            
        elif self.state.current_view == DashboardView.STORAGE:
            self._update_storage_view(layout)
            
        elif self.state.current_view == DashboardView.ROLLBACK:
            self._update_rollback_view(layout)
            
        elif self.state.current_view == DashboardView.AI_STATUS:
            self._update_ai_status_view(layout)
            
        elif self.state.current_view == DashboardView.PERFORMANCE:
            self._update_performance_view(layout)
    
    def _update_health_view(self, layout: Layout):
        """Update detailed health view"""
        
        # Health charts
        profile = self.ml_predictor.analyze_current_health()
        
        # Create detailed metrics table
        metrics_table = Table(title="System Health Metrics", show_header=True)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", justify="right")
        metrics_table.add_column("Trend", justify="center")
        metrics_table.add_column("Status", justify="center")
        
        for metric, value in profile.current_health.items():
            trend = profile.trends.get(metric)
            
            # Trend symbol
            if trend:
                trend_str = {
                    'improving': '[green]↑[/green]',
                    'stable': '[cyan]→[/cyan]',
                    'degrading': '[yellow]↓[/yellow]',
                    'critical': '[red]⚠[/red]'
                }.get(trend.value, '?')
            else:
                trend_str = '?'
            
            # Status color
            if value > 80:
                status = "[red]High[/red]"
            elif value > 60:
                status = "[yellow]Med[/yellow]"
            else:
                status = "[green]Low[/green]"
            
            metrics_table.add_row(
                metric.value.replace("_", " ").title(),
                f"{value:.1f}%",
                trend_str,
                status
            )
        
        layout["metrics"]["health_table"].update(Panel(metrics_table))
        
        # Create ASCII chart for selected metric
        if self.state.selected_metric:
            chart = self._create_metric_chart(self.state.selected_metric)
            layout["metrics"]["health_charts"].update(Panel(chart, title="Metric History"))
        else:
            layout["metrics"]["health_charts"].update(
                Panel("Select a metric to view history", title="Metric History")
            )
        
        # Update predictions
        layout["predictions"].update(self.update_predictions())
    
    def _update_dna_view(self, layout: Layout):
        """Update DNA analysis view"""
        
        try:
            dna = self.dna_analyzer.analyze_config('/etc/nixos/configuration.nix')
            
            # Visual DNA helix
            from ..ai.advanced_features.dna_visualizer import DNAVisualizer
            visualizer = DNAVisualizer()
            helix = visualizer.create_helix(dna)
            
            layout["dna_visual"].update(
                Panel(helix, title="[bold]Configuration DNA[/bold]", border_style="magenta")
            )
            
            # DNA details
            details = f"""
[bold]Fingerprint:[/bold] {dna.fingerprint[:16]}...

[bold]Complexity:[/bold] {dna.complexity_score:.1f}/100
[bold]Health:[/bold] {dna.health_score:.1f}/100
[bold]Evolution:[/bold] {dna.evolution_stage}

[bold]Dominant Genes:[/bold]
            """
            
            for gene, strength in list(dna.genes.items())[:5]:
                details += f"\n  • {gene}: {strength:.1f}"
            
            layout["dna_details"].update(
                Panel(details, title="[bold]DNA Analysis[/bold]", border_style="blue")
            )
            
        except Exception as e:
            layout["body"]["main_content"].update(
                Panel(f"[red]Error analyzing DNA: {e}[/red]", title="DNA Analysis")
            )
    
    def _update_modes_view(self, layout: Layout):
        """Update modes view"""
        
        # Create modes table
        modes_table = Table(title="System Modes", show_header=True)
        modes_table.add_column("Mode", style="cyan")
        modes_table.add_column("Status", justify="center")
        modes_table.add_column("CPU", justify="center")
        modes_table.add_column("GPU", justify="center")
        modes_table.add_column("Description")
        
        current_mode = self.mode_manager.current_mode
        
        for mode, profile in self.mode_manager.profiles.items():
            # Icon
            icon = {
                SystemMode.MINIMAL: '📦',
                SystemMode.GAMING: '🎮',
                SystemMode.PRIVACY: '🔒',
                SystemMode.DEVELOPER: '💻',
                SystemMode.CREATIVE: '🎨',
                SystemMode.SERVER: '🖥️'
            }.get(mode, '⚡')
            
            # Status
            if mode == current_mode:
                status = "[bold green]ACTIVE[/bold green]"
            else:
                status = "[dim]available[/dim]"
            
            modes_table.add_row(
                f"{icon} {mode.value}",
                status,
                profile.cpu_governor,
                profile.gpu_profile,
                profile.description[:40] + "..."
            )
        
        # Get recommendations
        recommendations = self.mode_manager.get_mode_recommendations()
        
        rec_text = "\n[bold]Recommendations:[/bold]\n"
        if recommendations:
            for mode, reason in recommendations[:3]:
                rec_text += f"\n• {mode.value}: {reason}"
        else:
            rec_text += "\n[dim]No recommendations at this time[/dim]"
        
        content = modes_table
        
        layout["body"]["main_content"].update(
            Panel(
                Columns([modes_table, rec_text]),
                title="[bold]System Mode Management[/bold]",
                border_style="green"
            )
        )
    
    def _update_storage_view(self, layout: Layout):
        """Update storage optimization view"""
        
        analysis = self.storage_optimizer.analyze_usage()
        
        # Create storage table
        storage_table = Table(title="Storage Analysis", show_header=True)
        storage_table.add_column("Category", style="cyan")
        storage_table.add_column("Size", justify="right")
        storage_table.add_column("Percentage", justify="right")
        
        for category, size in analysis.by_category.items():
            percentage = (size / analysis.total_used) * 100 if analysis.total_used > 0 else 0
            storage_table.add_row(
                category,
                f"{size / 1e9:.2f} GB",
                f"{percentage:.1f}%"
            )
        
        # Optimization suggestions
        opt_text = "\n[bold]Optimization Opportunities:[/bold]\n"
        
        for opp in analysis.optimization_opportunities[:5]:
            opt_text += f"\n• {opp.description}"
            opt_text += f"\n  Can free: {opp.size / 1e9:.2f} GB"
        
        layout["body"]["main_content"].update(
            Panel(
                Columns([storage_table, opt_text]),
                title="[bold]Storage Optimization[/bold]",
                border_style="blue"
            )
        )
    
    def _update_rollback_view(self, layout: Layout):
        """Update rollback timeline view"""
        
        analysis = self.rollback_intel.analyze_generations()
        
        # Create timeline
        timeline = Tree("[bold]Generation Timeline[/bold]")
        
        for gen in analysis.generations[:10]:
            # Determine icon
            if gen.generation == analysis.current_generation:
                icon = "🟢"
                style = "bold green"
            elif gen.is_safe:
                icon = "✅"
                style = "cyan"
            else:
                icon = "⚠️"
                style = "yellow"
            
            node = timeline.add(
                f"{icon} Gen {gen.generation} - {gen.date}",
                style=style
            )
            
            # Add details
            if gen.description:
                node.add(f"[dim]{gen.description}[/dim]")
            node.add(f"Risk: {gen.risk_score:.1f}/10")
        
        # Recommendations
        rec_panel = Panel(
            "\n".join(analysis.recommendations),
            title="[bold]Rollback Recommendations[/bold]",
            border_style="yellow"
        )
        
        layout["body"]["main_content"].update(
            Columns([timeline, rec_panel])
        )
    
    def _update_ai_status_view(self, layout: Layout):
        """Update AI/LLM status view"""
        
        # Check AI availability
        ai_status = []
        
        # Ollama status
        try:
            from ..ai.ollama_integration import ollama_client
            if ollama_client.is_available():
                ai_status.append(("[green]✅[/green]", "Ollama", "Online", "Ready"))
            else:
                ai_status.append(("[red]❌[/red]", "Ollama", "Offline", "Not available"))
        except:
            ai_status.append(("[yellow]⚠️[/yellow]", "Ollama", "Error", "Check installation"))
        
        # HRM status
        ai_status.append(("[green]✅[/green]", "HRM", "Loaded", "Reasoning ready"))
        
        # POML status
        ai_status.append(("[green]✅[/green]", "POML", "Active", f"{len(self._get_poml_templates())} templates"))
        
        # Create status table
        status_table = Table(title="AI/LLM Status", show_header=True)
        status_table.add_column("Status", justify="center")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("State")
        status_table.add_column("Details")
        
        for row in ai_status:
            status_table.add_row(*row)
        
        # POML templates list
        templates_text = "\n[bold]Available POML Templates:[/bold]\n"
        for template in self._get_poml_templates()[:10]:
            templates_text += f"\n• {template}"
        
        layout["body"]["main_content"].update(
            Panel(
                Columns([status_table, templates_text]),
                title="[bold]AI/LLM Status[/bold]",
                border_style="magenta"
            )
        )
    
    def _update_performance_view(self, layout: Layout):
        """Update performance monitoring view"""
        
        # Get performance metrics
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        # CPU cores visualization
        cpu_visual = "[bold]CPU Cores:[/bold]\n"
        for i, percent in enumerate(cpu_percent):
            bar_length = 20
            filled = int(percent / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            if percent > 80:
                color = "red"
            elif percent > 50:
                color = "yellow"
            else:
                color = "green"
            
            cpu_visual += f"Core {i}: [{color}]{bar}[/{color}] {percent:5.1f}%\n"
        
        # Memory visualization
        mem_visual = f"""
[bold]Memory:[/bold]
Used:  {memory.used / 1e9:.1f} GB / {memory.total / 1e9:.1f} GB ({memory.percent:.1f}%)
Free:  {memory.available / 1e9:.1f} GB
Swap:  {swap.used / 1e9:.1f} GB / {swap.total / 1e9:.1f} GB ({swap.percent:.1f}%)
        """
        
        # I/O stats
        io_visual = f"""
[bold]I/O Statistics:[/bold]
Disk Read:  {disk_io.read_bytes / 1e9:.2f} GB
Disk Write: {disk_io.write_bytes / 1e9:.2f} GB
Net Sent:   {net_io.bytes_sent / 1e9:.2f} GB
Net Recv:   {net_io.bytes_recv / 1e9:.2f} GB
        """
        
        layout["body"]["main_content"].update(
            Panel(
                Columns([cpu_visual, mem_visual, io_visual]),
                title="[bold]Performance Monitoring[/bold]",
                border_style="cyan"
            )
        )
    
    def _create_metric_chart(self, metric: HealthMetric) -> str:
        """Create ASCII chart for a metric"""
        
        history = list(self.ml_predictor.metric_history[metric])
        
        if len(history) < 2:
            return "Insufficient data for chart"
        
        # Get last 20 values
        values = [dp.value for dp in history[-20:]]
        
        # Normalize to 0-10 scale
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val if max_val > min_val else 1
        
        chart_lines = []
        chart_lines.append(f"[bold]{metric.value} History[/bold]")
        chart_lines.append("")
        
        for i, val in enumerate(values):
            normalized = int((val - min_val) / range_val * 10)
            bar = "█" * normalized + "░" * (10 - normalized)
            chart_lines.append(f"{i:2d}: {bar} {val:.1f}")
        
        return "\n".join(chart_lines)
    
    def _format_uptime(self) -> str:
        """Format system uptime"""
        
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _get_poml_templates(self) -> List[str]:
        """Get list of POML templates"""
        
        from pathlib import Path
        
        template_dir = Path(__file__).parent.parent / "poml" / "templates"
        
        if template_dir.exists():
            return [f.stem for f in template_dir.glob("*.poml")]
        
        return []
    
    def _collect_metrics(self):
        """Collect current metrics for all components"""
        
        # Collect health metrics
        self.ml_predictor.collect_metric(
            HealthMetric.CPU_USAGE,
            psutil.cpu_percent(interval=0.1)
        )
        
        self.ml_predictor.collect_metric(
            HealthMetric.MEMORY_USAGE,
            psutil.virtual_memory().percent
        )
        
        self.ml_predictor.collect_metric(
            HealthMetric.DISK_USAGE,
            psutil.disk_usage('/').percent
        )
    
    def handle_input(self, key: str) -> bool:
        """
        Handle keyboard input
        
        Returns True to continue, False to quit
        """
        
        if key == 'q':
            return False
            
        elif key == 'r':
            # Force refresh
            self._collect_metrics()
            
        elif key == 'a':
            # Toggle animations
            self.state.show_animations = not self.state.show_animations
            
        elif key == 'p':
            # Toggle predictions
            self.state.show_predictions = not self.state.show_predictions
            
        elif key.isdigit():
            # Switch view
            view_num = int(key)
            if 1 <= view_num <= len(DashboardView):
                self.state.current_view = list(DashboardView)[view_num - 1]
        
        return True
    
    async def run(self):
        """Run the interactive dashboard"""
        
        layout = self.create_layout()
        
        with Live(layout, refresh_per_second=1, screen=True) as live:
            try:
                while True:
                    # Update metrics
                    self._collect_metrics()
                    
                    # Update all sections
                    self.update_header(layout)
                    self.update_main_view(layout)
                    self.update_footer(layout)
                    
                    # Wait for refresh interval
                    await asyncio.sleep(self.state.refresh_rate)
                    
            except KeyboardInterrupt:
                pass
        
        self.console.print("\n[cyan]Dashboard closed. Thank you for using Luminous Nix![/cyan]")


def main():
    """Run the dashboard"""
    
    dashboard = InteractiveDashboard()
    asyncio.run(dashboard.run())


if __name__ == "__main__":
    main()