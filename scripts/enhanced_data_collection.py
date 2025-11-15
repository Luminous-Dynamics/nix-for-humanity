#!/usr/bin/env python3
"""
Enhanced training data collection to reach 500+ queries
Includes more comprehensive generation strategies
"""

import json
import logging
import random
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedQueryGenerator:
    """Generate comprehensive NixOS training queries"""

    def __init__(self):
        self.queries = []

        # Common packages people install
        self.packages = [
            "firefox",
            "chromium",
            "brave",
            "vivaldi",
            "vscode",
            "vim",
            "neovim",
            "emacs",
            "sublime-text",
            "git",
            "gh",
            "docker",
            "podman",
            "kubernetes",
            "python3",
            "nodejs",
            "rustc",
            "go",
            "gcc",
            "slack",
            "discord",
            "telegram-desktop",
            "signal-desktop",
            "vlc",
            "mpv",
            "obs-studio",
            "kdenlive",
            "gimp",
            "inkscape",
            "blender",
            "krita",
            "libreoffice",
            "thunderbird",
            "evolution",
            "steam",
            "lutris",
            "wine",
            "virtualbox",
            "postgresql",
            "mysql",
            "redis",
            "mongodb",
            "nginx",
            "apache",
            "caddy",
            "traefik",
            "htop",
            "btop",
            "neofetch",
            "tree",
            "tmux",
            "screen",
            "alacritty",
            "kitty",
            "zsh",
            "fish",
            "starship",
            "powerline",
        ]

        # Services to configure
        self.services = [
            "ssh",
            "bluetooth",
            "printing",
            "scanning",
            "docker",
            "virtualbox",
            "libvirtd",
            "podman",
            "nginx",
            "apache",
            "mysql",
            "postgresql",
            "xserver",
            "wayland",
            "pipewire",
            "pulseaudio",
            "networkmanager",
            "firewall",
            "fail2ban",
            "syncthing",
            "nextcloud",
            "samba",
            "nfs",
            "cups",
            "avahi",
            "resolved",
            "timesyncd",
        ]

        # Programming languages and frameworks
        self.languages = [
            "python",
            "javascript",
            "typescript",
            "rust",
            "go",
            "java",
            "kotlin",
            "scala",
            "clojure",
            "c",
            "cpp",
            "csharp",
            "fsharp",
            "ruby",
            "php",
            "perl",
            "lua",
            "haskell",
            "elm",
            "purescript",
            "ocaml",
            "swift",
            "dart",
            "julia",
            "r",
        ]

    def generate_install_queries(self) -> list[dict]:
        """Generate package installation queries"""
        queries = []

        templates = [
            "install {package}",
            "how to install {package}",
            "add {package} to my system",
            "get {package} on nixos",
            "i need {package}",
            "setup {package}",
            "can you install {package}",
            "help me install {package}",
            "{package} installation",
            "download {package}",
        ]

        for package in self.packages:
            # Pick 2-3 random templates per package
            for template in random.sample(templates, min(3, len(templates))):
                queries.append(
                    {
                        "query": template.format(package=package),
                        "category": "install",
                        "expected_command": f"nix-env -iA nixos.{package.replace('-', '')}",
                    }
                )

        logger.info(f"Generated {len(queries)} install queries")
        return queries

    def generate_config_queries(self) -> list[dict]:
        """Generate configuration queries"""
        queries = []

        templates = [
            "enable {service}",
            "configure {service}",
            "setup {service} service",
            "how to enable {service}",
            "turn on {service}",
            "activate {service}",
            "start {service} service",
            "{service} configuration",
        ]

        for service in self.services:
            for template in random.sample(templates, min(2, len(templates))):
                queries.append(
                    {
                        "query": template.format(service=service),
                        "category": "config",
                        "expected_command": f"services.{service}.enable = true",
                    }
                )

        # Add specific configuration queries
        specific_configs = [
            {"query": "set hostname", "category": "config"},
            {"query": "change timezone", "category": "config"},
            {"query": "add user account", "category": "config"},
            {"query": "configure sudo access", "category": "config"},
            {"query": "setup auto login", "category": "config"},
            {"query": "enable unfree packages", "category": "config"},
            {"query": "allow broken packages", "category": "config"},
            {"query": "configure display manager", "category": "config"},
            {"query": "setup desktop environment", "category": "config"},
            {"query": "change default shell", "category": "config"},
        ]
        queries.extend(specific_configs)

        logger.info(f"Generated {len(queries)} config queries")
        return queries

    def generate_dev_queries(self) -> list[dict]:
        """Generate development environment queries"""
        queries = []

        templates = [
            "{lang} development environment",
            "setup {lang} development",
            "create {lang} dev shell",
            "{lang} programming environment",
            "develop in {lang}",
            "{lang} ide setup",
            "{lang} compiler and tools",
            "i want to code in {lang}",
        ]

        for lang in self.languages:
            for template in random.sample(templates, min(2, len(templates))):
                queries.append({"query": template.format(lang=lang), "category": "dev"})

        # Add specific dev queries
        specific_dev = [
            {"query": "create shell.nix file", "category": "dev"},
            {"query": "setup direnv", "category": "dev"},
            {"query": "use nix flakes", "category": "dev"},
            {"query": "python virtual environment", "category": "dev"},
            {"query": "nodejs with npm", "category": "dev"},
            {"query": "rust cargo workspace", "category": "dev"},
            {"query": "docker development", "category": "dev"},
            {"query": "latex writing environment", "category": "dev"},
            {"query": "jupyter notebook setup", "category": "dev"},
            {"query": "android development tools", "category": "dev"},
        ]
        queries.extend(specific_dev)

        logger.info(f"Generated {len(queries)} dev queries")
        return queries

    def generate_update_queries(self) -> list[dict]:
        """Generate update and maintenance queries"""
        queries = []

        update_patterns = [
            "update system",
            "upgrade nixos",
            "update all packages",
            "check for updates",
            "update channel",
            "switch to unstable",
            "upgrade to latest",
            "refresh packages",
            "sync channels",
            "update configuration",
        ]

        maintenance_patterns = [
            "clean old generations",
            "free disk space",
            "garbage collect",
            "remove unused packages",
            "optimize store",
            "repair nix store",
            "list generations",
            "rollback system",
            "previous generation",
            "undo last update",
        ]

        for pattern in update_patterns:
            queries.append(
                {
                    "query": pattern,
                    "category": "update",
                    "expected_command": "sudo nixos-rebuild switch",
                }
            )
            # Add variation
            queries.append({"query": f"how to {pattern}", "category": "update"})

        for pattern in maintenance_patterns:
            queries.append({"query": pattern, "category": "update"})
            # Add variation
            queries.append({"query": f"please {pattern}", "category": "update"})

        logger.info(f"Generated {len(queries)} update queries")
        return queries

    def generate_search_queries(self) -> list[dict]:
        """Generate search queries"""
        queries = []

        search_terms = [
            "text editor",
            "web browser",
            "terminal emulator",
            "file manager",
            "image viewer",
            "video player",
            "music player",
            "pdf reader",
            "markdown editor",
            "code editor",
            "database client",
            "api testing",
            "screen recorder",
            "screenshot tool",
            "color picker",
            "password manager",
            "note taking",
            "task manager",
            "system monitor",
            "disk usage analyzer",
            "backup tool",
        ]

        templates = [
            "search {term}",
            "find {term}",
            "list {term}s",
            "what {term}s are available",
            "show me {term} options",
            "alternatives to {term}",
        ]

        for term in search_terms:
            for template in random.sample(templates, min(2, len(templates))):
                queries.append(
                    {
                        "query": template.format(term=term),
                        "category": "search",
                        "expected_command": f"nix search {term.replace(' ', '-')}",
                    }
                )

        logger.info(f"Generated {len(queries)} search queries")
        return queries

    def generate_troubleshooting_queries(self) -> list[dict]:
        """Generate error and troubleshooting queries"""
        queries = []

        error_scenarios = [
            "configuration.nix has errors",
            "nixos-rebuild failed",
            "package conflicts",
            "channel update failed",
            "permission denied error",
            "out of disk space",
            "broken symlinks",
            "service won't start",
            "display manager crashed",
            "network not working",
            "audio not working",
            "graphics driver issues",
            "boot failure",
            "kernel panic",
            "dependency hell",
        ]

        templates = [
            "fix {error}",
            "resolve {error}",
            "help with {error}",
            "{error} how to fix",
            "debug {error}",
            "troubleshoot {error}",
        ]

        for error in error_scenarios:
            template = random.choice(templates)
            queries.append({"query": template.format(error=error), "category": "error"})

        logger.info(f"Generated {len(queries)} troubleshooting queries")
        return queries

    def generate_all(self) -> list[dict]:
        """Generate all query types"""
        all_queries = []

        all_queries.extend(self.generate_install_queries())
        all_queries.extend(self.generate_config_queries())
        all_queries.extend(self.generate_dev_queries())
        all_queries.extend(self.generate_update_queries())
        all_queries.extend(self.generate_search_queries())
        all_queries.extend(self.generate_troubleshooting_queries())

        # Shuffle for variety
        random.shuffle(all_queries)

        logger.info(f"Total queries generated: {len(all_queries)}")
        return all_queries


def combine_with_existing():
    """Combine with existing training data"""

    # Load existing data
    existing_files = [
        "data/training/week2_training_data.json",
        "data/dev_training_data.json",
        "data/update_training_data.json",
    ]

    all_queries = []

    for file in existing_files:
        if Path(file).exists():
            with open(file) as f:
                data = json.load(f)
                if isinstance(data, dict) and "queries" in data:
                    all_queries.extend(data["queries"])
                    logger.info(f"Loaded {len(data['queries'])} queries from {file}")
                elif isinstance(data, list):
                    all_queries.extend(data)
                    logger.info(f"Loaded {len(data)} queries from {file}")

    # Generate new queries
    generator = EnhancedQueryGenerator()
    new_queries = generator.generate_all()
    all_queries.extend(new_queries)

    # Remove duplicates based on query text
    seen = set()
    unique_queries = []
    for query in all_queries:
        q_text = query["query"].lower().strip()
        if q_text not in seen:
            seen.add(q_text)
            unique_queries.append(query)

    logger.info(f"Total unique queries: {len(unique_queries)}")

    return unique_queries


def main():
    """Run enhanced data collection"""

    print("🚀 Enhanced Training Data Collection")
    print("=" * 60)

    # Combine all data sources
    all_queries = combine_with_existing()

    # Save comprehensive dataset
    output_file = Path("data/training/comprehensive_training_data.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "metadata": {
            "version": "0.2.2",
            "collected_at": datetime.now().isoformat(),
            "total_queries": len(all_queries),
            "sources": ["forums", "github", "docs", "synthetic", "generated"],
        },
        "queries": all_queries,
    }

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    # Generate report
    categories = {}
    for q in all_queries:
        cat = q.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    print("\n📊 Collection Summary:")
    print(f"Total Queries: {len(all_queries)}")
    print("\nBy Category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:12} : {count:4} ({count/len(all_queries)*100:.1f}%)")

    print(f"\n📁 Saved to: {output_file}")

    if len(all_queries) >= 500:
        print(f"\n🎉 SUCCESS! Collected {len(all_queries)} queries (goal was 500+)")
        print("✅ Week 2 data collection goal achieved!")
    else:
        print(f"\n⚠️  Collected {len(all_queries)} queries")
        print(f"   Need {500 - len(all_queries)} more for goal")


if __name__ == "__main__":
    main()
