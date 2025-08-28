#!/usr/bin/env python3
"""
Package Intelligence System for Luminous Nix

Smart package discovery that understands what users actually want.
This is a working prototype that can be expanded with the full design.
"""

import json
import re
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


@dataclass
class PackageInfo:
    """Rich package information."""
    name: str
    version: str
    description: str
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    commonly_with: List[str] = field(default_factory=list)
    popularity: float = 0.5
    size_mb: Optional[int] = None
    homepage: Optional[str] = None


@dataclass
class SearchIntent:
    """Parsed user search intent."""
    query: str
    category: Optional[str] = None
    action: str = "find"  # find, install, alternative, similar
    confidence: float = 1.0


class PackageCategories:
    """
    Package category knowledge base.
    Maps common terms to package categories and specific packages.
    """
    
    CATEGORIES = {
        # Browsers
        "browser": {
            "packages": ["firefox", "chromium", "brave", "qutebrowser", "vivaldi", 
                        "opera", "librewolf", "ungoogled-chromium", "tor-browser"],
            "keywords": ["web", "internet", "browse", "surf"],
            "description": "Web browsers for internet access"
        },
        
        # Editors
        "editor": {
            "packages": ["vim", "neovim", "emacs", "vscode", "vscodium", "sublime", 
                        "atom", "kate", "gedit", "nano", "notepadqq", "xi-editor"],
            "keywords": ["text", "code", "ide", "notepad", "writing"],
            "description": "Text and code editors"
        },
        
        # Terminals
        "terminal": {
            "packages": ["alacritty", "kitty", "wezterm", "foot", "konsole", 
                        "gnome-terminal", "terminator", "rxvt-unicode", "st"],
            "keywords": ["console", "shell", "command-line", "cli"],
            "description": "Terminal emulators"
        },
        
        # Development
        "development": {
            "packages": ["git", "gcc", "cmake", "make", "docker", "podman",
                        "nodejs", "python3", "rust", "go", "java", "dotnet"],
            "keywords": ["programming", "coding", "build", "compile", "dev"],
            "description": "Development tools and compilers"
        },
        
        # Media Players
        "media": {
            "packages": ["vlc", "mpv", "mplayer", "celluloid", "kodi", "plex",
                        "jellyfin", "spotify", "rhythmbox", "clementine"],
            "keywords": ["video", "audio", "music", "player", "movie", "streaming"],
            "description": "Media players and streaming"
        },
        
        # Graphics
        "graphics": {
            "packages": ["gimp", "inkscape", "blender", "krita", "darktable",
                        "rawtherapee", "digikam", "imagemagick", "gthumb"],
            "keywords": ["image", "photo", "picture", "draw", "paint", "design"],
            "description": "Graphics and image editing"
        },
        
        # Office
        "office": {
            "packages": ["libreoffice", "onlyoffice", "calligra", "abiword",
                        "gnumeric", "thunderbird", "evolution", "kmail"],
            "keywords": ["document", "spreadsheet", "presentation", "word", "excel"],
            "description": "Office and productivity software"
        },
        
        # Security
        "security": {
            "packages": ["keepassxc", "bitwarden", "pass", "gnupg", "age",
                        "openssl", "wireshark", "nmap", "metasploit"],
            "keywords": ["password", "encryption", "vpn", "firewall", "antivirus"],
            "description": "Security and privacy tools"
        },
        
        # System
        "system": {
            "packages": ["htop", "btop", "neofetch", "lm-sensors", "powertop",
                        "iotop", "ncdu", "duf", "dust", "fd", "ripgrep", "exa"],
            "keywords": ["monitor", "process", "disk", "cpu", "memory", "hardware"],
            "description": "System monitoring and utilities"
        },
        
        # Communication
        "communication": {
            "packages": ["discord", "slack", "telegram-desktop", "signal-desktop",
                        "element", "teams", "zoom", "skype", "pidgin", "hexchat"],
            "keywords": ["chat", "message", "call", "video", "conference", "irc"],
            "description": "Communication and messaging"
        },
    }
    
    # Common alternatives mapping
    ALTERNATIVES = {
        "firefox": ["chromium", "brave", "librewolf", "qutebrowser"],
        "chromium": ["firefox", "brave", "ungoogled-chromium", "vivaldi"],
        "vim": ["neovim", "emacs", "vscode", "helix"],
        "vscode": ["vscodium", "vim", "neovim", "emacs", "sublime"],
        "vlc": ["mpv", "mplayer", "celluloid", "kodi"],
        "gimp": ["krita", "inkscape", "darktable"],
        "docker": ["podman", "lxc", "systemd-nspawn"],
        "bash": ["zsh", "fish", "nushell", "elvish"],
        "gnome": ["kde", "xfce", "i3", "sway"],
    }
    
    # Commonly installed together
    COMMONLY_TOGETHER = {
        "firefox": ["thunderbird", "ublock-origin"],
        "vim": ["tmux", "fzf", "ripgrep"],
        "git": ["gh", "tig", "lazygit"],
        "docker": ["docker-compose", "lazydocker"],
        "python3": ["python3-pip", "python3-venv", "ipython"],
        "nodejs": ["yarn", "pnpm", "npm"],
        "vscode": ["vscode-extensions"],
    }


class PackageIntelligence:
    """
    Intelligent package discovery system.
    Understands natural language and provides smart recommendations.
    """
    
    def __init__(self):
        self.categories = PackageCategories()
        self.package_cache = {}
        self.last_search = None
        
    def parse_intent(self, query: str) -> SearchIntent:
        """
        Parse user query to understand intent.
        
        Examples:
        - "I need a text editor" -> category: editor, action: find
        - "alternative to firefox" -> action: alternative, target: firefox
        - "install python" -> action: install, target: python
        """
        query_lower = query.lower()
        
        # Check for alternative requests
        alt_patterns = [
            r"alternative(?:s)? (?:to|for) (\w+)",
            r"(\w+) alternative",
            r"something like (\w+)",
            r"similar to (\w+)",
        ]
        for pattern in alt_patterns:
            if match := re.search(pattern, query_lower):
                target = match.group(1)
                return SearchIntent(
                    query=query,
                    action="alternative",
                    category=self._find_category(target)
                )
        
        # Check for category requests
        category_patterns = [
            r"(?:i need|looking for|want|find me) (?:a|an|some)?\s*(\w+(?:\s+\w+)?)",
            r"best (\w+(?:\s+\w+)?)",
            r"(?:list|show) (?:all )?\s*(\w+(?:\s+\w+)?)",
        ]
        for pattern in category_patterns:
            if match := re.search(pattern, query_lower):
                potential_category = match.group(1)
                if category := self._match_category(potential_category):
                    return SearchIntent(
                        query=query,
                        action="find",
                        category=category
                    )
        
        # Default to search
        return SearchIntent(query=query, action="search")
    
    def _match_category(self, term: str) -> Optional[str]:
        """Match a term to a known category."""
        term_lower = term.lower()
        
        # Direct match
        if term_lower in self.categories.CATEGORIES:
            return term_lower
        
        # Check keywords
        for category, info in self.categories.CATEGORIES.items():
            if term_lower in info["keywords"]:
                return category
            # Partial match on keywords
            if any(term_lower in keyword for keyword in info["keywords"]):
                return category
        
        # Check if term is in category name
        for category in self.categories.CATEGORIES:
            if term_lower in category or category in term_lower:
                return category
        
        return None
    
    def _find_category(self, package: str) -> Optional[str]:
        """Find which category a package belongs to."""
        for category, info in self.categories.CATEGORIES.items():
            if package in info["packages"]:
                return category
        return None
    
    async def search_packages(self, query: str) -> List[PackageInfo]:
        """
        Smart package search with intent understanding.
        """
        try:
            # Parse intent
            intent = self.parse_intent(query)
            
            if intent.action == "alternative":
                # Find alternatives
                return self.find_alternatives(query)
            
            elif intent.category:
                # Category search
                return self.search_by_category(intent.category)
            
            else:
                # Regular search with enhancements
                return await self.enhanced_search(query)
                
        except Exception as e:
            # Log error but don't crash
            import logging
            logging.error(f"Package search error: {e}")
            # Return empty results with error message
            return []
    
    def find_alternatives(self, query: str) -> List[PackageInfo]:
        """Find alternative packages."""
        # Extract package name from query - handle multi-word packages
        package = None
        patterns = [
            r"alternative(?:s)? (?:to|for) ([\w\-]+)",
            r"something like ([\w\-]+)",
            r"similar to ([\w\-]+)",
            r"like ([\w\-]+)",
        ]
        
        for pattern in patterns:
            if match := re.search(pattern, query.lower()):
                package = match.group(1)
                break
        
        if not package:
            return []
        
        # Get alternatives
        alternatives = self.categories.ALTERNATIVES.get(package, [])
        
        results = []
        for alt in alternatives:
            results.append(PackageInfo(
                name=alt,
                version="latest",
                description=f"Alternative to {package}",
                categories=[self._find_category(alt) or "unknown"],
                alternatives=[p for p in alternatives if p != alt],
                popularity=0.8
            ))
        
        return results
    
    def search_by_category(self, category: str) -> List[PackageInfo]:
        """Search packages by category."""
        if category not in self.categories.CATEGORIES:
            return []
        
        cat_info = self.categories.CATEGORIES[category]
        results = []
        
        for pkg in cat_info["packages"]:
            results.append(PackageInfo(
                name=pkg,
                version="latest",
                description=f"Popular {category}",
                categories=[category],
                tags=cat_info["keywords"],
                alternatives=self.categories.ALTERNATIVES.get(pkg, []),
                commonly_with=self.categories.COMMONLY_TOGETHER.get(pkg, []),
                popularity=0.9 if pkg in cat_info["packages"][:3] else 0.7
            ))
        
        return results
    
    async def enhanced_search(self, query: str) -> List[PackageInfo]:
        """
        Enhanced search with multiple strategies.
        """
        results = []
        
        # Strategy 1: Direct package search
        try:
            direct_results = await self._nix_search(query)
            results.extend(direct_results)
        except Exception as e:
            logger.warning(f"Nix search failed: {e}")
        
        # Strategy 2: Category matching
        if category := self._match_category(query):
            cat_results = self.search_by_category(category)
            results.extend(cat_results)
        
        # Strategy 3: Keyword expansion
        expanded_results = await self._search_with_synonyms(query)
        results.extend(expanded_results)
        
        # Deduplicate and rank
        seen = set()
        unique_results = []
        for r in results:
            if r.name not in seen:
                seen.add(r.name)
                unique_results.append(r)
        
        # Sort by relevance/popularity
        unique_results.sort(key=lambda x: x.popularity, reverse=True)
        
        return unique_results[:20]
    
    async def _nix_search(self, query: str) -> List[PackageInfo]:
        """Direct nix search."""
        cache_key = f"search:{query}"
        if cache_key in self.package_cache:
            return self.package_cache[cache_key]
        
        try:
            result = subprocess.run(
                ["nix", "search", "nixpkgs", query, "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                packages = json.loads(result.stdout)
                results = []
                
                for path, info in packages.items():
                    pkg = PackageInfo(
                        name=info.get("pname", path.split(".")[-1]),
                        version=info.get("version", "unknown"),
                        description=info.get("description", ""),
                        categories=[self._find_category(info.get("pname", "")) or "uncategorized"]
                    )
                    results.append(pkg)
                
                self.package_cache[cache_key] = results
                return results
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
        
        return []
    
    async def _search_with_synonyms(self, query: str) -> List[PackageInfo]:
        """Search with synonym expansion."""
        synonyms = {
            "browser": ["web", "internet"],
            "editor": ["ide", "text", "code"],
            "terminal": ["console", "shell"],
            "music": ["audio", "sound"],
            "video": ["movie", "film"],
        }
        
        results = []
        query_lower = query.lower()
        
        for base, syns in synonyms.items():
            if query_lower in syns or base in query_lower:
                cat_results = self.search_by_category(base)
                results.extend(cat_results)
        
        return results
    
    def get_recommendations(self, installed_packages: List[str]) -> List[PackageInfo]:
        """
        Get package recommendations based on what's installed.
        """
        recommendations = []
        seen = set(installed_packages)
        
        for pkg in installed_packages:
            # Get commonly installed together
            if pkg in self.categories.COMMONLY_TOGETHER:
                for rec in self.categories.COMMONLY_TOGETHER[pkg]:
                    if rec not in seen:
                        recommendations.append(PackageInfo(
                            name=rec,
                            version="latest",
                            description=f"Commonly installed with {pkg}",
                            popularity=0.8
                        ))
                        seen.add(rec)
        
        return recommendations[:10]


# Demo and testing
async def demo_package_intelligence():
    """Demonstrate the package intelligence system."""
    
    pi = PackageIntelligence()
    
    print("\n" + "="*60)
    print("🧠 PACKAGE INTELLIGENCE DEMO")
    print("="*60)
    
    # Test queries
    test_queries = [
        "I need a text editor",
        "alternative to firefox",
        "best terminal",
        "something like photoshop",
        "python development tools",
        "music player",
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        # Parse intent
        intent = pi.parse_intent(query)
        print(f"🎯 Intent: action={intent.action}, category={intent.category}")
        
        # Search
        results = await pi.search_packages(query)
        
        # Display results
        if results:
            print(f"📦 Found {len(results)} packages:")
            for i, pkg in enumerate(results[:5], 1):
                print(f"  {i}. {pkg.name} - {pkg.description[:50]}...")
                if pkg.alternatives:
                    print(f"     Alternatives: {', '.join(pkg.alternatives[:3])}")
                if pkg.commonly_with:
                    print(f"     Install with: {', '.join(pkg.commonly_with[:3])}")
        else:
            print("  No packages found")
    
    # Test recommendations
    print("\n" + "="*40)
    print("📊 Recommendations based on installed packages:")
    print("-" * 40)
    
    installed = ["firefox", "vim", "git", "python3"]
    print(f"Installed: {', '.join(installed)}")
    
    recommendations = pi.get_recommendations(installed)
    print("Recommended:")
    for rec in recommendations:
        print(f"  • {rec.name} - {rec.description}")


if __name__ == "__main__":
    asyncio.run(demo_package_intelligence())