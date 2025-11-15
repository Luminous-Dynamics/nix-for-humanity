#!/usr/bin/env python3
"""
NixOS State Analyzer - Core infrastructure for all advanced features
Provides system state reading, generation listing, and configuration access
"""

import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class SystemGeneration:
    """Represents a NixOS system generation"""

    number: int
    date: datetime
    current: bool
    path: str
    kernel: Optional[str] = None
    config_path: Optional[str] = None
    description: Optional[str] = None


@dataclass
class SystemState:
    """Current system state snapshot"""

    current_generation: int
    total_generations: int
    nixos_version: str
    kernel_version: str
    store_size_gb: float
    installed_packages: List[str]
    running_services: List[str]
    disk_usage: Dict[str, float]
    memory_usage: Dict[str, float]
    boot_time_seconds: Optional[float] = None


class NixOSStateAnalyzer:
    """Analyze NixOS system state for all advanced features"""

    def __init__(self):
        self.generations_cache = {}
        self.state_cache = None

    def get_system_state(self, refresh: bool = False) -> SystemState:
        """Get comprehensive system state snapshot"""
        if self.state_cache and not refresh:
            return self.state_cache

        try:
            # Get current generation
            current_gen = self._get_current_generation()

            # Get NixOS version
            nixos_version = self._run_command("nixos-version") or "unknown"

            # Get kernel version
            kernel_version = self._run_command("uname -r") or "unknown"

            # Get store size
            store_size = self._get_store_size()

            # Get installed packages (sample)
            packages = self._get_installed_packages()

            # Get running services
            services = self._get_running_services()

            # Get disk usage
            disk_usage = self._get_disk_usage()

            # Get memory usage
            memory_usage = self._get_memory_usage()

            # Get boot time
            boot_time = self._get_boot_time()

            # Count total generations
            total_gens = len(self.list_generations())

            self.state_cache = SystemState(
                current_generation=current_gen,
                total_generations=total_gens,
                nixos_version=nixos_version,
                kernel_version=kernel_version,
                store_size_gb=store_size,
                installed_packages=packages[:100],  # Limit for performance
                running_services=services,
                disk_usage=disk_usage,
                memory_usage=memory_usage,
                boot_time_seconds=boot_time,
            )

            return self.state_cache

        except Exception as e:
            logger.error(f"Failed to get system state: {e}")
            # Return minimal state
            return SystemState(
                current_generation=0,
                total_generations=0,
                nixos_version="unknown",
                kernel_version="unknown",
                store_size_gb=0.0,
                installed_packages=[],
                running_services=[],
                disk_usage={},
                memory_usage={},
            )

    def list_generations(self, limit: int = 50) -> List[SystemGeneration]:
        """List all system generations"""
        if self.generations_cache:
            return list(self.generations_cache.values())[:limit]

        generations = []

        try:
            # Run nixos-rebuild list-generations
            output = self._run_command("sudo nixos-rebuild list-generations")
            if not output:
                # Fallback: try to list from /nix/var/nix/profiles
                return self._list_generations_fallback()

            current_gen = self._get_current_generation()

            # Parse output
            for line in output.split("\n"):
                if not line.strip():
                    continue

                # Parse generation line format:
                # 420   2024-01-15 10:23:45   (current)
                match = re.match(
                    r"(\d+)\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s*(\(current\))?",
                    line,
                )
                if match:
                    gen_num = int(match.group(1))
                    date_str = f"{match.group(2)} {match.group(3)}"
                    is_current = match.group(4) is not None

                    generation = SystemGeneration(
                        number=gen_num,
                        date=datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S"),
                        current=is_current or gen_num == current_gen,
                        path=f"/nix/var/nix/profiles/system-{gen_num}-link",
                        description=self._get_generation_description(gen_num),
                    )

                    generations.append(generation)
                    self.generations_cache[gen_num] = generation

        except Exception as e:
            logger.error(f"Failed to list generations: {e}")
            return self._list_generations_fallback()

        return generations[:limit]

    def get_generation_diff(self, gen1: int, gen2: int) -> Dict[str, Any]:
        """Get differences between two generations"""
        diff = {
            "packages_added": [],
            "packages_removed": [],
            "packages_updated": [],
            "config_changes": [],
            "kernel_changed": False,
            "services_changed": [],
        }

        try:
            # Get package lists for both generations
            pkgs1 = self._get_generation_packages(gen1)
            pkgs2 = self._get_generation_packages(gen2)

            # Calculate package differences
            pkgs1_set = set(pkgs1.keys())
            pkgs2_set = set(pkgs2.keys())

            diff["packages_added"] = list(pkgs2_set - pkgs1_set)
            diff["packages_removed"] = list(pkgs1_set - pkgs2_set)

            # Check for updates
            for pkg in pkgs1_set & pkgs2_set:
                if pkgs1[pkg] != pkgs2[pkg]:
                    diff["packages_updated"].append(
                        f"{pkg}: {pkgs1[pkg]} → {pkgs2[pkg]}"
                    )

            # Check kernel changes
            kernel1 = self._get_generation_kernel(gen1)
            kernel2 = self._get_generation_kernel(gen2)
            diff["kernel_changed"] = kernel1 != kernel2

        except Exception as e:
            logger.error(f"Failed to diff generations {gen1} and {gen2}: {e}")

        return diff

    def _get_current_generation(self) -> int:
        """Get current system generation number"""
        try:
            output = self._run_command(
                "sudo nix-env --list-generations -p /nix/var/nix/profiles/system | grep current"
            )
            if output:
                match = re.search(r"(\d+)", output)
                if match:
                    return int(match.group(1))
        except:
            pass
        return 0

    def _get_generation_packages(self, generation: int) -> Dict[str, str]:
        """Get packages installed in a specific generation"""
        packages = {}
        gen_path = f"/nix/var/nix/profiles/system-{generation}-link"

        if not Path(gen_path).exists():
            return packages

        try:
            # Get package manifest
            manifest_path = f"{gen_path}/sw/share/nix-support/manifest.nix"
            if Path(manifest_path).exists():
                # Parse manifest (simplified)
                # In production, would use proper Nix evaluation
                pass
        except Exception as e:
            logger.error(f"Failed to get packages for generation {generation}: {e}")

        return packages

    def _get_generation_kernel(self, generation: int) -> Optional[str]:
        """Get kernel version for a generation"""
        gen_path = f"/nix/var/nix/profiles/system-{generation}-link"
        kernel_path = f"{gen_path}/kernel"

        if Path(kernel_path).exists():
            try:
                # Extract kernel version from path
                kernel_link = Path(kernel_path).readlink()
                match = re.search(r"linux-(\d+\.\d+\.\d+)", str(kernel_link))
                if match:
                    return match.group(1)
            except:
                pass

        return None

    def _get_generation_description(self, generation: int) -> Optional[str]:
        """Get description/commit message for a generation"""
        # Would read from generation metadata if available
        return None

    def _get_store_size(self) -> float:
        """Get /nix/store size in GB"""
        try:
            output = self._run_command("du -sb /nix/store")
            if output:
                size_bytes = int(output.split()[0])
                return size_bytes / (1024**3)  # Convert to GB
        except:
            pass
        return 0.0

    def _get_installed_packages(self) -> List[str]:
        """Get list of installed packages"""
        packages = []
        try:
            output = self._run_command("nix-env -qa --installed")
            if output:
                packages = [line.strip() for line in output.split("\n") if line.strip()]
        except:
            pass
        return packages

    def _get_running_services(self) -> List[str]:
        """Get list of running systemd services"""
        services = []
        try:
            output = self._run_command(
                "systemctl list-units --type=service --state=running --no-legend"
            )
            if output:
                for line in output.split("\n"):
                    if line.strip():
                        service_name = line.split()[0]
                        services.append(service_name)
        except:
            pass
        return services

    def _get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage by mountpoint"""
        usage = {}
        try:
            output = self._run_command("df -h")
            if output:
                for line in output.split("\n")[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 6:
                            mountpoint = parts[5]
                            used_pct = parts[4].rstrip("%")
                            try:
                                usage[mountpoint] = float(used_pct)
                            except:
                                pass
        except:
            pass
        return usage

    def _get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics"""
        usage = {}
        try:
            output = self._run_command("free -m")
            if output:
                lines = output.split("\n")
                if len(lines) > 1:
                    mem_line = lines[1].split()
                    if len(mem_line) >= 3:
                        total = float(mem_line[1])
                        used = float(mem_line[2])
                        usage["total_mb"] = total
                        usage["used_mb"] = used
                        usage["percent"] = (used / total * 100) if total > 0 else 0
        except:
            pass
        return usage

    def _get_boot_time(self) -> Optional[float]:
        """Get system boot time in seconds"""
        try:
            output = self._run_command("systemd-analyze")
            if output:
                match = re.search(r"= (\d+\.\d+)s", output)
                if match:
                    return float(match.group(1))
        except:
            pass
        return None

    def _list_generations_fallback(self) -> List[SystemGeneration]:
        """Fallback method to list generations from profile directory"""
        generations = []
        profile_dir = Path("/nix/var/nix/profiles")

        if not profile_dir.exists():
            return generations

        try:
            current_gen = self._get_current_generation()

            for link in profile_dir.glob("system-*-link"):
                match = re.match(r"system-(\d+)-link", link.name)
                if match:
                    gen_num = int(match.group(1))

                    # Get modification time as date
                    stat = link.stat()
                    date = datetime.fromtimestamp(stat.st_mtime)

                    generation = SystemGeneration(
                        number=gen_num,
                        date=date,
                        current=(gen_num == current_gen),
                        path=str(link),
                    )
                    generations.append(generation)

            # Sort by generation number
            generations.sort(key=lambda g: g.number, reverse=True)

        except Exception as e:
            logger.error(f"Fallback generation listing failed: {e}")

        return generations

    def _run_command(self, command: str) -> Optional[str]:
        """Run a shell command and return output"""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None


# Singleton instance
_analyzer = None


def get_state_analyzer() -> NixOSStateAnalyzer:
    """Get or create singleton state analyzer"""
    global _analyzer
    if _analyzer is None:
        _analyzer = NixOSStateAnalyzer()
    return _analyzer
