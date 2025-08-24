#!/usr/bin/env python3
"""
Simple Configuration Generator - Fallback for when AST parser is unavailable
"""

from typing import Dict, Any, Optional


class SimpleConfigGenerator:
    """
    Simple configuration generator with common templates
    Works without AST dependencies
    """
    
    def __init__(self):
        # Common service templates
        self.service_templates = {
            'nginx': '''services.nginx = {
  enable = true;
  virtualHosts."example.com" = {
    root = "/var/www";
  };
};''',
            'docker': '''virtualisation.docker = {
  enable = true;
  enableOnBoot = true;
};''',
            'ssh': '''services.openssh = {
  enable = true;
  settings.PermitRootLogin = "no";
  settings.PasswordAuthentication = false;
};''',
            'bluetooth': '''hardware.bluetooth = {
  enable = true;
  powerOnBoot = true;
};''',
            'firewall': '''networking.firewall = {
  enable = true;
  allowedTCPPorts = [ 80 443 ];
  allowedUDPPorts = [ ];
};''',
            'automatic-updates': '''system.autoUpgrade = {
  enable = true;
  allowReboot = false;
  dates = "02:00";
};''',
            'automatic updates': '''system.autoUpgrade = {
  enable = true;
  allowReboot = false;
  dates = "02:00";
};''',
            'auto-upgrade': '''system.autoUpgrade = {
  enable = true;
  allowReboot = false;
  dates = "02:00";
};''',
        }
    
    def generate(self, command: str, config_type: str = 'general') -> str:
        """Generate configuration based on command"""
        command_lower = command.lower()
        
        # Check for service configurations
        for service, template in self.service_templates.items():
            if service in command_lower:
                return template
        
        # Generate generic config
        if 'python' in command_lower:
            return self._generate_python_config(command)
        elif 'package' in command_lower:
            return self._generate_package_config(command)
        else:
            return self._generate_generic_config(command)
    
    def _generate_python_config(self, command: str) -> str:
        """Generate Python development configuration"""
        return '''environment.systemPackages = with pkgs; [
  python311
  python311Packages.pip
  python311Packages.virtualenv
];'''
    
    def _generate_package_config(self, command: str) -> str:
        """Generate package installation configuration"""
        # Extract package name from command
        words = command.lower().split()
        package = 'package'  # Default
        
        for word in words:
            if word not in ['add', 'install', 'configure', 'package', 'the', 'a']:
                package = word
                break
        
        return f'''environment.systemPackages = with pkgs; [
  {package}
];'''
    
    def _generate_generic_config(self, command: str) -> str:
        """Generate generic configuration suggestion"""
        return '''# Add to your configuration.nix:
environment.systemPackages = with pkgs; [
  # Add your packages here
];

services = {
  # Configure services here
};'''


# Compatibility wrapper
class ConfigGeneratorAST:
    """Wrapper to maintain compatibility"""
    
    def __init__(self):
        self.generator = SimpleConfigGenerator()
    
    def generate(self, command: str, config_type: str = 'general') -> str:
        return self.generator.generate(command, config_type)