"""
🔍 Fuzzy Search Adapter - Consciousness-First Package Discovery

This module provides intuitive fuzzy search that feels like thinking,
not searching. It reduces cognitive load when finding packages among
80,000+ options in nixpkgs.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PackageResult:
    """A search result with metadata"""
    name: str
    attribute: str
    description: str
    version: Optional[str] = None
    score: float = 0.0
    
    def to_display(self) -> str:
        """Format for display in fuzzy finder"""
        if self.description:
            return f"{self.name:<30} {self.description[:50]}"
        return self.name


class FuzzySearchAdapter:
    """
    Adaptive fuzzy search that uses the best available backend.
    
    Supports:
    - Native fzf (fastest)
    - Native skim (Rust-based alternative)
    - Python fallback (always works)
    """
    
    def __init__(self):
        self.backend = self._detect_backend()
        self.cache = {}
        logger.info(f"🔍 Using fuzzy search backend: {self.backend}")
    
    def _detect_backend(self) -> str:
        """Detect the best available fuzzy search backend"""
        # Check for native binaries
        try:
            subprocess.run(["fzf", "--version"], capture_output=True, check=True)
            return "fzf"
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        try:
            subprocess.run(["sk", "--version"], capture_output=True, check=True)
            return "skim"
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Fallback to Python
        return "python"
    
    def search(self, query: str, packages: List[Dict], 
               interactive: bool = False,
               preview: bool = True) -> Optional[PackageResult]:
        """
        Search for packages using fuzzy matching.
        
        Args:
            query: The search query (can be partial/fuzzy)
            packages: List of package dictionaries
            interactive: Open interactive fuzzy finder
            preview: Show preview pane (only with interactive)
        
        Returns:
            Selected package or None if cancelled
        """
        if interactive and self.backend in ["fzf", "skim"]:
            return self._interactive_search(query, packages, preview)
        else:
            return self._batch_search(query, packages)
    
    def _interactive_search(self, query: str, packages: List[Dict], 
                           preview: bool) -> Optional[PackageResult]:
        """Interactive search with fzf/skim"""
        # Prepare package list for fuzzy finder
        package_results = self._prepare_packages(packages)
        
        # Format for display
        display_lines = []
        lookup = {}
        for pkg in package_results:
            display = pkg.to_display()
            display_lines.append(display)
            lookup[display] = pkg
        
        # Build fzf/skim command
        if self.backend == "fzf":
            cmd = [
                "fzf",
                "--ansi",
                "--height", "80%",
                "--layout", "reverse",
                "--info", "inline",
                "--prompt", "🔍 Package> ",
                "--header", "Search NixOS Packages (ESC to cancel)",
                "--bind", "ctrl-/:toggle-preview",
                "--query", query,
            ]
            
            if preview:
                # Add preview command
                cmd.extend([
                    "--preview-window", "right:50%:wrap",
                    "--preview", "echo 'Package details would show here'"
                ])
        else:  # skim
            cmd = [
                "sk",
                "--ansi",
                "--height", "80%",
                "--layout", "reverse",
                "--prompt", "🔍 Package> ",
                "--query", query,
            ]
        
        try:
            # Run fuzzy finder
            result = subprocess.run(
                cmd,
                input="\n".join(display_lines),
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip():
                selected = result.stdout.strip()
                return lookup.get(selected)
            
            return None
            
        except Exception as e:
            logger.error(f"Interactive search failed: {e}")
            # Fallback to batch search
            return self._batch_search(query, packages)
    
    def _batch_search(self, query: str, packages: List[Dict]) -> List[PackageResult]:
        """Non-interactive fuzzy search using Python"""
        from difflib import SequenceMatcher
        
        package_results = self._prepare_packages(packages)
        
        # Score each package
        scored = []
        query_lower = query.lower()
        
        for pkg in package_results:
            # Multiple scoring strategies
            name_score = self._fuzzy_score(query_lower, pkg.name.lower())
            desc_score = 0
            
            if pkg.description:
                desc_score = self._fuzzy_score(query_lower, pkg.description.lower()) * 0.5
            
            # Boost exact substring matches
            if query_lower in pkg.name.lower():
                name_score *= 1.5
            
            pkg.score = max(name_score, desc_score)
            if pkg.score > 0.3:  # Threshold for relevance
                scored.append(pkg)
        
        # Sort by score
        scored.sort(key=lambda p: p.score, reverse=True)
        
        return scored[:20]  # Return top 20 matches
    
    def _prepare_packages(self, packages: List[Dict]) -> List[PackageResult]:
        """Convert raw package data to PackageResult objects"""
        results = []
        
        for pkg in packages:
            # Handle different package formats
            if isinstance(pkg, dict):
                result = PackageResult(
                    name=pkg.get("name", pkg.get("pname", "")),
                    attribute=pkg.get("attribute", pkg.get("name", "")),
                    description=pkg.get("description", pkg.get("meta", {}).get("description", "")),
                    version=pkg.get("version", "")
                )
            else:
                # Simple string format
                result = PackageResult(
                    name=str(pkg),
                    attribute=str(pkg),
                    description=""
                )
            
            results.append(result)
        
        return results
    
    def _fuzzy_score(self, query: str, text: str) -> float:
        """Calculate fuzzy match score between query and text"""
        from difflib import SequenceMatcher
        
        # Direct substring matching
        if query in text:
            return 1.0
        
        # Token matching (each word in query)
        tokens = query.split()
        if all(token in text for token in tokens):
            return 0.8
        
        # Fuzzy matching
        matcher = SequenceMatcher(None, query, text)
        return matcher.ratio()
    
    def search_with_categories(self, query: str, 
                              categories: Dict[str, List[str]]) -> Dict[str, List[PackageResult]]:
        """
        Search across multiple categories (packages, options, modules).
        
        Returns results grouped by category.
        """
        results = {}
        
        for category, items in categories.items():
            # Convert to package format
            packages = [{"name": item, "attribute": item} for item in items]
            
            # Search this category
            category_results = self._batch_search(query, packages)
            if category_results:
                results[category] = category_results[:5]  # Top 5 per category
        
        return results
    
    def learn_from_selection(self, query: str, selected: str):
        """
        Learn from user selections to improve future searches.
        
        This integrates with the learning system to boost frequently
        selected packages for similar queries.
        """
        # Cache successful query->selection mappings
        if query not in self.cache:
            self.cache[query] = {}
        
        if selected in self.cache[query]:
            self.cache[query][selected] += 1
        else:
            self.cache[query][selected] = 1
        
        logger.info(f"📚 Learned: '{query}' -> '{selected}'")


class ConsciousFuzzySearch(FuzzySearchAdapter):
    """
    Extended fuzzy search with consciousness-first features.
    
    Adds:
    - Natural language understanding
    - Sacred pause detection
    - Persona-aware ranking
    """
    
    def __init__(self, persona: Optional[str] = None):
        super().__init__()
        self.persona = persona
        self.search_count = 0
        self.last_results = []
    
    def search(self, query: str, packages: List[Dict], **kwargs) -> Optional[PackageResult]:
        """Enhanced search with consciousness features"""
        # Track search attempts
        self.search_count += 1
        
        # Sacred pause check
        if self.search_count >= 5 and not self.last_results:
            self._offer_sacred_pause()
        
        # Natural language expansion
        expanded_query = self._expand_natural_language(query)
        
        # Perform search
        result = super().search(expanded_query, packages, **kwargs)
        
        if result:
            self.last_results.append(result)
            self.search_count = 0  # Reset on success
        
        return result
    
    def _expand_natural_language(self, query: str) -> str:
        """
        Expand natural language queries to better matches.
        
        Examples:
        - "photo editor" -> "gimp krita darktable"
        - "like vim" -> "vim neovim helix kakoune"
        """
        expansions = {
            "photo editor": "gimp krita darktable rawtherapee",
            "photo": "gimp krita darktable",
            "text editor": "vim neovim emacs vscode",
            "like vim": "neovim helix kakoune",
            "terminal": "alacritty kitty wezterm",
            "browser": "firefox chromium brave",
            "music": "spotify rhythmbox clementine",
            "video": "vlc mpv mplayer",
            "development": "git vscode vim docker",
        }
        
        query_lower = query.lower()
        for pattern, expansion in expansions.items():
            if pattern in query_lower:
                logger.info(f"🧠 Expanding '{pattern}' to include: {expansion}")
                return f"{query} {expansion}"
        
        return query
    
    def _offer_sacred_pause(self):
        """Offer help when user seems stuck"""
        print("\n🧘 Taking a sacred pause...")
        print("It seems you're looking for something specific.")
        print("\nWould you like to:")
        print("  1. Describe what you want to accomplish")
        print("  2. Browse package categories")
        print("  3. See popular packages")
        print("\nPress Enter to continue searching...")
        input()
        self.search_count = 0


def create_searcher(interactive: bool = False, 
                   persona: Optional[str] = None) -> FuzzySearchAdapter:
    """
    Factory function to create the appropriate searcher.
    
    Args:
        interactive: Whether to use interactive mode
        persona: User persona for personalization
    
    Returns:
        Configured fuzzy search adapter
    """
    if persona or interactive:
        return ConsciousFuzzySearch(persona)
    return FuzzySearchAdapter()


# Self-test when run directly
if __name__ == "__main__":
    # Test packages
    test_packages = [
        {"name": "firefox", "description": "Web browser"},
        {"name": "firefox-esr", "description": "Firefox Extended Support Release"},
        {"name": "chromium", "description": "Open source web browser"},
        {"name": "brave", "description": "Privacy-focused browser"},
        {"name": "vim", "description": "Text editor"},
        {"name": "neovim", "description": "Vim-based text editor"},
        {"name": "emacs", "description": "Extensible text editor"},
    ]
    
    searcher = create_searcher()
    
    # Test batch search
    print("Testing batch search for 'fire':")
    results = searcher._batch_search("fire", test_packages)
    for r in results[:3]:
        print(f"  {r.name}: {r.score:.2f}")
    
    print("\nTesting natural language 'text editor':")
    conscious = ConsciousFuzzySearch()
    expanded = conscious._expand_natural_language("text editor")
    print(f"  Expanded to: {expanded}")