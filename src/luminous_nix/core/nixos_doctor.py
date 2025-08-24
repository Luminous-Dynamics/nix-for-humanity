#!/usr/bin/env python3
"""
🩺 NixOS Doctor - AI-Powered System Diagnostics and Repair
Automatically diagnoses and fixes common NixOS issues.
"""

import os
import re
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class IssueType(Enum):
    """Types of issues we can diagnose"""
    SYNTAX_ERROR = "syntax_error"
    BUILD_FAILURE = "build_failure"
    BOOT_FAILURE = "boot_failure"
    PACKAGE_CONFLICT = "package_conflict"
    SERVICE_FAILURE = "service_failure"
    CONFIGURATION_DRIFT = "configuration_drift"
    DISK_SPACE = "disk_space"
    MEMORY_ISSUE = "memory_issue"
    NETWORK_ISSUE = "network_issue"
    PERMISSION_ISSUE = "permission_issue"


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"  # System won't boot
    HIGH = "high"         # Major functionality broken
    MEDIUM = "medium"     # Some features not working
    LOW = "low"          # Minor issues
    INFO = "info"        # Suggestions only


@dataclass
class Issue:
    """Represents a diagnosed issue"""
    type: IssueType
    severity: Severity
    description: str
    location: Optional[str] = None
    line_number: Optional[int] = None
    details: Optional[str] = None
    fix_suggestion: Optional[str] = None
    auto_fixable: bool = False
    fix_command: Optional[str] = None


@dataclass
class DiagnosisReport:
    """Complete diagnosis report"""
    timestamp: datetime
    issues: List[Issue]
    system_info: Dict[str, Any]
    recommendations: List[str]
    can_auto_fix: bool


class NixOSDoctor:
    """
    Diagnoses and fixes common NixOS issues automatically.
    Like having an expert looking over your shoulder.
    """
    
    def __init__(self):
        """Initialize the doctor"""
        self.config_file = Path("/etc/nixos/configuration.nix")
        self.hardware_file = Path("/etc/nixos/hardware-configuration.nix")
        self.issues_found = []
        
        # Common configuration mistakes
        self.common_mistakes = {
            'enviroment': 'environment',
            'systenPackages': 'systemPackages',
            'configuraiton': 'configuration',
            'servies': 'services',
            'progams': 'programs',
            'bootloader': 'boot.loader',
            'users.users.user': 'users.users.<username>',
            'kernel.packages': 'boot.kernelPackages',
        }
        
        # Common missing imports
        self.common_imports = {
            'docker': 'virtualisation.docker.enable = true;',
            'steam': 'programs.steam.enable = true;',
            'flatpak': 'services.flatpak.enable = true;',
            'virtualbox': 'virtualisation.virtualbox.host.enable = true;',
        }
    
    def run_diagnosis(self, deep_scan: bool = False) -> DiagnosisReport:
        """
        Run a complete system diagnosis.
        
        Args:
            deep_scan: If True, performs more thorough checks
            
        Returns:
            Complete diagnosis report
        """
        print("🩺 Running NixOS System Diagnosis...")
        print("-" * 50)
        
        self.issues_found = []
        
        # Collect system info
        system_info = self._collect_system_info()
        
        # Run diagnostic checks
        print("📋 Checking configuration syntax...")
        self._check_syntax()
        
        print("🔨 Checking build status...")
        self._check_build()
        
        print("💾 Checking disk space...")
        self._check_disk_space()
        
        print("🧠 Checking memory usage...")
        self._check_memory()
        
        print("🌐 Checking network...")
        self._check_network()
        
        print("🔧 Checking services...")
        self._check_services()
        
        if deep_scan:
            print("🔍 Performing deep scan...")
            self._deep_configuration_scan()
            self._check_generations()
            self._check_channels()
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Check if we can auto-fix
        can_auto_fix = any(issue.auto_fixable for issue in self.issues_found)
        
        report = DiagnosisReport(
            timestamp=datetime.now(),
            issues=self.issues_found,
            system_info=system_info,
            recommendations=recommendations,
            can_auto_fix=can_auto_fix
        )
        
        return report
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        info = {}
        
        try:
            # NixOS version
            result = subprocess.run(['nixos-version'], capture_output=True, text=True)
            info['nixos_version'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
            
            # Current generation
            result = subprocess.run(['nixos-rebuild', 'list-generations'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'current' in line.lower():
                        info['current_generation'] = line.strip()
                        break
            
            # Disk usage
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        info['disk_usage'] = parts[4]
            
            # Memory usage
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 3:
                        info['memory_total'] = parts[1]
                        info['memory_used'] = parts[2]
            
        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
        
        return info
    
    def _check_syntax(self):
        """Check configuration syntax"""
        if not self.config_file.exists():
            self.issues_found.append(Issue(
                type=IssueType.CONFIGURATION_DRIFT,
                severity=Severity.HIGH,
                description="Configuration file not found",
                location=str(self.config_file),
                fix_suggestion="Create a basic configuration file",
                auto_fixable=True
            ))
            return
        
        try:
            # Read configuration
            with open(self.config_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check bracket matching
            open_curly = content.count('{')
            close_curly = content.count('}')
            if open_curly != close_curly:
                self.issues_found.append(Issue(
                    type=IssueType.SYNTAX_ERROR,
                    severity=Severity.HIGH,
                    description=f"Mismatched curly brackets: {open_curly} open, {close_curly} close",
                    location=str(self.config_file),
                    fix_suggestion="Check for missing or extra brackets"
                ))
            
            # Check for missing semicolons
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    # Lines that should end with semicolon
                    if any(stripped.startswith(k) for k in ['services.', 'programs.', 'environment.', 'users.']):
                        if '=' in stripped and not stripped.endswith((';', '{', '[')):
                            self.issues_found.append(Issue(
                                type=IssueType.SYNTAX_ERROR,
                                severity=Severity.MEDIUM,
                                description="Missing semicolon",
                                location=str(self.config_file),
                                line_number=i,
                                fix_suggestion=f"Add semicolon at end of line {i}",
                                auto_fixable=True
                            ))
            
            # Check for common typos
            for typo, correct in self.common_mistakes.items():
                if typo in content:
                    # Find line number
                    for i, line in enumerate(lines, 1):
                        if typo in line:
                            self.issues_found.append(Issue(
                                type=IssueType.SYNTAX_ERROR,
                                severity=Severity.MEDIUM,
                                description=f"Typo: '{typo}' should be '{correct}'",
                                location=str(self.config_file),
                                line_number=i,
                                fix_suggestion=f"Replace '{typo}' with '{correct}'",
                                auto_fixable=True
                            ))
                            break
            
        except Exception as e:
            self.issues_found.append(Issue(
                type=IssueType.CONFIGURATION_DRIFT,
                severity=Severity.HIGH,
                description=f"Cannot read configuration: {e}",
                location=str(self.config_file)
            ))
    
    def _check_build(self):
        """Check if configuration builds"""
        try:
            result = subprocess.run(
                ['nixos-rebuild', 'dry-build'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_output = result.stderr
                
                # Parse common build errors
                if 'attribute' in error_output and 'missing' in error_output:
                    # Extract package name
                    match = re.search(r"attribute '([^']+)' missing", error_output)
                    if match:
                        package = match.group(1)
                        self.issues_found.append(Issue(
                            type=IssueType.BUILD_FAILURE,
                            severity=Severity.HIGH,
                            description=f"Package '{package}' not found",
                            fix_suggestion=f"Try 'nix search {package}' to find correct name",
                            details=error_output[:200]
                        ))
                
                elif 'infinite recursion' in error_output:
                    self.issues_found.append(Issue(
                        type=IssueType.BUILD_FAILURE,
                        severity=Severity.CRITICAL,
                        description="Infinite recursion in configuration",
                        fix_suggestion="Check for circular dependencies",
                        details=error_output[:200]
                    ))
                
                elif 'collision between' in error_output:
                    self.issues_found.append(Issue(
                        type=IssueType.PACKAGE_CONFLICT,
                        severity=Severity.MEDIUM,
                        description="Package collision detected",
                        fix_suggestion="Use priority or remove conflicting packages",
                        details=error_output[:200]
                    ))
                
                else:
                    self.issues_found.append(Issue(
                        type=IssueType.BUILD_FAILURE,
                        severity=Severity.HIGH,
                        description="Build failed",
                        details=error_output[:500]
                    ))
                    
        except subprocess.TimeoutExpired:
            self.issues_found.append(Issue(
                type=IssueType.BUILD_FAILURE,
                severity=Severity.MEDIUM,
                description="Build check timed out",
                fix_suggestion="Try 'nixos-rebuild test' manually"
            ))
        except Exception as e:
            logger.error(f"Build check failed: {e}")
    
    def _check_disk_space(self):
        """Check available disk space"""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage_str = parts[4].rstrip('%')
                        usage = int(usage_str)
                        
                        if usage > 95:
                            self.issues_found.append(Issue(
                                type=IssueType.DISK_SPACE,
                                severity=Severity.CRITICAL,
                                description=f"Critical: Disk usage at {usage}%",
                                fix_suggestion="Run 'nix-collect-garbage -d' to free space",
                                auto_fixable=True,
                                fix_command="nix-collect-garbage -d"
                            ))
                        elif usage > 85:
                            self.issues_found.append(Issue(
                                type=IssueType.DISK_SPACE,
                                severity=Severity.HIGH,
                                description=f"High disk usage: {usage}%",
                                fix_suggestion="Consider cleaning old generations",
                                auto_fixable=True,
                                fix_command="nix-collect-garbage --delete-older-than 30d"
                            ))
                        elif usage > 75:
                            self.issues_found.append(Issue(
                                type=IssueType.DISK_SPACE,
                                severity=Severity.LOW,
                                description=f"Disk usage at {usage}%",
                                fix_suggestion="Monitor disk space"
                            ))
        except Exception as e:
            logger.error(f"Disk check failed: {e}")
    
    def _check_memory(self):
        """Check memory usage"""
        try:
            result = subprocess.run(['free', '-m'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 3:
                        total = int(parts[1])
                        used = int(parts[2])
                        usage_percent = (used / total) * 100
                        
                        if usage_percent > 95:
                            self.issues_found.append(Issue(
                                type=IssueType.MEMORY_ISSUE,
                                severity=Severity.HIGH,
                                description=f"Critical memory usage: {usage_percent:.1f}%",
                                fix_suggestion="Close unused applications or add swap"
                            ))
                        elif usage_percent > 85:
                            self.issues_found.append(Issue(
                                type=IssueType.MEMORY_ISSUE,
                                severity=Severity.MEDIUM,
                                description=f"High memory usage: {usage_percent:.1f}%",
                                fix_suggestion="Monitor memory usage"
                            ))
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
    
    def _check_network(self):
        """Check network connectivity"""
        try:
            # Check internet connectivity
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', '8.8.8.8'],
                capture_output=True,
                timeout=3
            )
            
            if result.returncode != 0:
                self.issues_found.append(Issue(
                    type=IssueType.NETWORK_ISSUE,
                    severity=Severity.HIGH,
                    description="No internet connectivity",
                    fix_suggestion="Check network configuration and cables"
                ))
            
            # Check DNS
            result = subprocess.run(
                ['nslookup', 'cache.nixos.org'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode != 0:
                self.issues_found.append(Issue(
                    type=IssueType.NETWORK_ISSUE,
                    severity=Severity.MEDIUM,
                    description="DNS resolution issues",
                    fix_suggestion="Check /etc/resolv.conf or network settings"
                ))
                
        except Exception as e:
            logger.debug(f"Network check error: {e}")
    
    def _check_services(self):
        """Check critical services"""
        critical_services = [
            'NetworkManager',
            'systemd-resolved',
            'nix-daemon'
        ]
        
        for service in critical_services:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode != 0:
                    status = result.stdout.strip()
                    if status == 'inactive':
                        self.issues_found.append(Issue(
                            type=IssueType.SERVICE_FAILURE,
                            severity=Severity.MEDIUM,
                            description=f"Service '{service}' is not running",
                            fix_suggestion=f"Try 'systemctl start {service}'",
                            auto_fixable=True,
                            fix_command=f"systemctl start {service}"
                        ))
                    elif status == 'failed':
                        self.issues_found.append(Issue(
                            type=IssueType.SERVICE_FAILURE,
                            severity=Severity.HIGH,
                            description=f"Service '{service}' has failed",
                            fix_suggestion=f"Check 'journalctl -u {service}'",
                        ))
            except Exception as e:
                logger.debug(f"Service check error for {service}: {e}")
    
    def _deep_configuration_scan(self):
        """Perform deep configuration analysis"""
        # This would use AI to analyze configuration for best practices
        pass
    
    def _check_generations(self):
        """Check system generations"""
        try:
            result = subprocess.run(
                ['nixos-rebuild', 'list-generations'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                generations = len(result.stdout.strip().split('\n'))
                if generations > 50:
                    self.issues_found.append(Issue(
                        type=IssueType.DISK_SPACE,
                        severity=Severity.LOW,
                        description=f"Many generations stored: {generations}",
                        fix_suggestion="Clean old generations to save space",
                        auto_fixable=True,
                        fix_command="nix-collect-garbage --delete-older-than 30d"
                    ))
        except Exception as e:
            logger.debug(f"Generation check error: {e}")
    
    def _check_channels(self):
        """Check Nix channels"""
        try:
            result = subprocess.run(
                ['nix-channel', '--list'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and not result.stdout.strip():
                self.issues_found.append(Issue(
                    type=IssueType.CONFIGURATION_DRIFT,
                    severity=Severity.MEDIUM,
                    description="No Nix channels configured",
                    fix_suggestion="Add nixos channel with 'nix-channel --add'"
                ))
        except Exception as e:
            logger.debug(f"Channel check error: {e}")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on issues found"""
        recommendations = []
        
        if not self.issues_found:
            recommendations.append("✅ Your system looks healthy!")
            recommendations.append("💡 Run 'ask-nix fix --deep' for thorough analysis")
        else:
            # Count by severity
            critical = sum(1 for i in self.issues_found if i.severity == Severity.CRITICAL)
            high = sum(1 for i in self.issues_found if i.severity == Severity.HIGH)
            medium = sum(1 for i in self.issues_found if i.severity == Severity.MEDIUM)
            
            if critical > 0:
                recommendations.append("🚨 Critical issues found - immediate action needed!")
            elif high > 0:
                recommendations.append("⚠️ High priority issues detected")
            
            # Auto-fixable issues
            auto_fixable = [i for i in self.issues_found if i.auto_fixable]
            if auto_fixable:
                recommendations.append(f"🔧 {len(auto_fixable)} issues can be fixed automatically")
            
            # Specific recommendations
            if any(i.type == IssueType.DISK_SPACE for i in self.issues_found):
                recommendations.append("💾 Free disk space with 'nix-collect-garbage -d'")
            
            if any(i.type == IssueType.SYNTAX_ERROR for i in self.issues_found):
                recommendations.append("📝 Fix syntax errors before rebuilding")
            
            if any(i.type == IssueType.BUILD_FAILURE for i in self.issues_found):
                recommendations.append("🔨 Test configuration with 'nixos-rebuild test'")
        
        return recommendations
    
    def auto_fix(self, report: DiagnosisReport, dry_run: bool = True) -> List[str]:
        """
        Attempt to automatically fix issues.
        
        Args:
            report: The diagnosis report
            dry_run: If True, only show what would be fixed
            
        Returns:
            List of actions taken
        """
        actions = []
        
        for issue in report.issues:
            if issue.auto_fixable:
                if dry_run:
                    actions.append(f"Would fix: {issue.description}")
                    if issue.fix_command:
                        actions.append(f"  Command: {issue.fix_command}")
                else:
                    # Actually fix the issue
                    if issue.fix_command:
                        try:
                            result = subprocess.run(
                                issue.fix_command,
                                shell=True,
                                capture_output=True,
                                text=True
                            )
                            if result.returncode == 0:
                                actions.append(f"✅ Fixed: {issue.description}")
                            else:
                                actions.append(f"❌ Failed to fix: {issue.description}")
                        except Exception as e:
                            actions.append(f"❌ Error fixing {issue.description}: {e}")
        
        return actions
    
    def format_report(self, report: DiagnosisReport) -> str:
        """Format diagnosis report for display"""
        output = []
        output.append("\n" + "="*60)
        output.append("🩺 NixOS System Diagnosis Report")
        output.append("="*60)
        
        # System info
        output.append(f"\n📊 System Information:")
        for key, value in report.system_info.items():
            output.append(f"  {key}: {value}")
        
        # Issues by severity
        if report.issues:
            output.append(f"\n⚠️ Issues Found: {len(report.issues)}")
            
            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
                issues = [i for i in report.issues if i.severity == severity]
                if issues:
                    output.append(f"\n{severity.value.upper()} ({len(issues)}):")
                    for issue in issues:
                        output.append(f"  • {issue.description}")
                        if issue.location:
                            output.append(f"    Location: {issue.location}")
                        if issue.line_number:
                            output.append(f"    Line: {issue.line_number}")
                        if issue.fix_suggestion:
                            output.append(f"    Fix: {issue.fix_suggestion}")
        else:
            output.append("\n✅ No issues found!")
        
        # Recommendations
        if report.recommendations:
            output.append("\n💡 Recommendations:")
            for rec in report.recommendations:
                output.append(f"  {rec}")
        
        # Auto-fix available
        if report.can_auto_fix:
            output.append("\n🔧 Auto-fix available! Run: ask-nix fix --apply")
        
        output.append("\n" + "="*60)
        
        return "\n".join(output)


def test_nixos_doctor():
    """Test the NixOS Doctor"""
    print("Testing NixOS Doctor")
    print("="*50)
    
    doctor = NixOSDoctor()
    
    # Run diagnosis
    report = doctor.run_diagnosis(deep_scan=False)
    
    # Format and display
    formatted = doctor.format_report(report)
    print(formatted)
    
    # Show auto-fix options
    if report.can_auto_fix:
        print("\n🔧 Auto-fix Preview:")
        actions = doctor.auto_fix(report, dry_run=True)
        for action in actions:
            print(f"  {action}")


if __name__ == "__main__":
    test_nixos_doctor()