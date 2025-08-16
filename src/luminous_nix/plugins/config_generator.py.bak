"""
🔧 Configuration Generator Plugin

Natural language to NixOS configuration translation.
This is a killer feature that makes NixOS accessible to everyone.
"""

from ..core.unified_backend import Context, Intent, IntentType, Plugin, Result


class ConfigGeneratorPlugin(Plugin):
    """
    Generate NixOS configurations from natural language descriptions

    Examples:
        "web server with nginx and postgresql"
        "development environment with python and rust"
        "desktop with firefox and vscode"
    """

    @property
    def name(self) -> str:
        return "config_generator"

    def __init__(self):
        """Initialize with NixOS module knowledge"""
        self.service_map = {
            # Web servers
            "nginx": "services.nginx.enable = true",
            "apache": "services.httpd.enable = true",
            "caddy": "services.caddy.enable = true",
            # Databases
            "postgresql": "services.postgresql.enable = true",
            "postgres": "services.postgresql.enable = true",
            "mysql": "services.mysql.enable = true",
            "mariadb": "services.mysql.enable = true",
            "redis": 'services.redis.servers."".enable = true',
            "mongodb": "services.mongodb.enable = true",
            # Development
            "docker": "virtualisation.docker.enable = true",
            "podman": "virtualisation.podman.enable = true",
            "libvirt": "virtualisation.libvirtd.enable = true",
            "virtualbox": "virtualisation.virtualbox.host.enable = true",
            # Desktop
            "plasma": "services.xserver.desktopManager.plasma5.enable = true",
            "gnome": "services.xserver.desktopManager.gnome.enable = true",
            "xfce": "services.xserver.desktopManager.xfce.enable = true",
            "i3": "services.xserver.windowManager.i3.enable = true",
            # System services
            "ssh": "services.openssh.enable = true",
            "firewall": "networking.firewall.enable = true",
            "fail2ban": "services.fail2ban.enable = true",
            "tailscale": "services.tailscale.enable = true",
        }

        self.package_categories = {
            "python": ["python3", "python3Packages.pip", "python3Packages.virtualenv"],
            "rust": ["rustc", "cargo", "rustfmt", "clippy"],
            "nodejs": ["nodejs", "nodePackages.npm", "nodePackages.yarn"],
            "node": ["nodejs", "nodePackages.npm"],
            "go": ["go", "gopls", "go-tools"],
            "java": ["openjdk", "maven", "gradle"],
            "haskell": ["ghc", "cabal-install", "stack"],
            "cpp": ["gcc", "cmake", "gdb", "valgrind"],
            "c++": ["gcc", "cmake", "gdb", "valgrind"],
        }

    def can_handle(self, intent: Intent) -> bool:
        """Handle config generation requests"""
        if intent.type == IntentType.GENERATE_CONFIG:
            return True

        # Also handle natural language that looks like config requests
        query_lower = intent.query.lower()
        config_keywords = [
            "config",
            "configuration",
            "setup",
            "environment",
            "with",
            "server",
            "desktop",
            "development",
        ]
        return any(keyword in query_lower for keyword in config_keywords)

    async def process(self, intent: Intent, context: Context) -> Result | None:
        """Generate NixOS configuration from intent"""
        try:
            config = self.generate_config(intent.query)

            return Result(
                success=True,
                output=config,
                intent=intent,
                metadata={"type": "nix_config", "generator": "config_generator_v1"},
            )
        except Exception as e:
            return Result(
                success=False,
                output="",
                intent=intent,
                error=str(e),
                suggestions=[
                    "Try being more specific about what services you need",
                    "Example: 'web server with nginx and postgresql'",
                    "Example: 'development environment with python and docker'",
                ],
            )

    def generate_config(self, description: str) -> str:
        """
        Generate NixOS configuration from natural language

        Args:
            description: Natural language description

        Returns:
            NixOS configuration as string
        """
        description_lower = description.lower()

        # Collect services to enable (use set to avoid duplicates)
        services = set()
        for service_name, config_line in self.service_map.items():
            if service_name in description_lower:
                services.add(config_line)

        # Convert to sorted list for consistent output
        services = sorted(list(services))

        # Collect packages to install (use set to avoid duplicates)
        packages = set()

        # Check for development environments
        for lang, pkgs in self.package_categories.items():
            if lang in description_lower:
                packages.update(pkgs)

        # Check for specific packages mentioned
        package_keywords = [
            "firefox",
            "chromium",
            "vscode",
            "vim",
            "neovim",
            "emacs",
            "git",
            "htop",
            "tmux",
            "zsh",
            "fish",
            "alacritty",
            "kitty",
            "slack",
            "discord",
            "zoom",
            "thunderbird",
            "libreoffice",
        ]
        for pkg in package_keywords:
            if pkg in description_lower:
                packages.add(pkg)

        # Convert to sorted list for consistent output
        packages = sorted(list(packages))

        # Build the configuration
        config_lines = []
        config_lines.append("{ config, pkgs, ... }:")
        config_lines.append("")
        config_lines.append("{")

        # Add description as comment
        config_lines.append(f"  # Generated from: {description}")
        config_lines.append("")

        # Add services
        if services:
            config_lines.append("  # Services")
            for service in services:
                config_lines.append(f"  {service};")
            config_lines.append("")

        # Add packages
        if packages:
            config_lines.append("  # Packages")
            config_lines.append("  environment.systemPackages = with pkgs; [")
            for pkg in packages:
                config_lines.append(f"    {pkg}")
            config_lines.append("  ];")
            config_lines.append("")

        # Add common settings based on description
        if "desktop" in description_lower:
            config_lines.append("  # Desktop environment")
            config_lines.append("  services.xserver.enable = true;")
            config_lines.append("  services.xserver.displayManager.sddm.enable = true;")
            config_lines.append("")

        if "server" in description_lower:
            config_lines.append("  # Server settings")
            config_lines.append("  networking.firewall.enable = true;")
            config_lines.append("  services.openssh.enable = true;")
            config_lines.append("")

        if "development" in description_lower or "dev" in description_lower:
            config_lines.append("  # Development settings")
            config_lines.append("  programs.git.enable = true;")
            config_lines.append("")

        config_lines.append("}")

        return "\n".join(config_lines)


class SmartSearchPlugin(Plugin):
    """
    Smart package search that understands descriptions

    Instead of exact names, search by what the package does.
    """

    @property
    def name(self) -> str:
        return "smart_search"

    def can_handle(self, intent: Intent) -> bool:
        """Handle search with descriptions"""
        if intent.type == IntentType.SEARCH:
            # Check if it's a description rather than exact name
            query = intent.query.lower()
            return any(
                word in query
                for word in ["that", "which", "for", "to", "like", "similar"]
            )
        return False

    async def process(self, intent: Intent, context: Context) -> Result | None:
        """Smart search by description"""
        query = intent.parameters.get("query", intent.query)

        # Map descriptions to likely packages
        search_map = {
            "markdown editor": ["obsidian", "typora", "marktext", "ghostwriter"],
            "code editor": ["vscode", "sublime-text", "atom", "neovim"],
            "terminal": ["alacritty", "kitty", "wezterm", "foot"],
            "browser": ["firefox", "chromium", "brave", "vivaldi"],
            "music player": ["spotify", "rhythmbox", "clementine", "deadbeef"],
            "video player": ["vlc", "mpv", "celluloid", "kodi"],
            "image editor": ["gimp", "krita", "inkscape", "darktable"],
            "notes": ["obsidian", "joplin", "notion", "logseq"],
            "password manager": ["bitwarden", "keepassxc", "pass", "1password"],
        }

        # Find matching category
        suggestions = []
        for category, packages in search_map.items():
            if any(word in query.lower() for word in category.split()):
                suggestions.extend(packages)

        if suggestions:
            output = "📦 Smart search found these packages:\n"
            for pkg in suggestions[:5]:  # Limit to top 5
                output += f"  • {pkg}\n"
            output += f"\nInstall with: nix-env -iA nixos.{suggestions[0]}"

            return Result(
                success=True,
                output=output,
                intent=intent,
                metadata={"packages": suggestions},
            )

        # Fallback to regular search
        return None
