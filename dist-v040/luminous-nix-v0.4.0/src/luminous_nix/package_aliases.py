#!/usr/bin/env python3
"""
Extended package aliases for Luminous Nix
Maps common names to actual NixOS package names
"""

# 100+ common package mappings for better user experience
EXTENDED_PACKAGE_ALIASES = {
    # Browsers
    "chrome": "google-chrome",
    "chromium": "chromium",
    "firefox": "firefox",
    "brave": "brave",
    "edge": "microsoft-edge",
    "opera": "opera",
    "vivaldi": "vivaldi",
    "tor": "tor-browser-bundle-bin",
    "tor-browser": "tor-browser-bundle-bin",
    # Editors & IDEs
    "vim": "vim",
    "neovim": "neovim",
    "nvim": "neovim",
    "emacs": "emacs",
    "vscode": "vscode",
    "code": "vscode",
    "sublime": "sublime4",
    "sublime-text": "sublime4",
    "atom": "atom",
    "notepad++": "notepadqq",
    "nano": "nano",
    "helix": "helix",
    "zed": "zed-editor",
    "idea": "jetbrains.idea-community",
    "intellij": "jetbrains.idea-community",
    "pycharm": "jetbrains.pycharm-community",
    "webstorm": "jetbrains.webstorm",
    "goland": "jetbrains.goland",
    "rider": "jetbrains.rider",
    # Terminal & Shell
    "alacritty": "alacritty",
    "kitty": "kitty",
    "wezterm": "wezterm",
    "terminator": "terminator",
    "tmux": "tmux",
    "screen": "screen",
    "zsh": "zsh",
    "fish": "fish",
    "bash": "bash",
    "oh-my-zsh": "oh-my-zsh",
    "starship": "starship",
    "zellij": "zellij",
    # Development Tools
    "git": "git",
    "docker": "docker",
    "docker-compose": "docker-compose",
    "podman": "podman",
    "kubectl": "kubectl",
    "k8s": "kubernetes",
    "k9s": "k9s",
    "helm": "kubernetes-helm",
    "terraform": "terraform",
    "ansible": "ansible",
    "vagrant": "vagrant",
    "virtualbox": "virtualbox",
    # Programming Languages
    "python": "python3",
    "python3": "python3",
    "node": "nodejs",
    "nodejs": "nodejs",
    "npm": "nodejs",
    "yarn": "yarn",
    "pnpm": "nodePackages.pnpm",
    "rust": "rustc",
    "cargo": "cargo",
    "rustup": "rustup",
    "go": "go",
    "golang": "go",
    "java": "jdk",
    "jdk": "jdk",
    "scala": "scala",
    "kotlin": "kotlin",
    "ruby": "ruby",
    "php": "php",
    "dotnet": "dotnet-sdk",
    ".net": "dotnet-sdk",
    "gcc": "gcc",
    "g++": "gcc",
    "clang": "clang",
    "cmake": "cmake",
    "make": "gnumake",
    # Databases
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "mysql": "mysql",
    "mariadb": "mariadb",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "redis": "redis",
    "sqlite": "sqlite",
    "sqlite3": "sqlite",
    "cassandra": "cassandra",
    "elasticsearch": "elasticsearch",
    "neo4j": "neo4j",
    # Web Servers
    "nginx": "nginx",
    "apache": "apacheHttpd",
    "httpd": "apacheHttpd",
    "caddy": "caddy",
    "traefik": "traefik",
    # Utilities
    "curl": "curl",
    "wget": "wget",
    "htop": "htop",
    "btop": "btop",
    "top": "htop",
    "tree": "tree",
    "fzf": "fzf",
    "ripgrep": "ripgrep",
    "rg": "ripgrep",
    "fd": "fd",
    "find": "findutils",
    "bat": "bat",
    "cat": "coreutils",
    "ls": "coreutils",
    "eza": "eza",
    "exa": "eza",
    "jq": "jq",
    "yq": "yq",
    "sed": "gnused",
    "awk": "gawk",
    "grep": "gnugrep",
    "zip": "zip",
    "unzip": "unzip",
    "tar": "gnutar",
    "7zip": "p7zip",
    "rsync": "rsync",
    "scp": "openssh",
    "ssh": "openssh",
    # Media & Graphics
    "vlc": "vlc",
    "mpv": "mpv",
    "ffmpeg": "ffmpeg",
    "obs": "obs-studio",
    "obs-studio": "obs-studio",
    "gimp": "gimp",
    "inkscape": "inkscape",
    "blender": "blender",
    "krita": "krita",
    "audacity": "audacity",
    "spotify": "spotify",
    "discord": "discord",
    "slack": "slack",
    "teams": "teams",
    "zoom": "zoom-us",
    # System Tools
    "gparted": "gparted",
    "gnome-disks": "gnome.gnome-disk-utility",
    "baobab": "gnome.baobab",
    "filelight": "filelight",
    "ncdu": "ncdu",
    "neofetch": "neofetch",
    "fastfetch": "fastfetch",
    "screenfetch": "screenfetch",
    "lm-sensors": "lm_sensors",
    "sensors": "lm_sensors",
    # Security Tools
    "nmap": "nmap",
    "wireshark": "wireshark",
    "tcpdump": "tcpdump",
    "metasploit": "metasploit",
    "john": "john",
    "hashcat": "hashcat",
    "aircrack": "aircrack-ng",
    "aircrack-ng": "aircrack-ng",
    "burp": "burpsuite",
    "burpsuite": "burpsuite",
    "openssl": "openssl",
    "gpg": "gnupg",
    "pass": "pass",
    "keepass": "keepassxc",
    "keepassxc": "keepassxc",
    "bitwarden": "bitwarden",
    "1password": "_1password-gui",
    # Office & Productivity
    "libreoffice": "libreoffice",
    "office": "libreoffice",
    "thunderbird": "thunderbird",
    "evolution": "evolution",
    "signal": "signal-desktop",
    "telegram": "telegram-desktop",
    "whatsapp": "whatsapp-for-linux",
    # File Managers
    "nautilus": "gnome.nautilus",
    "dolphin": "dolphin",
    "thunar": "xfce.thunar",
    "ranger": "ranger",
    "nnn": "nnn",
    "lf": "lf",
    "mc": "mc",
    "midnight-commander": "mc",
    # Package Managers & Build Tools
    "flatpak": "flatpak",
    "snap": "snapd",
    "appimage": "appimage-run",
    "nix": "nix",
    "home-manager": "home-manager",
    "poetry": "poetry",
    "pipenv": "pipenv",
    "conda": "conda",
    "maven": "maven",
    "gradle": "gradle",
    "ant": "ant",
    "bazel": "bazel",
    "meson": "meson",
    "ninja": "ninja",
    # Cloud Tools
    "aws": "awscli2",
    "aws-cli": "awscli2",
    "gcloud": "google-cloud-sdk",
    "azure": "azure-cli",
    "az": "azure-cli",
    "doctl": "doctl",
    "linode": "linode-cli",
    # Monitoring & Logging
    "prometheus": "prometheus",
    "grafana": "grafana",
    "loki": "grafana-loki",
    "datadog": "datadog-agent",
    "nagios": "nagios",
    "zabbix": "zabbix",
    # AI/ML Tools
    "ollama": "ollama",
    "stable-diffusion": "stable-diffusion",
    "jupyter": "jupyter",
    "jupyterlab": "jupyterlab",
    "pandas": "python3Packages.pandas",
    "numpy": "python3Packages.numpy",
    "tensorflow": "python3Packages.tensorflow",
    "pytorch": "python3Packages.pytorch",
    "scikit-learn": "python3Packages.scikit-learn",
}


def get_package_name(alias: str) -> str:
    """
    Get the actual package name from an alias

    Args:
        alias: Common name or alias

    Returns:
        Actual NixOS package name
    """
    # Check exact match first
    if alias in EXTENDED_PACKAGE_ALIASES:
        return EXTENDED_PACKAGE_ALIASES[alias]

    # Check lowercase match
    alias_lower = alias.lower()
    if alias_lower in EXTENDED_PACKAGE_ALIASES:
        return EXTENDED_PACKAGE_ALIASES[alias_lower]

    # Check if it's already a valid package name
    if "." in alias or "-" in alias:
        return alias

    # Default to the alias itself
    return alias


def suggest_similar(alias: str, max_suggestions: int = 5) -> list:
    """
    Suggest similar package names

    Args:
        alias: User input
        max_suggestions: Maximum number of suggestions

    Returns:
        List of similar package names
    """
    from difflib import get_close_matches

    alias_lower = alias.lower()
    all_aliases = list(EXTENDED_PACKAGE_ALIASES.keys())

    # Find close matches
    matches = get_close_matches(alias_lower, all_aliases, n=max_suggestions, cutoff=0.6)

    # Map to actual package names
    return [(match, EXTENDED_PACKAGE_ALIASES[match]) for match in matches]


def get_category_packages(category: str) -> dict:
    """
    Get all packages in a category

    Args:
        category: Category name (browsers, editors, etc.)

    Returns:
        Dictionary of aliases and package names
    """
    categories = {
        "browsers": ["chrome", "firefox", "brave", "edge", "opera", "vivaldi", "tor"],
        "editors": ["vim", "neovim", "emacs", "vscode", "sublime", "atom", "helix"],
        "terminals": ["alacritty", "kitty", "wezterm", "terminator"],
        "databases": ["postgres", "mysql", "mongodb", "redis", "sqlite"],
        "development": ["git", "docker", "kubectl", "terraform", "ansible"],
        "languages": ["python", "node", "rust", "go", "java", "ruby"],
        "media": ["vlc", "mpv", "obs", "gimp", "inkscape", "blender"],
        "security": ["nmap", "wireshark", "metasploit", "openssl", "gpg"],
    }

    if category.lower() in categories:
        packages = categories[category.lower()]
        return {pkg: EXTENDED_PACKAGE_ALIASES.get(pkg, pkg) for pkg in packages}

    return {}


# Export for easy import
__all__ = [
    "EXTENDED_PACKAGE_ALIASES",
    "get_package_name",
    "suggest_similar",
    "get_category_packages",
]
