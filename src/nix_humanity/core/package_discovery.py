#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List, Optional
Smart Package Discovery for Nix for Humanity

Helps users find packages through:
- Natural language descriptions
- Common aliases and alternative names
- Feature-based search
- Category browsing
- Similarity matching
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from difflib import get_close_matches
import re


@dataclass
class PackageMatch:
    """A potential package match"""
    name: str
    description: str
    score: float
    reason: str  # Why this was matched
    alternatives: List[str] = None
    category: Optional[str] = None
    

@dataclass
class PackageInfo:
    """Detailed package information"""
    name: str
    description: str
    version: Optional[str]
    homepage: Optional[str]
    license: Optional[str]
    maintainers: List[str]
    platforms: List[str]
    similar_packages: List[str]
    common_commands: List[str]
    

class PackageDiscovery:
    """Smart package discovery with natural language understanding"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / ".cache" / "nix-humanity" / "packages.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Common package aliases and mappings
        self.aliases = {
            # Browsers
            "browser": ["firefox", "chromium", "brave", "qutebrowser"],
            "chrome": ["chromium", "google-chrome"],
            "ff": ["firefox"],
            
            # Editors
            "editor": ["vim", "neovim", "emacs", "vscode", "sublime3", "atom"],
            "code": ["vscode", "vscodium"],
            "sublime": ["sublime3", "sublime4"],
            
            # Development
            "python": ["python3", "python311", "python312"],
            "node": ["nodejs", "nodejs_20", "nodejs_21"],
            "java": ["openjdk", "openjdk17", "openjdk21"],
            "c++": ["gcc", "clang", "llvm"],
            "rust": ["rustc", "cargo", "rustup"],
            
            # Tools
            "unzip": ["unzip", "p7zip"],
            "screenshot": ["flameshot", "spectacle", "gnome-screenshot"],
            "terminal": ["alacritty", "kitty", "wezterm", "gnome-terminal"],
            "music": ["spotify", "rhythmbox", "clementine", "mpd"],
            "video": ["vlc", "mpv", "mplayer"],
            "image": ["gimp", "inkscape", "krita"],
            
            # System
            "vpn": ["openvpn", "wireguard", "tailscale"],
            "backup": ["borgbackup", "restic", "duplicity"],
            "monitor": ["htop", "btop", "glances"],
            "network": ["nmap", "wireshark", "tcpdump"],
        }
        
        # Category mappings
        self.categories = {
            "development": {
                "keywords": ["programming", "coding", "development", "ide", "compiler"],
                "packages": ["vim", "neovim", "emacs", "vscode", "gcc", "clang", "python3", "nodejs", "rustc"]
            },
            "multimedia": {
                "keywords": ["music", "video", "audio", "media", "player"],
                "packages": ["vlc", "mpv", "spotify", "audacity", "obs-studio", "ffmpeg"]
            },
            "graphics": {
                "keywords": ["image", "photo", "graphics", "drawing", "design"],
                "packages": ["gimp", "inkscape", "krita", "blender", "darktable"]
            },
            "networking": {
                "keywords": ["network", "internet", "wifi", "vpn", "security"],
                "packages": ["nmap", "wireshark", "openvpn", "wireguard", "curl", "wget"]
            },
            "productivity": {
                "keywords": ["office", "document", "spreadsheet", "presentation"],
                "packages": ["libreoffice", "thunderbird", "zathura", "pandoc"]
            },
            "utilities": {
                "keywords": ["tool", "utility", "system", "file", "backup"],
                "packages": ["htop", "tree", "ranger", "fzf", "ripgrep", "fd", "bat"]
            }
        }
        
        # Feature to package mappings
        self.features = {
            "pdf": ["zathura", "evince", "okular", "mupdf"],
            "markdown": ["pandoc", "grip", "markdown"],
            "screenshot": ["flameshot", "spectacle", "scrot"],
            "clipboard": ["xclip", "xsel", "copyq"],
            "torrents": ["transmission", "qbittorrent", "deluge"],
            "encryption": ["gnupg", "veracrypt", "cryptsetup"],
            "virtualization": ["virtualbox", "qemu", "virt-manager"],
            "containers": ["docker", "podman", "lxc"],
            "databases": ["postgresql", "mysql", "sqlite", "redis"],
            "web servers": ["nginx", "apache", "caddy"],
        }
        
        # Initialize or update database
        self._init_db()
        
    def _init_db(self):
        """Initialize the package database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS packages (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    version TEXT,
                    homepage TEXT,
                    license TEXT,
                    category TEXT,
                    keywords TEXT,
                    last_updated INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    query TEXT,
                    selected_package TEXT,
                    timestamp INTEGER
                )
            """)
            
            # Create full-text search index
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS packages_fts
                USING fts5(name, description, keywords, content=packages)
            """)
    
    def search_packages(self, query: str, limit: int = 10) -> List[PackageMatch]:
        """Search for packages using natural language"""
        query_lower = query.lower()
        matches = []
        
        # 1. Check direct aliases
        for alias, packages in self.aliases.items():
            if alias in query_lower:
                for pkg in packages:
                    matches.append(PackageMatch(
                        name=pkg,
                        description=f"Common name for {alias}",
                        score=1.0,
                        reason=f"Alias match for '{alias}'"
                    ))
        
        # 2. Check features
        for feature, packages in self.features.items():
            if feature in query_lower:
                for pkg in packages:
                    matches.append(PackageMatch(
                        name=pkg,
                        description=f"Supports {feature}",
                        score=0.9,
                        reason=f"Feature match for '{feature}'"
                    ))
        
        # 3. Check categories
        for category, data in self.categories.items():
            if any(keyword in query_lower for keyword in data["keywords"]):
                for pkg in data["packages"][:5]:  # Top 5 per category
                    matches.append(PackageMatch(
                        name=pkg,
                        description=f"Popular {category} tool",
                        score=0.8,
                        reason=f"Category match for '{category}'",
                        category=category
                    ))
        
        # 4. Database search
        db_matches = self._search_database(query)
        matches.extend(db_matches)
        
        # 5. Fuzzy matching on package names
        all_packages = set()
        for packages in self.aliases.values():
            all_packages.update(packages)
        for packages in self.features.values():
            all_packages.update(packages)
        
        fuzzy_matches = get_close_matches(query_lower, all_packages, n=3, cutoff=0.6)
        for match in fuzzy_matches:
            if not any(m.name == match for m in matches):
                matches.append(PackageMatch(
                    name=match,
                    description="Similar package name",
                    score=0.6,
                    reason="Fuzzy name match"
                ))
        
        # Remove duplicates and sort by score
        seen = set()
        unique_matches = []
        for match in sorted(matches, key=lambda x: x.score, reverse=True):
            if match.name not in seen:
                seen.add(match.name)
                unique_matches.append(match)
        
        return unique_matches[:limit]
    
    def _search_database(self, query: str) -> List[PackageMatch]:
        """Search the package database"""
        matches = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Full-text search
                cursor = conn.execute("""
                    SELECT p.name, p.description, p.category
                    FROM packages p
                    JOIN packages_fts ON p.rowid = packages_fts.rowid
                    WHERE packages_fts MATCH ?
                    ORDER BY rank
                    LIMIT 10
                """, (query,))
                
                for name, description, category in cursor:
                    matches.append(PackageMatch(
                        name=name,
                        description=description or "Package in Nixpkgs",
                        score=0.7,
                        reason="Database search match",
                        category=category
                    ))
                    
        except sqlite3.OperationalError:
            # Table might not exist or be populated yet
            pass
            
        return matches
    
    def find_alternatives(self, package_name: str) -> List[str]:
        """Find alternative packages for a given package"""
        alternatives = []
        
        # Check aliases
        for alias, packages in self.aliases.items():
            if package_name in packages:
                alternatives.extend([p for p in packages if p != package_name])
                
        # Check features
        for feature, packages in self.features.items():
            if package_name in packages:
                alternatives.extend([p for p in packages if p != package_name])
                
        # Check categories
        for category, data in self.categories.items():
            if package_name in data["packages"]:
                alternatives.extend([p for p in data["packages"][:3] if p != package_name])
                
        return list(set(alternatives))
    
    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get detailed information about a package"""
        # Try database first
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT name, description, version, homepage, license
                    FROM packages
                    WHERE name = ?
                """, (package_name,))
                
                row = cursor.fetchone()
                if row:
                    name, description, version, homepage, license = row
                    return PackageInfo(
                        name=name,
                        description=description or "No description available",
                        version=version,
                        homepage=homepage,
                        license=license,
                        maintainers=[],
                        platforms=["x86_64-linux"],
                        similar_packages=self.find_alternatives(name),
                        common_commands=self._get_common_commands(name)
                    )
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
            
        # Fallback to basic info
        return PackageInfo(
            name=package_name,
            description=self._get_basic_description(package_name),
            version=None,
            homepage=None,
            license=None,
            maintainers=[],
            platforms=["x86_64-linux"],
            similar_packages=self.find_alternatives(package_name),
            common_commands=self._get_common_commands(package_name)
        )
    
    def _get_basic_description(self, package_name: str) -> str:
        """Get a basic description for known packages"""
        descriptions = {
            "firefox": "Free and open source web browser",
            "chromium": "Open source web browser",
            "vim": "Highly configurable text editor",
            "neovim": "Vim-fork focused on extensibility",
            "vscode": "Visual Studio Code - Open source code editor",
            "htop": "Interactive process viewer",
            "git": "Distributed version control system",
            "tmux": "Terminal multiplexer",
            "docker": "Container platform",
            "python3": "Python programming language",
            "nodejs": "JavaScript runtime",
            "gcc": "GNU Compiler Collection",
            "rustc": "Rust compiler",
        }
        
        return descriptions.get(package_name, f"{package_name} package")
    
    def _get_common_commands(self, package_name: str) -> List[str]:
        """Get common commands for a package"""
        commands = {
            "git": ["git status", "git add", "git commit", "git push"],
            "docker": ["docker ps", "docker run", "docker build"],
            "python3": ["python3", "pip3"],
            "nodejs": ["node", "npm", "npx"],
            "vim": ["vim", "vimdiff"],
            "htop": ["htop"],
            "tmux": ["tmux", "tmux attach", "tmux new"],
        }
        
        return commands.get(package_name, [package_name])
    
    def suggest_by_command(self, command: str) -> List[PackageMatch]:
        """Suggest packages that provide a specific command"""
        # Command to package mappings
        command_mappings = {
            "python": ["python3", "python311", "python312"],
            "pip": ["python3", "python311-pip"],
            "node": ["nodejs", "nodejs_20"],
            "npm": ["nodejs", "nodejs_20"],
            "cargo": ["rustc", "cargo", "rustup"],
            "rustc": ["rustc", "cargo"],
            "gcc": ["gcc", "gcc12", "gcc13"],
            "g++": ["gcc", "gcc12", "gcc13"],
            "make": ["gnumake", "cmake"],
            "docker": ["docker", "docker-compose"],
            "kubectl": ["kubectl", "kubernetes"],
            "aws": ["awscli", "awscli2"],
            "terraform": ["terraform"],
            "ansible": ["ansible"],
        }
        
        matches = []
        
        # Direct mapping
        if command in command_mappings:
            for pkg in command_mappings[command]:
                matches.append(PackageMatch(
                    name=pkg,
                    description=f"Provides the '{command}' command",
                    score=1.0,
                    reason=f"Command provider for '{command}'"
                ))
        
        # Fuzzy match on command
        similar_commands = get_close_matches(command, command_mappings.keys(), n=3, cutoff=0.6)
        for similar in similar_commands:
            if similar != command:
                for pkg in command_mappings[similar]:
                    matches.append(PackageMatch(
                        name=pkg,
                        description=f"Provides similar command '{similar}'",
                        score=0.7,
                        reason=f"Similar command match"
                    ))
        
        return matches
    
    def browse_categories(self) -> Dict[str, List[str]]:
        """Get all categories and their top packages"""
        result = {}
        
        for category, data in self.categories.items():
            result[category] = {
                "description": f"Packages for {category}",
                "keywords": data["keywords"],
                "top_packages": data["packages"][:10]
            }
            
        return result
    
    def learn_from_selection(self, query: str, selected_package: str):
        """Learn from user's package selection"""
        import time
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO search_history (query, selected_package, timestamp)
                VALUES (?, ?, ?)
            """, (query, selected_package, int(time.time())))
    
    def get_popular_packages(self, category: Optional[str] = None) -> List[Tuple[str, str]]:
        """Get popular packages, optionally filtered by category"""
        popular = []
        
        if category and category in self.categories:
            packages = self.categories[category]["packages"]
            for pkg in packages[:10]:
                desc = self._get_basic_description(pkg)
                popular.append((pkg, desc))
        else:
            # General popular packages
            general_popular = [
                ("firefox", "Web browser"),
                ("vim", "Text editor"),
                ("git", "Version control"),
                ("htop", "System monitor"),
                ("tmux", "Terminal multiplexer"),
                ("docker", "Container platform"),
                ("python3", "Programming language"),
                ("nodejs", "JavaScript runtime"),
                ("vscode", "Code editor"),
                ("vlc", "Media player"),
            ]
            popular = general_popular
            
        return popular


def demonstrate_package_discovery():
    """Demo the package discovery functionality"""
    discovery = PackageDiscovery()
    
    print("🔍 Smart Package Discovery Demo")
    print("=" * 50)
    
    # Example 1: Natural language search
    print("\n1. Natural Language Search:")
    test_queries = [
        "i need a web browser",
        "something to edit photos",
        "tool for programming in python",
        "play music files",
        "monitor my system resources"
    ]
    
    for query in test_queries:
        print(f"\n💬 Query: '{query}'")
        results = discovery.search_packages(query, limit=3)
        for match in results:
            print(f"   • {match.name}: {match.description}")
            print(f"     (Score: {match.score:.1f}, Reason: {match.reason})")
    
    # Example 2: Command-based search
    print("\n\n2. Command-Based Search:")
    commands = ["python", "npm", "cargo", "kubectl"]
    
    for cmd in commands:
        print(f"\n🔧 Command '{cmd}' not found")
        suggestions = discovery.suggest_by_command(cmd)
        if suggestions:
            print(f"   Install one of these packages:")
            for match in suggestions:
                print(f"   • nix-env -iA nixpkgs.{match.name}")
    
    # Example 3: Browse categories
    print("\n\n3. Browse by Category:")
    categories = discovery.browse_categories()
    
    for category, info in list(categories.items())[:3]:
        print(f"\n📁 {category.title()}:")
        print(f"   Keywords: {', '.join(info['keywords'][:3])}")
        print(f"   Popular: {', '.join(info['top_packages'][:5])}")
    
    # Example 4: Find alternatives
    print("\n\n4. Package Alternatives:")
    test_packages = ["firefox", "vim", "docker"]
    
    for pkg in test_packages:
        alternatives = discovery.find_alternatives(pkg)
        if alternatives:
            print(f"\n🔄 Alternatives to {pkg}:")
            for alt in alternatives[:3]:
                print(f"   • {alt}")
    
    print("\n\n✨ Smart discovery helps find packages naturally!")


if __name__ == "__main__":
    demonstrate_package_discovery()