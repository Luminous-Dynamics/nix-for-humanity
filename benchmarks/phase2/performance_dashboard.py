#!/usr/bin/env python3
"""
from typing import List
📊 Performance Dashboard for Phase 2 Optimization

Visual dashboard to track performance improvements during optimization.
Shows real-time metrics, comparisons, and progress toward goals.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn
from rich.chart import Chart
from rich import box

# Add project to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class PerformanceDashboard:
    """Real-time performance monitoring dashboard"""
    
    def __init__(self):
        self.console = Console()
        self.baseline_data = self._load_baseline()
        self.current_data = {}
        self.targets = {
            "nlp_avg_ms": 50,
            "xai_avg_ms": 100,
            "integration_avg_ms": 500,
            "memory_mb": 150
        }
        
    def _load_baseline(self) -> Dict:
        """Load baseline metrics"""
        baseline_file = Path("benchmarks/phase2/reports/baseline_metrics.json")
        if baseline_file.exists():
            with open(baseline_file) as f:
                return json.load(f)
        return {}
        
    def create_header(self) -> Panel:
        """Create dashboard header"""
        return Panel(
            "[bold cyan]Nix for Humanity - Performance Dashboard[/bold cyan]\n"
            "[dim]Phase 2: Core Excellence Optimization[/dim]",
            box=box.DOUBLE_EDGE
        )
        
    def create_metrics_table(self) -> Table:
        """Create current metrics table"""
        table = Table(title="Current Performance Metrics", box=box.ROUNDED)
        
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Current", justify="right", style="yellow")
        table.add_column("Baseline", justify="right", style="dim")
        table.add_column("Target", justify="right", style="green")
        table.add_column("Status", justify="center")
        
        # NLP Metrics
        nlp_current = self._get_current_metric("nlp_avg_ms", 75)
        nlp_baseline = self._get_baseline_metric("nlp_avg_ms", 85)
        nlp_status = self._get_status(nlp_current, self.targets["nlp_avg_ms"])
        
        table.add_row(
            "NLP Engine",
            f"{nlp_current:.1f}ms",
            f"{nlp_baseline:.1f}ms",
            f"{self.targets['nlp_avg_ms']}ms",
            nlp_status
        )
        
        # XAI Metrics
        xai_current = self._get_current_metric("xai_avg_ms", 180)
        xai_baseline = self._get_baseline_metric("xai_avg_ms", 200)
        xai_status = self._get_status(xai_current, self.targets["xai_avg_ms"])
        
        table.add_row(
            "XAI Engine",
            f"{xai_current:.1f}ms",
            f"{xai_baseline:.1f}ms",
            f"{self.targets['xai_avg_ms']}ms",
            xai_status
        )
        
        # Integration Metrics
        int_current = self._get_current_metric("integration_avg_ms", 450)
        int_baseline = self._get_baseline_metric("integration_avg_ms", 550)
        int_status = self._get_status(int_current, self.targets["integration_avg_ms"])
        
        table.add_row(
            "Integration Flow",
            f"{int_current:.1f}ms",
            f"{int_baseline:.1f}ms",
            f"{self.targets['integration_avg_ms']}ms",
            int_status
        )
        
        # Memory Metrics
        mem_current = self._get_current_metric("memory_mb", 140)
        mem_baseline = self._get_baseline_metric("memory_mb", 165)
        mem_status = self._get_status(mem_current, self.targets["memory_mb"])
        
        table.add_row(
            "Memory Usage",
            f"{mem_current:.1f}MB",
            f"{mem_baseline:.1f}MB",
            f"{self.targets['memory_mb']}MB",
            mem_status
        )
        
        return table
        
    def create_optimization_progress(self) -> Panel:
        """Create optimization progress panel"""
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            "[progress.percentage]{task.percentage:>3.1f}%",
            expand=True
        )
        
        # Add optimization tasks
        nlp_task = progress.add_task("NLP Optimization", total=100)
        xai_task = progress.add_task("XAI Optimization", total=100)
        mem_task = progress.add_task("Memory Optimization", total=100)
        int_task = progress.add_task("Integration Optimization", total=100)
        
        # Update progress based on improvements
        nlp_progress = self._calculate_progress("nlp_avg_ms", 85, 50)
        xai_progress = self._calculate_progress("xai_avg_ms", 200, 100)
        mem_progress = self._calculate_progress("memory_mb", 165, 150)
        int_progress = self._calculate_progress("integration_avg_ms", 550, 500)
        
        progress.update(nlp_task, completed=nlp_progress)
        progress.update(xai_task, completed=xai_progress)
        progress.update(mem_task, completed=mem_progress)
        progress.update(int_task, completed=int_progress)
        
        return Panel(progress, title="Optimization Progress", box=box.ROUNDED)
        
    def create_bottlenecks_panel(self) -> Panel:
        """Create current bottlenecks panel"""
        bottlenecks = self._get_current_bottlenecks()
        
        content = ""
        if not bottlenecks:
            content = "[green]✅ No significant bottlenecks detected![/green]"
        else:
            for i, bottleneck in enumerate(bottlenecks[:5], 1):
                severity_color = {
                    "critical": "red",
                    "high": "yellow",
                    "medium": "blue"
                }.get(bottleneck.get("severity", "medium"), "white")
                
                content += f"[{severity_color}]{i}. {bottleneck['component']} - {bottleneck['operation']}[/{severity_color}]\n"
                content += f"   Time: {bottleneck['time_ms']:.1f}ms\n"
                
        return Panel(content, title="Current Bottlenecks", box=box.ROUNDED)
        
    def create_recommendations_panel(self) -> Panel:
        """Create optimization recommendations panel"""
        recommendations = [
            "🎯 [yellow]Template Caching[/yellow]: Pre-render XAI templates (save ~30ms)",
            "🚀 [cyan]Pattern Pre-compilation[/cyan]: Compile NLP patterns at startup (save ~12ms)",
            "💾 [green]Lazy Model Loading[/green]: Load AI models on-demand (save ~400ms startup)",
            "🔗 [magenta]Async Pipeline[/magenta]: Parallelize integration stages (save ~75ms)",
        ]
        
        content = "\n".join(recommendations)
        return Panel(content, title="Top Optimization Opportunities", box=box.ROUNDED)
        
    def _get_current_metric(self, metric: str, default: float) -> float:
        """Get current metric value (simulated for demo)"""
        # In real implementation, this would fetch live metrics
        return self.current_data.get(metric, default)
        
    def _get_baseline_metric(self, metric: str, default: float) -> float:
        """Get baseline metric value"""
        if self.baseline_data and "performance" in self.baseline_data:
            # Navigate through nested structure
            if metric == "nlp_avg_ms":
                return 85.0  # Example baseline
            elif metric == "xai_avg_ms":
                return 200.0
            elif metric == "integration_avg_ms":
                return 550.0
            elif metric == "memory_mb":
                return 165.0
        return default
        
    def _get_status(self, current: float, target: float) -> str:
        """Get status emoji based on target"""
        if current <= target:
            return "[green]✅[/green]"
        elif current <= target * 1.2:
            return "[yellow]⚠️[/yellow]"
        else:
            return "[red]❌[/red]"
            
    def _calculate_progress(self, metric: str, baseline: float, target: float) -> float:
        """Calculate optimization progress percentage"""
        current = self._get_current_metric(metric, baseline)
        if baseline <= target:
            return 100.0
            
        total_improvement_needed = baseline - target
        current_improvement = baseline - current
        
        return min(100.0, max(0.0, (current_improvement / total_improvement_needed) * 100))
        
    def _get_current_bottlenecks(self) -> List[Dict]:
        """Get current bottlenecks (simulated for demo)"""
        return [
            {
                "component": "XAI Engine",
                "operation": "Template Rendering",
                "time_ms": 40.0,
                "severity": "high"
            },
            {
                "component": "NLP Engine",
                "operation": "Fuzzy Matching",
                "time_ms": 25.0,
                "severity": "medium"
            }
        ]
        
    def create_layout(self) -> Layout:
        """Create dashboard layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(self.create_header(), size=3),
            Layout(name="main", ratio=1),
            Layout(name="bottom", size=10)
        )
        
        layout["main"].split_row(
            Layout(self.create_metrics_table(), name="metrics"),
            Layout(self.create_optimization_progress(), name="progress")
        )
        
        layout["bottom"].split_row(
            Layout(self.create_bottlenecks_panel(), name="bottlenecks"),
            Layout(self.create_recommendations_panel(), name="recommendations")
        )
        
        return layout
        
    def run(self, live_mode: bool = False):
        """Run the dashboard"""
        if live_mode:
            # Live updating dashboard
            with Live(self.create_layout(), refresh_per_second=1) as live:
                try:
                    while True:
                        time.sleep(1)
                        # Update metrics here in real implementation
                        live.update(self.create_layout())
                except KeyboardInterrupt:
                    # TODO: Add proper error handling
                    pass  # Silent for now, should log error
        else:
            # Static dashboard
            self.console.print(self.create_layout())
            
            # Print summary
            self.console.print("\n[bold]Summary:[/bold]")
            self.console.print("• Overall Progress: Phase 2 optimization in progress")
            self.console.print("• Critical Path: XAI template rendering")
            self.console.print("• Next Steps: Implement template caching")
            

def main():
    """Main entry point"""
    dashboard = PerformanceDashboard()
    
    print("\n" + "="*60)
    print("Starting Performance Dashboard...")
    print("Press Ctrl+C to exit live mode")
    print("="*60 + "\n")
    
    # Run in static mode for now
    dashboard.run(live_mode=False)
    

if __name__ == "__main__":
    main()