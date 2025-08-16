"""
Safe NixOS Configuration Modifier
Uses regex and careful parsing to safely modify NixOS configurations
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import difflib


@dataclass
class ConfigSection:
    """Represents a section of the configuration"""
    name: str
    start_line: int
    end_line: int
    content: List[str]
    indent_level: int


class SafeNixConfigModifier:
    """
    Safely modify NixOS configurations without full AST parsing
    
    Features:
    - Detect existing packages and services
    - Add packages without duplicates
    - Add services with proper formatting
    - Create backups before modifications
    - Validate basic syntax
    """
    
    def __init__(self, config_path: str = "/etc/nixos/configuration.nix"):
        self.config_path = Path(config_path)
        self.lines = []
        self.original_content = ""
        self.backup_path = None
        
    def load_config(self) -> bool:
        """Load the configuration file"""
        try:
            if not self.config_path.exists():
                print(f"❌ Configuration not found: {self.config_path}")
                return False
            
            self.original_content = self.config_path.read_text()
            self.lines = self.original_content.splitlines()
            return True
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return False
    
    def load_from_string(self, content: str) -> bool:
        """Load configuration from a string (for testing)"""
        self.original_content = content
        self.lines = content.splitlines()
        return True
    
    def find_system_packages(self) -> List[str]:
        """Find all packages in environment.systemPackages"""
        packages = []
        in_packages = False
        bracket_depth = 0
        
        for line in self.lines:
            # Check if we're entering systemPackages
            if 'environment.systemPackages' in line:
                in_packages = True
                bracket_depth = 0
            
            if in_packages:
                # Track bracket depth
                bracket_depth += line.count('[') - line.count(']')
                
                # Extract package names
                # Look for patterns like: vim, firefox, pkgs.wget
                cleaned = line.strip()
                
                # Remove comments
                if '#' in cleaned:
                    cleaned = cleaned[:cleaned.index('#')]
                
                # Find package names
                if cleaned and not cleaned.startswith('#'):
                    # Handle different package reference styles
                    # Direct: firefox
                    # With pkgs: pkgs.firefox
                    # In list: [ vim git firefox ]
                    
                    # Remove list brackets and 'with pkgs;'
                    cleaned = re.sub(r'with\s+pkgs\s*;', '', cleaned)
                    cleaned = re.sub(r'[\[\]]', '', cleaned)
                    
                    # Split by whitespace and filter
                    tokens = cleaned.split()
                    for token in tokens:
                        # Clean up the token
                        token = token.strip().rstrip(';').rstrip(',')
                        
                        # Remove pkgs. prefix if present
                        if token.startswith('pkgs.'):
                            token = token[5:]
                        
                        # Check if it looks like a package name
                        if token and re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', token):
                            if token not in ['with', 'pkgs', 'in', 'let', 'if', 'then', 'else']:
                                packages.append(token)
                
                # Check if we've exited the packages section
                if bracket_depth == 0 and '];' in line:
                    in_packages = False
        
        return list(set(packages))  # Remove duplicates
    
    def find_services(self) -> Dict[str, Dict[str, Any]]:
        """Find all services and their configurations"""
        services = {}
        
        for line in self.lines:
            # Look for service enable patterns
            # services.serviceName.enable = true/false;
            match = re.search(r'services\.([a-zA-Z0-9_-]+)\.enable\s*=\s*(true|false)', line)
            if match:
                service_name = match.group(1)
                enabled = match.group(2) == 'true'
                
                if service_name not in services:
                    services[service_name] = {}
                services[service_name]['enable'] = enabled
            
            # Look for other service configurations
            # services.serviceName.setting = value;
            match = re.search(r'services\.([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)\s*=\s*(.+);', line)
            if match:
                service_name = match.group(1)
                setting = match.group(2)
                value = match.group(3).strip()
                
                if service_name not in services:
                    services[service_name] = {}
                
                # Parse the value
                if value == 'true':
                    value = True
                elif value == 'false':
                    value = False
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                
                services[service_name][setting] = value
        
        return services
    
    def has_package(self, package_name: str) -> bool:
        """Check if a package is already in the configuration"""
        packages = self.find_system_packages()
        return package_name in packages
    
    def has_service(self, service_name: str) -> bool:
        """Check if a service is already configured"""
        services = self.find_services()
        return service_name in services
    
    def add_package(self, package_name: str, dry_run: bool = True) -> Optional[str]:
        """
        Add a package to environment.systemPackages
        
        Args:
            package_name: Name of the package to add
            dry_run: If True, return modified content without saving
            
        Returns:
            Modified configuration content or None if failed
        """
        # Check if package already exists
        if self.has_package(package_name):
            print(f"✅ Package '{package_name}' already in configuration")
            return self.original_content
        
        modified_lines = self.lines.copy()
        in_packages = False
        package_added = False
        bracket_depth = 0
        
        for i, line in enumerate(modified_lines):
            # Find systemPackages section
            if 'environment.systemPackages' in line:
                in_packages = True
                bracket_depth = 0
            
            if in_packages:
                bracket_depth += line.count('[') - line.count(']')
                
                # Find the closing bracket
                if '];' in line and bracket_depth == 0:
                    # Add package before the closing bracket
                    indent = len(line) - len(line.lstrip())
                    
                    # Determine the indent for package items
                    # Look at previous lines to match formatting
                    item_indent = indent + 2
                    for j in range(max(0, i-5), i):
                        if modified_lines[j].strip() and not modified_lines[j].strip().startswith('#'):
                            prev_indent = len(modified_lines[j]) - len(modified_lines[j].lstrip())
                            if prev_indent > indent:
                                item_indent = prev_indent
                                break
                    
                    # Insert the package
                    modified_lines.insert(i, ' ' * item_indent + package_name)
                    package_added = True
                    in_packages = False
                    break
        
        if not package_added:
            print(f"⚠️  Could not find systemPackages section")
            return None
        
        modified_content = '\n'.join(modified_lines)
        
        if dry_run:
            print(f"✅ Would add package '{package_name}' (dry run)")
            self._show_diff(self.original_content, modified_content)
        else:
            # Create backup and save
            self._create_backup()
            self.config_path.write_text(modified_content)
            print(f"✅ Added package '{package_name}'")
            print(f"   Backup: {self.backup_path}")
        
        return modified_content
    
    def add_service(self, service_name: str, config: Dict[str, Any], dry_run: bool = True) -> Optional[str]:
        """
        Add or configure a service
        
        Args:
            service_name: Name of the service
            config: Service configuration dict
            dry_run: If True, return modified content without saving
            
        Returns:
            Modified configuration content or None if failed
        """
        # Check if service already exists
        if self.has_service(service_name):
            print(f"✅ Service '{service_name}' already configured")
            # Could update existing config here
            return self.original_content
        
        modified_lines = self.lines.copy()
        
        # Find a good place to add the service
        # Look for existing services section or before the final }
        insert_index = -1
        base_indent = 2
        
        # Find existing services to match formatting
        for i, line in enumerate(modified_lines):
            if 'services.' in line and '.enable' in line:
                # Found existing service, insert after services section
                base_indent = len(line) - len(line.lstrip())
                # Find end of services section
                for j in range(i+1, len(modified_lines)):
                    if not modified_lines[j].strip().startswith('services.'):
                        insert_index = j
                        break
                break
        
        # If no services found, add before final closing brace
        if insert_index == -1:
            for i in range(len(modified_lines) - 1, -1, -1):
                if '}' in modified_lines[i]:
                    insert_index = i
                    break
        
        if insert_index == -1:
            print("⚠️  Could not find insertion point for service")
            return None
        
        # Generate service configuration
        service_lines = []
        service_lines.append('')  # Empty line before
        service_lines.append(' ' * base_indent + f'# {service_name} service')
        
        # Handle nested configuration
        def format_value(value, indent_level):
            if isinstance(value, bool):
                return 'true' if value else 'false'
            elif isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, list):
                items = ' '.join(f'"{v}"' if isinstance(v, str) else str(v) for v in value)
                return f'[ {items} ]'
            elif isinstance(value, dict):
                lines = ['{']
                for k, v in value.items():
                    lines.append(' ' * (indent_level + 2) + f'{k} = {format_value(v, indent_level + 2)};')
                lines.append(' ' * indent_level + '}')
                return '\n'.join(lines)
            else:
                return str(value)
        
        # Add main service configuration
        if len(config) == 1 and 'enable' in config:
            # Simple enable line
            service_lines.append(' ' * base_indent + f'services.{service_name}.enable = {format_value(config["enable"], base_indent)};')
        else:
            # Complex configuration
            service_lines.append(' ' * base_indent + f'services.{service_name} = {{')
            for key, value in config.items():
                if isinstance(value, dict):
                    # Nested configuration
                    service_lines.append(' ' * (base_indent + 2) + f'{key} = {{')
                    for k, v in value.items():
                        service_lines.append(' ' * (base_indent + 4) + f'{k} = {format_value(v, base_indent + 4)};')
                    service_lines.append(' ' * (base_indent + 2) + '};')
                else:
                    service_lines.append(' ' * (base_indent + 2) + f'{key} = {format_value(value, base_indent + 2)};')
            service_lines.append(' ' * base_indent + '};')
        
        # Insert the service configuration
        for line in reversed(service_lines):
            modified_lines.insert(insert_index, line)
        
        modified_content = '\n'.join(modified_lines)
        
        if dry_run:
            print(f"✅ Would configure service '{service_name}' (dry run)")
            self._show_diff(self.original_content, modified_content)
        else:
            # Create backup and save
            self._create_backup()
            self.config_path.write_text(modified_content)
            print(f"✅ Configured service '{service_name}'")
            print(f"   Backup: {self.backup_path}")
        
        return modified_content
    
    def validate_syntax(self, content: str) -> Tuple[bool, List[str]]:
        """Basic syntax validation"""
        errors = []
        
        # Check bracket balance
        open_brackets = content.count('{') + content.count('[') + content.count('(')
        close_brackets = content.count('}') + content.count(']') + content.count(')')
        
        if open_brackets != close_brackets:
            errors.append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
        
        # Check for common syntax errors
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            # Check for missing semicolons
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                if '=' in stripped and not stripped.endswith((';', '{', '[')):
                    if i < len(lines) and not lines[i].strip().startswith((')', ']', '}')):
                        errors.append(f"Line {i}: Possible missing semicolon")
        
        return len(errors) == 0, errors
    
    def _create_backup(self) -> Path:
        """Create a backup of the current configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = self.config_path.parent / f"{self.config_path.name}.backup_{timestamp}"
        
        if self.config_path.exists():
            import shutil
            shutil.copy(self.config_path, self.backup_path)
        
        return self.backup_path
    
    def _show_diff(self, original: str, modified: str):
        """Show diff between original and modified"""
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile="configuration.nix",
            tofile="configuration.nix (modified)"
        )
        print("\n📝 Preview of changes:")
        print("-" * 40)
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                print(f"\033[32m{line}\033[0m", end='')
            elif line.startswith('-') and not line.startswith('---'):
                print(f"\033[31m{line}\033[0m", end='')
            else:
                print(line, end='')
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze the configuration"""
        if not self.lines:
            self.load_config()
        
        return {
            "packages": self.find_system_packages(),
            "services": self.find_services(),
            "lines": len(self.lines),
            "has_hardware_config": any("hardware-configuration.nix" in line for line in self.lines),
            "has_bootloader": any("boot.loader" in line for line in self.lines),
            "has_networking": any("networking.hostName" in line for line in self.lines),
            "has_users": any("users.users" in line for line in self.lines),
        }


# Integration with the main system
class NixConfigIntegration:
    """Integration layer for the Nix for Humanity system"""
    
    def __init__(self):
        self.modifier = SafeNixConfigModifier()
    
    def handle_install_request(self, package_name: str, dry_run: bool = True) -> Dict[str, Any]:
        """Handle a package installation request"""
        
        # Load current configuration
        if not self.modifier.load_config():
            return {
                "success": False,
                "error": "Could not load configuration",
                "suggestion": "Check if /etc/nixos/configuration.nix exists"
            }
        
        # Check if package already exists
        if self.modifier.has_package(package_name):
            return {
                "success": True,
                "message": f"Package '{package_name}' is already installed",
                "action": "none"
            }
        
        # Add the package
        result = self.modifier.add_package(package_name, dry_run=dry_run)
        
        if result:
            return {
                "success": True,
                "message": f"{'Would add' if dry_run else 'Added'} package '{package_name}'",
                "action": "modified",
                "next_step": "Run: sudo nixos-rebuild switch" if not dry_run else None
            }
        else:
            return {
                "success": False,
                "error": f"Failed to add package '{package_name}'",
                "suggestion": "Check configuration syntax"
            }
    
    def handle_service_request(self, service_name: str, enable: bool = True, dry_run: bool = True) -> Dict[str, Any]:
        """Handle a service configuration request"""
        
        # Load current configuration
        if not self.modifier.load_config():
            return {
                "success": False,
                "error": "Could not load configuration",
            }
        
        # Check if service already exists
        services = self.modifier.find_services()
        if service_name in services:
            current_state = services[service_name].get('enable', False)
            if current_state == enable:
                return {
                    "success": True,
                    "message": f"Service '{service_name}' is already {'enabled' if enable else 'disabled'}",
                    "action": "none"
                }
        
        # Configure the service
        config = {"enable": enable}
        result = self.modifier.add_service(service_name, config, dry_run=dry_run)
        
        if result:
            return {
                "success": True,
                "message": f"{'Would configure' if dry_run else 'Configured'} service '{service_name}'",
                "action": "modified"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to configure service '{service_name}'"
            }


if __name__ == "__main__":
    # Test the modifier
    print("🧪 Testing Safe Nix Config Modifier\n")
    
    # Test with sample configuration
    sample_config = """
{ config, pkgs, ... }:

{
  imports = [
    ./hardware-configuration.nix
  ];

  boot.loader.systemd-boot.enable = true;
  
  networking.hostName = "nixos-test";
  
  environment.systemPackages = with pkgs; [
    vim
    git
    firefox
  ];
  
  services.openssh.enable = true;
  
  system.stateVersion = "24.05";
}
"""
    
    modifier = SafeNixConfigModifier()
    modifier.load_from_string(sample_config)
    
    print("📊 Configuration Analysis:")
    analysis = modifier.analyze()
    print(f"   Packages: {analysis['packages']}")
    print(f"   Services: {analysis['services']}")
    
    print("\n🧪 Testing package addition (dry run)...")
    modifier.add_package("htop", dry_run=True)
    
    print("\n🧪 Testing service addition (dry run)...")
    modifier.add_service("docker", {"enable": True}, dry_run=True)