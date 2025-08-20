#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List, Optional
Generation Management & System Recovery

This module provides tools for managing NixOS generations,
performing rollbacks, and recovering from system issues.
"""

import os
import re
import subprocess
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class Generation:
    """Represents a NixOS generation"""
    number: int
    date: datetime
    kernel: str
    nixos_version: str
    is_current: bool
    description: str = ""
    packages_added: List[str] = None
    packages_removed: List[str] = None
    config_changes: List[str] = None
    
    def __post_init__(self):
        if self.packages_added is None:
            self.packages_added = []
        if self.packages_removed is None:
            self.packages_removed = []
        if self.config_changes is None:
            self.config_changes = []

@dataclass
class SystemHealth:
    """System health status"""
    disk_usage_percent: float
    memory_usage_percent: float
    failed_services: List[str]
    config_errors: List[str]
    last_successful_boot: Optional[datetime]
    warnings: List[str]
    
    @property
    def is_healthy(self) -> bool:
        return (self.disk_usage_percent < 90 and
                self.memory_usage_percent < 90 and
                len(self.failed_services) == 0 and
                len(self.config_errors) == 0)

class GenerationManager:
    """Manage NixOS generations and system recovery"""
    
    def __init__(self):
        self.system_profile = Path("/nix/var/nix/profiles/system")
        self.current_generation = self._get_current_generation()
        
    def _get_current_generation(self) -> Optional[int]:
        """Get the current generation number"""
        try:
            result = subprocess.run(
                ["readlink", str(self.system_profile)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Extract generation number from path
                match = re.search(r'system-(\d+)-link', result.stdout)
                if match:
                    return int(match.group(1))
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return None
    
    def list_generations(self, limit: Optional[int] = None) -> List[Generation]:
        """List all system generations"""
        generations = []
        
        try:
            # Get generation list
            result = subprocess.run(
                ["sudo", "nix-env", "--list-generations", "--profile", str(self.system_profile)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        gen = self._parse_generation_line(line)
                        if gen:
                            generations.append(gen)
                
                # Sort by generation number (newest first)
                generations.sort(key=lambda g: g.number, reverse=True)
                
                # Apply limit if specified
                if limit:
                    generations = generations[:limit]
        
        except Exception as e:
            print(f"Error listing generations: {e}")
        
        return generations
    
    def _parse_generation_line(self, line: str) -> Optional[Generation]:
        """Parse a generation line from nix-env output"""
        # Format: "  123   2024-01-15 14:30:45   (current)"
        match = re.match(r'\s*(\d+)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*(\(current\))?', line)
        if match:
            number = int(match.group(1))
            date_str = match.group(2)
            is_current = match.group(3) is not None
            
            # Parse date
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            
            # Get additional info for this generation
            gen_info = self._get_generation_info(number)
            
            return Generation(
                number=number,
                date=date,
                kernel=gen_info.get('kernel', 'unknown'),
                nixos_version=gen_info.get('nixos_version', 'unknown'),
                is_current=is_current,
                description=gen_info.get('description', ''),
                packages_added=gen_info.get('packages_added', []),
                packages_removed=gen_info.get('packages_removed', []),
                config_changes=gen_info.get('config_changes', [])
            )
        return None
    
    def _get_generation_info(self, generation: int) -> Dict[str, Any]:
        """Get detailed information about a generation"""
        info = {
            'kernel': 'unknown',
            'nixos_version': 'unknown',
            'description': '',
            'packages_added': [],
            'packages_removed': [],
            'config_changes': []
        }
        
        try:
            # Try to read generation metadata
            gen_path = self.system_profile.parent / f"system-{generation}-link"
            
            # Get kernel version
            kernel_path = gen_path / "kernel"
            if kernel_path.exists():
                kernel_name = kernel_path.name
                info['kernel'] = kernel_name
            
            # Get NixOS version
            version_file = gen_path / "nixos-version"
            if version_file.exists():
                info['nixos_version'] = version_file.read_text().strip()
            
            # Try to get generation description if available
            desc_file = gen_path / "nixos-generation-description"
            if desc_file.exists():
                info['description'] = desc_file.read_text().strip()
        
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        
        return info
    
    def get_generation_diff(self, gen1: int, gen2: int) -> Dict[str, Any]:
        """Get differences between two generations"""
        diff = {
            'packages_added': [],
            'packages_removed': [],
            'config_changes': [],
            'kernel_changed': False,
            'nixos_version_changed': False
        }
        
        try:
            # Use nix-diff if available
            result = subprocess.run(
                ["nix-diff", f"/nix/var/nix/profiles/system-{gen1}-link",
                 f"/nix/var/nix/profiles/system-{gen2}-link"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Parse nix-diff output
                diff = self._parse_nix_diff(result.stdout)
            else:
                # Fallback to basic comparison
                diff = self._basic_generation_diff(gen1, gen2)
        
        except FileNotFoundError:
            # nix-diff not installed, use basic comparison
            diff = self._basic_generation_diff(gen1, gen2)
        
        return diff
    
    def _parse_nix_diff(self, diff_output: str) -> Dict[str, Any]:
        """Parse nix-diff output"""
        diff = {
            'packages_added': [],
            'packages_removed': [],
            'config_changes': [],
            'kernel_changed': False,
            'nixos_version_changed': False
        }
        
        # Simple parsing - can be enhanced
        for line in diff_output.split('\n'):
            if line.startswith('+'):
                if 'kernel' in line:
                    diff['kernel_changed'] = True
                elif any(pkg in line for pkg in ['.drv', '-env']):
                    diff['packages_added'].append(line[1:].strip())
            elif line.startswith('-'):
                if any(pkg in line for pkg in ['.drv', '-env']):
                    diff['packages_removed'].append(line[1:].strip())
        
        return diff
    
    def _basic_generation_diff(self, gen1: int, gen2: int) -> Dict[str, Any]:
        """Basic comparison between generations"""
        info1 = self._get_generation_info(gen1)
        info2 = self._get_generation_info(gen2)
        
        return {
            'packages_added': [],
            'packages_removed': [],
            'config_changes': [],
            'kernel_changed': info1['kernel'] != info2['kernel'],
            'nixos_version_changed': info1['nixos_version'] != info2['nixos_version']
        }
    
    def rollback(self, generation: Optional[int] = None) -> Tuple[bool, str]:
        """Rollback to a specific generation or the previous one"""
        try:
            if generation is None:
                # Rollback to previous
                cmd = ["sudo", "nixos-rebuild", "switch", "--rollback"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, "Successfully rolled back to previous generation"
                else:
                    return False, f"Rollback failed: {result.stderr}"
            else:
                # Switch to specific generation
                cmd = ["sudo", "nix-env", "--switch-generation", str(generation),
                       "--profile", str(self.system_profile)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Activate the generation
                    activate_cmd = ["sudo", f"/nix/var/nix/profiles/system-{generation}-link/bin/switch-to-configuration", "switch"]
                    activate_result = subprocess.run(activate_cmd, capture_output=True, text=True)
                    
                    if activate_result.returncode == 0:
                        return True, f"Successfully switched to generation {generation}"
                    else:
                        return False, f"Switched generation but activation failed: {activate_result.stderr}"
                else:
                    return False, f"Failed to switch generation: {result.stderr}"
        
        except Exception as e:
            return False, f"Rollback error: {str(e)}"
    
    def delete_generations(self, keep_last: int = 5) -> Tuple[bool, str]:
        """Delete old generations, keeping the specified number"""
        try:
            # Get all generations
            generations = self.list_generations()
            
            if len(generations) <= keep_last:
                return True, f"Only {len(generations)} generations exist, nothing to delete"
            
            # Determine which to delete
            to_delete = generations[keep_last:]
            
            # Delete each generation
            deleted = 0
            for gen in to_delete:
                if not gen.is_current:  # Never delete current
                    cmd = ["sudo", "nix-env", "--delete-generations", str(gen.number),
                           "--profile", str(self.system_profile)]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        deleted += 1
            
            return True, f"Deleted {deleted} old generations, kept last {keep_last}"
        
        except Exception as e:
            return False, f"Error deleting generations: {str(e)}"
    
    def check_system_health(self) -> SystemHealth:
        """Check overall system health"""
        health = SystemHealth(
            disk_usage_percent=self._get_disk_usage(),
            memory_usage_percent=self._get_memory_usage(),
            failed_services=self._get_failed_services(),
            config_errors=self._check_config_errors(),
            last_successful_boot=self._get_last_successful_boot(),
            warnings=[]
        )
        
        # Add warnings based on health check
        if health.disk_usage_percent > 80:
            health.warnings.append(f"High disk usage: {health.disk_usage_percent:.1f}%")
        
        if health.memory_usage_percent > 80:
            health.warnings.append(f"High memory usage: {health.memory_usage_percent:.1f}%")
        
        if len(health.failed_services) > 0:
            health.warnings.append(f"{len(health.failed_services)} services are failing")
        
        return health
    
    def _get_disk_usage(self) -> float:
        """Get disk usage percentage for root partition"""
        try:
            result = subprocess.run(["df", "/", "--output=pcent"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Extract percentage from output
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    percent_str = lines[1].strip().rstrip('%')
                    return float(percent_str)
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            result = subprocess.run(["free", "-m"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('Mem:'):
                        parts = line.split()
                        total = float(parts[1])
                        used = float(parts[2])
                        return (used / total) * 100
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return 0.0
    
    def _get_failed_services(self) -> List[str]:
        """Get list of failed systemd services"""
        failed = []
        try:
            result = subprocess.run(
                ["systemctl", "--failed", "--no-pager", "--no-legend"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        # Extract service name from line
                        parts = line.split()
                        if parts:
                            failed.append(parts[0])
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return failed
    
    def _check_config_errors(self) -> List[str]:
        """Check for configuration errors"""
        errors = []
        try:
            # Test build current configuration
            result = subprocess.run(
                ["nixos-rebuild", "build", "--dry-run"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                # Extract error messages
                for line in result.stderr.split('\n'):
                    if 'error:' in line:
                        errors.append(line.strip())
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return errors[:5]  # Limit to 5 errors
    
    def _get_last_successful_boot(self) -> Optional[datetime]:
        """Get timestamp of last successful boot"""
        try:
            result = subprocess.run(
                ["journalctl", "-b", "-0", "-n", "1", "--no-pager"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                # Extract timestamp from first line
                match = re.match(r'(\w{3}\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', result.stdout)
                if match:
                    return datetime.strptime(match.group(1), "%b %Y-%m-%d %H:%M:%S")
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return None
    
    def create_recovery_snapshot(self, description: str) -> Tuple[bool, str]:
        """Create a snapshot of current system state for recovery"""
        try:
            # First, ensure current config builds
            test_result = subprocess.run(
                ["sudo", "nixos-rebuild", "test"],
                capture_output=True,
                text=True
            )
            
            if test_result.returncode != 0:
                return False, "Current configuration has errors, cannot create snapshot"
            
            # Create a descriptive generation
            # Note: This is a simplified version - real implementation would
            # need to properly tag the generation
            desc_file = Path("/tmp/nixos-generation-description")
            desc_file.write_text(f"Recovery snapshot: {description}")
            
            # Rebuild to create new generation
            result = subprocess.run(
                ["sudo", "nixos-rebuild", "boot"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                new_gen = self._get_current_generation()
                return True, f"Created recovery snapshot as generation {new_gen}"
            else:
                return False, f"Failed to create snapshot: {result.stderr}"
        
        except Exception as e:
            return False, f"Error creating snapshot: {str(e)}"
    
    def suggest_recovery_actions(self, health: SystemHealth) -> List[str]:
        """Suggest recovery actions based on system health"""
        suggestions = []
        
        if health.disk_usage_percent > 90:
            suggestions.append("Run 'nix-collect-garbage -d' to free disk space")
            suggestions.append("Delete old generations with 'ask-nix delete old generations'")
        
        if health.failed_services:
            suggestions.append(f"Investigate failed services: {', '.join(health.failed_services[:3])}")
            suggestions.append("Try 'systemctl restart <service>' for each failed service")
        
        if health.config_errors:
            suggestions.append("Fix configuration errors before next rebuild")
            suggestions.append("Consider rolling back to a working generation")
        
        if not health.is_healthy:
            suggestions.append("Create a recovery snapshot before making changes")
            suggestions.append("Review recent changes with 'ask-nix show generation changes'")
        
        return suggestions


# Example usage functions
def list_system_generations(limit: int = 10) -> str:
    """List recent system generations"""
    manager = GenerationManager()
    generations = manager.list_generations(limit)
    
    if not generations:
        return "No generations found"
    
    output = f"System Generations (showing last {limit}):\n\n"
    for gen in generations:
        marker = " [CURRENT]" if gen.is_current else ""
        output += f"Generation {gen.number}{marker}\n"
        output += f"  Date: {gen.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += f"  Kernel: {gen.kernel}\n"
        output += f"  NixOS: {gen.nixos_version}\n"
        if gen.description:
            output += f"  Description: {gen.description}\n"
        output += "\n"
    
    return output

def check_system_recovery_status() -> str:
    """Check system health and suggest recovery actions"""
    manager = GenerationManager()
    health = manager.check_system_health()
    
    output = "System Health Check:\n\n"
    output += f"✓ Disk Usage: {health.disk_usage_percent:.1f}%\n"
    output += f"✓ Memory Usage: {health.memory_usage_percent:.1f}%\n"
    output += f"✓ Failed Services: {len(health.failed_services)}\n"
    output += f"✓ Config Errors: {len(health.config_errors)}\n"
    
    if health.last_successful_boot:
        output += f"✓ Last Boot: {health.last_successful_boot.strftime('%Y-%m-%d %H:%M')}\n"
    
    output += f"\nOverall Status: {'✅ Healthy' if health.is_healthy else '⚠️  Issues Detected'}\n"
    
    if health.warnings:
        output += "\nWarnings:\n"
        for warning in health.warnings:
            output += f"  ⚠️  {warning}\n"
    
    suggestions = manager.suggest_recovery_actions(health)
    if suggestions:
        output += "\nRecommended Actions:\n"
        for i, suggestion in enumerate(suggestions, 1):
            output += f"  {i}. {suggestion}\n"
    
    return output


if __name__ == "__main__":
    # Test the generation manager
    print("🔄 NixOS Generation Manager Test\n")
    
    print(list_system_generations(5))
    print("\n" + "=" * 60 + "\n")
    print(check_system_recovery_status())