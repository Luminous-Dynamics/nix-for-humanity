"""
Enhanced Configuration Generator with Tree-sitter Safety
Generates and modifies NixOS configurations intelligently
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from .safe_nix_modifier import SafeNixConfigModifier, NixConfigIntegration


class ConfigGenerator:
    """
    Generate and modify NixOS configurations safely
    Now with Tree-sitter-like safe parsing!
    """
    
    def __init__(self):
        self.modifier = SafeNixConfigModifier()
        self.integration = NixConfigIntegration()
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, str]:
        """Load configuration templates"""
        return {
            "minimal": """
{{ config, pkgs, ... }}:

{{
  imports = [
    ./hardware-configuration.nix
  ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "{hostname}";
  networking.networkmanager.enable = true;

  time.timeZone = "{timezone}";

  i18n.defaultLocale = "{locale}";

  environment.systemPackages = with pkgs; [
    vim
    wget
    git
  ];

  services.openssh.enable = true;

  users.users.{username} = {{{{
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  }}}};

  system.stateVersion = "{version}";
}}
""",
            "desktop": """
{ config, pkgs, ... }:

{
  imports = [
    ./hardware-configuration.nix
  ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "{hostname}";
  networking.networkmanager.enable = true;

  time.timeZone = "{timezone}";
  i18n.defaultLocale = "{locale}";

  services.xserver.enable = true;
  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;

  sound.enable = true;
  hardware.pulseaudio.enable = true;

  environment.systemPackages = with pkgs; [
    vim
    wget
    firefox
    git
    vscode
    gnome.gnome-terminal
    gnome.gnome-tweaks
  ];

  services.openssh.enable = true;

  users.users.{username} = {{{{
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" "audio" ];
  }}}};

  system.stateVersion = "{version}";
}}
""",
            "development": """
{ config, pkgs, ... }:

{
  imports = [
    ./hardware-configuration.nix
  ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "{hostname}";
  networking.networkmanager.enable = true;

  time.timeZone = "{timezone}";
  i18n.defaultLocale = "{locale}";

  environment.systemPackages = with pkgs; [
    vim
    neovim
    emacs
    git
    gh
    docker
    docker-compose
    nodejs
    python3
    rustc
    cargo
    go
    gcc
    gnumake
    vscode
    jetbrains.idea-community
  ];

  services.openssh.enable = true;
  services.docker.enable = true;

  virtualisation.docker.enable = true;

  users.users.{username} = {{{{
    isNormalUser = true;
    extraGroups = [ "wheel" "docker" "networkmanager" ];
  }}}};

  system.stateVersion = "{version}";
}}
"""
        }
    
    def analyze_current_config(self, config_path: str = "/etc/nixos/configuration.nix") -> Dict[str, Any]:
        """
        Analyze the current configuration
        
        Returns:
            Analysis results including packages, services, etc.
        """
        self.modifier.config_path = Path(config_path)
        
        if not self.modifier.load_config():
            return {"error": "Could not load configuration"}
        
        analysis = self.modifier.analyze()
        
        # Add summary
        analysis["summary"] = {
            "total_packages": len(analysis.get("packages", [])),
            "total_services": len(analysis.get("services", {})),
            "enabled_services": sum(1 for s in analysis.get("services", {}).values() if s.get("enable")),
            "config_complete": all([
                analysis.get("has_hardware_config"),
                analysis.get("has_bootloader"),
                analysis.get("has_networking"),
                analysis.get("has_users")
            ])
        }
        
        return analysis
    
    def add_package(self, package_name: str, config_path: str = "/etc/nixos/configuration.nix", 
                   dry_run: bool = True) -> Dict[str, Any]:
        """
        Add a package to the configuration safely
        
        Args:
            package_name: Package to add
            config_path: Path to configuration file
            dry_run: If True, don't actually modify
            
        Returns:
            Result dictionary with success status and messages
        """
        self.modifier.config_path = Path(config_path)
        return self.integration.handle_install_request(package_name, dry_run)
    
    def add_service(self, service_name: str, enable: bool = True, 
                   config_path: str = "/etc/nixos/configuration.nix",
                   dry_run: bool = True) -> Dict[str, Any]:
        """
        Configure a service safely
        
        Args:
            service_name: Service to configure
            enable: Whether to enable the service
            config_path: Path to configuration file
            dry_run: If True, don't actually modify
            
        Returns:
            Result dictionary with success status and messages
        """
        self.modifier.config_path = Path(config_path)
        return self.integration.handle_service_request(service_name, enable, dry_run)
    
    def generate_config(self, template: str = "minimal", **kwargs) -> str:
        """
        Generate a new configuration from template
        
        Args:
            template: Template name (minimal, desktop, development)
            **kwargs: Template variables
            
        Returns:
            Generated configuration
        """
        if template not in self.templates:
            raise ValueError(f"Unknown template: {template}")
        
        # Default values
        defaults = {
            "hostname": "nixos",
            "username": "user",
            "timezone": "America/Chicago",
            "locale": "en_US.UTF-8",
            "version": "24.05"
        }
        
        # Merge with provided values
        values = {**defaults, **kwargs}
        
        # Generate from template
        config = self.templates[template].format(**values)
        
        return config
    
    def check_conflicts(self, package_name: str = None, service_name: str = None,
                       config_path: str = "/etc/nixos/configuration.nix") -> Dict[str, Any]:
        """
        Check for potential conflicts before adding
        
        Args:
            package_name: Package to check
            service_name: Service to check
            config_path: Configuration file path
            
        Returns:
            Conflict analysis
        """
        self.modifier.config_path = Path(config_path)
        
        if not self.modifier.load_config():
            return {"error": "Could not load configuration"}
        
        conflicts = {
            "has_conflicts": False,
            "conflicts": []
        }
        
        if package_name:
            if self.modifier.has_package(package_name):
                conflicts["has_conflicts"] = True
                conflicts["conflicts"].append(f"Package '{package_name}' already exists")
            
            # Check for known incompatibilities
            packages = self.modifier.find_system_packages()
            
            # Example conflict checks
            if package_name == "docker" and "podman" in packages:
                conflicts["has_conflicts"] = True
                conflicts["conflicts"].append("Docker conflicts with Podman")
            
            if package_name == "pulseaudio" and "pipewire" in packages:
                conflicts["has_conflicts"] = True
                conflicts["conflicts"].append("PulseAudio conflicts with PipeWire")
        
        if service_name:
            if self.modifier.has_service(service_name):
                services = self.modifier.find_services()
                if services.get(service_name, {}).get("enable"):
                    conflicts["has_conflicts"] = True
                    conflicts["conflicts"].append(f"Service '{service_name}' already enabled")
        
        return conflicts
    
    def suggest_packages(self, description: str) -> List[str]:
        """
        Suggest packages based on description
        
        Args:
            description: What the user wants to do
            
        Returns:
            List of suggested packages
        """
        # Package suggestion mappings
        suggestions = {
            "editor": ["vim", "neovim", "emacs", "vscode", "sublime3"],
            "browser": ["firefox", "chromium", "brave", "vivaldi"],
            "terminal": ["alacritty", "kitty", "wezterm", "gnome.gnome-terminal"],
            "development": ["git", "gh", "vscode", "docker", "nodejs", "python3"],
            "python": ["python3", "python311", "python312", "poetry", "pipenv"],
            "rust": ["rustc", "cargo", "rust-analyzer", "rustup"],
            "docker": ["docker", "docker-compose", "docker-credential-helpers"],
            "music": ["spotify", "rhythmbox", "clementine", "mpd", "ncmpcpp"],
            "video": ["vlc", "mpv", "obs-studio", "kdenlive"],
            "image": ["gimp", "inkscape", "krita", "darktable"],
            "office": ["libreoffice", "onlyoffice-bin", "wpsoffice"],
            "games": ["steam", "lutris", "wine", "playonlinux"],
            "system": ["htop", "btop", "neofetch", "tree", "ncdu"],
        }
        
        # Find matching suggestions
        description_lower = description.lower()
        matched = []
        
        for category, packages in suggestions.items():
            if category in description_lower:
                matched.extend(packages)
        
        # Also check individual package names
        for category, packages in suggestions.items():
            for pkg in packages:
                if pkg.lower() in description_lower or description_lower in pkg.lower():
                    if pkg not in matched:
                        matched.append(pkg)
        
        return matched[:5]  # Return top 5 suggestions
    
    def validate_config(self, config_content: str) -> Dict[str, Any]:
        """
        Validate a configuration
        
        Args:
            config_content: Configuration to validate
            
        Returns:
            Validation results
        """
        valid, errors = self.modifier.validate_syntax(config_content)
        
        return {
            "valid": valid,
            "errors": errors,
            "warnings": []  # Could add warnings for best practices
        }


# Integration with main system
def handle_config_modification_request(request: str) -> Dict[str, Any]:
    """
    Handle a configuration modification request from the user
    
    Args:
        request: Natural language request
        
    Returns:
        Result of the operation
    """
    generator = ConfigGenerator()
    
    # Parse the request (simplified)
    request_lower = request.lower()
    
    if "install" in request_lower:
        # Extract package name (simplified)
        words = request.split()
        for i, word in enumerate(words):
            if word.lower() == "install" and i + 1 < len(words):
                package = words[i + 1]
                return generator.add_package(package, dry_run=True)
    
    elif "enable" in request_lower:
        # Extract service name
        if "docker" in request_lower:
            return generator.add_service("docker", enable=True, dry_run=True)
        elif "ssh" in request_lower or "openssh" in request_lower:
            return generator.add_service("openssh", enable=True, dry_run=True)
    
    elif "analyze" in request_lower or "check" in request_lower:
        return generator.analyze_current_config()
    
    return {
        "success": False,
        "error": "Could not understand request",
        "suggestion": "Try: 'install firefox' or 'enable docker'"
    }


if __name__ == "__main__":
    # Test the generator
    print("🧪 Testing Configuration Generator with Safe Modifications\n")
    
    generator = ConfigGenerator()
    
    # Test template generation
    print("📝 Generating minimal configuration:")
    config = generator.generate_config("minimal", hostname="test-nixos", username="testuser")
    print(config[:200] + "...")
    
    # Test package suggestions
    print("\n💡 Package suggestions for 'text editor':")
    suggestions = generator.suggest_packages("text editor")
    for pkg in suggestions:
        print(f"   - {pkg}")
    
    # Test request handling
    print("\n🎯 Handling request: 'install htop'")
    result = handle_config_modification_request("install htop")
    print(f"   Success: {result.get('success')}")
    print(f"   Message: {result.get('message')}")