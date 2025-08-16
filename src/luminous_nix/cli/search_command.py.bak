"""
🔍 Search Command - Fuzzy package discovery for the CLI

This integrates fuzzy search into the main ask-nix CLI.
"""

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

from ..search import create_searcher, PackageResult

logger = logging.getLogger(__name__)


class SearchCommand:
    """
    Handles package search with fuzzy finding.
    
    Supports both interactive (with fzf) and batch modes.
    """
    
    def __init__(self):
        self.searcher = None
        self._package_cache = None
    
    def _get_packages(self) -> List[Dict]:
        """Get all available packages (with caching)"""
        if self._package_cache is None:
            logger.info("📦 Loading package database...")
            
            # Try to get packages from nix (using faster method)
            try:
                # First try to use cached package list if available
                cache_file = Path.home() / ".cache" / "nix-for-humanity" / "packages.json"
                
                if cache_file.exists() and cache_file.stat().st_mtime > (time.time() - 86400):
                    # Cache is less than 24 hours old
                    with open(cache_file) as f:
                        packages_dict = json.load(f)
                    logger.info("📦 Using cached package list")
                else:
                    # Get fresh package list (limited to common packages for speed)
                    result = subprocess.run(
                        ["nix-env", "-qaP", "--description"],
                        capture_output=True,
                        text=True,
                        timeout=5  # Much shorter timeout
                    )
                
                if result.returncode == 0:
                    packages_dict = json.loads(result.stdout)
                    # Convert to list format
                    self._package_cache = [
                        {
                            "name": name,
                            "attribute": name,
                            "version": info.get("version", ""),
                            "description": info.get("meta", {}).get("description", "")
                        }
                        for name, info in packages_dict.items()
                    ]
                else:
                    # Fallback to basic package list
                    self._package_cache = self._get_fallback_packages()
                    
            except Exception as e:
                logger.warning(f"Could not load full package list: {e}")
                self._package_cache = self._get_fallback_packages()
        
        return self._package_cache
    
    def _get_fallback_packages(self) -> List[Dict]:
        """Get a curated list of common packages as fallback"""
        return [
            # Browsers
            {"name": "firefox", "description": "Free and open source web browser"},
            {"name": "chromium", "description": "Open source web browser from Google"},
            {"name": "brave", "description": "Privacy-focused web browser"},
            
            # Editors
            {"name": "vim", "description": "Highly configurable text editor"},
            {"name": "neovim", "description": "Vim-fork focused on extensibility"},
            {"name": "emacs", "description": "Extensible, customizable text editor"},
            {"name": "vscode", "description": "Code editor from Microsoft"},
            {"name": "sublime3", "description": "Sophisticated text editor"},
            
            # Development
            {"name": "git", "description": "Distributed version control system"},
            {"name": "docker", "description": "Container platform"},
            {"name": "nodejs", "description": "JavaScript runtime"},
            {"name": "python3", "description": "Python programming language"},
            {"name": "rustc", "description": "Rust compiler"},
            {"name": "go", "description": "Go programming language"},
            
            # Terminal
            {"name": "alacritty", "description": "GPU-accelerated terminal"},
            {"name": "kitty", "description": "Modern terminal emulator"},
            {"name": "tmux", "description": "Terminal multiplexer"},
            {"name": "zsh", "description": "Powerful shell"},
            
            # Media
            {"name": "vlc", "description": "Media player"},
            {"name": "mpv", "description": "Minimalist media player"},
            {"name": "gimp", "description": "Image editor"},
            {"name": "krita", "description": "Digital painting"},
            {"name": "obs-studio", "description": "Video recording and streaming"},
            
            # System
            {"name": "htop", "description": "Interactive process viewer"},
            {"name": "btop", "description": "Resource monitor"},
            {"name": "neofetch", "description": "System info tool"},
            {"name": "tree", "description": "Directory listing"},
            {"name": "ripgrep", "description": "Fast text search"},
            {"name": "fd", "description": "Simple, fast alternative to find"},
            {"name": "bat", "description": "Cat clone with syntax highlighting"},
            {"name": "eza", "description": "Modern ls replacement"},
        ]
    
    def search(self, query: str, interactive: bool = False, 
               limit: int = 10, show_all: bool = False) -> List[PackageResult]:
        """
        Search for packages.
        
        Args:
            query: Search query (can be fuzzy)
            interactive: Open interactive fuzzy finder
            limit: Maximum results to return (batch mode)
            show_all: Show all matches, not just top ones
        
        Returns:
            List of matching packages
        """
        # Create searcher if needed
        if self.searcher is None:
            self.searcher = create_searcher(interactive=interactive)
        
        # Get packages
        packages = self._get_packages()
        
        if interactive:
            # Interactive search returns single result
            result = self.searcher.search(query, packages, interactive=True)
            return [result] if result else []
        else:
            # Batch search returns multiple results
            results = self.searcher._batch_search(query, packages)
            
            if not show_all:
                results = results[:limit]
            
            return results
    
    def search_with_install(self, query: str, interactive: bool = True) -> Optional[str]:
        """
        Search for a package and optionally install it.
        
        Returns the selected package name or None.
        """
        results = self.search(query, interactive=interactive, limit=1)
        
        if not results:
            print("No packages found.")
            return None
        
        if interactive:
            # Already selected in interactive mode
            selected = results[0]
        else:
            # Show results and ask for selection
            print("\n🔍 Search Results:")
            for i, pkg in enumerate(results[:5], 1):
                print(f"  {i}. {pkg.name:<20} {pkg.description[:50]}")
            
            print("\nSelect package number (or 0 to cancel): ", end="")
            try:
                choice = int(input())
                if 0 < choice <= len(results[:5]):
                    selected = results[choice - 1]
                else:
                    return None
            except (ValueError, KeyboardInterrupt):
                return None
        
        # Ask to install
        print(f"\n📦 Selected: {selected.name}")
        if selected.description:
            print(f"   {selected.description}")
        
        print("\nInstall this package? [y/N]: ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            return selected.attribute or selected.name
        
        return None


def handle_search_in_query(query: str) -> bool:
    """
    Check if a query is search-related and handle it.
    
    Returns True if handled, False otherwise.
    """
    search_keywords = [
        "search", "find", "look for", "discover",
        "what packages", "which packages", "list packages"
    ]
    
    query_lower = query.lower()
    
    # Check if this is a search query
    is_search = any(keyword in query_lower for keyword in search_keywords)
    
    if not is_search:
        return False
    
    # Extract search term
    for keyword in search_keywords:
        if keyword in query_lower:
            # Get everything after the keyword
            search_term = query_lower.split(keyword)[-1].strip()
            
            # Remove common words
            for word in ["for", "packages", "package", "me", "a", "an", "the"]:
                search_term = search_term.replace(word, "").strip()
            
            if search_term:
                # Perform search
                cmd = SearchCommand()
                
                # Check if user wants interactive mode
                interactive = "--interactive" in query or "-i" in query
                
                results = cmd.search(search_term, interactive=interactive)
                
                if results:
                    if interactive and len(results) == 1:
                        # Interactive mode selected something
                        print(f"✅ Selected: {results[0].name}")
                    else:
                        # Show results
                        print(f"\n🔍 Found {len(results)} packages for '{search_term}':\n")
                        for pkg in results[:10]:
                            desc = pkg.description[:50] if pkg.description else ""
                            print(f"  • {pkg.name:<25} {desc}")
                        
                        if len(results) > 10:
                            print(f"\n  ... and {len(results) - 10} more")
                else:
                    print(f"No packages found for '{search_term}'")
                
                return True
    
    return False


# Integration function for the main CLI
def add_search_to_cli(cli):
    """Add search command to the main CLI"""
    try:
        import click
        
        @cli.command()
        @click.argument("query", nargs=-1, required=True)
        @click.option("-i", "--interactive", is_flag=True, 
                     help="Interactive fuzzy search with fzf")
        @click.option("-l", "--limit", default=10, 
                     help="Maximum results to show")
        @click.option("-a", "--all", "show_all", is_flag=True,
                     help="Show all matches")
        @click.option("--install", is_flag=True,
                     help="Offer to install selected package")
        def search(query, interactive, limit, show_all, install):
            """Search for NixOS packages with fuzzy matching"""
            query_str = " ".join(query)
            
            cmd = SearchCommand()
            
            if install:
                package = cmd.search_with_install(query_str, interactive)
                if package:
                    print(f"\n📦 To install: nix-env -iA nixos.{package}")
                    print(f"   Or add to configuration.nix: {package}")
            else:
                results = cmd.search(query_str, interactive, limit, show_all)
                
                if results:
                    print(f"\n🔍 Search results for '{query_str}':\n")
                    for pkg in results:
                        desc = pkg.description[:60] if pkg.description else ""
                        print(f"  {pkg.name:<25} {desc}")
                else:
                    print(f"No packages found for '{query_str}'")
        
        return search
        
    except ImportError:
        # Click not available, return None
        return None


if __name__ == "__main__":
    # Test the search command
    import sys
    
    cmd = SearchCommand()
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Searching for: {query}")
        
        results = cmd.search(query, interactive=False)
        
        for pkg in results[:5]:
            print(f"  {pkg.name}: {pkg.description[:50] if pkg.description else 'No description'}")