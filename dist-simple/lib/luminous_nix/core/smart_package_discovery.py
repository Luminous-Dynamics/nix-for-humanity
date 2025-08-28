#!/usr/bin/env python3
"""
🔍 Smart Package Discovery - Intelligent Package Finding
Uses fuzzy matching and semantic understanding to find packages
"""

import difflib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class PackageMatch:
    """Represents a package match with confidence"""
    name: str
    description: str
    confidence: float  # 0.0 to 1.0
    match_reason: str  # Why this was suggested


class SmartPackageDiscovery:
    """
    Intelligent package discovery with fuzzy matching
    Helps users find packages even with imperfect queries
    """
    
    def __init__(self):
        # Common package aliases and alternatives
        self.package_aliases = {
            # Editors
            'editor': ['vim', 'neovim', 'emacs', 'nano', 'vscode', 'sublime-text'],
            'vim': ['neovim', 'vim', 'gvim'],
            'code': ['vscode', 'vscodium', 'sublime-text', 'atom'],
            
            # Browsers
            'browser': ['firefox', 'chromium', 'brave', 'vivaldi'],
            'chrome': ['chromium', 'google-chrome', 'brave'],
            
            # Terminals
            'terminal': ['alacritty', 'kitty', 'wezterm', 'terminator', 'gnome-terminal'],
            
            # Development
            'python': ['python3', 'python311', 'python312', 'python313'],
            'node': ['nodejs', 'nodejs_18', 'nodejs_20'],
            'java': ['jdk', 'openjdk', 'temurin-bin'],
            
            # Media
            'music': ['spotify', 'rhythmbox', 'clementine', 'audacious'],
            'video': ['vlc', 'mpv', 'mplayer', 'celluloid'],
            'photo': ['gimp', 'inkscape', 'krita', 'darktable'],
            'photoshop': ['gimp', 'krita', 'inkscape'],
            
            # System
            'docker': ['docker', 'podman'],
            'vm': ['virtualbox', 'qemu', 'virt-manager'],
            'vpn': ['openvpn', 'wireguard', 'tailscale'],
            
            # Office
            'office': ['libreoffice', 'onlyoffice', 'wps-office'],
            'word': ['libreoffice-writer', 'abiword'],
            'excel': ['libreoffice-calc', 'gnumeric'],
            
            # Communication
            'chat': ['discord', 'slack', 'element', 'telegram-desktop'],
            'email': ['thunderbird', 'evolution', 'geary'],
            
            # Utilities
            'archive': ['p7zip', 'unzip', 'ark', 'file-roller'],
            'backup': ['restic', 'borg', 'duplicity'],
            'password': ['keepassxc', 'bitwarden', '1password'],
        }
        
        # Semantic categories for better suggestions
        self.categories = {
            'development': ['git', 'gcc', 'make', 'cmake', 'cargo', 'go', 'rustc'],
            'productivity': ['obsidian', 'notion', 'joplin', 'logseq', 'zettlr'],
            'security': ['nmap', 'wireshark', 'metasploit', 'john', 'hashcat'],
            'graphics': ['blender', 'freecad', 'openscad', 'godot'],
            'science': ['octave', 'scilab', 'R', 'julia', 'sage'],
            'gaming': ['steam', 'lutris', 'wine', 'proton'],
        }
        
        # Common misspellings
        self.common_misspellings = {
            'fierefox': 'firefox',
            'firfox': 'firefox',
            'chrom': 'chromium',
            'viscode': 'vscode',
            'pythn': 'python',
            'dokcer': 'docker',
            'kubernets': 'kubernetes',
            'postgre': 'postgresql',
            'mysql': 'mariadb',  # Common alternative
        }
    
    def find_packages(
        self,
        query: str,
        available_packages: Optional[List[Dict[str, str]]] = None
    ) -> List[PackageMatch]:
        """
        Find packages using multiple strategies
        Returns sorted list by confidence
        """
        query_lower = query.lower().strip()
        matches = []
        
        # Strategy 1: Check for common misspellings
        if query_lower in self.common_misspellings:
            corrected = self.common_misspellings[query_lower]
            matches.append(PackageMatch(
                name=corrected,
                description=f"Corrected from '{query}'",
                confidence=0.95,
                match_reason="Spelling correction"
            ))
        
        # Strategy 2: Check aliases
        if query_lower in self.package_aliases:
            for alias in self.package_aliases[query_lower]:
                matches.append(PackageMatch(
                    name=alias,
                    description=f"Alternative for {query}",
                    confidence=0.9,
                    match_reason="Known alternative"
                ))
        
        # Strategy 3: Fuzzy matching on available packages
        if available_packages:
            fuzzy_matches = self._fuzzy_match_packages(query_lower, available_packages)
            matches.extend(fuzzy_matches)
        
        # Strategy 4: Category-based suggestions
        category_matches = self._find_by_category(query_lower)
        matches.extend(category_matches)
        
        # Strategy 5: Semantic understanding
        semantic_matches = self._semantic_search(query_lower)
        matches.extend(semantic_matches)
        
        # Remove duplicates and sort by confidence
        unique_matches = self._deduplicate_matches(matches)
        return sorted(unique_matches, key=lambda x: x.confidence, reverse=True)
    
    def _fuzzy_match_packages(
        self,
        query: str,
        packages: List[Dict[str, str]]
    ) -> List[PackageMatch]:
        """Fuzzy match against available packages"""
        matches = []
        
        for package in packages:
            name = package.get('name', '')
            description = package.get('description', '')
            
            # Name similarity
            name_ratio = difflib.SequenceMatcher(None, query, name.lower()).ratio()
            
            # Description contains query
            desc_match = query in description.lower()
            
            if name_ratio > 0.6:
                matches.append(PackageMatch(
                    name=name,
                    description=description[:100],
                    confidence=name_ratio,
                    match_reason="Name similarity"
                ))
            elif desc_match and name_ratio > 0.3:
                matches.append(PackageMatch(
                    name=name,
                    description=description[:100],
                    confidence=0.5 + (name_ratio * 0.3),
                    match_reason="Description match"
                ))
        
        return matches
    
    def _find_by_category(self, query: str) -> List[PackageMatch]:
        """Find packages by category"""
        matches = []
        
        # Check if query matches a category
        for category, packages in self.categories.items():
            if category in query or query in category:
                for package in packages[:3]:  # Top 3 from category
                    matches.append(PackageMatch(
                        name=package,
                        description=f"Popular in {category}",
                        confidence=0.7,
                        match_reason=f"{category.title()} tool"
                    ))
        
        return matches
    
    def _semantic_search(self, query: str) -> List[PackageMatch]:
        """Semantic understanding of user intent"""
        matches = []
        
        # Parse intent patterns
        patterns = {
            r'like\s+(\w+)': self._find_similar_to,
            r'alternative\s+to\s+(\w+)': self._find_alternative_to,
            r'for\s+(\w+)': self._find_for_purpose,
            r'to\s+(\w+)': self._find_to_action,
        }
        
        for pattern, handler in patterns.items():
            match = re.search(pattern, query)
            if match:
                target = match.group(1)
                semantic_matches = handler(target)
                matches.extend(semantic_matches)
        
        return matches
    
    def _find_similar_to(self, target: str) -> List[PackageMatch]:
        """Find packages similar to target"""
        if target in self.package_aliases:
            return [
                PackageMatch(
                    name=alt,
                    description=f"Similar to {target}",
                    confidence=0.8,
                    match_reason="Similar software"
                )
                for alt in self.package_aliases[target][:2]
            ]
        return []
    
    def _find_alternative_to(self, target: str) -> List[PackageMatch]:
        """Find alternatives to target"""
        return self._find_similar_to(target)  # Same logic for now
    
    def _find_for_purpose(self, purpose: str) -> List[PackageMatch]:
        """Find packages for a specific purpose"""
        purpose_packages = {
            'coding': ['vscode', 'neovim', 'emacs'],
            'writing': ['libreoffice-writer', 'typora', 'obsidian'],
            'drawing': ['krita', 'inkscape', 'gimp'],
            'gaming': ['steam', 'lutris', 'wine'],
            'streaming': ['obs-studio', 'kdenlive', 'davinci-resolve'],
        }
        
        if purpose in purpose_packages:
            return [
                PackageMatch(
                    name=pkg,
                    description=f"Good for {purpose}",
                    confidence=0.75,
                    match_reason=f"Recommended for {purpose}"
                )
                for pkg in purpose_packages[purpose][:2]
            ]
        return []
    
    def _find_to_action(self, action: str) -> List[PackageMatch]:
        """Find packages to perform an action"""
        action_packages = {
            'edit': ['vim', 'neovim', 'nano'],
            'browse': ['firefox', 'chromium', 'brave'],
            'code': ['vscode', 'sublime-text', 'atom'],
            'watch': ['vlc', 'mpv', 'celluloid'],
            'listen': ['spotify', 'rhythmbox', 'clementine'],
        }
        
        if action in action_packages:
            return [
                PackageMatch(
                    name=pkg,
                    description=f"To {action}",
                    confidence=0.7,
                    match_reason=f"Can {action}"
                )
                for pkg in action_packages[action][:2]
            ]
        return []
    
    def _deduplicate_matches(self, matches: List[PackageMatch]) -> List[PackageMatch]:
        """Remove duplicate matches, keeping highest confidence"""
        seen = {}
        for match in matches:
            if match.name not in seen or match.confidence > seen[match.name].confidence:
                seen[match.name] = match
        return list(seen.values())
    
    def suggest_correction(self, query: str) -> Optional[str]:
        """Suggest a spelling correction for the query"""
        query_lower = query.lower()
        
        # Check direct misspellings
        if query_lower in self.common_misspellings:
            return self.common_misspellings[query_lower]
        
        # Check close matches to known packages
        all_known = set()
        for aliases in self.package_aliases.values():
            all_known.update(aliases)
        all_known.update(self.package_aliases.keys())
        
        # Find closest match
        close_matches = difflib.get_close_matches(query_lower, all_known, n=1, cutoff=0.6)
        if close_matches:
            return close_matches[0]
        
        return None


# Global instance
_DISCOVERY: Optional[SmartPackageDiscovery] = None

def get_smart_discovery() -> SmartPackageDiscovery:
    """Get or create smart discovery instance"""
    global _DISCOVERY
    if _DISCOVERY is None:
        _DISCOVERY = SmartPackageDiscovery()
    return _DISCOVERY


if __name__ == "__main__":
    # Test the smart discovery
    discovery = get_smart_discovery()
    
    test_queries = [
        "fierefox",  # Misspelling
        "text editor",  # Category
        "like photoshop",  # Semantic
        "alternative to chrome",  # Alternative
        "for coding",  # Purpose
        "to watch videos",  # Action
    ]
    
    print("🔍 Testing Smart Package Discovery\n")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        
        matches = discovery.find_packages(query)
        
        if matches:
            for match in matches[:3]:  # Top 3
                print(f"  {match.name} ({match.confidence:.0%})")
                print(f"    → {match.match_reason}")
        else:
            # Try correction
            correction = discovery.suggest_correction(query)
            if correction:
                print(f"  Did you mean: {correction}?")
            else:
                print("  No matches found")
        
        print("=" * 60)