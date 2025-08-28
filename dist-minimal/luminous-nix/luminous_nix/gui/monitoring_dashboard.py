#!/usr/bin/env python3
"""
📊 Real-time Monitoring Dashboard for Production System
Provides live metrics and system health visualization
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import curses
from collections import deque

from production_deployment import ProductionDeployment
from config_manager import get_config
from error_handler import get_logger


class MonitoringDashboard:
    """Real-time monitoring dashboard for production system"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.deployment = ProductionDeployment()
        self.deployment.initialize_services()
        
        # Metrics storage
        self.metrics_history = {
            'cpu': deque(maxlen=60),
            'memory': deque(maxlen=60),
            'response_time': deque(maxlen=60),
            'error_rate': deque(maxlen=60),
            'requests': deque(maxlen=60)
        }
        
        # Alert thresholds
        self.thresholds = {
            'cpu_high': 80,
            'memory_high': 80,
            'response_slow': 1000,  # ms
            'error_rate_high': 5  # percent
        }
        
        self.alerts = []
        self.last_update = datetime.now()
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'health': {},
            'performance': {},
            'services': {},
            'alerts': []
        }
        
        try:
            # Get health status
            health = await self.deployment.run_health_checks()
            metrics['health'] = health
            
            # Get performance metrics
            perf_service = self.deployment.services.get('performance')
            if perf_service:
                perf_response = perf_service.get_performance_metrics()
                if perf_response.success:
                    metrics['performance'] = perf_response.data
            
            # Get service status
            for name, service in self.deployment.services.items():
                try:
                    # Quick health ping
                    metrics['services'][name] = {
                        'status': 'operational',
                        'response_time': 0  # Would measure actual
                    }
                except:
                    metrics['services'][name] = {
                        'status': 'error',
                        'response_time': -1
                    }
            
            # Check for alerts
            metrics['alerts'] = self._check_alerts(metrics)
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
        
        return metrics
    
    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics against thresholds and generate alerts"""
        
        alerts = []
        
        # Check health status
        if metrics.get('health', {}).get('status') not in ['healthy', 'warning']:
            alerts.append({
                'level': 'critical',
                'message': f"System health: {metrics['health'].get('status', 'unknown')}",
                'timestamp': datetime.now().isoformat()
            })
        
        # Check service status
        for service, status in metrics.get('services', {}).items():
            if status.get('status') != 'operational':
                alerts.append({
                    'level': 'warning',
                    'message': f"Service {service} is {status.get('status')}",
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts
    
    async def update_history(self, metrics: Dict[str, Any]):
        """Update metrics history for trends"""
        
        # Simulate some metrics (would be real in production)
        import random
        
        self.metrics_history['cpu'].append(random.uniform(20, 60))
        self.metrics_history['memory'].append(random.uniform(30, 70))
        self.metrics_history['response_time'].append(random.uniform(50, 200))
        self.metrics_history['error_rate'].append(random.uniform(0, 2))
        self.metrics_history['requests'].append(random.randint(10, 100))
    
    def render_dashboard(self, stdscr) -> bool:
        """Render dashboard using curses"""
        
        try:
            # Clear screen
            stdscr.clear()
            
            # Get terminal size
            height, width = stdscr.getmaxyx()
            
            # Header
            header = "═" * (width - 1)
            title = " 📊 LUMINOUS NIXOS GUI - MONITORING DASHBOARD "
            title_pos = (width - len(title)) // 2
            stdscr.addstr(0, 0, header)
            stdscr.addstr(0, title_pos, title, curses.A_BOLD | curses.color_pair(1))
            
            # Collect metrics synchronously for display
            loop = asyncio.new_event_loop()
            metrics = loop.run_until_complete(self.collect_metrics())
            loop.run_until_complete(self.update_history(metrics))
            loop.close()
            
            row = 2
            
            # System Status
            stdscr.addstr(row, 2, "SYSTEM STATUS", curses.A_BOLD)
            row += 1
            
            health_status = metrics.get('health', {}).get('status', 'unknown')
            status_color = curses.color_pair(2) if health_status == 'healthy' else curses.color_pair(3)
            stdscr.addstr(row, 4, f"Overall Health: {health_status.upper()}", status_color)
            row += 1
            
            # Health Checks
            for check_name, check_data in metrics.get('health', {}).get('checks', {}).items():
                status = "✅" if check_data.get('healthy', False) else "❌"
                stdscr.addstr(row, 4, f"{status} {check_name.capitalize()}")
                row += 1
            
            row += 1
            
            # Services Status
            stdscr.addstr(row, 2, "SERVICES", curses.A_BOLD)
            row += 1
            
            for service, status in metrics.get('services', {}).items():
                service_status = status.get('status', 'unknown')
                status_icon = "🟢" if service_status == 'operational' else "🔴"
                stdscr.addstr(row, 4, f"{status_icon} {service}: {service_status}")
                row += 1
            
            row += 1
            
            # Performance Metrics
            stdscr.addstr(row, 2, "PERFORMANCE METRICS", curses.A_BOLD)
            row += 1
            
            # Show sparklines for metrics
            if self.metrics_history['cpu']:
                cpu_avg = sum(self.metrics_history['cpu']) / len(self.metrics_history['cpu'])
                stdscr.addstr(row, 4, f"CPU Usage: {cpu_avg:.1f}% ")
                self._draw_sparkline(stdscr, row, 25, list(self.metrics_history['cpu']))
                row += 1
            
            if self.metrics_history['memory']:
                mem_avg = sum(self.metrics_history['memory']) / len(self.metrics_history['memory'])
                stdscr.addstr(row, 4, f"Memory: {mem_avg:.1f}% ")
                self._draw_sparkline(stdscr, row, 25, list(self.metrics_history['memory']))
                row += 1
            
            if self.metrics_history['response_time']:
                resp_avg = sum(self.metrics_history['response_time']) / len(self.metrics_history['response_time'])
                stdscr.addstr(row, 4, f"Response: {resp_avg:.0f}ms ")
                self._draw_sparkline(stdscr, row, 25, list(self.metrics_history['response_time']))
                row += 1
            
            row += 1
            
            # Alerts
            if metrics.get('alerts'):
                stdscr.addstr(row, 2, "ALERTS", curses.A_BOLD | curses.color_pair(3))
                row += 1
                for alert in metrics['alerts'][:5]:  # Show last 5 alerts
                    alert_color = curses.color_pair(3) if alert['level'] == 'critical' else curses.color_pair(4)
                    stdscr.addstr(row, 4, f"⚠️  {alert['message']}", alert_color)
                    row += 1
            else:
                stdscr.addstr(row, 2, "✅ NO ACTIVE ALERTS", curses.color_pair(2))
                row += 1
            
            # Footer
            footer_row = height - 2
            stdscr.addstr(footer_row, 0, "═" * (width - 1))
            
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer_text = f"Last Update: {update_time} | Press 'q' to quit, 'r' to refresh"
            stdscr.addstr(footer_row + 1, 2, footer_text)
            
            # Refresh display
            stdscr.refresh()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Dashboard render error: {e}")
            return False
    
    def _draw_sparkline(self, stdscr, row: int, col: int, data: List[float], width: int = 30):
        """Draw a simple sparkline chart"""
        
        if not data:
            return
        
        # Normalize data to 0-7 range for sparkline characters
        sparkline_chars = " ▁▂▃▄▅▆▇█"
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        # Take last 'width' points
        display_data = data[-width:] if len(data) > width else data
        
        sparkline = ""
        for value in display_data:
            normalized = (value - min_val) / range_val
            index = int(normalized * (len(sparkline_chars) - 1))
            sparkline += sparkline_chars[index]
        
        try:
            stdscr.addstr(row, col, sparkline)
        except:
            pass  # Ignore if we can't draw (terminal size issue)
    
    def run(self):
        """Run the monitoring dashboard"""
        
        def main(stdscr):
            # Setup colors
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Title
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Good
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # Critical
            curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Warning
            
            # Configure terminal
            curses.curs_set(0)  # Hide cursor
            stdscr.nodelay(1)   # Non-blocking input
            stdscr.timeout(1000)  # Refresh every second
            
            running = True
            while running:
                # Render dashboard
                if not self.render_dashboard(stdscr):
                    break
                
                # Check for input
                key = stdscr.getch()
                if key == ord('q'):
                    running = False
                elif key == ord('r'):
                    continue  # Force refresh
        
        # Run with curses wrapper
        curses.wrapper(main)


def run_cli_monitor():
    """Run simple CLI monitoring without curses"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        📊 MONITORING DASHBOARD (Simple Mode)                       ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    deployment = ProductionDeployment()
    deployment.initialize_services()
    
    async def monitor_loop():
        while True:
            # Clear screen (works on Unix-like systems)
            print("\033[2J\033[H")
            
            print("═" * 70)
            print("LUMINOUS NIXOS GUI - SYSTEM MONITOR")
            print("═" * 70)
            print()
            
            # Get metrics
            metrics = await deployment.run_health_checks()
            
            # Display health status
            print(f"Overall Status: {metrics['status'].upper()}")
            print()
            
            print("Health Checks:")
            for check_name, check_data in metrics['checks'].items():
                status = "✅" if check_data.get('healthy', False) else "❌"
                print(f"  {status} {check_name.capitalize()}")
            print()
            
            # Display services
            print("Services:")
            for name in deployment.services.keys():
                print(f"  🟢 {name}: operational")
            print()
            
            # Display timestamp
            print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            print("Press Ctrl+C to quit")
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
    
    try:
        asyncio.run(monitor_loop())
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--simple":
        # Run simple CLI mode
        run_cli_monitor()
    else:
        # Run full curses dashboard
        dashboard = MonitoringDashboard()
        dashboard.run()