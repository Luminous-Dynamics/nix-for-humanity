#!/usr/bin/env python3
"""
Integration Monitoring Dashboard

A simple terminal-based dashboard that shows the current state of all
integration bridges and feature readiness in real-time.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from luminous_nix.bridges.poml_cli_bridge import POMLtoCLIBridge
from luminous_nix.bridges.store_trinity_bridge import StoreTrinityBridge
from luminous_nix.bridges.tui_backend_bridge import TUIBackendBridge
from luminous_nix.integration.feature_readiness import FeatureReadinessTracker


class IntegrationDashboard:
    """
    Terminal dashboard for monitoring integration progress.
    """
    
    def __init__(self):
        """Initialize dashboard components"""
        self.tracker = FeatureReadinessTracker()
        
        # Initialize bridges with current readiness levels
        poml_readiness = self.tracker.features.get('poml_consciousness', {}).readiness or 0.6
        store_readiness = self.tracker.features.get('data_trinity', {}).readiness or 0.4
        tui_readiness = self.tracker.features.get('tui_interface', {}).readiness or 0.7
        
        self.poml_bridge = POMLtoCLIBridge(readiness=poml_readiness)
        self.store_bridge = StoreTrinityBridge(readiness=store_readiness)
        self.tui_bridge = TUIBackendBridge(readiness=tui_readiness)
        
        # Dashboard state
        self.refresh_rate = 2.0  # seconds
        self.running = True
        self.last_update = datetime.now()
    
    def clear_screen(self):
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")
    
    def get_progress_bar(self, value: float, width: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int(value * width)
        empty = width - filled
        
        # Color based on readiness
        if value >= 0.75:
            color = "\033[92m"  # Green
        elif value >= 0.5:
            color = "\033[93m"  # Yellow
        elif value >= 0.25:
            color = "\033[91m"  # Light red
        else:
            color = "\033[90m"  # Gray
        
        reset = "\033[0m"
        return f"{color}[{'█' * filled}{'░' * empty}]{reset} {value:.1%}"
    
    def get_mode_indicator(self, mode: str) -> str:
        """Get colored mode indicator"""
        colors = {
            'shadow': '\033[90m',      # Gray
            'display': '\033[90m',     # Gray
            'memory': '\033[90m',      # Gray
            'suggest': '\033[93m',     # Yellow
            'read': '\033[93m',        # Yellow
            'backed': '\033[93m',      # Yellow
            'assisted': '\033[92m',    # Green
            'confirm': '\033[92m',     # Green
            'duckdb': '\033[92m',      # Green
            'chromadb': '\033[94m',    # Blue
            'full': '\033[95m',        # Magenta
            'control': '\033[95m',     # Magenta
            'trinity': '\033[95m',     # Magenta
            'kuzu': '\033[94m',        # Blue
        }
        
        color = colors.get(mode, '\033[0m')
        reset = '\033[0m'
        return f"{color}{mode:12}{reset}"
    
    def render_header(self):
        """Render dashboard header"""
        print("═" * 70)
        print("  🌟 LUMINOUS NIX INTEGRATION MONITORING DASHBOARD 🌟")
        print("═" * 70)
        print(f"  Last Update: {self.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Press Ctrl+C to exit | Auto-refresh every {self.refresh_rate}s")
        print()
    
    def render_overall_status(self):
        """Render overall system status"""
        status = self.tracker.get_status()
        
        print("┌" + "─" * 68 + "┐")
        print("│ OVERALL SYSTEM STATUS" + " " * 46 + "│")
        print("├" + "─" * 68 + "┤")
        
        # Overall progress
        print(f"│ System Readiness: {self.get_progress_bar(status['overall_readiness'], 30):50} │")
        
        # Feature counts
        working = status['working_count']
        enabled = status['enabled_count']
        total = status['total_features']
        
        print(f"│ Working Features: {working}/{total:15} Enabled: {enabled}/{total:20} │")
        print("└" + "─" * 68 + "┘")
        print()
    
    def render_bridge_status(self):
        """Render bridge status"""
        print("┌" + "─" * 68 + "┐")
        print("│ INTEGRATION BRIDGES" + " " * 48 + "│")
        print("├" + "─" * 68 + "┤")
        
        # POML Bridge
        poml_stats = self.poml_bridge.get_statistics()
        print(f"│ POML → CLI Bridge" + " " * 50 + "│")
        print(f"│   Readiness: {self.get_progress_bar(self.poml_bridge.readiness, 25):55} │")
        success_str = f"{poml_stats['success_rate']:.0%}"
        print(f"│   Mode: {self.get_mode_indicator(self.poml_bridge.get_execution_mode().value):35} "
              f"Success: {success_str:>18} │")
        print(f"│   Commands: {poml_stats.get('total_executions', 0):>3}  "
              f"Shadows: {poml_stats.get('shadows', 0):>3}  "
              f"Suggests: {poml_stats.get('suggestions', 0):>3}  "
              f"Executed: {poml_stats.get('executions', 0):>3}           │")
        
        print("├" + "─" * 68 + "┤")
        
        # Store Bridge
        store_stats = self.store_bridge.get_statistics()
        print(f"│ Store → Trinity Bridge" + " " * 45 + "│")
        print(f"│   Readiness: {self.get_progress_bar(self.store_bridge.readiness, 25):55} │")
        success_str = f"{store_stats['success_rate']:.0%}"
        print(f"│   Mode: {self.get_mode_indicator(self.store_bridge.storage_mode.value):35} "
              f"Success: {success_str:>18} │")
        
        backends = store_stats['backends_available']
        backend_str = []
        if backends.get('json_backup'):
            backend_str.append("JSON✓")
        if backends.get('duckdb'):
            backend_str.append("DuckDB✓")
        if backends.get('chromadb'):
            backend_str.append("ChromaDB✓")
        if backends.get('kuzu'):
            backend_str.append("Kùzu✓")
        
        backend_display = ', '.join(backend_str) if backend_str else 'Memory only'
        print(f"│   Items: {store_stats['memory_items']:>3}  "
              f"Events: {store_stats['total_events']:>3}  "
              f"Backends: {backend_display:>27} │")
        
        print("├" + "─" * 68 + "┤")
        
        # TUI Bridge
        tui_stats = self.tui_bridge.get_statistics()
        print(f"│ TUI ↔ Backend Bridge" + " " * 46 + "│")
        print(f"│   Readiness: {self.get_progress_bar(self.tui_bridge.readiness, 25):55} │")
        print(f"│   Mode: {self.get_mode_indicator(self.tui_bridge.interaction_mode.value):35} "
              f"Connected: {'Yes' if self.tui_bridge.is_connected else 'No':>16} │")
        print(f"│   Sent: {tui_stats['events_sent']:>3}  "
              f"Received: {tui_stats['events_received']:>3}  "
              f"Dropped: {tui_stats['events_dropped']:>3}  "
              f"Errors: {tui_stats['errors_count']:>3}           │")
        
        print("└" + "─" * 68 + "┘")
        print()
    
    def render_feature_grid(self):
        """Render feature readiness grid"""
        print("┌" + "─" * 68 + "┐")
        print("│ FEATURE READINESS GRID" + " " * 45 + "│")
        print("├" + "─" * 20 + "┬" + "─" * 47 + "┤")
        
        for name, feature in self.tracker.features.items():
            # Truncate name if too long
            display_name = (name[:17] + "...") if len(name) > 20 else name
            
            # Get completion count
            completed = sum(1 for c in feature.activation_criteria if c['completed'])
            total = len(feature.activation_criteria)
            
            # Format row
            icon = feature.level.icon
            enabled = "ON " if feature.enabled else "OFF"
            
            print(f"│ {icon} {display_name:17} │ "
                  f"{self.get_progress_bar(feature.readiness, 20):32} "
                  f"{enabled} {completed}/{total:2} │")
        
        print("└" + "─" * 20 + "┴" + "─" * 47 + "┘")
        print()
    
    def render_activation_timeline(self):
        """Render expected activation timeline"""
        print("┌" + "─" * 68 + "┐")
        print("│ ACTIVATION TIMELINE (Projected)" + " " * 35 + "│")
        print("├" + "─" * 68 + "┤")
        
        # Calculate weeks to activation for each feature
        timeline = []
        for name, feature in self.tracker.features.items():
            if feature.readiness < 0.75:
                # Assume 5% improvement per week
                weeks_needed = int((0.75 - feature.readiness) / 0.05)
                timeline.append((weeks_needed, name, feature.readiness))
        
        # Sort by weeks needed
        timeline.sort()
        
        # Show next 5 activations
        for weeks, name, current in timeline[:5]:
            if weeks == 0:
                time_str = "This week!"
            elif weeks == 1:
                time_str = "Next week"
            else:
                time_str = f"~{weeks} weeks"
            
            print(f"│   {time_str:12} → {name:25} (currently {current:.0%})     │")
        
        if not timeline:
            print("│   All features activated! 🎉" + " " * 38 + "│")
        
        print("└" + "─" * 68 + "┘")
        print()
    
    def render_integration_tips(self):
        """Render integration tips"""
        tips = [
            "💡 Run progressive tests weekly to increase readiness",
            "📈 Success increases readiness, failures decrease it",
            "🔗 Bridges work together - improve one to help others",
            "✅ Complete activation criteria to unlock features",
            "🎯 Focus on features closest to 75% activation threshold"
        ]
        
        # Rotate through tips
        tip_index = int(time.time() / 5) % len(tips)
        
        print("┌" + "─" * 68 + "┐")
        print(f"│ {tips[tip_index]:66} │")
        print("└" + "─" * 68 + "┘")
    
    def render(self):
        """Render complete dashboard"""
        self.clear_screen()
        self.render_header()
        self.render_overall_status()
        self.render_bridge_status()
        self.render_feature_grid()
        self.render_activation_timeline()
        self.render_integration_tips()
        
        self.last_update = datetime.now()
    
    def simulate_progress(self):
        """Simulate some progress for demonstration"""
        import random
        
        # Small random adjustments to show movement
        self.poml_bridge.readiness += random.uniform(-0.01, 0.02)
        self.poml_bridge.readiness = max(0, min(1, self.poml_bridge.readiness))
        
        self.store_bridge.readiness += random.uniform(-0.01, 0.02)
        self.store_bridge.readiness = max(0, min(1, self.store_bridge.readiness))
        
        self.tui_bridge.readiness += random.uniform(-0.01, 0.02)
        self.tui_bridge.readiness = max(0, min(1, self.tui_bridge.readiness))
        
        # Update tracker
        self.tracker.update_readiness('poml_consciousness', absolute=self.poml_bridge.readiness)
        self.tracker.update_readiness('data_trinity', absolute=self.store_bridge.readiness)
        self.tracker.update_readiness('tui_interface', absolute=self.tui_bridge.readiness)
        
        # Simulate some events
        if random.random() > 0.7:
            self.poml_bridge.progressive_test()
        if random.random() > 0.8:
            self.store_bridge.progressive_test()
        if random.random() > 0.9:
            self.tui_bridge.progressive_test()
    
    def run(self, demo_mode: bool = False):
        """
        Run the dashboard.
        
        Args:
            demo_mode: If True, simulate progress for demonstration
        """
        print("Starting Integration Dashboard...")
        print("Loading bridges and trackers...")
        time.sleep(1)
        
        try:
            while self.running:
                self.render()
                
                if demo_mode:
                    self.simulate_progress()
                
                time.sleep(self.refresh_rate)
                
        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")
            print("Final integration report saved to: integration_report.json")
            
            # Save final report
            self.save_report()
    
    def save_report(self):
        """Save integration report to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_readiness': self.tracker.get_status()['overall_readiness'],
            'bridges': {
                'poml_cli': {
                    'readiness': self.poml_bridge.readiness,
                    'mode': self.poml_bridge.get_execution_mode().value,
                    'statistics': self.poml_bridge.get_statistics()
                },
                'store_trinity': {
                    'readiness': self.store_bridge.readiness,
                    'mode': self.store_bridge.storage_mode.value,
                    'statistics': self.store_bridge.get_statistics()
                },
                'tui_backend': {
                    'readiness': self.tui_bridge.readiness,
                    'mode': self.tui_bridge.interaction_mode.value,
                    'statistics': self.tui_bridge.get_statistics()
                }
            },
            'features': {
                name: {
                    'readiness': feature.readiness,
                    'enabled': feature.enabled,
                    'level': feature.level.name
                }
                for name, feature in self.tracker.features.items()
            }
        }
        
        with open('integration_report.json', 'w') as f:
            json.dump(report, f, indent=2)


def main():
    """Run the dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Integration Monitoring Dashboard')
    parser.add_argument('--demo', action='store_true', 
                       help='Run in demo mode with simulated progress')
    parser.add_argument('--refresh', type=float, default=2.0,
                       help='Refresh rate in seconds (default: 2.0)')
    
    args = parser.parse_args()
    
    dashboard = IntegrationDashboard()
    dashboard.refresh_rate = args.refresh
    dashboard.run(demo_mode=args.demo)


if __name__ == "__main__":
    main()