"""
Search caching system for fast package lookups
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import hashlib

class SearchCache:
    """
    Persistent search cache to avoid timeouts
    
    Features:
    - Local JSON cache with TTL
    - Fuzzy matching on cached data
    - Background refresh
    - Instant results for common searches
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize search cache"""
        self.cache_dir = cache_dir or (Path.home() / ".cache/luminous-nix")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.search_cache_file = self.cache_dir / "search_cache.json"
        self.package_db_file = self.cache_dir / "package_db.json"
        
        # Cache settings
        self.search_ttl = timedelta(hours=24)
        self.db_ttl = timedelta(days=7)
        
        # Common searches to pre-cache
        self.common_terms = [
            'browser', 'editor', 'terminal', 'python', 'git',
            'docker', 'nodejs', 'rust', 'gcc', 'vim', 'emacs',
            'firefox', 'chromium', 'vscode', 'neovim'
        ]
        
    def get_cached_search(self, term: str) -> Optional[List[Dict[str, str]]]:
        """Get cached search results if available and fresh"""
        if not self.search_cache_file.exists():
            return None
            
        try:
            cache = json.loads(self.search_cache_file.read_text())
            
            # Create cache key
            cache_key = self._make_cache_key(term)
            
            if cache_key in cache:
                entry = cache[cache_key]
                cached_time = datetime.fromisoformat(entry['timestamp'])
                
                # Check if cache is still valid
                if datetime.now() - cached_time < self.search_ttl:
                    return entry['results']
                    
        except Exception as e:
            print(f"Cache read error: {e}")
            
        return None
        
    def cache_search_results(self, term: str, results: List[Dict[str, str]]):
        """Cache search results"""
        cache = {}
        
        # Load existing cache
        if self.search_cache_file.exists():
            try:
                cache = json.loads(self.search_cache_file.read_text())
            except:
                pass
                
        # Add new entry
        cache_key = self._make_cache_key(term)
        cache[cache_key] = {
            'term': term,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cleanup old entries
        self._cleanup_old_entries(cache)
        
        # Save cache
        self.search_cache_file.write_text(json.dumps(cache, indent=2))
        
    def search_with_cache(self, term: str, timeout: int = 5) -> List[Dict[str, str]]:
        """
        Search with caching - returns cached results or performs new search
        
        Returns list of dicts with 'name' and 'description' keys
        """
        # Check cache first
        cached = self.get_cached_search(term)
        if cached:
            print(f"📦 Using cached results for '{term}'")
            return cached
            
        # Perform actual search
        print(f"🔍 Searching packages for '{term}'...")
        results = self._perform_search(term, timeout)
        
        # Cache results
        if results:
            self.cache_search_results(term, results)
            
        return results
        
    def _perform_search(self, term: str, timeout: int) -> List[Dict[str, str]]:
        """Perform actual nix search"""
        results = []
        
        try:
            # Try nix search first (newer)
            result = subprocess.run(
                ['nix', 'search', 'nixpkgs', term, '--json'],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse JSON output
                try:
                    data = json.loads(result.stdout)
                    for key, info in data.items():
                        # Extract package name from the key
                        name = key.split('.')[-1]
                        results.append({
                            'name': name,
                            'description': info.get('description', ''),
                            'version': info.get('version', '')
                        })
                except json.JSONDecodeError:
                    # Fallback to line parsing
                    results = self._parse_text_results(result.stdout)
                    
        except subprocess.TimeoutExpired:
            print(f"⏱️ Search timed out after {timeout}s, trying fuzzy match on cached packages...")
            results = self.fuzzy_search_cached(term)
            
        except Exception as e:
            print(f"Search error: {e}")
            
        return results[:20]  # Limit results
        
    def _parse_text_results(self, output: str) -> List[Dict[str, str]]:
        """Parse text search output"""
        results = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if line.startswith('* '):
                # Parse line like: * nixpkgs.firefox (93.0): Web browser
                parts = line[2:].split(':', 1)
                if len(parts) == 2:
                    name_part = parts[0].strip()
                    description = parts[1].strip()
                    
                    # Extract package name
                    if '.' in name_part:
                        name = name_part.split('.')[-1]
                    else:
                        name = name_part.split()[0]
                        
                    results.append({
                        'name': name,
                        'description': description
                    })
                    
        return results
        
    def fuzzy_search_cached(self, term: str) -> List[Dict[str, str]]:
        """Fuzzy search on cached package database"""
        if not self.package_db_file.exists():
            self.build_package_database()
            
        try:
            db = json.loads(self.package_db_file.read_text())
            
            # Check if database is fresh
            db_time = datetime.fromisoformat(db['timestamp'])
            if datetime.now() - db_time > self.db_ttl:
                print("Package database is stale, rebuilding...")
                self.build_package_database()
                db = json.loads(self.package_db_file.read_text())
                
            # Fuzzy search
            term_lower = term.lower()
            matches = []
            
            for pkg in db['packages']:
                name = pkg['name'].lower()
                desc = pkg.get('description', '').lower()
                
                # Score based on match quality
                score = 0
                if term_lower == name:
                    score = 100
                elif term_lower in name:
                    score = 50
                elif term_lower in desc:
                    score = 25
                elif any(word in name for word in term_lower.split()):
                    score = 10
                elif any(word in desc for word in term_lower.split()):
                    score = 5
                    
                if score > 0:
                    matches.append((score, pkg))
                    
            # Sort by score and return top matches
            matches.sort(key=lambda x: x[0], reverse=True)
            return [pkg for _, pkg in matches[:20]]
            
        except Exception as e:
            print(f"Fuzzy search error: {e}")
            return []
            
    def build_package_database(self):
        """Build local package database for fast searching"""
        print("🔨 Building package database (this may take a minute)...")
        
        packages = []
        
        # Get common packages
        for term in self.common_terms:
            results = self._perform_search(term, timeout=10)
            for result in results:
                # Avoid duplicates
                if not any(p['name'] == result['name'] for p in packages):
                    packages.append(result)
                    
        # Save database
        db = {
            'packages': packages,
            'timestamp': datetime.now().isoformat(),
            'count': len(packages)
        }
        
        self.package_db_file.write_text(json.dumps(db, indent=2))
        print(f"✅ Package database built with {len(packages)} packages")
        
    def pre_cache_common_searches(self):
        """Pre-cache common search terms"""
        print("📦 Pre-caching common searches...")
        
        for term in self.common_terms:
            if not self.get_cached_search(term):
                results = self._perform_search(term, timeout=10)
                if results:
                    self.cache_search_results(term, results)
                    print(f"  ✓ Cached '{term}'")
                    
    def _make_cache_key(self, term: str) -> str:
        """Create cache key from search term"""
        return hashlib.md5(term.lower().strip().encode()).hexdigest()
        
    def _cleanup_old_entries(self, cache: Dict):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in cache.items():
            try:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                if now - timestamp > self.search_ttl:
                    expired_keys.append(key)
            except:
                expired_keys.append(key)
                
        for key in expired_keys:
            del cache[key]
            
    def clear_cache(self):
        """Clear all cache files"""
        if self.search_cache_file.exists():
            self.search_cache_file.unlink()
        if self.package_db_file.exists():
            self.package_db_file.unlink()
        print("✅ Cache cleared")