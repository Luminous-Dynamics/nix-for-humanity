"""
Config Generator - Generate REAL NixOS configurations

This is where we provide massive value - turning natural language
into actual working NixOS configurations.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from textwrap import dedent
import logging

logger = logging.getLogger(__name__)


@dataclass
class NixConfig:
    """Represents a NixOS configuration"""
    description: str
    config: str
    packages: List[str]
    services: Dict[str, Dict]
    
    def to_nix(self) -> str:
        """Convert to actual configuration.nix format"""
        return self.config


class ConfigGenerator:
    """
    Generate real, working NixOS configurations from natural language.
    
    This is a killer feature - users describe what they want,
    we generate the exact configuration they need.
    """
    
    def __init__(self):
        """Initialize with configuration templates"""
        self.templates = self._load_templates()
    
    def generate(self, request: str) -> NixConfig:
        """
        Generate NixOS configuration from natural language request.
        
        Examples:
            "I need a web server" -> nginx configuration
            "Setup PostgreSQL" -> PostgreSQL with good defaults
            "Python development environment" -> Python with tools
        """
        request_lower = request.lower()
        
        # Web server requests
        if any(word in request_lower for word in ["web server", "nginx", "apache", "http server"]):
            return self._generate_web_server(request)
        
        # Database requests
        if any(word in request_lower for word in ["database", "postgresql", "mysql", "postgres"]):
            return self._generate_database(request)
        
        # Development environment requests
        if any(word in request_lower for word in ["development", "dev environment", "programming"]):
            return self._generate_dev_environment(request)
        
        # Docker/containers
        if any(word in request_lower for word in ["docker", "container", "podman"]):
            return self._generate_docker(request)
        
        # Desktop environment
        if any(word in request_lower for word in ["desktop", "gnome", "kde", "xfce"]):
            return self._generate_desktop(request)
        
        # Default: basic system
        return self._generate_basic(request)
    
    def _generate_web_server(self, request: str) -> NixConfig:
        """Generate web server configuration"""
        
        # Check for SSL requirement
        with_ssl = "ssl" in request.lower() or "https" in request.lower()
        
        if with_ssl:
            config = dedent("""
                # Web server with SSL
                { config, pkgs, ... }:
                
                {
                  # Enable nginx web server
                  services.nginx = {
                    enable = true;
                    
                    # Recommended settings
                    recommendedGzipSettings = true;
                    recommendedOptimisation = true;
                    recommendedProxySettings = true;
                    recommendedTlsSettings = true;
                    
                    # Virtual hosts
                    virtualHosts."example.com" = {
                      enableACME = true;  # Automatic SSL with Let's Encrypt
                      forceSSL = true;
                      
                      locations."/" = {
                        root = "/var/www/example.com";
                        index = "index.html index.htm";
                      };
                    };
                  };
                  
                  # Open firewall for web traffic
                  networking.firewall.allowedTCPPorts = [ 80 443 ];
                  
                  # Let's Encrypt settings
                  security.acme = {
                    acceptTerms = true;
                    defaults.email = "admin@example.com";  # Change this!
                  };
                  
                  # Install useful web tools
                  environment.systemPackages = with pkgs; [
                    curl
                    wget
                    htop
                  ];
                }
            """).strip()
        else:
            config = dedent("""
                # Basic web server
                { config, pkgs, ... }:
                
                {
                  # Enable nginx web server
                  services.nginx = {
                    enable = true;
                    
                    # Virtual host
                    virtualHosts."localhost" = {
                      locations."/" = {
                        root = "/var/www";
                        index = "index.html index.htm";
                      };
                    };
                  };
                  
                  # Open firewall for web traffic
                  networking.firewall.allowedTCPPorts = [ 80 ];
                  
                  # Install useful web tools
                  environment.systemPackages = with pkgs; [
                    curl
                    wget
                  ];
                }
            """).strip()
        
        return NixConfig(
            description="Web server configuration" + (" with SSL" if with_ssl else ""),
            config=config,
            packages=["nginx", "curl", "wget"],
            services={"nginx": {"enable": True}}
        )
    
    def _generate_database(self, request: str) -> NixConfig:
        """Generate database configuration"""
        
        # Determine which database
        if "mysql" in request.lower() or "mariadb" in request.lower():
            db_type = "mysql"
        else:
            db_type = "postgresql"  # Default to PostgreSQL
        
        if db_type == "postgresql":
            config = dedent("""
                # PostgreSQL database server
                { config, pkgs, ... }:
                
                {
                  # Enable PostgreSQL
                  services.postgresql = {
                    enable = true;
                    package = pkgs.postgresql_15;
                    
                    # Good defaults for development
                    settings = {
                      shared_buffers = "256MB";
                      effective_cache_size = "1GB";
                      maintenance_work_mem = "64MB";
                      checkpoint_completion_target = 0.9;
                      wal_buffers = "16MB";
                      default_statistics_target = 100;
                      random_page_cost = 1.1;
                    };
                    
                    # Enable local connections
                    authentication = pkgs.lib.mkOverride 10 ''
                      # TYPE  DATABASE  USER  ADDRESS     METHOD
                      local   all       all               trust
                      host    all       all   127.0.0.1/32  trust
                      host    all       all   ::1/128     trust
                    '';
                    
                    # Create a database
                    initialScript = pkgs.writeText "backend-initScript" ''
                      CREATE USER myapp WITH PASSWORD 'myapp';
                      CREATE DATABASE myapp;
                      GRANT ALL PRIVILEGES ON DATABASE myapp TO myapp;
                    '';
                  };
                  
                  # PostgreSQL tools
                  environment.systemPackages = with pkgs; [
                    postgresql_15
                    pgcli  # Better PostgreSQL CLI
                  ];
                }
            """).strip()
            
            return NixConfig(
                description="PostgreSQL database configuration",
                config=config,
                packages=["postgresql_15", "pgcli"],
                services={"postgresql": {"enable": True, "package": "postgresql_15"}}
            )
        else:
            config = dedent("""
                # MySQL/MariaDB database server
                { config, pkgs, ... }:
                
                {
                  # Enable MariaDB (MySQL compatible)
                  services.mysql = {
                    enable = true;
                    package = pkgs.mariadb;
                    
                    # Good defaults
                    settings = {
                      mysqld = {
                        innodb_buffer_pool_size = "256M";
                        innodb_log_file_size = "64M";
                        max_connections = 100;
                      };
                    };
                    
                    # Initial databases
                    initialDatabases = [
                      { name = "myapp"; }
                    ];
                    
                    # Initial users
                    ensureUsers = [
                      {
                        name = "myapp";
                        ensurePermissions = {
                          "myapp.*" = "ALL PRIVILEGES";
                        };
                      }
                    ];
                  };
                  
                  # MySQL tools
                  environment.systemPackages = with pkgs; [
                    mariadb
                    mycli  # Better MySQL CLI
                  ];
                }
            """).strip()
            
            return NixConfig(
                description="MySQL/MariaDB database configuration",
                config=config,
                packages=["mariadb", "mycli"],
                services={"mysql": {"enable": True, "package": "mariadb"}}
            )
    
    def _generate_dev_environment(self, request: str) -> NixConfig:
        """Generate development environment configuration"""
        
        # Detect language
        languages = []
        if "python" in request.lower():
            languages.append("python")
        if "rust" in request.lower():
            languages.append("rust")
        if "node" in request.lower() or "javascript" in request.lower():
            languages.append("nodejs")
        if "go" in request.lower() or "golang" in request.lower():
            languages.append("go")
        
        # Default to Python if no specific language
        if not languages:
            languages = ["python"]
        
        config = dedent("""
            # Development environment
            { config, pkgs, ... }:
            
            {
              # Development tools
              environment.systemPackages = with pkgs; [
                # Version control
                git
                git-lfs
                
                # Editors
                vim
                neovim
                
                # Build tools
                gnumake
                gcc
                pkg-config
                
                # Container tools
                docker
                docker-compose
        """).strip()
        
        packages = ["git", "vim", "neovim", "gnumake", "gcc", "docker"]
        
        # Add language-specific tools
        if "python" in languages:
            config += """
                
                # Python development
                python311
                python311Packages.pip
                python311Packages.virtualenv
                python311Packages.ipython
                python311Packages.black
                python311Packages.pytest
                poetry"""
            packages.extend(["python311", "poetry"])
        
        if "rust" in languages:
            config += """
                
                # Rust development
                rustc
                cargo
                rustfmt
                clippy
                rust-analyzer"""
            packages.extend(["rustc", "cargo"])
        
        if "nodejs" in languages:
            config += """
                
                # Node.js development
                nodejs_20
                nodePackages.npm
                nodePackages.yarn
                nodePackages.typescript
                nodePackages.prettier"""
            packages.extend(["nodejs_20", "yarn"])
        
        if "go" in languages:
            config += """
                
                # Go development
                go
                gopls
                gotools"""
            packages.extend(["go", "gopls"])
        
        config += """
              ];
              
              # Enable Docker
              virtualisation.docker.enable = true;
              
              # Add user to docker group (replace 'user' with your username)
              users.users.user.extraGroups = [ "docker" ];
            }"""
        
        return NixConfig(
            description=f"Development environment for {', '.join(languages)}",
            config=config,
            packages=packages,
            services={"docker": {"enable": True}}
        )
    
    def _generate_docker(self, request: str) -> NixConfig:
        """Generate Docker/container configuration"""
        
        config = dedent("""
            # Docker container configuration
            { config, pkgs, ... }:
            
            {
              # Enable Docker
              virtualisation.docker = {
                enable = true;
                autoPrune = {
                  enable = true;
                  dates = "weekly";
                };
              };
              
              # Container tools
              environment.systemPackages = with pkgs; [
                docker
                docker-compose
                lazydocker  # TUI for docker
                dive        # Explore docker images
                skopeo      # Work with container images
              ];
              
              # Add your user to docker group (replace 'user' with your username)
              users.users.user.extraGroups = [ "docker" ];
              
              # Optional: Enable podman as docker alternative
              # virtualisation.podman = {
              #   enable = true;
              #   dockerCompat = true;
              # };
            }
        """).strip()
        
        return NixConfig(
            description="Docker container environment",
            config=config,
            packages=["docker", "docker-compose", "lazydocker", "dive"],
            services={"docker": {"enable": True, "autoPrune": True}}
        )
    
    def _generate_desktop(self, request: str) -> NixConfig:
        """Generate desktop environment configuration"""
        
        # Detect desktop environment
        if "kde" in request.lower() or "plasma" in request.lower():
            de = "kde"
        elif "gnome" in request.lower():
            de = "gnome"
        elif "xfce" in request.lower():
            de = "xfce"
        else:
            de = "gnome"  # Default
        
        configs = {
            "gnome": dedent("""
                # GNOME desktop environment
                { config, pkgs, ... }:
                
                {
                  # Enable X11 and GNOME
                  services.xserver = {
                    enable = true;
                    displayManager.gdm.enable = true;
                    desktopManager.gnome.enable = true;
                  };
                  
                  # GNOME apps and utilities
                  environment.systemPackages = with pkgs; [
                    gnome.gnome-tweaks
                    gnome.gnome-terminal
                    gnomeExtensions.dash-to-dock
                    gnomeExtensions.appindicator
                  ];
                  
                  # Enable sound
                  sound.enable = true;
                  hardware.pulseaudio.enable = true;
                }
            """).strip(),
            
            "kde": dedent("""
                # KDE Plasma desktop environment
                { config, pkgs, ... }:
                
                {
                  # Enable X11 and KDE
                  services.xserver = {
                    enable = true;
                    displayManager.sddm.enable = true;
                    desktopManager.plasma5.enable = true;
                  };
                  
                  # KDE apps and utilities
                  environment.systemPackages = with pkgs; [
                    kate
                    konsole
                    dolphin
                    ark
                    spectacle
                  ];
                  
                  # Enable sound
                  sound.enable = true;
                  hardware.pulseaudio.enable = true;
                }
            """).strip(),
            
            "xfce": dedent("""
                # XFCE desktop environment
                { config, pkgs, ... }:
                
                {
                  # Enable X11 and XFCE
                  services.xserver = {
                    enable = true;
                    displayManager.lightdm.enable = true;
                    desktopManager.xfce.enable = true;
                  };
                  
                  # XFCE apps and utilities
                  environment.systemPackages = with pkgs; [
                    xfce.xfce4-terminal
                    xfce.thunar
                    xfce.xfce4-screenshooter
                    xfce.xfce4-taskmanager
                  ];
                  
                  # Enable sound
                  sound.enable = true;
                  hardware.pulseaudio.enable = true;
                }
            """).strip()
        }
        
        return NixConfig(
            description=f"{de.upper()} desktop environment",
            config=configs[de],
            packages=[de],
            services={"xserver": {"enable": True}, "pulseaudio": {"enable": True}}
        )
    
    def _generate_basic(self, request: str) -> NixConfig:
        """Generate basic system configuration"""
        
        config = dedent("""
            # Basic NixOS configuration
            { config, pkgs, ... }:
            
            {
              # Basic system packages
              environment.systemPackages = with pkgs; [
                # Editors
                vim
                nano
                
                # System tools
                htop
                tree
                wget
                curl
                git
                
                # Archive tools
                zip
                unzip
                
                # Network tools
                nmap
                traceroute
              ];
              
              # Enable SSH
              services.openssh.enable = true;
              
              # Enable firewall
              networking.firewall.enable = true;
            }
        """).strip()
        
        return NixConfig(
            description="Basic system configuration",
            config=config,
            packages=["vim", "htop", "git", "wget", "curl"],
            services={"openssh": {"enable": True}}
        )
    
    def _load_templates(self) -> Dict:
        """Load configuration templates"""
        # This could load from files in the future
        return {}