#!/usr/bin/env python3
"""
System Health Monitor for Luminous Nix
Proactive problem detection and recommendations
Now with subprocess-based operations for standard speed monitoring!
"""

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import psutil

# Import native API for massive performance gains
try:
    from luminous_nix.core.native_nix_api import get_native_api

    NATIVE_API_AVAILABLE = True
except ImportError:
    NATIVE_API_AVAILABLE = False


class HealthStatus(Enum):
    """Health status levels"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class IssueCategory(Enum):
    """Issue categories"""

    DISK_SPACE = "disk_space"
    MEMORY = "memory"
    CPU = "cpu"
    PACKAGES = "packages"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    NETWORK = "network"


@dataclass
class HealthCheck:
    """Single health check result"""

    name: str
    status: HealthStatus
    message: str
    category: IssueCategory
    details: Optional[dict[str, Any]] = None
    recommendations: Optional[list[str]] = None


@dataclass
class SystemMetrics:
    """System performance metrics"""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    swap_percent: float
    network_connections: int
    process_count: int
    boot_time: datetime
    uptime: timedelta


class SystemHealthMonitor:
    """
    Monitors system health and provides proactive recommendations
    """

    def __init__(self):
        """Initialize health monitor"""
        self.checks = []
        self.metrics = None
        self.issues = []
        self.recommendations = []

        # Initialize native API for standard speed health checks
        self.native_api = get_native_api() if NATIVE_API_AVAILABLE else None

        # Thresholds
        self.thresholds = {
            "disk_warning": 80,
            "disk_critical": 90,
            "memory_warning": 80,
            "memory_critical": 95,
            "cpu_warning": 80,
            "cpu_critical": 95,
            "swap_warning": 50,
            "swap_critical": 80,
            "outdated_packages_warning": 50,
            "outdated_packages_critical": 100,
        }

    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            self.metrics = SystemMetrics(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=psutil.virtual_memory().percent,
                disk_percent=psutil.disk_usage("/").percent,
                swap_percent=psutil.swap_memory().percent,
                network_connections=len(psutil.net_connections()),
                process_count=len(psutil.pids()),
                boot_time=boot_time,
                uptime=uptime,
            )

            return self.metrics

        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return None

    def check_disk_space(self) -> HealthCheck:
        """Check disk space usage"""
        try:
            usage = psutil.disk_usage("/")
            percent = usage.percent

            # Determine status
            if percent >= self.thresholds["disk_critical"]:
                status = HealthStatus.CRITICAL
                message = f"Critical: Disk usage at {percent:.1f}%"
            elif percent >= self.thresholds["disk_warning"]:
                status = HealthStatus.WARNING
                message = f"Warning: Disk usage at {percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal ({percent:.1f}%)"

            # Generate recommendations
            recommendations = []
            if status != HealthStatus.HEALTHY:
                recommendations.extend(
                    [
                        "Run garbage collection: sudo nix-collect-garbage -d",
                        "Remove old generations: sudo nix-env --delete-generations old",
                        "Clean build artifacts: rm -rf /tmp/nix-build-*",
                        "Check large files: ncdu /",
                    ]
                )

                # Check /nix/store size
                try:
                    nix_store_size = sum(
                        f.stat().st_size
                        for f in Path("/nix/store").rglob("*")
                        if f.is_file()
                    ) / (
                        1024**3
                    )  # GB

                    if nix_store_size > 50:
                        recommendations.insert(
                            0,
                            f"Nix store is {nix_store_size:.1f}GB - consider optimization",
                        )
                except:
                    pass

            return HealthCheck(
                name="Disk Space",
                status=status,
                message=message,
                category=IssueCategory.DISK_SPACE,
                details={
                    "total_gb": usage.total / (1024**3),
                    "used_gb": usage.used / (1024**3),
                    "free_gb": usage.free / (1024**3),
                    "percent": percent,
                },
                recommendations=recommendations,
            )

        except Exception as e:
            return HealthCheck(
                name="Disk Space",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check disk space: {e}",
                category=IssueCategory.DISK_SPACE,
            )

    def check_memory(self) -> HealthCheck:
        """Check memory usage"""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Check RAM
            if mem.percent >= self.thresholds["memory_critical"]:
                status = HealthStatus.CRITICAL
                message = f"Critical: Memory usage at {mem.percent:.1f}%"
            elif mem.percent >= self.thresholds["memory_warning"]:
                status = HealthStatus.WARNING
                message = f"Warning: Memory usage at {mem.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal ({mem.percent:.1f}%)"

            # Check swap if used
            if swap.percent >= self.thresholds["swap_critical"]:
                status = HealthStatus.CRITICAL
                message += f" | Swap critically high ({swap.percent:.1f}%)"
            elif swap.percent >= self.thresholds["swap_warning"]:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.WARNING
                message += f" | Swap usage high ({swap.percent:.1f}%)"

            # Recommendations
            recommendations = []
            if status != HealthStatus.HEALTHY:
                # Find memory-hungry processes
                processes = []
                for proc in psutil.process_iter(["pid", "name", "memory_percent"]):
                    try:
                        if proc.info["memory_percent"] > 5:
                            processes.append(
                                (proc.info["name"], proc.info["memory_percent"])
                            )
                    except:
                        pass

                processes.sort(key=lambda x: x[1], reverse=True)

                if processes:
                    recommendations.append(
                        f"Top memory user: {processes[0][0]} ({processes[0][1]:.1f}%)"
                    )

                recommendations.extend(
                    [
                        "Close unnecessary applications",
                        "Check for memory leaks in running services",
                        "Consider adding more RAM or swap space",
                        "Restart resource-intensive services",
                    ]
                )

            return HealthCheck(
                name="Memory",
                status=status,
                message=message,
                category=IssueCategory.MEMORY,
                details={
                    "ram_total_gb": mem.total / (1024**3),
                    "ram_used_gb": mem.used / (1024**3),
                    "ram_percent": mem.percent,
                    "swap_total_gb": swap.total / (1024**3),
                    "swap_used_gb": swap.used / (1024**3),
                    "swap_percent": swap.percent,
                },
                recommendations=recommendations,
            )

        except Exception as e:
            return HealthCheck(
                name="Memory",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check memory: {e}",
                category=IssueCategory.MEMORY,
            )

    def check_cpu(self) -> HealthCheck:
        """Check CPU usage"""
        try:
            # Get average over 5 seconds
            cpu_percent = psutil.cpu_percent(interval=5)

            if cpu_percent >= self.thresholds["cpu_critical"]:
                status = HealthStatus.CRITICAL
                message = f"Critical: CPU usage at {cpu_percent:.1f}%"
            elif cpu_percent >= self.thresholds["cpu_warning"]:
                status = HealthStatus.WARNING
                message = f"Warning: CPU usage at {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal ({cpu_percent:.1f}%)"

            # Recommendations
            recommendations = []
            if status != HealthStatus.HEALTHY:
                # Find CPU-intensive processes
                processes = []
                for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
                    try:
                        if proc.info["cpu_percent"] > 10:
                            processes.append(
                                (proc.info["name"], proc.info["cpu_percent"])
                            )
                    except:
                        pass

                processes.sort(key=lambda x: x[1], reverse=True)

                if processes:
                    recommendations.append(
                        f"Top CPU user: {processes[0][0]} ({processes[0][1]:.1f}%)"
                    )

                recommendations.extend(
                    [
                        "Check for runaway processes",
                        "Consider nice/renice for background tasks",
                        "Review system services for optimization",
                        "Check for malware or crypto miners",
                    ]
                )

            return HealthCheck(
                name="CPU",
                status=status,
                message=message,
                category=IssueCategory.CPU,
                details={
                    "cpu_percent": cpu_percent,
                    "cpu_count": psutil.cpu_count(),
                    "load_average": os.getloadavg(),
                },
                recommendations=recommendations,
            )

        except Exception as e:
            return HealthCheck(
                name="CPU",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check CPU: {e}",
                category=IssueCategory.CPU,
            )

    def check_packages(self) -> HealthCheck:
        """Check for package issues"""
        try:
            issues = []
            recommendations = []

            # Check for broken packages
            try:
                result = subprocess.run(
                    ["nix-store", "--verify", "--check-contents"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    issues.append("Broken packages detected")
                    recommendations.append(
                        "Run: nix-store --verify --check-contents --repair"
                    )
            except:
                pass

            # Check for outdated channels
            try:
                result = subprocess.run(
                    ["nix-channel", "--list"], capture_output=True, text=True, timeout=5
                )
                # Simple check - could be improved
                if result.stdout:
                    recommendations.append("Update channels: nix-channel --update")
            except:
                pass

            # Count packages
            try:
                result = subprocess.run(
                    ["nix-env", "-q"], capture_output=True, text=True, timeout=5
                )
                package_count = (
                    len(result.stdout.strip().split("\n")) if result.stdout else 0
                )
            except:
                package_count = 0

            # Determine status
            if issues:
                status = HealthStatus.WARNING
                message = f"Package issues detected: {', '.join(issues)}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Package system healthy ({package_count} packages)"

            return HealthCheck(
                name="Packages",
                status=status,
                message=message,
                category=IssueCategory.PACKAGES,
                details={"package_count": package_count, "issues": issues},
                recommendations=recommendations,
            )

        except Exception as e:
            return HealthCheck(
                name="Packages",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check packages: {e}",
                category=IssueCategory.PACKAGES,
            )

    def check_security(self) -> HealthCheck:
        """Check security status"""
        try:
            issues = []
            recommendations = []

            # Check firewall
            try:
                result = subprocess.run(
                    ["sudo", "iptables", "-L", "-n"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if "ACCEPT" in result.stdout and "all" in result.stdout:
                    issues.append("Firewall may be too permissive")
                    recommendations.append("Review firewall rules")
            except:
                pass

            # Check SSH configuration
            ssh_config = Path("/etc/ssh/sshd_config")
            if ssh_config.exists():
                try:
                    content = ssh_config.read_text()
                    if "PermitRootLogin yes" in content:
                        issues.append("Root SSH login enabled")
                        recommendations.append(
                            "Set PermitRootLogin to 'no' in sshd_config"
                        )
                    if "PasswordAuthentication yes" in content:
                        issues.append("Password authentication enabled for SSH")
                        recommendations.append(
                            "Consider using key-based authentication only"
                        )
                except:
                    pass

            # Check for security updates
            recommendations.append(
                "Check for security updates: nixos-rebuild dry-build"
            )

            # Determine status
            if issues:
                status = HealthStatus.WARNING
                message = f"Security concerns: {len(issues)} issue(s)"
            else:
                status = HealthStatus.HEALTHY
                message = "Security checks passed"

            return HealthCheck(
                name="Security",
                status=status,
                message=message,
                category=IssueCategory.SECURITY,
                details={"issues": issues},
                recommendations=recommendations,
            )

        except Exception as e:
            return HealthCheck(
                name="Security",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check security: {e}",
                category=IssueCategory.SECURITY,
            )

    def check_performance(self) -> HealthCheck:
        """Check system performance"""
        try:
            issues = []
            recommendations = []

            # Check I/O wait
            cpu_times = psutil.cpu_times_percent(interval=1)
            if hasattr(cpu_times, "iowait") and cpu_times.iowait > 30:
                issues.append(f"High I/O wait ({cpu_times.iowait:.1f}%)")
                recommendations.append("Check disk performance with iotop")

            # Check zombie processes
            zombies = [
                p for p in psutil.process_iter() if p.status() == psutil.STATUS_ZOMBIE
            ]
            if zombies:
                issues.append(f"{len(zombies)} zombie process(es)")
                recommendations.append("Clean up zombie processes")

            # Check system load
            load = os.getloadavg()
            cpu_count = psutil.cpu_count()
            if load[0] > cpu_count * 2:
                issues.append(f"High system load ({load[0]:.2f})")
                recommendations.append("Investigate high load with htop")

            # Determine status
            if issues:
                status = HealthStatus.WARNING
                message = "Performance issues detected"
            else:
                status = HealthStatus.HEALTHY
                message = "System performance optimal"

            return HealthCheck(
                name="Performance",
                status=status,
                message=message,
                category=IssueCategory.PERFORMANCE,
                details={
                    "load_average": load,
                    "io_wait": cpu_times.iowait if hasattr(cpu_times, "iowait") else 0,
                    "zombie_count": len(zombies),
                },
                recommendations=recommendations,
            )

        except Exception as e:
            return HealthCheck(
                name="Performance",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check performance: {e}",
                category=IssueCategory.PERFORMANCE,
            )

    def run_full_check(self) -> tuple[HealthStatus, list[HealthCheck]]:
        """Run all health checks"""
        self.checks = []

        # Collect metrics first
        self.collect_metrics()

        # Run all checks
        self.checks.append(self.check_disk_space())
        self.checks.append(self.check_memory())
        self.checks.append(self.check_cpu())
        self.checks.append(self.check_packages())
        self.checks.append(self.check_security())
        self.checks.append(self.check_performance())

        # Determine overall status
        if any(c.status == HealthStatus.CRITICAL for c in self.checks):
            overall_status = HealthStatus.CRITICAL
        elif any(c.status == HealthStatus.WARNING for c in self.checks):
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY

        return overall_status, self.checks

    def get_recommendations(self) -> list[str]:
        """Get all recommendations from checks"""
        recommendations = []

        for check in self.checks:
            if check.recommendations:
                recommendations.extend(check.recommendations)

        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)

        return unique_recommendations

    def get_summary(self) -> str:
        """Get health summary"""
        if not self.checks:
            return "No health checks run yet"

        overall_status, _ = self.run_full_check()

        summary_parts = [f"Overall Status: {overall_status.value.upper()}"]

        # Count by status
        status_counts = {}
        for check in self.checks:
            status = check.status
            status_counts[status] = status_counts.get(status, 0) + 1

        summary_parts.append(
            "Checks: "
            + ", ".join(
                f"{count} {status.value}" for status, count in status_counts.items()
            )
        )

        # Critical issues
        critical = [c for c in self.checks if c.status == HealthStatus.CRITICAL]
        if critical:
            summary_parts.append(f"CRITICAL: {', '.join(c.name for c in critical)}")

        # Warnings
        warnings = [c for c in self.checks if c.status == HealthStatus.WARNING]
        if warnings:
            summary_parts.append(f"Warnings: {', '.join(c.name for c in warnings)}")

        return " | ".join(summary_parts)

    def export_report(self, format: str = "json") -> str:
        """Export health report"""
        if format == "json":
            report = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": self.get_summary(),
                "metrics": {
                    "cpu_percent": self.metrics.cpu_percent if self.metrics else None,
                    "memory_percent": self.metrics.memory_percent
                    if self.metrics
                    else None,
                    "disk_percent": self.metrics.disk_percent if self.metrics else None,
                    "uptime": str(self.metrics.uptime) if self.metrics else None,
                },
                "checks": [
                    {
                        "name": check.name,
                        "status": check.status.value,
                        "message": check.message,
                        "category": check.category.value,
                        "recommendations": check.recommendations,
                    }
                    for check in self.checks
                ],
                "recommendations": self.get_recommendations(),
            }
            return json.dumps(report, indent=2)

        elif format == "text":
            lines = [
                "=" * 60,
                "SYSTEM HEALTH REPORT",
                "=" * 60,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                self.get_summary(),
                "",
                "DETAILED CHECKS:",
                "-" * 40,
            ]

            for check in self.checks:
                status_symbol = {
                    HealthStatus.HEALTHY: "✅",
                    HealthStatus.WARNING: "⚠️",
                    HealthStatus.CRITICAL: "🔴",
                    HealthStatus.UNKNOWN: "❓",
                }.get(check.status, "")

                lines.append(f"{status_symbol} {check.name}: {check.message}")

                if check.recommendations:
                    for rec in check.recommendations:
                        lines.append(f"   → {rec}")

            lines.extend(["", "RECOMMENDATIONS:", "-" * 40])

            for i, rec in enumerate(self.get_recommendations(), 1):
                lines.append(f"{i}. {rec}")

            return "\n".join(lines)

        return ""


# Example usage
if __name__ == "__main__":
    monitor = SystemHealthMonitor()

    print("Running system health check...")
    overall_status, checks = monitor.run_full_check()

    print("\n" + monitor.get_summary())

    print("\n" + "=" * 60)
    print("DETAILED REPORT")
    print("=" * 60)

    for check in checks:
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.WARNING: "⚠️",
            HealthStatus.CRITICAL: "🔴",
            HealthStatus.UNKNOWN: "❓",
        }.get(check.status, "")

        print(f"\n{status_emoji} {check.name}")
        print(f"   Status: {check.status.value}")
        print(f"   Message: {check.message}")

        if check.recommendations:
            print("   Recommendations:")
            for rec in check.recommendations:
                print(f"      • {rec}")

    print("\n" + "=" * 60)
    print("TOP RECOMMENDATIONS")
    print("=" * 60)

    for i, rec in enumerate(monitor.get_recommendations()[:5], 1):
        print(f"{i}. {rec}")

    # Export report
    # report_json = monitor.export_report('json')
    # Path('health_report.json').write_text(report_json)
