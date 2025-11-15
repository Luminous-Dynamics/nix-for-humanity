#!/usr/bin/env python3
"""
NixOS Configuration Generator
Generates complete NixOS configurations from natural language descriptions
"""

import re
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ServiceConfig:
    """Service configuration"""

    name: str
    enable: bool = True
    settings: dict[str, Any] = None
    packages: list[str] = None


@dataclass
class UserConfig:
    """User configuration"""

    name: str
    description: str = ""
    groups: list[str] = None
    shell: str = "bash"
    home: Optional[str] = None
    packages: list[str] = None


class ConfigGenerator:
    """
    Generates NixOS configurations from high-level descriptions
    """

    def __init__(self):
        """Initialize configuration generator"""
        self.templates = self.load_templates()
        self.services_db = self.load_services_database()

    def load_templates(self) -> dict[str, str]:
        """Load configuration templates"""
        return {
            "base": """{{ config, pkgs, ... }}:

{{
  imports = [
    ./hardware-configuration.nix
{imports}
  ];

  # Boot loader
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # Networking
  networking.hostName = "{hostname}";
  networking.networkmanager.enable = true;

  # Time zone and localization
  time.timeZone = "{timezone}";
  i18n.defaultLocale = "{locale}";

  # System packages
  environment.systemPackages = with pkgs; [
{packages}
  ];

{services}

{users}

{extra}

  # System version
  system.stateVersion = "{state_version}";
}}""",
            "service": """  # {service_description}
  services.{service_name} = {{
    enable = true;
{service_settings}
  }};""",
            "user": """  users.users.{username} = {{
    isNormalUser = true;
    description = "{description}";
    extraGroups = [ {groups} ];
    shell = pkgs.{shell};
{user_extra}
  }};""",
            "desktop_gnome": """  # Enable GNOME Desktop
  services.xserver.enable = true;
  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;

  # GNOME packages
  environment.systemPackages = with pkgs; [
    gnome.gnome-tweaks
    gnome.gnome-terminal
    gnomeExtensions.appindicator
  ];""",
            "desktop_kde": """  # Enable KDE Plasma Desktop
  services.xserver.enable = true;
  services.xserver.displayManager.sddm.enable = true;
  services.xserver.desktopManager.plasma5.enable = true;

  # KDE packages
  environment.systemPackages = with pkgs; [
    kate
    konsole
    dolphin
    ark
  ];""",
            "development": """  # Development environment
  environment.systemPackages = with pkgs; [
    # Version control
    git
    gh

    # Editors
    vim
    neovim
    vscode

    # Languages
    python3
    nodejs
    rustc
    cargo
    go

    # Build tools
    gnumake
    cmake
    gcc

    # Containers
    docker
    docker-compose

    # Utils
    curl
    wget
    jq
    ripgrep
    fd
    bat
    htop
  ];

  # Enable Docker
  virtualisation.docker.enable = true;""",
            "gaming": """  # Gaming configuration
  programs.steam = {
    enable = true;
    remotePlay.openFirewall = true;
    dedicatedServer.openFirewall = true;
  };

  # Graphics drivers
  hardware.opengl = {
    enable = true;
    driSupport = true;
    driSupport32Bit = true;
  };

  # Gaming packages
  environment.systemPackages = with pkgs; [
    lutris
    wine
    winetricks
    discord
  ];""",
            "server": """  # Server configuration
  # SSH
  services.openssh = {
    enable = true;
    settings = {
      PermitRootLogin = "no";
      PasswordAuthentication = false;
    };
  };

  # Firewall
  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 22 {ports} ];
  };

  # Fail2ban
  services.fail2ban.enable = true;""",
        }

    def load_services_database(self) -> dict[str, dict]:
        """Load database of service configurations"""
        return {
            "nginx": {
                "package": "nginx",
                "settings": """    virtualHosts."{domain}" = {{
      enableACME = true;
      forceSSL = true;
      root = "{webroot}";
    }};""",
            },
            "postgresql": {
                "package": "postgresql",
                "settings": """    ensureDatabases = [ "{dbname}" ];
    ensureUsers = [
      {{
        name = "{dbuser}";
        ensurePermissions = {{
          "DATABASE {dbname}" = "ALL PRIVILEGES";
        }};
      }}
    ];""",
            },
            "docker": {
                "package": "docker",
                "module": "virtualisation.docker",
                "settings": """    enableOnBoot = true;
    autoPrune.enable = true;""",
            },
            "syncthing": {
                "package": "syncthing",
                "settings": """    user = "{user}";
    dataDir = "/home/{user}/Sync";
    configDir = "/home/{user}/.config/syncthing";""",
            },
            "jellyfin": {
                "package": "jellyfin",
                "settings": """    openFirewall = true;""",
            },
            "nextcloud": {
                "package": "nextcloud",
                "settings": """    hostName = "{domain}";
    config = {{
      dbtype = "pgsql";
      adminpassFile = "/var/lib/nextcloud/admin-pass";
    }};""",
            },
            "grafana": {
                "package": "grafana",
                "settings": """    addr = "0.0.0.0";
    port = 3000;""",
            },
            "prometheus": {
                "package": "prometheus",
                "settings": """    port = 9090;
    scrapeConfigs = [
      {{
        job_name = "node";
        static_configs = [
          {{ targets = [ "localhost:9100" ]; }}
        ];
      }}
    ];""",
            },
        }

    def parse_requirements(self, description: str) -> dict[str, Any]:
        """
        Parse natural language requirements into configuration elements

        Args:
            description: Natural language description

        Returns:
            Parsed configuration requirements
        """
        requirements = {
            "hostname": "nixos",
            "timezone": "UTC",
            "locale": "en_US.UTF-8",
            "packages": [],
            "services": [],
            "users": [],
            "desktop": None,
            "features": [],
        }

        description_lower = description.lower()

        # Detect hostname
        hostname_match = re.search(r"hostname[:\s]+(\S+)", description_lower)
        if hostname_match:
            requirements["hostname"] = hostname_match.group(1)

        # Detect desktop environment
        if any(de in description_lower for de in ["gnome", "gtk"]):
            requirements["desktop"] = "gnome"
        elif any(de in description_lower for de in ["kde", "plasma"]):
            requirements["desktop"] = "kde"
        elif "xfce" in description_lower:
            requirements["desktop"] = "xfce"
        elif "desktop" in description_lower:
            requirements["desktop"] = "gnome"  # Default to GNOME

        # Detect features
        if any(
            word in description_lower for word in ["develop", "programming", "coding"]
        ):
            requirements["features"].append("development")
        if any(word in description_lower for word in ["gaming", "steam", "games"]):
            requirements["features"].append("gaming")
        if any(word in description_lower for word in ["server", "headless", "ssh"]):
            requirements["features"].append("server")
        if any(word in description_lower for word in ["media", "plex", "jellyfin"]):
            requirements["features"].append("media")

        # Detect services
        for service in self.services_db.keys():
            if service in description_lower:
                requirements["services"].append(service)

        # Detect common packages
        common_packages = [
            "firefox",
            "chrome",
            "chromium",
            "brave",
            "vim",
            "neovim",
            "emacs",
            "vscode",
            "git",
            "docker",
            "python",
            "nodejs",
            "htop",
            "tmux",
            "zsh",
            "fish",
        ]

        for package in common_packages:
            if package in description_lower:
                requirements["packages"].append(package)

        # Detect users
        user_match = re.findall(r"user[:\s]+(\w+)", description_lower)
        for username in user_match:
            requirements["users"].append(
                {"name": username, "groups": ["wheel", "networkmanager"]}
            )

        return requirements

    def generate_config(
        self,
        description: str,
        hostname: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> str:
        """
        Generate NixOS configuration from description

        Args:
            description: Natural language description
            hostname: Override hostname
            timezone: Override timezone

        Returns:
            Generated configuration.nix content
        """
        # Parse requirements
        requirements = self.parse_requirements(description)

        # Override if provided
        if hostname:
            requirements["hostname"] = hostname
        if timezone:
            requirements["timezone"] = timezone

        # Build configuration sections
        imports = []
        packages = set(["wget", "vim", "git"])  # Base packages
        services = []
        users = []
        extra = []

        # Add desktop configuration
        if requirements["desktop"]:
            if requirements["desktop"] == "gnome":
                extra.append(self.templates["desktop_gnome"])
            elif requirements["desktop"] == "kde":
                extra.append(self.templates["desktop_kde"])

        # Add features
        for feature in requirements["features"]:
            if feature == "development":
                extra.append(self.templates["development"])
            elif feature == "gaming":
                extra.append(self.templates["gaming"])
            elif feature == "server":
                ports = []
                if "nginx" in requirements["services"]:
                    ports.extend(["80", "443"])
                extra.append(
                    self.templates["server"].replace("{ports}", " ".join(ports))
                )

        # Add services
        for service_name in requirements["services"]:
            if service_name in self.services_db:
                service_info = self.services_db[service_name]

                # Add service package
                if "package" in service_info:
                    packages.add(service_info["package"])

                # Build service configuration
                service_config = self.templates["service"].format(
                    service_description=f"{service_name.title()} Service",
                    service_name=service_info.get("module", service_name),
                    service_settings=service_info.get(
                        "settings", "    # Additional settings here"
                    ),
                )

                # Replace placeholders with defaults
                service_config = service_config.replace("{domain}", "example.com")
                service_config = service_config.replace("{webroot}", "/var/www")
                service_config = service_config.replace("{dbname}", "mydb")
                service_config = service_config.replace("{dbuser}", "dbuser")
                service_config = service_config.replace("{user}", "user")

                services.append(service_config)

        # Add packages from requirements
        packages.update(requirements["packages"])

        # Add users
        for user_info in requirements["users"]:
            user_config = self.templates["user"].format(
                username=user_info["name"],
                description=user_info.get("description", f"{user_info['name']} user"),
                groups='"' + '" "'.join(user_info.get("groups", ["wheel"])) + '"',
                shell=user_info.get("shell", "bash"),
                user_extra="",
            )
            users.append(user_config)

        # Default user if none specified
        if not users:
            users.append(
                self.templates["user"].format(
                    username="user",
                    description="Default user",
                    groups='"wheel" "networkmanager"',
                    shell="bash",
                    user_extra="",
                )
            )

        # Format packages
        packages_str = "\n".join(f"    {pkg}" for pkg in sorted(packages))

        # Build final configuration
        config = self.templates["base"].format(
            imports="\n".join(f"    {imp}" for imp in imports) if imports else "",
            hostname=requirements["hostname"],
            timezone=requirements["timezone"],
            locale=requirements["locale"],
            packages=packages_str,
            services="\n\n".join(services),
            users="\n\n".join(users),
            extra="\n\n".join(extra),
            state_version="24.05",
        )

        # Clean up empty sections
        config = re.sub(r"\n{3,}", "\n\n", config)

        return config

    def generate_home_manager_config(self, username: str, description: str) -> str:
        """
        Generate Home Manager configuration

        Args:
            username: User name
            description: Configuration description

        Returns:
            Generated home.nix content
        """
        template = """{ config, pkgs, ... }:

{
  # Home Manager configuration for {username}
  home.username = "{username}";
  home.homeDirectory = "/home/{username}";
  home.stateVersion = "24.05";

  # Packages
  home.packages = with pkgs; [
{packages}
  ];

  # Program configurations
{programs}

  # Services
{services}

  # Session variables
  home.sessionVariables = {
    EDITOR = "{editor}";
  };
}"""

        # Parse requirements
        packages = []
        programs = []
        editor = "vim"

        description_lower = description.lower()

        # Detect editor preference
        if "neovim" in description_lower or "nvim" in description_lower:
            editor = "nvim"
            programs.append(
                """  programs.neovim = {
    enable = true;
    viAlias = true;
    vimAlias = true;
  };"""
            )
        elif "emacs" in description_lower:
            editor = "emacs"
            programs.append(
                """  programs.emacs = {
    enable = true;
  };"""
            )
        elif "vscode" in description_lower:
            packages.append("vscode")
            editor = "code"

        # Detect shell
        if "zsh" in description_lower:
            programs.append(
                """  programs.zsh = {
    enable = true;
    enableAutosuggestions = true;
    enableCompletion = true;
    oh-my-zsh = {
      enable = true;
      theme = "robbyrussell";
    };
  };"""
            )
        elif "fish" in description_lower:
            programs.append(
                """  programs.fish = {
    enable = true;
  };"""
            )

        # Detect git
        if "git" in description_lower:
            programs.append(
                """  programs.git = {
    enable = true;
    userName = "Your Name";
    userEmail = "you@example.com";
  };"""
            )

        # Detect terminal
        if "alacritty" in description_lower:
            programs.append(
                """  programs.alacritty = {
    enable = true;
  };"""
            )
        elif "kitty" in description_lower:
            programs.append(
                """  programs.kitty = {
    enable = true;
  };"""
            )

        # Format
        packages_str = (
            "\n".join(f"    {pkg}" for pkg in packages)
            if packages
            else "    # Add packages here"
        )
        programs_str = (
            "\n\n".join(programs) if programs else "  # Program configurations here"
        )

        return template.format(
            username=username,
            packages=packages_str,
            programs=programs_str,
            services="  # Services here",
            editor=editor,
        )

    def generate_flake(self, description: str) -> str:
        """
        Generate a flake.nix configuration

        Args:
            description: Project description

        Returns:
            Generated flake.nix content
        """
        template = """{
  description = "{description}";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
{packages}
          ];

          shellHook = ''
            echo "Welcome to {project_name} development environment"
{shell_hook}
          '';
        };

        packages.default = pkgs.stdenv.mkDerivation {
          pname = "{project_name}";
          version = "0.1.0";
          src = ./.;

          buildInputs = with pkgs; [
{build_inputs}
          ];
        };
      }
    );
}"""

        # Parse project type
        description_lower = description.lower()
        packages = []
        build_inputs = []
        shell_hook = ""
        project_name = "my-project"

        # Detect project type
        if "python" in description_lower:
            packages.extend(
                ["python3", "python3Packages.pip", "python3Packages.virtualenv"]
            )
            shell_hook = """            python -m venv .venv
            source .venv/bin/activate"""
        elif "node" in description_lower or "javascript" in description_lower:
            packages.extend(["nodejs", "yarn"])
            shell_hook = "            npm install"
        elif "rust" in description_lower:
            packages.extend(["rustc", "cargo", "rustfmt", "clippy"])
            shell_hook = "            cargo build"
        elif "go" in description_lower or "golang" in description_lower:
            packages.extend(["go", "gopls"])
            shell_hook = "            go mod download"

        # Add common tools
        packages.extend(["git", "gnumake"])

        # Format
        packages_str = "\n".join(f"            {pkg}" for pkg in packages)
        build_inputs_str = (
            "\n".join(f"            {pkg}" for pkg in build_inputs)
            if build_inputs
            else "            # Build dependencies"
        )

        return template.format(
            description=description,
            project_name=project_name,
            packages=packages_str,
            build_inputs=build_inputs_str,
            shell_hook=shell_hook,
        )

    def validate_config(self, config: str) -> tuple[bool, list[str]]:
        """
        Validate a NixOS configuration

        Args:
            config: Configuration content

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # Check basic structure
        if "{ config, pkgs, ... }:" not in config:
            errors.append("Missing function header")

        if "system.stateVersion" not in config:
            errors.append("Missing system.stateVersion")

        # Check for common issues
        if config.count("{") != config.count("}"):
            errors.append("Mismatched braces")

        if config.count("[") != config.count("]"):
            errors.append("Mismatched brackets")

        if config.count('"') % 2 != 0:
            errors.append("Mismatched quotes")

        # Check for undefined variables
        undefined_pattern = r"\b[a-z][a-zA-Z0-9]*\b(?!\s*=)(?!\s*:)(?!\s*\.)(?!\s*\{)"
        # This is simplified - real validation would use nix-2-5 secondsiate

        return len(errors) == 0, errors


# Example usage
if __name__ == "__main__":
    generator = ConfigGenerator()

    # Example 1: Desktop system
    print("=== Desktop Configuration ===")
    desktop_config = generator.generate_config(
        "Create a desktop system with GNOME, development tools, Firefox, and user john"
    )
    print(desktop_config[:500] + "...")

    # Example 2: Server configuration
    print("\n=== Server Configuration ===")
    server_config = generator.generate_config(
        "Setup a web server with nginx, postgresql, docker, and SSH access"
    )
    print(server_config[:500] + "...")

    # Example 3: Development flake
    print("\n=== Development Flake ===")
    flake = generator.generate_flake(
        "Python development environment with data science tools"
    )
    print(flake[:500] + "...")

    # Validate
    is_valid, errors = generator.validate_config(desktop_config)
    print("\n=== Validation ===")
    print(f"Valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
