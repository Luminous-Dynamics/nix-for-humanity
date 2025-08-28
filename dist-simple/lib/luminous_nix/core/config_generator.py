#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
Configuration.nix Generation & Management

This module handles natural language to Nix configuration translation,
making it easy for users to generate and manage their NixOS configurations.
"""

import os
import re
import json
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path
import difflib
import subprocess
from datetime import datetime

@dataclass
class NixModule:
    """Represents a NixOS module with its configuration"""
    name: str
    config: Dict[str, Any]
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    
@dataclass
class ConfigSection:
    """Represents a section of NixOS configuration"""
    name: str
    content: str
    module: Optional[str] = None
    priority: int = 50  # 0-100, higher = more important

class NixConfigGenerator:
    """Generate and manage NixOS configurations from natural language"""
    
    def __init__(self):
        self.modules_db = self._load_modules_database()
        self.templates = self._load_templates()
        self.current_config = None
        self.config_history = []
        
    def _load_modules_database(self) -> Dict[str, NixModule]:
        """Load database of NixOS modules and their configurations"""
        return {
            # System modules
            "boot.uefi": NixModule(
                name="boot.loader.systemd-boot",
                config={
                    "boot.loader.systemd-boot.enable": True,
                    "boot.loader.efi.canTouchEfiVariables": True
                },
                description="UEFI boot with systemd-boot"
            ),
            "boot.grub": NixModule(
                name="boot.loader.grub",
                config={
                    "boot.loader.grub.enable": True,
                    "boot.loader.grub.device": "/dev/sda"
                },
                description="Legacy BIOS boot with GRUB",
                conflicts=["boot.uefi"]
            ),
            
            # Desktop environments
            "desktop.gnome": NixModule(
                name="services.xserver.desktopManager.gnome",
                config={
                    "services.xserver.enable": True,
                    "services.xserver.displayManager.gdm.enable": True,
                    "services.xserver.desktopManager.gnome.enable": True
                },
                description="GNOME desktop environment",
                conflicts=["desktop.kde", "desktop.xfce"]
            ),
            "desktop.kde": NixModule(
                name="services.xserver.desktopManager.plasma5",
                config={
                    "services.xserver.enable": True,
                    "services.xserver.displayManager.sddm.enable": True,
                    "services.xserver.desktopManager.plasma5.enable": True
                },
                description="KDE Plasma desktop environment",
                conflicts=["desktop.gnome", "desktop.xfce"]
            ),
            
            # Web servers
            "web.nginx": NixModule(
                name="services.nginx",
                config={
                    "services.nginx.enable": True,
                    "services.nginx.recommendedProxySettings": True,
                    "services.nginx.recommendedTlsSettings": True
                },
                description="Nginx web server",
                conflicts=["web.apache"]
            ),
            "web.apache": NixModule(
                name="services.httpd",
                config={
                    "services.httpd.enable": True
                },
                description="Apache web server",
                conflicts=["web.nginx"]
            ),
            
            # Databases
            "db.postgresql": NixModule(
                name="services.postgresql",
                config={
                    "services.postgresql.enable": True,
                    "services.postgresql.package": "pkgs.postgresql_15"
                },
                description="PostgreSQL database server"
            ),
            "db.mysql": NixModule(
                name="services.mysql",
                config={
                    "services.mysql.enable": True,
                    "services.mysql.package": "pkgs.mariadb"
                },
                description="MySQL/MariaDB database server"
            ),
            
            # Development tools
            "dev.docker": NixModule(
                name="virtualisation.docker",
                config={
                    "virtualisation.docker.enable": True
                },
                description="Docker container runtime"
            ),
            "dev.vscode": NixModule(
                name="programs.vscode",
                config={
                    "environment.systemPackages": ["pkgs.vscode"]
                },
                description="Visual Studio Code editor"
            ),
            
            # Security
            "security.firewall": NixModule(
                name="networking.firewall",
                config={
                    "networking.firewall.enable": True,
                    "networking.firewall.allowedTCPPorts": [22]
                },
                description="Basic firewall configuration"
            ),
            "security.ssh": NixModule(
                name="services.openssh",
                config={
                    "services.openssh.enable": True,
                    "services.openssh.settings.PermitRootLogin": "no"
                },
                description="OpenSSH server"
            ),
        }
    
    def _load_templates(self) -> Dict[str, str]:
        """Load configuration templates"""
        return {
            "base": '''{{ config, pkgs, ... }}:

{{
  imports = [
    ./hardware-configuration.nix{imports}
  ];

  # Boot loader
{boot}

  # Networking
  networking.hostName = "{hostname}";
  networking.networkmanager.enable = true;

  # Time zone and locale
  time.timeZone = "{timezone}";
  i18n.defaultLocale = "{locale}";

  # Users
{users}

  # System packages
  environment.systemPackages = with pkgs; [
{packages}
  ];

{services}

  # System version
  system.stateVersion = "{state_version}";
}}
''',
            "user": '''  users.users.{username} = {{
    isNormalUser = true;
    description = "{description}";
    extraGroups = [ {groups} ];
    shell = pkgs.{shell};
  }};''',
            
            "service_section": '''  # {category} services
{content}''',
        }
    
    def parse_intent(self, natural_language: str) -> Dict[str, Any]:
        """Parse natural language into configuration intent"""
        intent = {
            "modules": [],
            "packages": [],
            "users": [],
            "settings": {},
            "action": "generate"  # generate, modify, validate, explain
        }
        
        # Normalize input
        text = natural_language.lower()
        
        # Detect action
        if any(word in text for word in ["modify", "change", "update", "edit"]):
            intent["action"] = "modify"
        elif any(word in text for word in ["check", "validate", "verify"]):
            intent["action"] = "validate"
        elif any(word in text for word in ["explain", "what", "why"]):
            intent["action"] = "explain"
        
        # Detect desktop environments
        if any(de in text for de in ["gnome", "kde", "plasma", "xfce"]):
            if "gnome" in text:
                intent["modules"].append("desktop.gnome")
            elif "kde" in text or "plasma" in text:
                intent["modules"].append("desktop.kde")
        
        # Detect web servers
        if any(web in text for web in ["web server", "nginx", "apache", "httpd"]):
            if "nginx" in text:
                intent["modules"].append("web.nginx")
            elif "apache" in text or "httpd" in text:
                intent["modules"].append("web.apache")
            else:
                intent["modules"].append("web.nginx")  # Default
        
        # Detect databases
        if any(db in text for db in ["database", "postgres", "postgresql", "mysql", "mariadb"]):
            if "postgres" in text:
                intent["modules"].append("db.postgresql")
            elif "mysql" in text or "mariadb" in text:
                intent["modules"].append("db.mysql")
        
        # Detect development tools
        if "docker" in text:
            intent["modules"].append("dev.docker")
        if "vscode" in text or "vs code" in text:
            intent["modules"].append("dev.vscode")
        
        # Detect security features
        if "ssh" in text or "remote access" in text:
            intent["modules"].append("security.ssh")
        if "firewall" in text:
            intent["modules"].append("security.firewall")
        
        # Detect user creation
        user_patterns = [
            r"add (?:user|account) (\w+)",
            r"create (?:user|account) (\w+)",
            r"user (\w+)",
        ]
        for pattern in user_patterns:
            match = re.search(pattern, text)
            if match:
                intent["users"].append({
                    "name": match.group(1),
                    "admin": "admin" in text or "sudo" in text
                })
        
        # Detect hostname
        hostname_match = re.search(r"hostname (\S+)", text)
        if hostname_match:
            intent["settings"]["hostname"] = hostname_match.group(1)
        
        # Detect common packages
        package_keywords = {
            "firefox": "firefox",
            "chrome": "google-chrome",
            "vim": "vim",
            "emacs": "emacs",
            "git": "git",
            "python": "python3",
            "node": "nodejs",
            "development": ["git", "vim", "tmux", "htop"],
            "programming": ["git", "vim", "gcc", "gnumake"],
        }
        
        for keyword, packages in package_keywords.items():
            if keyword in text:
                if isinstance(packages, list):
                    intent["packages"].extend(packages)
                else:
                    intent["packages"].append(packages)
        
        return intent
    
    def check_conflicts(self, modules: List[str]) -> List[tuple]:
        """Check for conflicts between modules"""
        conflicts = []
        for i, module1 in enumerate(modules):
            if module1 in self.modules_db:
                for module2 in modules[i+1:]:
                    if module2 in self.modules_db[module1].conflicts:
                        conflicts.append((module1, module2))
        return conflicts
    
    def generate_config(self, intent: Dict[str, Any]) -> str:
        """Generate NixOS configuration from intent"""
        # Check for conflicts
        conflicts = self.check_conflicts(intent["modules"])
        if conflicts:
            conflict_msg = "\n".join([f"  - {m1} conflicts with {m2}" for m1, m2 in conflicts])
            return f"Error: Module conflicts detected:\n{conflict_msg}\nPlease choose only one."
        
        # Start with base template
        template = self.templates["base"]
        
        # Configure boot loader
        boot_config = ""
        if "boot.uefi" in intent["modules"]:
            boot_config = self._format_config(self.modules_db["boot.uefi"].config, indent=2)
        else:
            boot_config = self._format_config(self.modules_db["boot.uefi"].config, indent=2)  # Default
        
        # Configure services
        service_configs = []
        service_categories = {
            "Desktop Environment": ["desktop."],
            "Web Services": ["web."],
            "Database Services": ["db."],
            "Development Tools": ["dev."],
            "Security": ["security."]
        }
        
        for category, prefixes in service_categories.items():
            category_configs = []
            for module_name in intent["modules"]:
                if any(module_name.startswith(prefix) for prefix in prefixes):
                    if module_name in self.modules_db:
                        module = self.modules_db[module_name]
                        config_str = self._format_config(module.config, indent=2)
                        category_configs.append(config_str)
            
            if category_configs:
                section = self.templates["service_section"].format(
                    category=category,
                    content="\n".join(category_configs)
                )
                service_configs.append(section)
        
        # Configure users
        user_configs = []
        for user in intent["users"]:
            groups = ["networkmanager"]
            if user.get("admin"):
                groups.append("wheel")
            if "dev.docker" in intent["modules"]:
                groups.append("docker")
            
            user_config = self.templates["user"].format(
                username=user["name"],
                description=user.get("description", user["name"]),
                groups='"' + '" "'.join(groups) + '"',
                shell="bash"
            )
            user_configs.append(user_config)
        
        # Add default user if none specified
        if not user_configs:
            user_configs.append(self.templates["user"].format(
                username="user",
                description="Default user",
                groups='"networkmanager" "wheel"',
                shell="bash"
            ))
        
        # Format packages
        packages = list(set(intent["packages"]))  # Remove duplicates
        if not packages:
            packages = ["vim", "wget", "git"]  # Minimal defaults
        package_list = "\n".join([f"    {pkg}" for pkg in packages])
        
        # Fill in template
        config = template.format(
            imports="",  # Additional imports if needed
            boot=boot_config,
            hostname=intent["settings"].get("hostname", "nixos"),
            timezone=intent["settings"].get("timezone", "UTC"),
            locale=intent["settings"].get("locale", "en_US.UTF-8"),
            users="\n".join(user_configs),
            packages=package_list,
            services="\n".join(service_configs),
            state_version="24.05"  # Current stable
        )
        
        return config
    
    def _format_config(self, config: Dict[str, Any], indent: int = 0) -> str:
        """Format configuration dictionary as Nix syntax"""
        lines = []
        indent_str = "  " * indent
        
        for key, value in config.items():
            if isinstance(value, bool):
                lines.append(f"{indent_str}{key} = {str(value).lower()};")
            elif isinstance(value, str):
                if value.startswith("pkgs."):
                    lines.append(f"{indent_str}{key} = {value};")
                else:
                    lines.append(f'{indent_str}{key} = "{value}";')
            elif isinstance(value, list):
                if all(isinstance(v, str) and v.startswith("pkgs.") for v in value):
                    # Package list
                    lines.append(f"{indent_str}{key} = with pkgs; [ {' '.join(v.replace('pkgs.', '') for v in value)} ];")
                else:
                    # String list
                    lines.append(f"{indent_str}{key} = [ {' '.join(f'"{v}"' for v in value)} ];")
            elif isinstance(value, int):
                lines.append(f"{indent_str}{key} = {value};")
        
        return "\n".join(lines)
    
    def validate_config(self, config_path: str) -> tuple[bool, str]:
        """Validate a NixOS configuration file"""
        try:
            # Use nix-instantiate to check syntax
            result = subprocess.run(
                ["nix-instantiate", "--parse", config_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True, "Configuration syntax is valid!"
            else:
                return False, f"Syntax errors:\n{result.stderr}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def explain_config(self, config_path: str) -> str:
        """Explain what a configuration does in plain language"""
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            explanation = ["This NixOS configuration:"]
            
            # Check boot loader
            if "systemd-boot" in content:
                explanation.append("- Uses UEFI boot with systemd-boot")
            elif "grub" in content:
                explanation.append("- Uses GRUB bootloader")
            
            # Check desktop
            if "gnome.enable = true" in content:
                explanation.append("- Runs GNOME desktop environment")
            elif "plasma5.enable = true" in content:
                explanation.append("- Runs KDE Plasma desktop")
            
            # Check services
            if "nginx.enable = true" in content:
                explanation.append("- Runs Nginx web server")
            if "postgresql.enable = true" in content:
                explanation.append("- Runs PostgreSQL database")
            if "docker.enable = true" in content:
                explanation.append("- Has Docker container support")
            
            # Check networking
            if "openssh.enable = true" in content:
                explanation.append("- Allows SSH remote access")
            if "firewall.enable = true" in content:
                explanation.append("- Has firewall enabled")
            
            # Find hostname
            hostname_match = re.search(r'hostname\s*=\s*"([^"]+)"', content)
            if hostname_match:
                explanation.append(f"- System name: {hostname_match.group(1)}")
            
            # Count packages
            packages = re.findall(r'^\s+(\w+)\s*$', content, re.MULTILINE)
            if packages:
                explanation.append(f"- Includes {len(packages)} system packages")
            
            return "\n".join(explanation)
        except Exception as e:
            return f"Error reading configuration: {str(e)}"
    
    def diff_configs(self, old_path: str, new_path: str) -> str:
        """Show differences between two configurations"""
        try:
            with open(old_path, 'r') as f:
                old_lines = f.readlines()
            with open(new_path, 'r') as f:
                new_lines = f.readlines()
            
            diff = difflib.unified_diff(
                old_lines, new_lines,
                fromfile=old_path,
                tofile=new_path,
                lineterm=''
            )
            
            return '\n'.join(diff)
        except Exception as e:
            return f"Error comparing configurations: {str(e)}"
    
    def save_config(self, config: str, path: str, backup: bool = True) -> tuple[bool, str]:
        """Save configuration with optional backup"""
        try:
            path_obj = Path(path)
            
            # Backup existing config
            if backup and path_obj.exists():
                backup_path = path_obj.with_suffix(f'.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                path_obj.rename(backup_path)
                
            # Write new config
            with open(path, 'w') as f:
                f.write(config)
            
            return True, f"Configuration saved to {path}"
        except Exception as e:
            return False, f"Error saving configuration: {str(e)}"


# Example usage functions
def generate_from_natural_language(text: str) -> str:
    """Generate configuration from natural language"""
    generator = NixConfigGenerator()
    intent = generator.parse_intent(text)
    
    if intent["action"] == "generate":
        return generator.generate_config(intent)
    else:
        return f"Action '{intent['action']}' not implemented in this example"


if __name__ == "__main__":
    # Test examples
    examples = [
        "Make me a web server with nginx and postgresql",
        "Set up a development machine with docker and vscode", 
        "Create a desktop system with KDE and user john with admin access",
        "Configure a secure server with ssh and firewall"
    ]
    
    for example in examples:
        print(f"\n{'='*60}")
        print(f"Input: {example}")
        print(f"{'='*60}")
        config = generate_from_natural_language(example)
        print(config)