#!/usr/bin/env python3
"""
from typing import Tuple, Dict, Optional
NixOS Version Detection and Compatibility Management

This module handles NixOS version detection and provides guidance
for upgrading to 25.11+ for native API support.
"""

import os
import re
import subprocess
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NixOSVersion:
    """Represents a NixOS version"""
    major: int
    minor: int
    patch: Optional[str] = None
    codename: Optional[str] = None
    raw_version: str = ""
    
    def __str__(self):
        version = f"{self.major}.{self.minor}"
        if self.patch:
            version += f".{self.patch}"
        if self.codename:
            version += f" ({self.codename})"
        return version
    
    def supports_native_api(self) -> bool:
        """Check if this version supports native Python API"""
        # 25.11 and later support native API
        if self.major > 25:
            return True
        if self.major == 25 and self.minor >= 11:
            return True
        return False
    
    def __ge__(self, other):
        """Compare versions"""
        if self.major != other.major:
            return self.major > other.major
        return self.minor >= other.minor


class NixOSVersionChecker:
    """Check NixOS version and provide upgrade guidance"""
    
    # Minimum version for native API support
    MIN_VERSION = NixOSVersion(major=25, minor=11, codename="Xantusia")
    
    # Known codenames for versions
    CODENAMES = {
        "24.05": "Uakari",
        "24.11": "Vicuna", 
        "25.05": "Warbler",
        "25.11": "Xantusia",
    }
    
    def __init__(self):
        self._version_cache = None
        self._allow_override = os.environ.get('NIX_HUMANITY_FORCE_NATIVE_API', 'false').lower() == 'true'
        
    def get_current_version(self) -> Optional[NixOSVersion]:
        """Get the current NixOS version"""
        if self._version_cache:
            return self._version_cache
            
        # Try multiple methods to get version
        version = None
        
        # Method 1: Check /etc/os-release
        version = self._get_version_from_os_release()
        
        # Method 2: Check nixos-version command
        if not version:
            version = self._get_version_from_command()
            
        # Method 3: Check system profile
        if not version:
            version = self._get_version_from_system_profile()
            
        self._version_cache = version
        return version
        
    def _get_version_from_os_release(self) -> Optional[NixOSVersion]:
        """Parse version from /etc/os-release"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                
            # Look for VERSION_ID
            version_match = re.search(r'VERSION_ID="?([0-9]+\.[0-9]+(?:\.[0-9]+)?)"?', content)
            if version_match:
                return self._parse_version_string(version_match.group(1))
                
            # Look for VERSION with codename
            version_match = re.search(r'VERSION="?([0-9]+\.[0-9]+(?:\.[0-9]+)?)\s*\(([^)]+)\)"?', content)
            if version_match:
                version = self._parse_version_string(version_match.group(1))
                if version:
                    version.codename = version_match.group(2)
                return version
                
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return None
        
    def _get_version_from_command(self) -> Optional[NixOSVersion]:
        """Get version from nixos-version command"""
        try:
            result = subprocess.run(
                ['nixos-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse output like "24.05.20240501.1234567 (Uakari)"
                output = result.stdout.strip()
                match = re.match(r'([0-9]+\.[0-9]+)(?:\.[0-9]+)?(?:\.[a-f0-9]+)?\s*(?:\(([^)]+)\))?', output)
                if match:
                    version = self._parse_version_string(match.group(1))
                    if version and match.group(2):
                        version.codename = match.group(2)
                    return version
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return None
        
    def _get_version_from_system_profile(self) -> Optional[NixOSVersion]:
        """Try to determine version from system profile"""
        try:
            system_link = Path('/run/current-system')
            if system_link.exists():
                # Check for nixos-version file in the system
                version_file = system_link / 'nixos-version'
                if version_file.exists():
                    version_str = version_file.read_text().strip()
                    return self._parse_version_string(version_str)
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return None
        
    def _parse_version_string(self, version_str: str) -> Optional[NixOSVersion]:
        """Parse a version string like 24.05 or 25.11.1"""
        try:
            parts = version_str.split('.')
            if len(parts) >= 2:
                major = int(parts[0])
                minor = int(parts[1])
                patch = parts[2] if len(parts) > 2 else None
                
                # Look up codename
                codename = self.CODENAMES.get(f"{major}.{minor:02d}")
                
                return NixOSVersion(
                    major=major,
                    minor=minor,
                    patch=patch,
                    codename=codename,
                    raw_version=version_str
                )
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return None
        
    def check_compatibility(self) -> Dict[str, Any]:
        """Check if current system is compatible with native API"""
        current_version = self.get_current_version()
        
        if not current_version:
            return {
                'compatible': False,
                'current_version': None,
                'required_version': str(self.MIN_VERSION),
                'can_override': self._allow_override,
                'reason': 'Unable to detect NixOS version',
                'upgrade_instructions': self._get_upgrade_instructions(None)
            }
            
        is_compatible = current_version.supports_native_api()
        
        return {
            'compatible': is_compatible,
            'current_version': str(current_version),
            'required_version': str(self.MIN_VERSION),
            'can_override': self._allow_override,
            'reason': 'Version supports native API' if is_compatible else f'NixOS {current_version} does not support native Python API',
            'upgrade_instructions': None if is_compatible else self._get_upgrade_instructions(current_version)
        }
        
    def _get_upgrade_instructions(self, current_version: Optional[NixOSVersion]) -> Dict[str, Any]:
        """Get upgrade instructions for the current version"""
        instructions = {
            'summary': f'Upgrade to NixOS {self.MIN_VERSION} or later for native Python API support',
            'benefits': [
                '10x-1500x performance improvement',
                'Real-time progress tracking',
                'No subprocess timeouts',
                'Better error handling',
                'Direct Python exceptions'
            ],
            'steps': []
        }
        
        if current_version and current_version.major == 24:
            # Upgrading from 24.x
            instructions['steps'] = [
                "1. Update your channel:",
                "   sudo nix-channel --add https://nixos.org/channels/nixos-25.11 nixos",
                "   sudo nix-channel --update",
                "",
                "2. Update your configuration.nix:",
                "   - Review release notes for breaking changes",
                "   - Update any deprecated options",
                "",
                "3. Rebuild your system:",
                "   sudo nixos-rebuild switch --upgrade",
                "",
                "4. Reboot if kernel was updated:",
                "   sudo reboot"
            ]
        else:
            # Generic upgrade instructions
            instructions['steps'] = [
                "1. Check current channels:",
                "   sudo nix-channel --list",
                "",
                "2. Add NixOS 25.11 channel:",
                "   sudo nix-channel --add https://nixos.org/channels/nixos-25.11 nixos",
                "   sudo nix-channel --update",
                "",
                "3. Update configuration and rebuild:",
                "   sudo nixos-rebuild switch --upgrade"
            ]
            
        instructions['override'] = {
            'description': 'To use native API anyway (at your own risk):',
            'command': 'export NIX_HUMANITY_FORCE_NATIVE_API=true',
            'warning': 'Some features may not work correctly on older versions'
        }
        
        return instructions
        
    def print_compatibility_report(self):
        """Print a user-friendly compatibility report"""
        compat = self.check_compatibility()
        
        print("\n🔍 NixOS Version Compatibility Check")
        print("=" * 50)
        
        if compat['current_version']:
            print(f"Current Version: {compat['current_version']}")
        else:
            print("Current Version: Unable to detect")
            
        print(f"Required Version: {compat['required_version']}")
        print(f"Native API Compatible: {'✅ Yes' if compat['compatible'] else '❌ No'}")
        
        if not compat['compatible']:
            print(f"\nReason: {compat['reason']}")
            
            if compat['upgrade_instructions']:
                print("\n📚 Upgrade Instructions:")
                print("-" * 50)
                
                instructions = compat['upgrade_instructions']
                print(f"\n{instructions['summary']}\n")
                
                print("Benefits of upgrading:")
                for benefit in instructions['benefits']:
                    print(f"  • {benefit}")
                    
                print("\nUpgrade steps:")
                for step in instructions['steps']:
                    print(step)
                    
                if compat['can_override']:
                    print("\n⚠️  Override Detected:")
                    print("Native API will be attempted despite version mismatch.")
                else:
                    override = instructions['override']
                    print(f"\n💡 {override['description']}")
                    print(f"   {override['command']}")
                    print(f"   ⚠️  {override['warning']}")
                    
        print("\n" + "=" * 50)
        

# Convenience function for quick checks
def check_nixos_version() -> Tuple[bool, Optional[str]]:
    """
    Quick check if NixOS version supports native API
    Returns: (is_compatible, version_string)
    """
    checker = NixOSVersionChecker()
    compat = checker.check_compatibility()
    return compat['compatible'], compat['current_version']


if __name__ == "__main__":
    # Run compatibility check when executed directly
    checker = NixOSVersionChecker()
    checker.print_compatibility_report()