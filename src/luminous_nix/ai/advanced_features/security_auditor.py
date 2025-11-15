#!/usr/bin/env python3
"""
Security Auditor - Comprehensive vulnerability scanning and CVE analysis
Identifies security issues and provides actionable remediation steps
"""

import logging
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Import core infrastructure
try:
    from .core.state_analyzer import get_state_analyzer
except ImportError:
    import sys

    sys.path.append("..")
    from core.state_analyzer import get_state_analyzer

logger = logging.getLogger(__name__)


class Severity(Enum):
    """CVE severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class CVEInfo:
    """CVE vulnerability information"""

    cve_id: str
    package: str
    version: str
    severity: Severity
    description: str
    fixed_version: Optional[str] = None
    exploitable: bool = False
    patch_available: bool = False
    workaround: Optional[str] = None


@dataclass
class SecurityAuditResult:
    """Complete security audit result"""

    scan_date: datetime
    total_packages_scanned: int
    vulnerabilities_found: list[CVEInfo]
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

    # Security configuration issues
    firewall_enabled: bool
    auto_updates_enabled: bool
    secure_boot: bool
    encrypted_root: bool

    # Recommendations
    immediate_actions: list[str]
    recommended_patches: list[str]
    configuration_fixes: list[str]

    # Overall score
    security_score: float  # 0-100
    risk_level: str  # "critical", "high", "medium", "low", "secure"


class SecurityAuditor:
    """
    Intelligent security auditing using HRM reasoning
    Scans system for vulnerabilities and provides remediation
    """

    def __init__(self):
        self.analyzer = get_state_analyzer()

        # CVE database (in production, would fetch from NVD or nixpkgs)
        self.cve_database = self._load_cve_database()

        # Known vulnerable packages patterns
        self.vulnerable_patterns = {
            "openssl": {
                "3.0.0": ["CVE-2022-3602", "CVE-2022-3786"],  # Critical buffer overflow
                "1.1.1": ["CVE-2021-3711", "CVE-2021-3712"],  # High severity
            },
            "log4j": {
                "2.14.1": ["CVE-2021-44228"],  # Log4Shell - Critical
                "2.15.0": ["CVE-2021-45046"],  # Incomplete fix
            },
            "sudo": {
                "1.8.31": ["CVE-2021-3156"],  # Baron Samedit - Critical
            },
            "polkit": {
                "0.105": ["CVE-2021-4034"],  # PwnKit - Critical
            },
            "glibc": {
                "2.33": ["CVE-2021-33574"],  # Use-after-free
            },
        }

        # Security configuration checks
        self.security_checks = {
            "firewall": self._check_firewall,
            "updates": self._check_auto_updates,
            "secure_boot": self._check_secure_boot,
            "encryption": self._check_disk_encryption,
            "ssh": self._check_ssh_security,
            "services": self._check_exposed_services,
            "kernel": self._check_kernel_hardening,
            "passwords": self._check_password_policy,
        }

    def audit_system(self, deep_scan: bool = False) -> SecurityAuditResult:
        """
        Perform comprehensive security audit

        Args:
            deep_scan: If True, perform thorough scan (slower)

        Returns:
            Complete security audit result
        """
        try:
            # Get system state
            state = self.analyzer.get_system_state()

            # Scan for vulnerabilities
            vulnerabilities = self._scan_for_vulnerabilities(
                state.installed_packages, deep_scan
            )

            # Count by severity
            severity_counts = self._count_severities(vulnerabilities)

            # Check security configurations
            config_results = self._check_security_configurations()

            # Generate recommendations
            immediate_actions = self._generate_immediate_actions(
                vulnerabilities, config_results
            )
            patches = self._generate_patch_recommendations(vulnerabilities)
            config_fixes = self._generate_configuration_fixes(config_results)

            # Calculate security score
            score, risk_level = self._calculate_security_score(
                vulnerabilities, config_results
            )

            return SecurityAuditResult(
                scan_date=datetime.now(),
                total_packages_scanned=len(state.installed_packages),
                vulnerabilities_found=vulnerabilities[:50],  # Limit for display
                critical_count=severity_counts["critical"],
                high_count=severity_counts["high"],
                medium_count=severity_counts["medium"],
                low_count=severity_counts["low"],
                firewall_enabled=config_results.get("firewall", False),
                auto_updates_enabled=config_results.get("updates", False),
                secure_boot=config_results.get("secure_boot", False),
                encrypted_root=config_results.get("encryption", False),
                immediate_actions=immediate_actions[:10],
                recommended_patches=patches[:20],
                configuration_fixes=config_fixes[:10],
                security_score=score,
                risk_level=risk_level,
            )

        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            return self._create_fallback_audit()

    def check_package_security(self, package_name: str) -> list[CVEInfo]:
        """
        Check security of a specific package

        Args:
            package_name: Name of package to check

        Returns:
            List of vulnerabilities for that package
        """
        vulnerabilities = []

        try:
            # Get package version
            version = self._get_package_version(package_name)
            if not version:
                return []

            # Check against known vulnerabilities
            if package_name in self.vulnerable_patterns:
                for vuln_version, cves in self.vulnerable_patterns[
                    package_name
                ].items():
                    if self._version_vulnerable(version, vuln_version):
                        for cve_id in cves:
                            vulnerabilities.append(
                                self._create_cve_info(cve_id, package_name, version)
                            )

            # Check CVE database
            db_vulns = self._check_cve_database(package_name, version)
            vulnerabilities.extend(db_vulns)

        except Exception as e:
            logger.error(f"Failed to check package {package_name}: {e}")

        return vulnerabilities

    def suggest_hardening(self) -> dict[str, Any]:
        """
        Suggest system hardening configurations

        Returns:
            Dictionary with hardening recommendations
        """
        hardening = {
            "kernel": self._suggest_kernel_hardening(),
            "network": self._suggest_network_hardening(),
            "services": self._suggest_service_hardening(),
            "filesystem": self._suggest_filesystem_hardening(),
            "authentication": self._suggest_auth_hardening(),
        }

        # Generate NixOS configuration
        config = self._generate_hardening_config(hardening)

        return {
            "recommendations": hardening,
            "configuration": config,
            "impact": self._assess_hardening_impact(hardening),
            "priority": self._prioritize_hardening(hardening),
        }

    def track_security_updates(self) -> list[dict]:
        """
        Track available security updates

        Returns:
            List of available security updates
        """
        updates = []

        try:
            # Check nixpkgs for security updates
            # In production, would query nixpkgs or channels
            vulnerable_packages = self._get_vulnerable_packages()

            for pkg in vulnerable_packages:
                update_info = self._check_for_update(pkg)
                if update_info:
                    updates.append(update_info)

        except Exception as e:
            logger.error(f"Failed to track security updates: {e}")

        return updates

    def _scan_for_vulnerabilities(
        self, packages: list[str], deep: bool
    ) -> list[CVEInfo]:
        """Scan packages for known vulnerabilities"""
        vulnerabilities = []

        for package in packages:
            # Extract package name and version
            name, version = self._parse_package_string(package)
            if not name:
                continue

            # Check for vulnerabilities
            pkg_vulns = self.check_package_security(name)
            vulnerabilities.extend(pkg_vulns)

            # Deep scan checks dependencies too
            if deep and pkg_vulns:
                dep_vulns = self._check_dependency_vulnerabilities(name)
                vulnerabilities.extend(dep_vulns)

        # Remove duplicates
        seen = set()
        unique_vulns = []
        for vuln in vulnerabilities:
            if vuln.cve_id not in seen:
                seen.add(vuln.cve_id)
                unique_vulns.append(vuln)

        # Sort by severity
        return sorted(
            unique_vulns, key=lambda v: self._severity_weight(v.severity), reverse=True
        )

    def _check_security_configurations(self) -> dict[str, bool]:
        """Check various security configurations"""
        results = {}

        for check_name, check_func in self.security_checks.items():
            try:
                results[check_name] = check_func()
            except Exception as e:
                logger.error(f"Security check {check_name} failed: {e}")
                results[check_name] = False

        return results

    def _check_firewall(self) -> bool:
        """Check if firewall is enabled"""
        try:
            output = self._run_command("sudo iptables -L -n")
            return output and "ACCEPT" not in output.split("\n")[0]
        except:
            return False

    def _check_auto_updates(self) -> bool:
        """Check if automatic updates are enabled"""
        try:
            # Check for auto-upgrade service
            output = self._run_command("systemctl is-enabled nixos-auto-upgrade")
            return output and "enabled" in output.lower()
        except:
            return False

    def _check_secure_boot(self) -> bool:
        """Check if secure boot is enabled"""
        try:
            output = self._run_command("bootctl status")
            return output and "Secure Boot: enabled" in output
        except:
            return False

    def _check_disk_encryption(self) -> bool:
        """Check if root filesystem is encrypted"""
        try:
            output = self._run_command("lsblk -o NAME,FSTYPE,MOUNTPOINT,ENCRYPTED")
            # Look for encrypted root
            for line in output.split("\n"):
                if "/" in line and line.endswith("1"):
                    return True
        except:
            pass
        return False

    def _check_ssh_security(self) -> bool:
        """Check SSH security settings"""
        try:
            # Check for key-only auth and no root login
            config_path = Path("/etc/ssh/sshd_config")
            if config_path.exists():
                config = config_path.read_text()
                return (
                    "PasswordAuthentication no" in config
                    and "PermitRootLogin no" in config
                )
        except:
            pass
        return False

    def _check_exposed_services(self) -> bool:
        """Check for unnecessarily exposed services"""
        try:
            output = self._run_command("ss -tlpn")
            if output:
                # Check for services on 0.0.0.0 (all interfaces)
                exposed = []
                for line in output.split("\n"):
                    if "0.0.0.0:" in line or ":::" in line:
                        exposed.append(line)
                # Fewer exposed services is better
                return len(exposed) < 5
        except:
            pass
        return False

    def _check_kernel_hardening(self) -> bool:
        """Check kernel hardening parameters"""
        try:
            # Check key sysctl parameters
            checks = [
                "sysctl kernel.kptr_restrict",
                "sysctl kernel.dmesg_restrict",
                "sysctl kernel.yama.ptrace_scope",
            ]

            hardened = 0
            for check in checks:
                output = self._run_command(check)
                if output and "= 1" in output or "= 2" in output:
                    hardened += 1

            return hardened >= 2
        except:
            return False

    def _check_password_policy(self) -> bool:
        """Check password policy strength"""
        try:
            # Check PAM configuration
            pam_path = Path("/etc/pam.d/system-auth")
            if pam_path.exists():
                config = pam_path.read_text()
                return "pam_pwquality" in config or "pam_cracklib" in config
        except:
            pass
        return False

    def _generate_immediate_actions(
        self, vulns: list[CVEInfo], config: dict
    ) -> list[str]:
        """Generate immediate action items"""
        actions = []

        # Critical vulnerabilities first
        critical_vulns = [v for v in vulns if v.severity == Severity.CRITICAL]
        if critical_vulns:
            for vuln in critical_vulns[:3]:
                actions.append(f"CRITICAL: Patch {vuln.package} (CVE: {vuln.cve_id})")

        # Configuration issues
        if not config.get("firewall"):
            actions.append("Enable firewall: networking.firewall.enable = true")

        if not config.get("updates"):
            actions.append("Enable auto-updates: system.autoUpgrade.enable = true")

        if not config.get("ssh") and config.get("ssh_installed"):
            actions.append(
                "Harden SSH: services.openssh.passwordAuthentication = false"
            )

        return actions

    def _generate_patch_recommendations(self, vulns: list[CVEInfo]) -> list[str]:
        """Generate patch recommendations"""
        patches = []

        for vuln in vulns:
            if vuln.patch_available and vuln.fixed_version:
                patches.append(f"Update {vuln.package} to {vuln.fixed_version}")
            elif vuln.workaround:
                patches.append(f"{vuln.package}: {vuln.workaround}")

        return patches

    def _generate_configuration_fixes(self, config: dict) -> list[str]:
        """Generate configuration fixes"""
        fixes = []

        if not config.get("firewall"):
            fixes.append("networking.firewall.enable = true;")

        if not config.get("updates"):
            fixes.append("system.autoUpgrade.enable = true;")
            fixes.append("system.autoUpgrade.allowReboot = false;")

        if not config.get("kernel"):
            fixes.append('boot.kernel.sysctl."kernel.kptr_restrict" = 2;')
            fixes.append('boot.kernel.sysctl."kernel.yama.ptrace_scope" = 1;')

        return fixes

    def _calculate_security_score(
        self, vulns: list[CVEInfo], config: dict
    ) -> tuple[float, str]:
        """Calculate overall security score and risk level"""
        score = 100.0

        # Deduct for vulnerabilities
        for vuln in vulns:
            weight = self._severity_weight(vuln.severity)
            score -= weight * 2

        # Deduct for configuration issues
        for check, passed in config.items():
            if not passed:
                score -= 5

        # Ensure score stays in range
        score = max(0, min(100, score))

        # Determine risk level
        if score >= 90:
            risk_level = "secure"
        elif score >= 75:
            risk_level = "low"
        elif score >= 50:
            risk_level = "medium"
        elif score >= 25:
            risk_level = "high"
        else:
            risk_level = "critical"

        return score, risk_level

    def _severity_weight(self, severity: Severity) -> float:
        """Get numeric weight for severity"""
        weights = {
            Severity.CRITICAL: 10.0,
            Severity.HIGH: 5.0,
            Severity.MEDIUM: 2.0,
            Severity.LOW: 0.5,
            Severity.NONE: 0.0,
        }
        return weights.get(severity, 0.0)

    def _count_severities(self, vulns: list[CVEInfo]) -> dict[str, int]:
        """Count vulnerabilities by severity"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for vuln in vulns:
            if vuln.severity == Severity.CRITICAL:
                counts["critical"] += 1
            elif vuln.severity == Severity.HIGH:
                counts["high"] += 1
            elif vuln.severity == Severity.MEDIUM:
                counts["medium"] += 1
            elif vuln.severity == Severity.LOW:
                counts["low"] += 1

        return counts

    def _parse_package_string(
        self, package: str
    ) -> tuple[Optional[str], Optional[str]]:
        """Parse package string into name and version"""
        # Handle various formats: name-version, name, etc.
        match = re.match(r"^([a-zA-Z0-9_-]+)(?:-(\d+[\.\d]+))?", package)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def _get_package_version(self, package_name: str) -> Optional[str]:
        """Get version of installed package"""
        try:
            output = self._run_command(f"nix-env -qa {package_name}")
            if output:
                # Extract version from output
                match = re.search(r"(\d+[\.\d]+)", output)
                if match:
                    return match.group(1)
        except:
            pass
        return None

    def _version_vulnerable(self, installed: str, vulnerable: str) -> bool:
        """Check if installed version is vulnerable"""
        try:
            # Simple version comparison (in production, use proper version comparison)
            return installed.startswith(vulnerable)
        except:
            return False

    def _create_cve_info(self, cve_id: str, package: str, version: str) -> CVEInfo:
        """Create CVE info object"""
        # Get CVE details from database or use defaults
        severity = self._get_cve_severity(cve_id)
        description = self._get_cve_description(cve_id)

        return CVEInfo(
            cve_id=cve_id,
            package=package,
            version=version,
            severity=severity,
            description=description,
            fixed_version=self._get_fixed_version(package, cve_id),
            exploitable=self._is_exploitable(cve_id),
            patch_available=self._has_patch(package, cve_id),
            workaround=self._get_workaround(cve_id),
        )

    def _get_cve_severity(self, cve_id: str) -> Severity:
        """Get severity for CVE"""
        # Known critical CVEs
        critical_cves = ["CVE-2021-44228", "CVE-2021-3156", "CVE-2021-4034"]
        if cve_id in critical_cves:
            return Severity.CRITICAL

        # Default based on year (newer = potentially more severe)
        year = int(cve_id.split("-")[1])
        if year >= 2023:
            return Severity.HIGH
        elif year >= 2021:
            return Severity.MEDIUM
        else:
            return Severity.LOW

    def _get_cve_description(self, cve_id: str) -> str:
        """Get description for CVE"""
        descriptions = {
            "CVE-2021-44228": "Log4Shell - Remote code execution in Log4j",
            "CVE-2021-3156": "Baron Samedit - Sudo heap-based buffer overflow",
            "CVE-2021-4034": "PwnKit - Local privilege escalation in polkit",
            "CVE-2022-3602": "OpenSSL buffer overflow vulnerability",
        }
        return descriptions.get(cve_id, "Security vulnerability detected")

    def _load_cve_database(self) -> dict:
        """Load CVE database (mock for demo)"""
        # In production, would load from NVD or nixpkgs
        return {}

    def _check_cve_database(self, package: str, version: str) -> list[CVEInfo]:
        """Check CVE database for package"""
        # In production, would query real database
        return []

    def _check_dependency_vulnerabilities(self, package: str) -> list[CVEInfo]:
        """Check vulnerabilities in dependencies"""
        # Would trace dependency tree
        return []

    def _get_vulnerable_packages(self) -> list[str]:
        """Get list of vulnerable packages"""
        vulnerable = []
        state = self.analyzer.get_system_state()

        for package in state.installed_packages[:20]:  # Limit for performance
            vulns = self.check_package_security(package)
            if vulns:
                vulnerable.append(package)

        return vulnerable

    def _check_for_update(self, package: str) -> Optional[dict]:
        """Check if update is available for package"""
        # In production, would check nixpkgs
        return None

    def _suggest_kernel_hardening(self) -> list[str]:
        """Suggest kernel hardening options"""
        return [
            'boot.kernel.sysctl."kernel.kptr_restrict" = 2;',
            'boot.kernel.sysctl."kernel.dmesg_restrict" = 1;',
            'boot.kernel.sysctl."kernel.yama.ptrace_scope" = 2;',
            'boot.kernel.sysctl."kernel.unprivileged_bpf_disabled" = 1;',
        ]

    def _suggest_network_hardening(self) -> list[str]:
        """Suggest network hardening options"""
        return [
            "networking.firewall.enable = true;",
            "networking.firewall.allowPing = false;",
            "networking.firewall.logRefusedConnections = true;",
            'networking.firewall.checkReversePath = "strict";',
        ]

    def _suggest_service_hardening(self) -> list[str]:
        """Suggest service hardening options"""
        return [
            "services.openssh.passwordAuthentication = false;",
            'services.openssh.permitRootLogin = "no";',
            "services.fail2ban.enable = true;",
        ]

    def _suggest_filesystem_hardening(self) -> list[str]:
        """Suggest filesystem hardening options"""
        return [
            "boot.tmp.useTmpfs = true;",
            "boot.cleanTmpDir = true;",
            "security.hideProcessInformation = true;",
        ]

    def _suggest_auth_hardening(self) -> list[str]:
        """Suggest authentication hardening options"""
        return [
            "security.pam.enableSudoTouchIdAuth = true;",
            "security.sudo.wheelNeedsPassword = true;",
            'security.pam.loginLimits = [{ domain = "*"; type = "-"; item = "maxlogins"; value = "3"; }];',
        ]

    def _generate_hardening_config(self, hardening: dict) -> str:
        """Generate complete hardening configuration"""
        config_lines = ["{ config, pkgs, ... }:", "{"]

        for category, suggestions in hardening.items():
            config_lines.append(f"  # {category.capitalize()} hardening")
            config_lines.extend([f"  {s}" for s in suggestions])
            config_lines.append("")

        config_lines.append("}")
        return "\n".join(config_lines)

    def _assess_hardening_impact(self, hardening: dict) -> dict[str, str]:
        """Assess impact of hardening recommendations"""
        return {
            "performance": "minimal",
            "usability": "moderate",
            "security": "significant",
            "compatibility": "high",
        }

    def _prioritize_hardening(self, hardening: dict) -> list[str]:
        """Prioritize hardening recommendations"""
        priorities = []

        # Critical first
        if "kernel" in hardening:
            priorities.extend(hardening["kernel"][:2])
        if "network" in hardening:
            priorities.extend(hardening["network"][:2])

        return priorities

    def _get_fixed_version(self, package: str, cve_id: str) -> Optional[str]:
        """Get fixed version for CVE"""
        # In production, would query package database
        return None

    def _is_exploitable(self, cve_id: str) -> bool:
        """Check if CVE is actively exploitable"""
        exploitable_cves = ["CVE-2021-44228", "CVE-2021-3156"]
        return cve_id in exploitable_cves

    def _has_patch(self, package: str, cve_id: str) -> bool:
        """Check if patch is available"""
        # In production, would check nixpkgs
        return False

    def _get_workaround(self, cve_id: str) -> Optional[str]:
        """Get workaround for CVE"""
        workarounds = {
            "CVE-2021-44228": "Set -Dlog4j2.formatMsgNoLookups=true",
        }
        return workarounds.get(cve_id)

    def _run_command(self, command: str) -> Optional[str]:
        """Run shell command and return output"""
        try:
            # Security: Use shlex.split to avoid shell injection
            import shlex

            result = subprocess.run(
                shlex.split(command),
                shell=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def _create_fallback_audit(self) -> SecurityAuditResult:
        """Create fallback audit result when scan fails"""
        return SecurityAuditResult(
            scan_date=datetime.now(),
            total_packages_scanned=0,
            vulnerabilities_found=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=0,
            firewall_enabled=False,
            auto_updates_enabled=False,
            secure_boot=False,
            encrypted_root=False,
            immediate_actions=["Run security audit manually"],
            recommended_patches=[],
            configuration_fixes=[],
            security_score=50.0,
            risk_level="unknown",
        )
