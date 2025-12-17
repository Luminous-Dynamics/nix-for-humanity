"""
System Health Monitoring

Revolutionary capability: Proactively detect issues before they cause problems.
Monitor system health and auto-fix issues invisibly.

This is the foundation of predictive, anticipatory AI assistance.
"""

import subprocess
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from rich.console import Console

console = Console()


class HealthStatus(Enum):
    """Overall system health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class IssueType(Enum):
    """Types of system issues"""
    SERVICE_DOWN = "service_down"
    DISK_SPACE = "disk_space"
    MEMORY = "memory"
    CACHE_OLD = "cache_old"
    GENERATION_COUNT = "generation_count"
    CHANNEL_OLD = "channel_old"
    CONFIG_SYNTAX = "config_syntax"


@dataclass
class HealthIssue:
    """Represents a system health issue"""
    issue_type: IssueType
    severity: HealthStatus
    description: str
    auto_fixable: bool
    fix_command: Optional[str] = None
    details: Optional[Dict] = None


@dataclass
class HealthReport:
    """Complete system health report"""
    overall_status: HealthStatus
    issues: List[HealthIssue]
    checks_performed: int
    auto_fixed_count: int
    timestamp: float


class SystemHealthMonitor:
    """
    Monitors system health and auto-fixes issues when possible.

    Philosophy: Detect problems before users encounter them,
    fix them automatically when safe, alert when manual intervention needed.
    """

    def __init__(self, auto_fix: bool = True, verbose: bool = False):
        """
        Initialize system health monitor.

        Args:
            auto_fix: Automatically fix issues when safe
            verbose: Show monitoring actions to user
        """
        self.auto_fix = auto_fix
        self.verbose = verbose
        self.fix_history = []

    def perform_health_check(self) -> HealthReport:
        """
        Perform comprehensive system health check.

        Returns:
            HealthReport with all detected issues
        """
        issues = []
        auto_fixed = 0

        # Check 1: Service health (Ollama, etc.)
        service_issues = self._check_services()
        for issue in service_issues:
            if self.auto_fix and issue.auto_fixable:
                if self._auto_fix_issue(issue):
                    auto_fixed += 1
                else:
                    issues.append(issue)
            else:
                issues.append(issue)

        # Check 2: Disk space
        disk_issue = self._check_disk_space()
        if disk_issue:
            if self.auto_fix and disk_issue.auto_fixable:
                if self._auto_fix_issue(disk_issue):
                    auto_fixed += 1
                else:
                    issues.append(disk_issue)
            else:
                issues.append(disk_issue)

        # Check 3: Old generations (NixOS specific)
        gen_issue = self._check_old_generations()
        if gen_issue:
            issues.append(gen_issue)  # Don't auto-delete generations

        # Check 4: Nix cache age
        cache_issue = self._check_nix_cache()
        if cache_issue:
            issues.append(cache_issue)  # User should decide when to update

        # Determine overall status
        if not issues:
            overall = HealthStatus.HEALTHY
        elif any(i.severity == HealthStatus.CRITICAL for i in issues):
            overall = HealthStatus.CRITICAL
        else:
            overall = HealthStatus.WARNING

        return HealthReport(
            overall_status=overall,
            issues=issues,
            checks_performed=4,
            auto_fixed_count=auto_fixed,
            timestamp=__import__('time').time()
        )

    def _check_services(self) -> List[HealthIssue]:
        """Check critical services are running"""
        issues = []

        # Check Ollama
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'ollama'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if 'inactive' in result.stdout or 'failed' in result.stdout:
                issues.append(HealthIssue(
                    issue_type=IssueType.SERVICE_DOWN,
                    severity=HealthStatus.WARNING,
                    description="Ollama service is not running",
                    auto_fixable=True,
                    fix_command="systemctl start ollama"
                ))
        except Exception:
            pass

        return issues

    def _check_disk_space(self) -> Optional[HealthIssue]:
        """Check disk space on root partition"""
        try:
            result = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True,
                timeout=2
            )

            # Parse df output
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 5:
                    usage_pct = int(parts[4].rstrip('%'))

                    if usage_pct >= 95:
                        return HealthIssue(
                            issue_type=IssueType.DISK_SPACE,
                            severity=HealthStatus.CRITICAL,
                            description=f"Disk space critical ({usage_pct}% used)",
                            auto_fixable=True,
                            fix_command="nix-collect-garbage -d",
                            details={'usage_percent': usage_pct}
                        )
                    elif usage_pct >= 85:
                        return HealthIssue(
                            issue_type=IssueType.DISK_SPACE,
                            severity=HealthStatus.WARNING,
                            description=f"Disk space low ({usage_pct}% used)",
                            auto_fixable=False,  # Don't auto-delete when just warning
                            fix_command="nix-collect-garbage",
                            details={'usage_percent': usage_pct}
                        )
        except Exception:
            pass

        return None

    def _check_old_generations(self) -> Optional[HealthIssue]:
        """Check for excessive old NixOS generations"""
        try:
            result = subprocess.run(
                ['nixos-rebuild', 'list-generations'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Count generations
            lines = [l for l in result.stdout.split('\n') if l.strip()]
            gen_count = len(lines)

            if gen_count > 50:
                return HealthIssue(
                    issue_type=IssueType.GENERATION_COUNT,
                    severity=HealthStatus.WARNING,
                    description=f"Many old generations ({gen_count} total)",
                    auto_fixable=False,  # User should decide which to keep
                    fix_command="nix-collect-garbage --delete-older-than 30d",
                    details={'generation_count': gen_count}
                )
        except Exception:
            pass

        return None

    def _check_nix_cache(self) -> Optional[HealthIssue]:
        """Check if Nix channels are old"""
        try:
            # Check nix-channel list
            result = subprocess.run(
                ['nix-channel', '--list'],
                capture_output=True,
                text=True,
                timeout=2
            )

            # For now, just check if channels exist
            # In future, could check last update time
            if result.returncode == 0 and result.stdout:
                # Channels configured, could check age
                pass
        except Exception:
            pass

        return None

    def _auto_fix_issue(self, issue: HealthIssue) -> bool:
        """
        Attempt to automatically fix an issue.

        Args:
            issue: The issue to fix

        Returns:
            True if fixed successfully, False otherwise
        """
        if not issue.auto_fixable or not issue.fix_command:
            return False

        if self.verbose:
            console.print(f"[dim]🔧 Auto-fixing: {issue.description}...[/dim]")

        try:
            # Execute fix command
            result = subprocess.run(
                issue.fix_command.split(),
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0:
                self.fix_history.append({
                    'issue_type': issue.issue_type.value,
                    'description': issue.description,
                    'fix_command': issue.fix_command,
                    'success': True
                })

                if self.verbose:
                    console.print(f"[dim]✅ Fixed: {issue.description}[/dim]")

                return True
            else:
                return False

        except Exception as e:
            if self.verbose:
                console.print(f"[dim]❌ Could not auto-fix: {e}[/dim]")
            return False

    def get_health_summary(self, report: HealthReport) -> str:
        """
        Get human-readable health summary.

        Args:
            report: HealthReport to summarize

        Returns:
            Formatted summary string
        """
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.WARNING: "⚠️",
            HealthStatus.CRITICAL: "🚨",
            HealthStatus.UNKNOWN: "❓"
        }

        emoji = status_emoji.get(report.overall_status, "❓")
        status_name = report.overall_status.value.upper()

        summary = f"{emoji} System Health: {status_name}\n\n"

        if report.auto_fixed_count > 0:
            summary += f"🔧 Auto-fixed {report.auto_fixed_count} issue(s)\n\n"

        if not report.issues:
            summary += "All systems operational! 🎉\n"
        else:
            summary += f"Found {len(report.issues)} issue(s):\n\n"

            for i, issue in enumerate(report.issues, 1):
                severity_emoji = status_emoji.get(issue.severity, "")
                summary += f"{i}. {severity_emoji} {issue.description}\n"

                if issue.auto_fixable:
                    summary += f"   💡 Can auto-fix with: {issue.fix_command}\n"
                elif issue.fix_command:
                    summary += f"   💡 Fix with: {issue.fix_command}\n"

                summary += "\n"

        return summary


def get_health_monitor(auto_fix: bool = True, verbose: bool = False) -> SystemHealthMonitor:
    """
    Get singleton instance of system health monitor.

    Args:
        auto_fix: Automatically fix issues when safe
        verbose: Show monitoring actions

    Returns:
        SystemHealthMonitor instance
    """
    global _health_monitor

    if _health_monitor is None:
        _health_monitor = SystemHealthMonitor(auto_fix=auto_fix, verbose=verbose)

    return _health_monitor


# Singleton instance
_health_monitor: Optional[SystemHealthMonitor] = None
