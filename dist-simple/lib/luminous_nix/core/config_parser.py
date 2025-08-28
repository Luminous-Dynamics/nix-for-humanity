#!/usr/bin/env python3
"""
NixOS Configuration Parser
===========================

This module provides intelligent parsing and understanding of NixOS configuration files,
enabling the system to:
- Parse configuration.nix files
- Understand the structure and dependencies
- Suggest improvements and fixes
- Generate configuration snippets
- Validate configurations
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class NixModule:
    """Represents a NixOS module or configuration section"""
    name: str
    path: List[str]  # e.g., ["services", "openssh", "enable"]
    value: Any
    line_number: int
    dependencies: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class NixImport:
    """Represents an import statement"""
    path: str
    line_number: int
    is_relative: bool
    is_flake: bool = False


@dataclass
class ParsedConfiguration:
    """Complete parsed NixOS configuration"""
    imports: List[NixImport]
    modules: List[NixModule]
    packages: List[str]
    services: Dict[str, Any]
    users: Dict[str, Any]
    boot_config: Dict[str, Any]
    networking_config: Dict[str, Any]
    raw_content: str
    parse_errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class ConfigurationParser:
    """
    Intelligent NixOS configuration parser.
    
    This parser understands NixOS configuration structure and can:
    - Extract key configuration elements
    - Identify common patterns and anti-patterns
    - Suggest improvements
    - Validate basic structure
    """
    
    def __init__(self):
        """Initialize the configuration parser"""
        self.logger = logger
        
        # Common NixOS options we understand
        self.known_options = {
            'boot.loader': 'Boot loader configuration',
            'networking.hostName': 'System hostname',
            'networking.networkmanager.enable': 'NetworkManager service',
            'services.openssh.enable': 'OpenSSH server',
            'services.xserver.enable': 'X11 windowing system',
            'users.users': 'User account definitions',
            'environment.systemPackages': 'System-wide packages',
            'programs.zsh.enable': 'Z shell',
            'programs.git.enable': 'Git version control',
            'virtualisation.docker.enable': 'Docker containerization',
            'virtualisation.libvirtd.enable': 'Libvirt virtualization',
        }
        
        # Patterns for common issues
        self.antipatterns = {
            r'allowUnfree\s*=\s*true': 'Consider using per-package unfree allowances',
            r'users\.users\.\w+\.password\s*=': 'Avoid plaintext passwords, use hashedPassword',
            r'services\.openssh\.permitRootLogin\s*=\s*"yes"': 'Root SSH login is a security risk',
            r'networking\.firewall\.enable\s*=\s*false': 'Disabling firewall reduces security',
        }
        
        logger.info("📝 ConfigurationParser initialized")
    
    def parse_file(self, filepath: str) -> ParsedConfiguration:
        """
        Parse a NixOS configuration file.
        
        Args:
            filepath: Path to configuration.nix
            
        Returns:
            Parsed configuration with extracted information
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return self.parse_content(content)
        except Exception as e:
            logger.error(f"Failed to parse file {filepath}: {e}")
            return ParsedConfiguration(
                imports=[],
                modules=[],
                packages=[],
                services={},
                users={},
                boot_config={},
                networking_config={},
                raw_content="",
                parse_errors=[str(e)]
            )
    
    def parse_content(self, content: str) -> ParsedConfiguration:
        """
        Parse NixOS configuration content.
        
        Args:
            content: Configuration file content
            
        Returns:
            Parsed configuration
        """
        config = ParsedConfiguration(
            imports=[],
            modules=[],
            packages=[],
            services={},
            users={},
            boot_config={},
            networking_config={},
            raw_content=content
        )
        
        lines = content.split('\n')
        
        # Extract imports
        config.imports = self._extract_imports(lines)
        
        # Extract packages
        config.packages = self._extract_packages(content)
        
        # Extract services
        config.services = self._extract_services(content)
        
        # Extract users
        config.users = self._extract_users(content)
        
        # Extract boot configuration
        config.boot_config = self._extract_boot_config(content)
        
        # Extract networking
        config.networking_config = self._extract_networking(content)
        
        # Extract modules
        config.modules = self._extract_modules(lines)
        
        # Check for antipatterns
        config.suggestions = self._check_antipatterns(content)
        
        # Add general suggestions
        config.suggestions.extend(self._generate_suggestions(config))
        
        return config
    
    def _extract_imports(self, lines: List[str]) -> List[NixImport]:
        """Extract import statements"""
        imports = []
        import_pattern = re.compile(r'^\s*imports\s*=\s*\[(.*?)\];', re.MULTILINE | re.DOTALL)
        
        for i, line in enumerate(lines):
            # Simple import detection
            if 'import' in line.lower():
                # Check for single import
                single_import = re.search(r'import\s+([./\w\-]+)', line)
                if single_import:
                    path = single_import.group(1)
                    imports.append(NixImport(
                        path=path,
                        line_number=i + 1,
                        is_relative=path.startswith('.'),
                        is_flake='flake' in path.lower()
                    ))
        
        return imports
    
    def _extract_packages(self, content: str) -> List[str]:
        """Extract system packages"""
        packages = []
        
        # Look for environment.systemPackages
        package_pattern = re.compile(
            r'environment\.systemPackages\s*=\s*with\s+pkgs;\s*\[(.*?)\];',
            re.MULTILINE | re.DOTALL
        )
        
        matches = package_pattern.findall(content)
        for match in matches:
            # Clean and split package names
            pkg_text = match.replace('\n', ' ').replace('\t', ' ')
            # Remove comments
            pkg_text = re.sub(r'#.*', '', pkg_text)
            # Split by whitespace and filter
            pkg_names = [p.strip() for p in pkg_text.split() if p.strip()]
            packages.extend(pkg_names)
        
        # Also look for individual package references
        individual_pattern = re.compile(r'pkgs\.(\w+)')
        for match in individual_pattern.findall(content):
            if match not in packages:
                packages.append(match)
        
        return packages
    
    def _extract_services(self, content: str) -> Dict[str, Any]:
        """Extract service configurations"""
        services = {}
        
        # Common service patterns
        service_patterns = [
            (r'services\.openssh\.enable\s*=\s*(\w+)', 'openssh'),
            (r'services\.nginx\.enable\s*=\s*(\w+)', 'nginx'),
            (r'services\.postgresql\.enable\s*=\s*(\w+)', 'postgresql'),
            (r'services\.docker\.enable\s*=\s*(\w+)', 'docker'),
            (r'services\.xserver\.enable\s*=\s*(\w+)', 'xserver'),
            (r'services\.pipewire\.enable\s*=\s*(\w+)', 'pipewire'),
        ]
        
        for pattern, service_name in service_patterns:
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                services[service_name] = {
                    'enabled': value == 'true',
                    'raw_value': value
                }
        
        # Extract more complex service configs
        services.update(self._extract_complex_services(content))
        
        return services
    
    def _extract_complex_services(self, content: str) -> Dict[str, Any]:
        """Extract complex service configurations"""
        complex_services = {}
        
        # OpenSSH with settings
        ssh_block = re.search(
            r'services\.openssh\s*=\s*\{(.*?)\};',
            content,
            re.MULTILINE | re.DOTALL
        )
        if ssh_block:
            ssh_config = {}
            block_content = ssh_block.group(1)
            
            # Extract SSH settings
            if 'enable = true' in block_content:
                ssh_config['enabled'] = True
            if 'permitRootLogin' in block_content:
                root_login = re.search(r'permitRootLogin\s*=\s*"?(\w+)"?', block_content)
                if root_login:
                    ssh_config['permitRootLogin'] = root_login.group(1)
            if 'passwordAuthentication' in block_content:
                pwd_auth = re.search(r'passwordAuthentication\s*=\s*(\w+)', block_content)
                if pwd_auth:
                    ssh_config['passwordAuthentication'] = pwd_auth.group(1) == 'true'
            
            if ssh_config:
                complex_services['openssh'] = ssh_config
        
        return complex_services
    
    def _extract_users(self, content: str) -> Dict[str, Any]:
        """Extract user configurations"""
        users = {}
        
        # Look for users.users blocks
        user_pattern = re.compile(
            r'users\.users\.(\w+)\s*=\s*\{(.*?)\};',
            re.MULTILINE | re.DOTALL
        )
        
        for match in user_pattern.finditer(content):
            username = match.group(1)
            user_block = match.group(2)
            
            user_config = {'name': username}
            
            # Extract user properties
            if 'isNormalUser = true' in user_block:
                user_config['isNormalUser'] = True
            if 'isSystemUser = true' in user_block:
                user_config['isSystemUser'] = True
            
            # Extract shell
            shell_match = re.search(r'shell\s*=\s*pkgs\.(\w+)', user_block)
            if shell_match:
                user_config['shell'] = shell_match.group(1)
            
            # Extract groups
            groups_match = re.search(r'extraGroups\s*=\s*\[(.*?)\]', user_block)
            if groups_match:
                groups_text = groups_match.group(1)
                groups = [g.strip().strip('"') for g in groups_text.split() if g.strip()]
                user_config['groups'] = groups
            
            # Check for password issues
            if 'password =' in user_block:
                user_config['has_plaintext_password'] = True
            if 'hashedPassword' in user_block:
                user_config['has_hashed_password'] = True
            
            users[username] = user_config
        
        return users
    
    def _extract_boot_config(self, content: str) -> Dict[str, Any]:
        """Extract boot configuration"""
        boot = {}
        
        # Boot loader
        if 'boot.loader.systemd-boot.enable = true' in content:
            boot['loader'] = 'systemd-boot'
        elif 'boot.loader.grub.enable = true' in content:
            boot['loader'] = 'grub'
            
            # GRUB device
            device_match = re.search(r'boot\.loader\.grub\.device\s*=\s*"([^"]+)"', content)
            if device_match:
                boot['grub_device'] = device_match.group(1)
        
        # EFI support
        if 'boot.loader.efi.canTouchEfiVariables = true' in content:
            boot['efi_enabled'] = True
        
        # Kernel modules
        modules_match = re.search(r'boot\.initrd\.kernelModules\s*=\s*\[(.*?)\]', content)
        if modules_match:
            modules_text = modules_match.group(1)
            modules = [m.strip().strip('"') for m in modules_text.split() if m.strip()]
            boot['kernel_modules'] = modules
        
        return boot
    
    def _extract_networking(self, content: str) -> Dict[str, Any]:
        """Extract networking configuration"""
        networking = {}
        
        # Hostname
        hostname_match = re.search(r'networking\.hostName\s*=\s*"([^"]+)"', content)
        if hostname_match:
            networking['hostname'] = hostname_match.group(1)
        
        # NetworkManager
        if 'networking.networkmanager.enable = true' in content:
            networking['networkmanager'] = True
        
        # Firewall
        if 'networking.firewall.enable = false' in content:
            networking['firewall_disabled'] = True
        elif 'networking.firewall.enable = true' in content:
            networking['firewall_enabled'] = True
        
        # Allowed ports
        tcp_ports = re.search(r'networking\.firewall\.allowedTCPPorts\s*=\s*\[(.*?)\]', content)
        if tcp_ports:
            ports_text = tcp_ports.group(1)
            ports = [int(p.strip()) for p in ports_text.split() if p.strip().isdigit()]
            networking['allowed_tcp_ports'] = ports
        
        return networking
    
    def _extract_modules(self, lines: List[str]) -> List[NixModule]:
        """Extract configuration modules/options"""
        modules = []
        
        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue
            
            # Look for option assignments
            option_match = re.match(r'\s*([\w\.]+)\s*=\s*(.+);?$', line)
            if option_match:
                option_path = option_match.group(1)
                value_str = option_match.group(2).rstrip(';').strip()
                
                # Parse value
                if value_str == 'true':
                    value = True
                elif value_str == 'false':
                    value = False
                elif value_str.startswith('"') and value_str.endswith('"'):
                    value = value_str[1:-1]
                else:
                    value = value_str
                
                # Create module
                path_parts = option_path.split('.')
                module = NixModule(
                    name=option_path,
                    path=path_parts,
                    value=value,
                    line_number=i + 1
                )
                
                # Add description if known
                if option_path in self.known_options:
                    module.description = self.known_options[option_path]
                
                modules.append(module)
        
        return modules
    
    def _check_antipatterns(self, content: str) -> List[str]:
        """Check for common antipatterns and issues"""
        suggestions = []
        
        for pattern, suggestion in self.antipatterns.items():
            if re.search(pattern, content):
                suggestions.append(f"⚠️ {suggestion}")
        
        # Additional checks
        if 'allowUnfree = true' in content and 'nixpkgs.config' in content:
            suggestions.append("💡 Consider using overlays for unfree packages")
        
        if not any(loader in content for loader in ['systemd-boot', 'grub']):
            suggestions.append("⚠️ No boot loader configured - system may not boot")
        
        if 'networking.hostName' not in content:
            suggestions.append("💡 Consider setting a hostname with networking.hostName")
        
        return suggestions
    
    def _generate_suggestions(self, config: ParsedConfiguration) -> List[str]:
        """Generate improvement suggestions based on parsed config"""
        suggestions = []
        
        # Security suggestions
        for username, user_config in config.users.items():
            if user_config.get('has_plaintext_password'):
                suggestions.append(f"🔒 User '{username}' has plaintext password - use hashedPassword instead")
        
        if config.networking_config.get('firewall_disabled'):
            suggestions.append("🔥 Firewall is disabled - consider enabling for security")
        
        # Service suggestions
        if 'openssh' in config.services and config.services['openssh'].get('permitRootLogin') == 'yes':
            suggestions.append("🔒 SSH root login enabled - consider using sudo instead")
        
        # Package suggestions
        if len(config.packages) > 50:
            suggestions.append("📦 Many packages installed - consider using Home Manager for user packages")
        
        # Boot suggestions
        if not config.boot_config.get('loader'):
            suggestions.append("⚠️ No boot loader configured")
        
        return suggestions
    
    def validate(self, config: ParsedConfiguration) -> Tuple[bool, List[str]]:
        """
        Validate a parsed configuration.
        
        Args:
            config: Parsed configuration
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for critical issues
        if not config.boot_config.get('loader'):
            errors.append("No boot loader configured")
        
        if not config.networking_config.get('hostname'):
            errors.append("No hostname set")
        
        # Check for security issues
        for username, user_config in config.users.items():
            if user_config.get('has_plaintext_password'):
                errors.append(f"User '{username}' has insecure plaintext password")
        
        # Check for parse errors
        errors.extend(config.parse_errors)
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def generate_snippet(self, option: str, value: Any) -> str:
        """
        Generate a configuration snippet for an option.
        
        Args:
            option: NixOS option path (e.g., "services.openssh.enable")
            value: Value for the option
            
        Returns:
            Configuration snippet
        """
        if isinstance(value, bool):
            value_str = 'true' if value else 'false'
        elif isinstance(value, str):
            value_str = f'"{value}"'
        elif isinstance(value, list):
            items = [f'"{item}"' if isinstance(item, str) else str(item) for item in value]
            value_str = f'[ {" ".join(items)} ]'
        else:
            value_str = str(value)
        
        snippet = f"{option} = {value_str};"
        
        # Add comment if known
        if option in self.known_options:
            snippet = f"# {self.known_options[option]}\n{snippet}"
        
        return snippet
    
    def suggest_improvements(self, config: ParsedConfiguration) -> List[str]:
        """
        Suggest specific improvements for a configuration.
        
        Args:
            config: Parsed configuration
            
        Returns:
            List of improvement suggestions with code snippets
        """
        improvements = []
        
        # Security improvements
        if config.networking_config.get('firewall_disabled'):
            improvements.append(
                "Enable firewall:\n" +
                self.generate_snippet('networking.firewall.enable', True)
            )
        
        # User improvements
        for username, user_config in config.users.items():
            if user_config.get('has_plaintext_password'):
                improvements.append(
                    f"Use hashed password for {username}:\n" +
                    f"# Generate with: mkpasswd -m sha-512\n" +
                    f"users.users.{username}.hashedPassword = \"$6$...$...\";"
                )
        
        # Service improvements
        if 'docker' not in config.services and any('container' in pkg for pkg in config.packages):
            improvements.append(
                "Enable Docker for containerization:\n" +
                self.generate_snippet('virtualisation.docker.enable', True)
            )
        
        return improvements


# Convenience function
def parse_configuration(filepath: str) -> ParsedConfiguration:
    """Parse a NixOS configuration file"""
    parser = ConfigurationParser()
    return parser.parse_file(filepath)