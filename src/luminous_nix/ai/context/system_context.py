"""
System Context Gatherer - Provides AI with complete understanding of the NixOS system
"""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class SystemContext:
    """Complete system context for AI"""
    # Hardware info
    hostname: str
    cpu_info: str
    memory_total: str
    disk_usage: Dict[str, Any]

    # NixOS info
    nixos_version: str
    current_generation: int
    channel_or_flake: str  # "channels" or "flakes"

    # Configuration
    has_configuration_nix: bool
    has_flake_nix: bool
    configuration_path: Optional[Path]

    # Installed packages (sample)
    installed_packages: List[str]

    # Current state
    running_services: List[str]
    failed_services: List[str]

    def to_context_string(self) -> str:
        """Convert to natural language context for AI"""
        context = f"""
System Context:
- Hostname: {self.hostname}
- NixOS: {self.nixos_version}
- Generation: {self.current_generation}
- Using: {self.channel_or_flake}
- Configuration: {'flake.nix' if self.has_flake_nix else 'configuration.nix'}

Hardware:
- CPU: {self.cpu_info}
- RAM: {self.memory_total}
- Disk: {self.disk_usage.get('used', 'Unknown')}/{self.disk_usage.get('total', 'Unknown')} ({self.disk_usage.get('percent', '?')})

Status:
- {len(self.installed_packages)} packages installed (sample)
- {len(self.running_services)} services running
- {len(self.failed_services)} failed services
"""
        if self.failed_services:
            context += f"\n⚠️ Failed services: {', '.join(self.failed_services)}"

        return context


class SystemContextGatherer:
    """Gathers comprehensive system information"""

    def gather(self) -> SystemContext:
        """Gather all system context"""
        return SystemContext(
            hostname=self._get_hostname(),
            cpu_info=self._get_cpu_info(),
            memory_total=self._get_memory(),
            disk_usage=self._get_disk_usage(),
            nixos_version=self._get_nixos_version(),
            current_generation=self._get_current_generation(),
            channel_or_flake=self._detect_config_type(),
            has_configuration_nix=Path("/etc/nixos/configuration.nix").exists(),
            has_flake_nix=Path("/etc/nixos/flake.nix").exists(),
            configuration_path=self._find_config_path(),
            installed_packages=self._get_installed_packages(),
            running_services=self._get_running_services(),
            failed_services=self._get_failed_services()
        )

    def _get_hostname(self) -> str:
        try:
            return subprocess.run(['hostname'], capture_output=True, text=True, timeout=2).stdout.strip()
        except:
            return "Unknown"

    def _get_cpu_info(self) -> str:
        try:
            result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=2)
            for line in result.stdout.split('\n'):
                if 'Model name:' in line:
                    return line.split(':')[1].strip()
        except:
            pass
        return "Unknown"

    def _get_memory(self) -> str:
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=2)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                mem_line = lines[1].split()
                return mem_line[1]  # Total memory
        except:
            pass
        return "Unknown"

    def _get_disk_usage(self) -> Dict[str, Any]:
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=2)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                return {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "percent": parts[4]
                }
        except:
            pass
        return {}

    def _get_nixos_version(self) -> str:
        try:
            result = subprocess.run(['nixos-version'], capture_output=True, text=True, timeout=2)
            return result.stdout.strip()
        except:
            return "Unknown"

    def _get_current_generation(self) -> int:
        try:
            result = subprocess.run(
                ['nix-env', '--list-generations', '-p', '/nix/var/nix/profiles/system'],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                if '(current)' in line:
                    return int(line.split()[0])
        except:
            pass
        return 0

    def _detect_config_type(self) -> str:
        """Detect if system uses flakes or channels"""
        if Path("/etc/nixos/flake.nix").exists():
            return "flakes"
        return "channels"

    def _find_config_path(self) -> Optional[Path]:
        """Find the main configuration file"""
        if Path("/etc/nixos/flake.nix").exists():
            return Path("/etc/nixos/flake.nix")
        if Path("/etc/nixos/configuration.nix").exists():
            return Path("/etc/nixos/configuration.nix")
        return None

    def _get_installed_packages(self) -> List[str]:
        """Get list of installed packages (first 50 for context)"""
        try:
            result = subprocess.run(
                ['nix-env', '-q'],
                capture_output=True, text=True, timeout=5
            )
            packages = [p for p in result.stdout.strip().split('\n') if p]
            return packages[:50]  # Limit for context
        except:
            return []

    def _get_running_services(self) -> List[str]:
        """Get running systemd services"""
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager', '--no-legend'],
                capture_output=True, text=True, timeout=5
            )
            services = []
            for line in result.stdout.split('\n')[:20]:  # First 20 services
                if '.service' in line:
                    service = line.split()[0]
                    services.append(service)
            return services
        except:
            return []

    def _get_failed_services(self) -> List[str]:
        """Get failed systemd services"""
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--state=failed', '--no-pager', '--no-legend'],
                capture_output=True, text=True, timeout=5
            )
            services = []
            for line in result.stdout.split('\n'):
                if '.service' in line:
                    service = line.split()[0]
                    services.append(service)
            return services
        except:
            return []
