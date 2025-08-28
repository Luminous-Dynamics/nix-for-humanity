#!/usr/bin/env python3
"""
📊 System Monitoring Dashboard Interface Generator
Creates real-time monitoring UIs for NixOS system metrics
"""

import subprocess
import psutil
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time

sys.path.insert(0, str(Path(__file__).parent))

from nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext
from component_synthesis_engine import ComponentRequirements
from synthesis_bridge import SynthesisBridge


@dataclass
class SystemMetric:
    """Represents a system metric"""
    
    name: str
    value: float
    unit: str
    category: str  # cpu, memory, disk, network, etc.
    timestamp: datetime
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    trend: str = "stable"  # rising, falling, stable


@dataclass
class ServiceStatus:
    """Represents a systemd service status"""
    
    name: str
    active: bool
    enabled: bool
    state: str  # running, stopped, failed, etc.
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    uptime: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ProcessInfo:
    """Represents a system process"""
    
    pid: int
    name: str
    user: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    command: str


class SystemMonitorDashboard:
    """Generates system monitoring dashboard interfaces"""
    
    def __init__(self):
        self.builder = NLInterfaceBuilderV2(use_llm=False)
        self.bridge = SynthesisBridge()
        self.metrics_history = []
        self.refresh_interval = 5  # seconds
        
    def get_system_metrics(self) -> Dict[str, SystemMetric]:
        """Collect current system metrics"""
        
        metrics = {}
        now = datetime.now()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics['cpu_usage'] = SystemMetric(
            name="CPU Usage",
            value=cpu_percent,
            unit="%",
            category="cpu",
            timestamp=now,
            threshold_warning=80,
            threshold_critical=95,
            trend=self._calculate_trend('cpu_usage', cpu_percent)
        )
        
        # Per-core CPU
        cpu_cores = psutil.cpu_percent(interval=1, percpu=True)
        for i, core_percent in enumerate(cpu_cores):
            metrics[f'cpu_core_{i}'] = SystemMetric(
                name=f"Core {i}",
                value=core_percent,
                unit="%",
                category="cpu",
                timestamp=now
            )
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics['memory_usage'] = SystemMetric(
            name="Memory Usage",
            value=memory.percent,
            unit="%",
            category="memory",
            timestamp=now,
            threshold_warning=80,
            threshold_critical=90,
            trend=self._calculate_trend('memory_usage', memory.percent)
        )
        
        metrics['memory_used'] = SystemMetric(
            name="Memory Used",
            value=memory.used / (1024**3),  # Convert to GB
            unit="GB",
            category="memory",
            timestamp=now
        )
        
        # Swap metrics
        swap = psutil.swap_memory()
        metrics['swap_usage'] = SystemMetric(
            name="Swap Usage",
            value=swap.percent,
            unit="%",
            category="memory",
            timestamp=now
        )
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics['disk_usage'] = SystemMetric(
            name="Root Disk Usage",
            value=disk.percent,
            unit="%",
            category="disk",
            timestamp=now,
            threshold_warning=85,
            threshold_critical=95
        )
        
        # Network metrics
        net_io = psutil.net_io_counters()
        metrics['network_sent'] = SystemMetric(
            name="Network Sent",
            value=net_io.bytes_sent / (1024**2),  # MB
            unit="MB",
            category="network",
            timestamp=now
        )
        
        metrics['network_recv'] = SystemMetric(
            name="Network Received",
            value=net_io.bytes_recv / (1024**2),  # MB
            unit="MB",
            category="network",
            timestamp=now
        )
        
        # System load
        load_avg = os.getloadavg()
        metrics['load_1min'] = SystemMetric(
            name="Load (1 min)",
            value=load_avg[0],
            unit="",
            category="system",
            timestamp=now
        )
        
        # Temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current:
                            metrics[f'temp_{name}'] = SystemMetric(
                                name=f"Temperature ({name})",
                                value=entry.current,
                                unit="°C",
                                category="hardware",
                                timestamp=now,
                                threshold_warning=70,
                                threshold_critical=85
                            )
                            break
                    break
        except:
            pass  # Temperature sensors not available
        
        return metrics
    
    def _calculate_trend(self, metric_name: str, current_value: float) -> str:
        """Calculate trend based on historical values"""
        
        # Simple trend calculation (would be more sophisticated in production)
        if len(self.metrics_history) > 0:
            last_metrics = self.metrics_history[-1]
            if metric_name in last_metrics:
                last_value = last_metrics[metric_name].value
                if current_value > last_value * 1.05:
                    return "rising"
                elif current_value < last_value * 0.95:
                    return "falling"
        
        return "stable"
    
    def get_service_status(self, service_names: List[str] = None) -> List[ServiceStatus]:
        """Get status of systemd services"""
        
        if service_names is None:
            # Default important services
            service_names = [
                "sshd", "NetworkManager", "firewalld", 
                "docker", "nginx", "postgresql", "redis"
            ]
        
        services = []
        
        for service_name in service_names:
            try:
                # Check if service exists
                result = subprocess.run(
                    ["systemctl", "show", service_name, "--no-pager"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    props = {}
                    for line in result.stdout.split('\n'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            props[key] = value
                    
                    services.append(ServiceStatus(
                        name=service_name,
                        active=props.get('ActiveState', '') == 'active',
                        enabled=props.get('UnitFileState', '') == 'enabled',
                        state=props.get('ActiveState', 'unknown'),
                        description=props.get('Description', ''),
                        memory_usage=None,  # Would need more parsing
                        cpu_usage=None,
                        uptime=props.get('ActiveEnterTimestamp', '')
                    ))
            except:
                # Service not found or error
                services.append(ServiceStatus(
                    name=service_name,
                    active=False,
                    enabled=False,
                    state="not-found",
                    description=""
                ))
        
        return services
    
    def get_top_processes(self, limit: int = 10) -> List[ProcessInfo]:
        """Get top processes by CPU/memory usage"""
        
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'cmdline']):
            try:
                info = proc.info
                processes.append(ProcessInfo(
                    pid=info['pid'],
                    name=info['name'],
                    user=info['username'] or 'unknown',
                    cpu_percent=info['cpu_percent'] or 0,
                    memory_percent=info['memory_percent'] or 0,
                    memory_mb=(info['memory_info'].rss / (1024**2)) if info['memory_info'] else 0,
                    status=info['status'],
                    command=' '.join(info['cmdline'][:3]) if info['cmdline'] else info['name']
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        
        return processes[:limit]
    
    def generate_dashboard_ui(self) -> Dict:
        """Generate complete system monitoring dashboard"""
        
        # Collect real metrics
        metrics = self.get_system_metrics()
        services = self.get_service_status()
        processes = self.get_top_processes(5)
        
        request = """Create a system monitoring dashboard with:
        1. Header with hostname and uptime
        2. CPU usage gauge with per-core breakdown
        3. Memory usage chart with used/available
        4. Disk usage progress bars
        5. Network activity sparklines
        6. Service status grid with indicators
        7. Top processes table
        8. System load graph
        9. Temperature sensors (if available)
        10. Auto-refresh toggle
        11. Dark theme with status colors (green=ok, yellow=warning, red=critical)"""
        
        context = UserContext(
            user_id="sysadmin",
            expertise_level="expert",
            device_type="desktop",
            preferences={"theme": "dark", "density": "high", "updates": "realtime"}
        )
        
        interface = self.builder.build_interface(request, context)
        
        # Inject real metrics
        self._inject_metrics(interface, metrics, services, processes)
        
        # Store for trend calculation
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 60:  # Keep last 5 minutes
            self.metrics_history.pop(0)
        
        return {
            "interface": interface,
            "metrics_count": len(metrics),
            "services_monitored": len(services),
            "top_processes": len(processes)
        }
    
    def _inject_metrics(self, interface, metrics: Dict[str, SystemMetric], 
                       services: List[ServiceStatus], processes: List[ProcessInfo]):
        """Inject real metrics into interface components"""
        
        for component in interface.components:
            purpose = component.dna.purpose.lower()
            
            # CPU gauge
            if 'cpu' in purpose and 'gauge' in purpose:
                cpu_metric = metrics.get('cpu_usage')
                if cpu_metric:
                    component.value = cpu_metric.value
                    component.max = 100
                    component.threshold_warning = cpu_metric.threshold_warning
                    component.threshold_critical = cpu_metric.threshold_critical
                    component.label = f"CPU: {cpu_metric.value:.1f}%"
            
            # Memory chart
            elif 'memory' in purpose:
                mem_metric = metrics.get('memory_usage')
                if mem_metric:
                    component.data = {
                        "used": mem_metric.value,
                        "free": 100 - mem_metric.value,
                        "label": f"Memory: {mem_metric.value:.1f}%"
                    }
            
            # Service grid
            elif 'service' in purpose or 'grid' in purpose:
                component.services = []
                for service in services:
                    component.services.append({
                        "name": service.name,
                        "status": "🟢" if service.active else "🔴",
                        "state": service.state,
                        "enabled": "✅" if service.enabled else "❌"
                    })
            
            # Process table
            elif 'process' in purpose or 'table' in purpose:
                component.processes = []
                for proc in processes:
                    component.processes.append({
                        "pid": proc.pid,
                        "name": proc.name,
                        "user": proc.user,
                        "cpu": f"{proc.cpu_percent:.1f}%",
                        "memory": f"{proc.memory_mb:.1f}MB",
                        "status": proc.status
                    })
            
            # System info header
            elif 'header' in purpose or 'hostname' in purpose:
                import socket
                component.hostname = socket.gethostname()
                boot_time = datetime.fromtimestamp(psutil.boot_time())
                uptime = datetime.now() - boot_time
                component.uptime = str(uptime).split('.')[0]
    
    def generate_cpu_detail_ui(self) -> Dict:
        """Generate detailed CPU monitoring interface"""
        
        request = """Create a detailed CPU monitoring interface:
        - Per-core usage bars with real-time updates
        - CPU frequency display
        - Process count and thread count
        - Context switches graph
        - Interrupts per second
        - CPU temperature if available
        - Top CPU-consuming processes list"""
        
        context = UserContext(
            user_id="sysadmin",
            expertise_level="expert"
        )
        
        interface = self.builder.build_interface(request, context)
        
        # Get detailed CPU info
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)
        
        # Inject CPU details
        for component in interface.components:
            if 'frequency' in component.dna.purpose.lower():
                component.text = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
            elif 'count' in component.dna.purpose.lower():
                component.text = f"Cores: {cpu_count} | Threads: {cpu_count_logical}"
        
        return {
            "interface": interface,
            "cpu_cores": cpu_count,
            "cpu_threads": cpu_count_logical
        }
    
    def generate_network_monitor_ui(self) -> Dict:
        """Generate network monitoring interface"""
        
        request = """Create a network monitoring interface:
        - Active connections list with IP addresses
        - Bandwidth usage graphs (upload/download)
        - Network interfaces status
        - Packet statistics
        - Connection states pie chart
        - Port usage table
        - Firewall rules summary"""
        
        context = UserContext(
            user_id="network_admin",
            expertise_level="expert"
        )
        
        interface = self.builder.build_interface(request, context)
        
        # Get network info
        connections = psutil.net_connections()
        interfaces = psutil.net_if_stats()
        
        return {
            "interface": interface,
            "active_connections": len(connections),
            "interfaces": len(interfaces)
        }
    
    def generate_alerts_ui(self, threshold_breaches: List[str] = None) -> Dict:
        """Generate alerts and notifications interface"""
        
        request = """Create an alerts dashboard:
        - Critical alerts at top in red
        - Warning alerts in yellow
        - Info messages in blue
        - Alert history timeline
        - Acknowledge button for each alert
        - Filter by severity
        - Export alerts button"""
        
        context = UserContext(
            user_id="sysadmin",
            expertise_level="intermediate"
        )
        
        interface = self.builder.build_interface(request, context)
        
        # Check for actual threshold breaches
        metrics = self.get_system_metrics()
        alerts = []
        
        for name, metric in metrics.items():
            if metric.threshold_critical and metric.value > metric.threshold_critical:
                alerts.append({
                    "severity": "critical",
                    "message": f"{metric.name} is {metric.value:.1f}{metric.unit} (critical: >{metric.threshold_critical})",
                    "timestamp": metric.timestamp.isoformat()
                })
            elif metric.threshold_warning and metric.value > metric.threshold_warning:
                alerts.append({
                    "severity": "warning",
                    "message": f"{metric.name} is {metric.value:.1f}{metric.unit} (warning: >{metric.threshold_warning})",
                    "timestamp": metric.timestamp.isoformat()
                })
        
        # Inject alerts
        for component in interface.components:
            if 'alert' in component.dna.purpose.lower():
                component.alerts = alerts
        
        return {
            "interface": interface,
            "alert_count": len(alerts),
            "critical_count": len([a for a in alerts if a['severity'] == 'critical'])
        }


def demo_system_monitor():
    """Demonstrate system monitoring dashboard generation"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        📊 SYSTEM MONITORING DASHBOARD INTERFACE DEMO               ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    monitor = SystemMonitorDashboard()
    
    # 1. Generate main dashboard
    print("\n1️⃣ Generating Main System Dashboard...")
    result = monitor.generate_dashboard_ui()
    print(f"   ✅ Created with {len(result['interface'].components)} components")
    print(f"   📊 Metrics: {result['metrics_count']}")
    print(f"   ⚙️ Services monitored: {result['services_monitored']}")
    print(f"   🔝 Top processes: {result['top_processes']}")
    
    # 2. Show current metrics
    print("\n2️⃣ Current System Metrics:")
    metrics = monitor.get_system_metrics()
    print(f"   CPU: {metrics['cpu_usage'].value:.1f}%")
    print(f"   Memory: {metrics['memory_usage'].value:.1f}%")
    print(f"   Disk: {metrics['disk_usage'].value:.1f}%")
    print(f"   Load: {metrics['load_1min'].value:.2f}")
    
    # 3. Generate CPU detail view
    print("\n3️⃣ Generating CPU Detail View...")
    result = monitor.generate_cpu_detail_ui()
    print(f"   ✅ CPU monitor created")
    print(f"   🔧 Cores: {result['cpu_cores']}")
    print(f"   🧵 Threads: {result['cpu_threads']}")
    
    # 4. Generate network monitor
    print("\n4️⃣ Generating Network Monitor...")
    result = monitor.generate_network_monitor_ui()
    print(f"   ✅ Network monitor created")
    print(f"   🌐 Active connections: {result['active_connections']}")
    print(f"   🔌 Network interfaces: {result['interfaces']}")
    
    # 5. Check for alerts
    print("\n5️⃣ Generating Alerts Dashboard...")
    result = monitor.generate_alerts_ui()
    print(f"   ✅ Alerts dashboard created")
    print(f"   ⚠️ Total alerts: {result['alert_count']}")
    print(f"   🚨 Critical alerts: {result['critical_count']}")
    
    # 6. Show service status
    print("\n6️⃣ Service Status Check:")
    services = monitor.get_service_status(["sshd", "NetworkManager", "firewalld"])
    for service in services:
        status_icon = "🟢" if service.active else "🔴"
        print(f"   {status_icon} {service.name}: {service.state}")
    
    # 7. Show top processes
    print("\n7️⃣ Top Processes by CPU:")
    processes = monitor.get_top_processes(5)
    for i, proc in enumerate(processes[:3], 1):
        print(f"   {i}. {proc.name} (PID: {proc.pid}) - CPU: {proc.cpu_percent:.1f}%, Mem: {proc.memory_mb:.1f}MB")
    
    print("""
═══════════════════════════════════════════════════════════════════════
✨ System monitoring interfaces generated with real metrics!

Key Features:
• Real-time system metrics collection
• Service status monitoring
• Process tracking and analysis
• Network connection monitoring
• Alert generation based on thresholds
• Multiple specialized views (CPU, Network, Alerts)

Real Data Integrated:
• CPU usage: ✅
• Memory metrics: ✅
• Disk usage: ✅
• Network stats: ✅
• Service status: ✅
• Process list: ✅

Next Steps:
1. Add WebSocket for real-time updates
2. Implement metric history storage
3. Add predictive alerting
4. Create custom metric definitions
5. Add export/reporting features
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    demo_system_monitor()