"""
Configuration Generator for NixOS
Transforms natural language requests into complete NixOS configurations
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent, indent

@dataclass
class ConfigRequest:
    """Represents a configuration generation request"""
    config_type: str  # nginx, shell, service, etc.
    description: str
    requirements: List[str]
    context: Dict[str, Any]

@dataclass 
class GeneratedConfig:
    """Represents a generated configuration"""
    config_type: str
    nix_code: str
    explanation: str
    dependencies: List[str]
    usage_instructions: str
    test_commands: List[str]

class NixOSConfigGenerator:
    """
    Generates NixOS configurations from natural language descriptions
    """
    
    def __init__(self):
        # Configuration templates for common services
        self.templates = {
            "nginx": self._nginx_template,
            "postgresql": self._postgresql_template,
            "docker": self._docker_template,
            "development": self._dev_env_template,
            "systemd": self._systemd_service_template,
            "firewall": self._firewall_template,
            "user": self._user_template,
            "shell": self._shell_env_template,
        }
        
        # Common configuration patterns
        self.patterns = {
            r"nginx.*ssl|https.*nginx|web.*server.*ssl": "nginx_ssl",
            r"nginx.*php|php.*nginx": "nginx_php",
            r"postgres|postgresql|database": "postgresql",
            r"docker|container": "docker",
            r"rust.*dev|rust.*environment": "rust_dev",
            r"python.*dev|python.*environment": "python_dev",
            r"node|nodejs|javascript.*dev": "node_dev",
            r"systemd.*service|background.*service": "systemd",
            r"firewall|ports?|network.*security": "firewall",
            r"user|account": "user",
            r"shell\.nix|dev.*shell|nix.*shell": "shell",
        }
    
    def generate_config(self, request: str) -> GeneratedConfig:
        """
        Main entry point - generates configuration from natural language
        """
        # Parse the request
        config_request = self._parse_request(request)
        
        # Determine configuration type
        config_type = self._determine_config_type(request, config_request)
        
        # Generate the appropriate configuration
        if config_type in self.templates:
            return self.templates[config_type](config_request)
        else:
            return self._generic_config(config_request)
    
    def _parse_request(self, request: str) -> ConfigRequest:
        """Parse natural language request into structured format"""
        # Extract requirements
        requirements = []
        
        # Look for common requirements
        if "ssl" in request.lower() or "https" in request.lower():
            requirements.append("ssl")
        if "php" in request.lower():
            requirements.append("php")
        if "python" in request.lower():
            requirements.append("python")
        if "rust" in request.lower():
            requirements.append("rust")
        if "node" in request.lower() or "nodejs" in request.lower():
            requirements.append("nodejs")
        if "database" in request.lower():
            requirements.append("database")
        
        # Extract context (domain names, ports, etc.)
        context = {}
        
        # Look for domain names
        domain_match = re.search(r"(?:for|domain|host)\s+([a-z0-9.-]+\.[a-z]{2,})", request.lower())
        if domain_match:
            context["domain"] = domain_match.group(1)
        
        # Look for port numbers
        port_match = re.search(r"port\s+(\d+)", request.lower())
        if port_match:
            context["port"] = int(port_match.group(1))
        
        # Look for usernames
        user_match = re.search(r"user\s+([a-z0-9_-]+)", request.lower())
        if user_match:
            context["user"] = user_match.group(1)
        
        return ConfigRequest(
            config_type="unknown",
            description=request,
            requirements=requirements,
            context=context
        )
    
    def _determine_config_type(self, request: str, parsed: ConfigRequest) -> str:
        """Determine what type of configuration to generate"""
        request_lower = request.lower()
        
        # Check patterns
        for pattern, config_type in self.patterns.items():
            if re.search(pattern, request_lower):
                return config_type.split("_")[0]  # Get base type
        
        # Default to development environment if unclear
        if any(lang in request_lower for lang in ["rust", "python", "node", "go", "java"]):
            return "development"
        
        return "generic"
    
    def _nginx_template(self, req: ConfigRequest) -> GeneratedConfig:
        """Generate nginx configuration"""
        domain = req.context.get("domain", "example.com")
        has_ssl = "ssl" in req.requirements or "https" in req.description.lower()
        has_php = "php" in req.requirements or "php" in req.description.lower()
        
        config = dedent(f"""
        # Nginx web server configuration
        services.nginx = {{
          enable = true;
          recommendedProxySettings = true;
          recommendedTlsSettings = true;
          recommendedOptimisation = true;
          recommendedGzipSettings = true;
          
          virtualHosts."{domain}" = {{
            {f'''enableACME = true;
            forceSSL = true;''' if has_ssl else '# No SSL configured'}
            root = "/var/www/{domain}";
            
            {f'''locations."~ \\.php$" = {{
              extraConfig = \'\'\'
                fastcgi_pass unix:${{config.services.phpfpm.pools.www.socket}};
                fastcgi_index index.php;
              \'\'\';
            }};''' if has_php else ''}
            
            locations."/" = {{
              index = "index.html index.htm{' index.php' if has_php else ''}";
              tryFiles = "$uri $uri/ {'/index.php?$query_string' if has_php else '=404'}";
            }};
          }};
        }};
        
        {f'''# PHP-FPM configuration
        services.phpfpm.pools.www = {{
          user = "nginx";
          group = "nginx";
          settings = {{
            "listen.owner" = config.services.nginx.user;
            "pm" = "dynamic";
            "pm.max_children" = 32;
            "pm.start_servers" = 2;
            "pm.min_spare_servers" = 2;
            "pm.max_spare_servers" = 4;
            "pm.max_requests" = 500;
          }};
        }};''' if has_php else ''}
        
        {f'''# ACME (Let's Encrypt) configuration
        security.acme = {{
          acceptTerms = true;
          defaults.email = "admin@{domain}";
        }};''' if has_ssl else ''}
        
        # Firewall configuration
        networking.firewall.allowedTCPPorts = [ 80{' 443' if has_ssl else ''} ];
        """).strip()
        
        return GeneratedConfig(
            config_type="nginx",
            nix_code=config,
            explanation=f"Nginx web server configuration for {domain}" + 
                       (f" with SSL/HTTPS" if has_ssl else "") +
                       (f" and PHP support" if has_php else ""),
            dependencies=["nginx"] + (["certbot"] if has_ssl else []) + (["php"] if has_php else []),
            usage_instructions=dedent(f"""
                1. Add this configuration to /etc/nixos/configuration.nix
                2. Create the web root directory: sudo mkdir -p /var/www/{domain}
                3. Apply configuration: sudo nixos-rebuild switch
                4. {'Wait for SSL certificate generation (first time only)' if has_ssl else 'Access your site at http://' + domain}
            """).strip(),
            test_commands=[
                "sudo systemctl status nginx",
                f"curl -I {'https' if has_ssl else 'http'}://{domain}",
                "sudo nginx -t",
            ] + (["sudo systemctl status phpfpm-www"] if has_php else [])
        )
    
    def _postgresql_template(self, req: ConfigRequest) -> GeneratedConfig:
        """Generate PostgreSQL configuration"""
        db_name = req.context.get("database", "myapp")
        user = req.context.get("user", "myuser")
        
        config = dedent(f"""
        # PostgreSQL database configuration
        services.postgresql = {{
          enable = true;
          package = pkgs.postgresql_15;
          
          ensureDatabases = [ "{db_name}" ];
          ensureUsers = [
            {{
              name = "{user}";
              ensureDBOwnership = true;
            }}
          ];
          
          authentication = pkgs.lib.mkOverride 10 \'\'\'
            # TYPE  DATABASE        USER            ADDRESS                 METHOD
            local   all             all                                     trust
            host    all             all             127.0.0.1/32            trust
            host    all             all             ::1/128                 trust
          \'\'\';
          
          settings = {{
            shared_buffers = "256MB";
            max_connections = 100;
            log_statement = "all";
            log_destination = "stderr";
            logging_collector = true;
          }};
        }};
        
        # Backup configuration (optional)
        services.postgresqlBackup = {{
          enable = true;
          databases = [ "{db_name}" ];
          location = "/var/backup/postgresql";
          startAt = "03:00";
        }};
        """).strip()
        
        return GeneratedConfig(
            config_type="postgresql",
            nix_code=config,
            explanation=f"PostgreSQL database server with database '{db_name}' and user '{user}'",
            dependencies=["postgresql_15"],
            usage_instructions=dedent(f"""
                1. Add this configuration to /etc/nixos/configuration.nix
                2. Apply configuration: sudo nixos-rebuild switch
                3. Connect to database: psql -U {user} -d {db_name}
                4. Create tables and start using your database
            """).strip(),
            test_commands=[
                "sudo systemctl status postgresql",
                f"sudo -u postgres psql -c '\\l' | grep {db_name}",
                f"sudo -u postgres psql -d {db_name} -c '\\dt'",
            ]
        )
    
    def _docker_template(self, req: ConfigRequest) -> GeneratedConfig:
        """Generate Docker configuration"""
        user = req.context.get("user", "$USER")
        
        config = dedent(f"""
        # Docker container runtime configuration
        virtualisation.docker = {{
          enable = true;
          enableOnBoot = true;
          
          # Enable Docker daemon
          daemon.settings = {{
            data-root = "/var/lib/docker";
            log-driver = "json-file";
            log-opts = {{
              max-size = "10m";
              max-file = "3";
            }};
          }};
          
          # Prune old images automatically
          autoPrune = {{
            enable = true;
            dates = "weekly";
          }};
        }};
        
        # Add user to docker group
        users.users.{user} = {{
          extraGroups = [ "docker" ];
        }};
        
        # Docker Compose (optional)
        environment.systemPackages = with pkgs; [
          docker-compose
        ];
        """).strip()
        
        return GeneratedConfig(
            config_type="docker",
            nix_code=config,
            explanation=f"Docker container runtime with user '{user}' added to docker group",
            dependencies=["docker", "docker-compose"],
            usage_instructions=dedent(f"""
                1. Add this configuration to /etc/nixos/configuration.nix
                2. Apply configuration: sudo nixos-rebuild switch
                3. Log out and log back in for group changes to take effect
                4. Test Docker: docker run hello-world
            """).strip(),
            test_commands=[
                "sudo systemctl status docker",
                "docker version",
                "docker run hello-world",
                "docker ps",
            ]
        )
    
    def _dev_env_template(self, req: ConfigRequest) -> GeneratedConfig:
        """Generate development environment configuration"""
        lang = "generic"
        if "rust" in req.description.lower():
            lang = "rust"
        elif "python" in req.description.lower():
            lang = "python"
        elif "node" in req.description.lower() or "javascript" in req.description.lower():
            lang = "node"
        elif "go" in req.description.lower():
            lang = "go"
        
        configs = {
            "rust": self._rust_dev_config(),
            "python": self._python_dev_config(),
            "node": self._node_dev_config(),
            "go": self._go_dev_config(),
            "generic": self._generic_dev_config(),
        }
        
        return configs[lang]
    
    def _rust_dev_config(self) -> GeneratedConfig:
        """Generate Rust development environment"""
        config = dedent("""
        # Rust development environment
        { pkgs ? import <nixpkgs> {} }:
        
        pkgs.mkShell {
          buildInputs = with pkgs; [
            # Rust toolchain
            rustc
            cargo
            rustfmt
            rust-analyzer
            clippy
            
            # Build tools
            gcc
            pkg-config
            openssl.dev
            
            # Useful tools
            cargo-watch
            cargo-edit
            cargo-audit
            bacon  # Background rust code checker
            
            # Optional: for web development
            wasm-pack
            trunk
          ];
          
          # Environment variables
          RUST_BACKTRACE = 1;
          RUST_LOG = "debug";
          
          shellHook = ''
            echo "🦀 Rust development environment loaded!"
            echo "Rust version: $(rustc --version)"
            echo "Cargo version: $(cargo --version)"
            echo ""
            echo "Useful commands:"
            echo "  cargo init      - Create new project"
            echo "  cargo build     - Build project"
            echo "  cargo run       - Run project"
            echo "  cargo test      - Run tests"
            echo "  cargo watch     - Watch for changes"
            echo "  bacon           - Background code checker"
          '';
        }
        """).strip()
        
        return GeneratedConfig(
            config_type="shell",
            nix_code=config,
            explanation="Complete Rust development environment with toolchain and common tools",
            dependencies=["rustc", "cargo", "rust-analyzer"],
            usage_instructions=dedent("""
                1. Save this as shell.nix in your project directory
                2. Enter the environment: nix-shell
                3. Start developing with cargo commands
                4. Use 'cargo watch' for automatic rebuilds
            """).strip(),
            test_commands=[
                "nix-shell --run 'rustc --version'",
                "nix-shell --run 'cargo --version'",
                "nix-shell --run 'cargo init my_project'",
            ]
        )
    
    def _python_dev_config(self) -> GeneratedConfig:
        """Generate Python development environment"""
        config = dedent("""
        # Python development environment
        { pkgs ? import <nixpkgs> {} }:
        
        let
          pythonPackages = pkgs.python311Packages;
        in
        pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python and package manager
            python311
            pythonPackages.pip
            pythonPackages.virtualenv
            poetry
            
            # Development tools
            pythonPackages.black
            pythonPackages.flake8
            pythonPackages.pytest
            pythonPackages.mypy
            pythonPackages.ipython
            pythonPackages.jupyter
            
            # Common libraries
            pythonPackages.numpy
            pythonPackages.pandas
            pythonPackages.requests
            pythonPackages.pyyaml
            
            # Database
            pythonPackages.psycopg2
            pythonPackages.sqlalchemy
            
            # Web frameworks (uncomment as needed)
            # pythonPackages.django
            # pythonPackages.flask
            # pythonPackages.fastapi
          ];
          
          shellHook = ''
            echo "🐍 Python development environment loaded!"
            echo "Python version: $(python --version)"
            echo ""
            echo "Useful commands:"
            echo "  python -m venv .venv  - Create virtual environment"
            echo "  poetry init           - Initialize Poetry project"
            echo "  pytest               - Run tests"
            echo "  black .              - Format code"
            echo "  mypy .               - Type check"
            echo ""
            echo "Creating .venv if it doesn't exist..."
            if [ ! -d .venv ]; then
              python -m venv .venv
            fi
            echo "Activate venv with: source .venv/bin/activate"
          '';
        }
        """).strip()
        
        return GeneratedConfig(
            config_type="shell",
            nix_code=config,
            explanation="Python 3.11 development environment with common tools and libraries",
            dependencies=["python311", "poetry"],
            usage_instructions=dedent("""
                1. Save this as shell.nix in your project directory
                2. Enter the environment: nix-shell
                3. Activate virtual environment: source .venv/bin/activate
                4. Install project dependencies: pip install -r requirements.txt
            """).strip(),
            test_commands=[
                "nix-shell --run 'python --version'",
                "nix-shell --run 'poetry --version'",
                "nix-shell --run 'python -c \"import numpy; print(numpy.__version__)\"'",
            ]
        )
    
    def _node_dev_config(self) -> GeneratedConfig:
        """Generate Node.js development environment"""
        config = dedent("""
        # Node.js development environment
        { pkgs ? import <nixpkgs> {} }:
        
        pkgs.mkShell {
          buildInputs = with pkgs; [
            # Node.js and package managers
            nodejs_20
            nodePackages.npm
            nodePackages.yarn
            nodePackages.pnpm
            
            # Development tools
            nodePackages.typescript
            nodePackages.ts-node
            nodePackages.nodemon
            nodePackages.eslint
            nodePackages.prettier
            
            # Testing
            nodePackages."@vue/cli"
            nodePackages.create-react-app
            nodePackages.jest
            
            # Build tools
            nodePackages.webpack
            nodePackages.vite
            
            # Database clients
            nodePackages.prisma
          ];
          
          shellHook = ''
            echo "📦 Node.js development environment loaded!"
            echo "Node version: $(node --version)"
            echo "NPM version: $(npm --version)"
            echo ""
            echo "Useful commands:"
            echo "  npm init         - Initialize new project"
            echo "  npm install      - Install dependencies"
            echo "  npm run dev      - Start dev server"
            echo "  npm test         - Run tests"
            echo "  npx create-react-app my-app  - Create React app"
            echo "  npx prisma init  - Initialize Prisma"
          '';
        }
        """).strip()
        
        return GeneratedConfig(
            config_type="shell",
            nix_code=config,
            explanation="Node.js 20 development environment with TypeScript and modern tools",
            dependencies=["nodejs_20", "npm"],
            usage_instructions=dedent("""
                1. Save this as shell.nix in your project directory
                2. Enter the environment: nix-shell
                3. Initialize project: npm init -y
                4. Install dependencies: npm install
                5. Start developing!
            """).strip(),
            test_commands=[
                "nix-shell --run 'node --version'",
                "nix-shell --run 'npm --version'",
                "nix-shell --run 'tsc --version'",
            ]
        )
    
    def _go_dev_config(self) -> GeneratedConfig:
        """Generate Go development environment"""
        config = dedent("""
        # Go development environment
        { pkgs ? import <nixpkgs> {} }:
        
        pkgs.mkShell {
          buildInputs = with pkgs; [
            # Go toolchain
            go_1_21
            gopls
            gotools
            go-tools
            golangci-lint
            delve
            
            # Build tools
            gnumake
            gcc
            
            # Database tools
            postgresql
            redis
            
            # Protobuf support
            protobuf
            protoc-gen-go
          ];
          
          shellHook = ''
            export GOPATH=$HOME/go
            export PATH=$PATH:$GOPATH/bin
            
            echo "🐹 Go development environment loaded!"
            echo "Go version: $(go version)"
            echo "GOPATH: $GOPATH"
            echo ""
            echo "Useful commands:"
            echo "  go mod init      - Initialize new module"
            echo "  go get          - Add dependencies"
            echo "  go build        - Build project"
            echo "  go test         - Run tests"
            echo "  golangci-lint run  - Lint code"
          '';
        }
        """).strip()
        
        return GeneratedConfig(
            config_type="shell",
            nix_code=config,
            explanation="Go 1.21 development environment with tools and linters",
            dependencies=["go_1_21", "gopls", "golangci-lint"],
            usage_instructions=dedent("""
                1. Save this as shell.nix in your project directory
                2. Enter the environment: nix-shell
                3. Initialize module: go mod init github.com/user/project
                4. Start developing with Go!
            """).strip(),
            test_commands=[
                "nix-shell --run 'go version'",
                "nix-shell --run 'gopls version'",
                "nix-shell --run 'golangci-lint version'",
            ]
        )
    
    def _generic_dev_config(self) -> GeneratedConfig:
        """Generate generic development environment"""
        config = dedent("""
        # Generic development environment
        { pkgs ? import <nixpkgs> {} }:
        
        pkgs.mkShell {
          buildInputs = with pkgs; [
            # Version control
            git
            gh  # GitHub CLI
            
            # Editors
            neovim
            vscode
            
            # Common tools
            curl
            wget
            jq
            ripgrep
            fd
            bat
            eza
            htop
            tmux
            
            # Build tools
            gnumake
            gcc
            cmake
            pkg-config
            
            # Container tools
            docker
            docker-compose
            
            # Database clients
            postgresql
            redis
            sqlite
          ];
          
          shellHook = ''
            echo "💻 Development environment loaded!"
            echo ""
            echo "Available tools:"
            echo "  git, gh         - Version control"
            echo "  neovim, vscode  - Editors"
            echo "  docker          - Containers"
            echo "  postgresql      - Database"
            echo "  And many more common development tools!"
          '';
        }
        """).strip()
        
        return GeneratedConfig(
            config_type="shell",
            nix_code=config,
            explanation="Generic development environment with common tools",
            dependencies=["git", "neovim", "docker"],
            usage_instructions=dedent("""
                1. Save this as shell.nix in your project directory
                2. Enter the environment: nix-shell
                3. All tools are now available!
            """).strip(),
            test_commands=[
                "nix-shell --run 'git --version'",
                "nix-shell --run 'nvim --version | head -1'",
            ]
        )
    
    def _systemd_service_template(self, req: ConfigRequest) -> GeneratedConfig:
        """Generate systemd service configuration"""
        service_name = req.context.get("name", "myservice")
        user = req.context.get("user", "serviceuser")
        
        config = dedent(f"""
        # Systemd service configuration
        systemd.services.{service_name} = {{
          description = "My Custom Service";
          wantedBy = [ "multi-user.target" ];
          after = [ "network.target" ];
          
          serviceConfig = {{
            Type = "simple";
            User = "{user}";
            Group = "{user}";
            WorkingDirectory = "/var/lib/{service_name}";
            
            # Service command
            ExecStart = "${{pkgs.bash}}/bin/bash /var/lib/{service_name}/run.sh";
            
            # Restart policy
            Restart = "always";
            RestartSec = "10s";
            
            # Security hardening
            PrivateTmp = true;
            NoNewPrivileges = true;
            ProtectSystem = "strict";
            ProtectHome = true;
            ReadWritePaths = [ "/var/lib/{service_name}" ];
            
            # Resource limits
            LimitNOFILE = "4096";
            MemoryMax = "512M";
            CPUQuota = "50%";
          }};
          
          # Optional: environment variables
          environment = {{
            SERVICE_PORT = "8080";
            SERVICE_ENV = "production";
          }};
        }};
        
        # Create service user
        users.users.{user} = {{
          isSystemUser = true;
          group = "{user}";
          home = "/var/lib/{service_name}";
          createHome = true;
        }};
        
        users.groups.{user} = {{}};
        """).strip()
        
        return GeneratedConfig(
            config_type="systemd",
            nix_code=config,
            explanation=f"Systemd service '{service_name}' running as user '{user}'",
            dependencies=[],
            usage_instructions=dedent(f"""
                1. Add this configuration to /etc/nixos/configuration.nix
                2. Create service script: /var/lib/{service_name}/run.sh
                3. Apply configuration: sudo nixos-rebuild switch
                4. Start service: sudo systemctl start {service_name}
                5. Enable on boot: sudo systemctl enable {service_name}
            """).strip(),
            test_commands=[
                f"sudo systemctl status {service_name}",
                f"sudo journalctl -u {service_name} -f",
                f"sudo systemctl restart {service_name}",
            ]
        )
    
    def _firewall_template(self, req: ConfigRequest) -> GeneratedConfig:
        """Generate firewall configuration"""
        ports = []
        if "web" in req.description.lower() or "http" in req.description.lower():
            ports.extend([80, 443])
        if "ssh" in req.description.lower():
            ports.append(22)
        if "database" in req.description.lower():
            ports.append(5432)  # PostgreSQL default
        
        # Add any specific ports mentioned
        port_matches = re.findall(r"\b(\d{2,5})\b", req.description)
        for port in port_matches:
            port_num = int(port)
            if 1 < port_num < 65536:
                ports.append(port_num)
        
        ports = sorted(set(ports))
        
        config = dedent(f"""
        # Firewall configuration
        networking.firewall = {{
          enable = true;
          
          # Allow specific TCP ports
          allowedTCPPorts = [ {' '.join(map(str, ports))} ];
          
          # Allow specific UDP ports (uncomment as needed)
          # allowedUDPPorts = [ 53 67 68 ];
          
          # Allow specific port ranges
          # allowedTCPPortRanges = [
          #   {{ from = 8000; to = 8010; }}
          # ];
          
          # Trusted interfaces (no firewall)
          # trustedInterfaces = [ "docker0" ];
          
          # Log rejected connections
          logRejected = false;
          
          # Allow ping
          allowPing = true;
          
          # Additional rules using iptables
          extraCommands = \'\'\'
            # Allow established connections
            iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
            
            # Rate limiting for SSH (if port 22 is open)
            {f'iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set' if 22 in ports else ''}
            {f'iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP' if 22 in ports else ''}
          \'\'\';
          
          # Stop additional rules
          extraStopCommands = \'\'\'
            iptables -D INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
          \'\'\';
        }};
        
        # Fail2ban for additional protection (optional)
        services.fail2ban = {{
          enable = true;
          maxretry = 5;
          ignoreIP = [ "127.0.0.1/8" "::1" ];
          
          jails = {{
            ssh.settings = {{
              enabled = true;
              port = "ssh";
              filter = "sshd";
              maxretry = 3;
            }};
          }};
        }};
        """).strip()
        
        return GeneratedConfig(
            config_type="firewall",
            nix_code=config,
            explanation=f"Firewall configuration allowing ports: {', '.join(map(str, ports))}",
            dependencies=["iptables", "fail2ban"],
            usage_instructions=dedent("""
                1. Add this configuration to /etc/nixos/configuration.nix
                2. Apply configuration: sudo nixos-rebuild switch
                3. Check firewall status: sudo iptables -L -n
                4. Test connectivity to allowed ports
            """).strip(),
            test_commands=[
                "sudo iptables -L -n",
                "sudo systemctl status firewall",
                "sudo nft list ruleset",  # If using nftables
            ] + [f"nc -zv localhost {port}" for port in ports[:3]]
        )
    
    def _user_template(self, req: ConfigRequest) -> GeneratedConfig:
        """Generate user account configuration"""
        username = req.context.get("user", "newuser")
        is_admin = "admin" in req.description.lower() or "sudo" in req.description.lower()
        
        config = dedent(f"""
        # User account configuration
        users.users.{username} = {{
          isNormalUser = true;
          description = "{username.capitalize()} User Account";
          home = "/home/{username}";
          
          # Groups membership
          extraGroups = [
            "wheel"     # Enable sudo
            "networkmanager"
            "audio"
            "video"
            {'"docker"' if "docker" in req.description.lower() else ''}
            {'"libvirtd"' if "vm" in req.description.lower() or "virtual" in req.description.lower() else ''}
            {'"dialout"' if "serial" in req.description.lower() else ''}
          ] ++ (lib.optionals config.services.xserver.enable [
            "input"
            "render"
          ]);
          
          # Shell configuration
          shell = pkgs.zsh;  # Or pkgs.bash, pkgs.fish
          
          # SSH public keys (add your keys here)
          openssh.authorizedKeys.keys = [
            # "ssh-rsa AAAAB3NzaC1... user@example.com"
          ];
          
          # Initial password (user should change on first login)
          initialPassword = "changeme";
          
          # Packages specific to this user
          packages = with pkgs; [
            firefox
            thunderbird
            git
            neovim
          ];
        }};
        
        # Enable zsh if selected as shell
        programs.zsh.enable = true;
        
        # Sudo configuration for admin users
        {f'''security.sudo.extraRules = [
          {{
            users = [ "{username}" ];
            commands = [
              {{
                command = "ALL";
                options = [ "NOPASSWD" ];  # Remove for password prompt
              }}
            ];
          }}
        ];''' if is_admin else '# Not configured as admin user'}
        """).strip()
        
        return GeneratedConfig(
            config_type="user",
            nix_code=config,
            explanation=f"User account '{username}' with {'admin privileges' if is_admin else 'standard privileges'}",
            dependencies=["zsh"],
            usage_instructions=dedent(f"""
                1. Add this configuration to /etc/nixos/configuration.nix
                2. Apply configuration: sudo nixos-rebuild switch
                3. User can now login with initial password: 'changeme'
                4. User should change password: passwd
                5. Add SSH keys to the configuration for key-based auth
            """).strip(),
            test_commands=[
                f"id {username}",
                f"groups {username}",
                f"sudo -l -U {username}",
            ]
        )
    
    def _shell_env_template(self, req: ConfigRequest) -> GeneratedConfig:
        """Generate shell.nix environment configuration"""
        # Delegate to appropriate dev config based on requirements
        if "rust" in req.description.lower():
            return self._rust_dev_config()
        elif "python" in req.description.lower():
            return self._python_dev_config()
        elif "node" in req.description.lower():
            return self._node_dev_config()
        elif "go" in req.description.lower():
            return self._go_dev_config()
        else:
            return self._generic_dev_config()
    
    def _generic_config(self, req: ConfigRequest) -> GeneratedConfig:
        """Generate a generic configuration template"""
        config = dedent("""
        # Generic NixOS configuration
        { config, pkgs, ... }:
        
        {
          # Add your configuration here
          environment.systemPackages = with pkgs; [
            # Add packages
          ];
          
          # Add services
          # services.example.enable = true;
          
          # Add system configuration
          # system.stateVersion = "24.05";
        }
        """).strip()
        
        return GeneratedConfig(
            config_type="generic",
            nix_code=config,
            explanation="Generic NixOS configuration template",
            dependencies=[],
            usage_instructions="Add this to your /etc/nixos/configuration.nix and customize as needed",
            test_commands=["sudo nixos-rebuild test"]
        )
    
    def format_config(self, config: GeneratedConfig) -> str:
        """Format the generated configuration for display"""
        output = []
        output.append(f"🎉 **Generated {config.config_type.title()} Configuration**")
        output.append(f"📝 **Description**: {config.explanation}")
        
        if config.dependencies:
            output.append(f"📦 **Dependencies**: {', '.join(config.dependencies)}")
        
        output.append("\n```nix")
        output.append(config.nix_code)
        output.append("```")
        
        output.append(f"\n📚 **Usage Instructions**:")
        output.append(config.usage_instructions)
        
        if config.test_commands:
            output.append(f"\n🧪 **Test Commands**:")
            for cmd in config.test_commands:
                output.append(f"  $ {cmd}")
        
        return "\n".join(output)


# Integration point for CLI
def generate_nixos_config(request: str) -> str:
    """
    Main entry point for configuration generation
    Returns formatted configuration for the user
    """
    generator = NixOSConfigGenerator()
    config = generator.generate_config(request)
    return generator.format_config(config)