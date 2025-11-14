"""
Semantic Search Service - Find packages by meaning, not just names

This is a killer feature that sets us apart - users can search
for concepts and we find the right packages.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class SemanticMatch:
    """A semantic search match"""

    name: str
    description: str
    score: float
    category: str

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "score": self.score,
            "category": self.category,
        }


class SemanticSearchService:
    """
    Semantic search using embeddings and concept mapping.

    This allows users to search for:
    - "video editor" → kdenlive, openshot, pitivi
    - "photo editor" → gimp, krita, darktable
    - "note taking" → obsidian, logseq, joplin
    - "music player" → spotify, rhythmbox, clementine
    """

    def __init__(self, index_path: Optional[Path] = None):
        """
        Initialize semantic search.

        Args:
            index_path: Path to semantic index
        """
        self.index_path = (
            index_path
            or Path.home() / ".cache" / "luminous-nix" / "semantic_index.json"
        )
        self.index = self._load_or_build_index()
        self.embeddings = None  # Lazy load if needed

    def search(self, query: str, limit: int = 10) -> List[SemanticMatch]:
        """
        Search for packages semantically.

        Args:
            query: Natural language query
            limit: Maximum results

        Returns:
            List of semantic matches
        """
        query_lower = query.lower()

        # First try concept mapping (fast)
        concept_matches = self._search_by_concept(query_lower)
        if concept_matches:
            return concept_matches[:limit]

        # Then try category mapping
        category_matches = self._search_by_category(query_lower)
        if category_matches:
            return category_matches[:limit]

        # Finally try keyword expansion
        keyword_matches = self._search_by_keywords(query_lower)
        return keyword_matches[:limit]

    def _search_by_concept(self, query: str) -> List[SemanticMatch]:
        """Search using concept mapping"""

        # Concept to package mapping
        concepts = {
            # Editors
            "video editor": [
                "kdenlive",
                "openshot",
                "pitivi",
                "shotcut",
                "davinci-resolve",
            ],
            "video editing": [
                "kdenlive",
                "openshot",
                "pitivi",
                "shotcut",
                "davinci-resolve",
            ],
            "photo editor": ["gimp", "krita", "darktable", "rawtherapee", "digikam"],
            "photo editing": ["gimp", "krita", "darktable", "rawtherapee", "digikam"],
            "image editor": ["gimp", "krita", "inkscape", "pinta"],
            "code editor": ["vscode", "vim", "neovim", "emacs", "sublime3", "atom"],
            "text editor": ["vim", "neovim", "emacs", "nano", "gedit", "kate"],
            "audio editor": ["audacity", "ardour", "lmms", "qtractor"],
            "3d modeling": ["blender", "freecad", "openscad", "wings"],
            # Productivity
            "note taking": ["obsidian", "logseq", "joplin", "notable", "standardnotes"],
            "notes": ["obsidian", "logseq", "joplin", "notable", "standardnotes"],
            "todo": ["todoist", "taskwarrior", "todo-txt", "getting-things-gnome"],
            "task management": ["taskwarrior", "todo-txt", "getting-things-gnome"],
            "calendar": ["gnome-calendar", "korganizer", "calcurse", "kalendar"],
            "email client": [
                "thunderbird",
                "evolution",
                "claws-mail",
                "mutt",
                "neomutt",
            ],
            "email": ["thunderbird", "evolution", "claws-mail", "mutt", "neomutt"],
            # Entertainment
            "music player": [
                "spotify",
                "rhythmbox",
                "clementine",
                "strawberry",
                "audacious",
            ],
            "video player": ["vlc", "mpv", "celluloid", "smplayer", "kodi"],
            "movie player": ["vlc", "mpv", "kodi", "plex", "jellyfin"],
            "streaming": ["obs-studio", "streamlink", "kodi", "plex", "jellyfin"],
            # Communication
            "chat": [
                "discord",
                "telegram-desktop",
                "signal-desktop",
                "element-desktop",
                "hexchat",
            ],
            "messaging": [
                "telegram-desktop",
                "signal-desktop",
                "element-desktop",
                "whatsapp-for-linux",
            ],
            "video call": ["zoom-us", "teams", "skypeforlinux", "jitsi-meet"],
            "video conference": ["zoom-us", "teams", "jitsi-meet"],
            # Development
            "database client": ["dbeaver", "pgadmin4", "mysql-workbench", "datagrip"],
            "database browser": ["dbeaver", "sqlitebrowser", "pgadmin4"],
            "api testing": ["postman", "insomnia", "httpie", "curl"],
            "git client": ["gitkraken", "sourcetree", "gitg", "lazygit", "tig"],
            "docker manager": ["lazydocker", "portainer", "dockstation"],
            # System
            "system monitor": [
                "htop",
                "btop",
                "glances",
                "nmon",
                "gnome-system-monitor",
            ],
            "file manager": ["nautilus", "dolphin", "thunar", "nemo", "ranger", "nnn"],
            "terminal emulator": [
                "alacritty",
                "kitty",
                "wezterm",
                "terminator",
                "gnome-terminal",
            ],
            "terminal": [
                "alacritty",
                "kitty",
                "wezterm",
                "terminator",
                "gnome-terminal",
            ],
            "backup": ["borgbackup", "restic", "duplicity", "deja-dup", "timeshift"],
            "password manager": ["bitwarden", "keepassxc", "pass", "gnome-secrets"],
            "vpn": ["openvpn", "wireguard", "mullvad-vpn", "protonvpn-cli"],
            # Office
            "office suite": ["libreoffice", "onlyoffice-bin", "wps-office"],
            "spreadsheet": ["libreoffice-calc", "gnumeric", "sc-im"],
            "presentation": ["libreoffice-impress", "sozi", "sent"],
            "pdf reader": ["evince", "okular", "zathura", "mupdf", "firefox"],
            "pdf editor": ["pdfarranger", "xournalpp", "libreoffice-draw"],
            # Graphics
            "vector graphics": ["inkscape", "karbon", "gravit-designer"],
            "drawing": ["krita", "mypaint", "drawpile"],
            "screenshot": [
                "flameshot",
                "spectacle",
                "gnome-screenshot",
                "scrot",
                "maim",
            ],
            "screen recorder": ["obs-studio", "simplescreenrecorder", "peek", "kazam"],
            # Security
            "firewall": ["ufw", "firewalld", "iptables", "nftables"],
            "antivirus": ["clamav", "chkrootkit", "rkhunter"],
            "encryption": ["veracrypt", "cryptsetup", "gnupg", "age"],
            "security scanner": ["nmap", "wireshark", "metasploit", "nikto"],
        }

        matches = []

        # Check each concept
        for concept, packages in concepts.items():
            if concept in query or query in concept:
                # Found matching concept
                for i, pkg in enumerate(packages):
                    matches.append(
                        SemanticMatch(
                            name=pkg,
                            description=self._get_package_description(pkg),
                            score=1.0 - (i * 0.1),  # Rank by order
                            category=self._extract_category(concept),
                        )
                    )
                break

        return matches

    def _search_by_category(self, query: str) -> List[SemanticMatch]:
        """Search by general category"""

        categories = {
            "browser": [
                "firefox",
                "chromium",
                "brave",
                "vivaldi",
                "qutebrowser",
                "nyxt",
            ],
            "editor": ["vim", "neovim", "emacs", "vscode", "sublime3", "atom", "nano"],
            "terminal": [
                "alacritty",
                "kitty",
                "wezterm",
                "terminator",
                "gnome-terminal",
            ],
            "shell": ["bash", "zsh", "fish", "nushell", "elvish", "xonsh"],
            "database": [
                "postgresql",
                "mysql",
                "mariadb",
                "sqlite",
                "redis",
                "mongodb",
            ],
            "server": ["nginx", "apache", "caddy", "lighttpd", "traefik"],
            "media": ["vlc", "mpv", "ffmpeg", "obs-studio", "kdenlive", "audacity"],
            "development": ["git", "docker", "gcc", "python", "nodejs", "rust", "go"],
            "network": ["curl", "wget", "nmap", "wireshark", "netcat", "tcpdump"],
            "security": ["gnupg", "pass", "keepassxc", "bitwarden", "veracrypt"],
        }

        matches = []

        for category, packages in categories.items():
            if category in query or query in category:
                for i, pkg in enumerate(packages):
                    matches.append(
                        SemanticMatch(
                            name=pkg,
                            description=self._get_package_description(pkg),
                            score=0.9 - (i * 0.1),
                            category=category,
                        )
                    )
                break

        return matches

    def _search_by_keywords(self, query: str) -> List[SemanticMatch]:
        """Search by keyword expansion"""

        # Keyword synonyms and related terms
        keyword_map = {
            "fast": ["performance", "speed", "quick", "rapid"],
            "simple": ["easy", "minimal", "basic", "lightweight"],
            "secure": ["security", "safe", "encrypted", "privacy"],
            "modern": ["new", "latest", "current", "updated"],
            "free": ["opensource", "foss", "libre", "gratis"],
            "cloud": ["online", "web", "saas", "remote"],
            "local": ["offline", "desktop", "native", "standalone"],
        }

        # Expand query with synonyms
        expanded_terms = [query]
        for keyword, synonyms in keyword_map.items():
            if keyword in query:
                expanded_terms.extend(synonyms)

        # Search with expanded terms
        matches = []
        # This would normally search the actual package database
        # For now, return empty as this is a fallback

        return matches

    def _get_package_description(self, package: str) -> str:
        """Get package description"""

        # Common package descriptions
        descriptions = {
            "firefox": "Free and open source web browser",
            "chromium": "Open source version of Chrome browser",
            "vim": "Highly configurable text editor",
            "neovim": "Vim-fork focused on extensibility",
            "vscode": "Visual Studio Code editor",
            "gimp": "GNU Image Manipulation Program",
            "vlc": "Cross-platform media player",
            "obs-studio": "Video recording and live streaming",
            "kdenlive": "Non-linear video editor",
            "thunderbird": "Email, news and chat client",
            "libreoffice": "Comprehensive office suite",
            "inkscape": "Vector graphics editor",
            "blender": "3D creation suite",
            "audacity": "Multi-track audio editor",
            "htop": "Interactive process viewer",
            "docker": "Container platform",
            "postgresql": "Advanced SQL database",
            "nginx": "High performance web server",
        }

        return descriptions.get(package, f"Package: {package}")

    def _extract_category(self, concept: str) -> str:
        """Extract category from concept"""

        # Simple extraction - take last word
        words = concept.split()
        if len(words) > 1:
            return words[-1]
        return "general"

    def _load_or_build_index(self) -> Dict:
        """Load or build semantic index"""

        if self.index_path.exists():
            try:
                with open(self.index_path, "r") as f:
                    return json.load(f)
            except:
                pass

        # Build default index
        return self._build_default_index()

    def _build_default_index(self) -> Dict:
        """Build default semantic index"""

        # This would normally build from package database
        # For now, return minimal index
        return {"version": "1.0", "packages": {}, "concepts": {}, "categories": {}}

    def add_user_mapping(self, query: str, selected_package: str):
        """
        Learn from user selections to improve search.

        Args:
            query: What the user searched for
            selected_package: What they selected from results
        """
        # Store user mappings to improve future searches
        if "user_mappings" not in self.index:
            self.index["user_mappings"] = {}

        if query not in self.index["user_mappings"]:
            self.index["user_mappings"][query] = []

        if selected_package not in self.index["user_mappings"][query]:
            self.index["user_mappings"][query].append(selected_package)
            self._save_index()

    def _save_index(self):
        """Save index to disk"""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, "w") as f:
            json.dump(self.index, f, indent=2)
