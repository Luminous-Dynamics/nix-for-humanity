#!/usr/bin/env python3
"""
from typing import Tuple, List, Optional
Intelligent Package Cache Manager for Nix for Humanity
Builds toward the AI partner vision by learning from user behavior
"""

import sqlite3
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import threading
import re

class IntelligentPackageCache:
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.cache_db = self.base_dir / "package_cache.db"
        self.search_history_db = self.base_dir / "search_history.db"
        self.init_databases()
        
        # Cache configuration
        self.cache_ttl = timedelta(days=7)  # Cache expires after 7 days
        self.popular_threshold = 3  # Searches needed to be "popular"
        self.background_update_interval = 3600  # 1 hour
        
        # Start background cache updater
        self.start_background_updater()
        
    def init_databases(self):
        """Initialize cache and search history databases"""
        # Package cache database
        conn = sqlite3.connect(self.cache_db)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS package_cache (
                package_name TEXT PRIMARY KEY,
                description TEXT,
                version TEXT,
                attribute_path TEXT,
                homepage TEXT,
                last_updated TIMESTAMP,
                search_rank INTEGER DEFAULT 0,
                install_count INTEGER DEFAULT 0
            )
        ''')
        
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_package_search 
            ON package_cache(package_name, description)
        ''')
        
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_search_rank 
            ON package_cache(search_rank DESC)
        ''')
        
        conn.commit()
        conn.close()
        
        # Search history database
        conn = sqlite3.connect(self.search_history_db)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_term TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                results_found INTEGER,
                user_selected TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS search_patterns (
                pattern TEXT PRIMARY KEY,
                frequency INTEGER DEFAULT 1,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def search_cache(self, query: str, limit: int = 20) -> List[Dict]:
        """Search packages in cache with intelligent ranking"""
        conn = sqlite3.connect(self.cache_db)
        c = conn.cursor()
        
        query_lower = query.lower()
        
        # Search with ranking:
        # 1. Exact name match (highest priority)
        # 2. Name starts with query
        # 3. Name contains query
        # 4. Description contains query
        # Boost by search_rank (popularity)
        
        results = c.execute('''
            SELECT package_name, description, version, attribute_path, homepage,
                   search_rank,
                   CASE 
                       WHEN LOWER(package_name) = ? THEN 1000
                       WHEN LOWER(package_name) LIKE ? THEN 500
                       WHEN LOWER(package_name) LIKE ? THEN 100
                       WHEN LOWER(description) LIKE ? THEN 10
                       ELSE 1
                   END + search_rank * 10 as relevance_score
            FROM package_cache
            WHERE LOWER(package_name) LIKE ? 
               OR LOWER(description) LIKE ?
            ORDER BY relevance_score DESC
            LIMIT ?
        ''', (
            query_lower,                    # Exact match
            f"{query_lower}%",             # Starts with
            f"%{query_lower}%",            # Contains
            f"%{query_lower}%",            # Description contains
            f"%{query_lower}%",            # WHERE clause
            f"%{query_lower}%",            # WHERE clause
            limit
        )).fetchall()
        
        conn.close()
        
        return [
            {
                'name': r[0],
                'description': r[1],
                'version': r[2],
                'attribute': r[3],
                'homepage': r[4],
                'popularity': r[5]
            }
            for r in results
        ]
        
    def update_cache_from_search(self, search_output: str):
        """Update cache from nix search output"""
        conn = sqlite3.connect(self.cache_db)
        c = conn.cursor()
        
        # Parse nix search output
        # Format: * attribute.path (version)
        #         description
        
        packages = []
        current_package = None
        
        for line in search_output.split('\n'):
            if line.startswith('*'):
                # New package
                if current_package:
                    packages.append(current_package)
                    
                # Parse: * nixpkgs.firefox (91.0.1)
                match = re.match(r'\* ([^\s]+)\s*\(([^)]+)\)', line)
                if match:
                    attr_path = match.group(1)
                    version = match.group(2)
                    # Extract package name from attribute path
                    name = attr_path.split('.')[-1]
                    
                    current_package = {
                        'name': name,
                        'attribute': attr_path,
                        'version': version,
                        'description': ''
                    }
            elif line.strip() and current_package:
                # Description line
                current_package['description'] = line.strip()
                
        if current_package:
            packages.append(current_package)
            
        # Update cache
        timestamp = datetime.now()
        for pkg in packages:
            c.execute('''
                INSERT OR REPLACE INTO package_cache 
                (package_name, description, version, attribute_path, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                pkg['name'],
                pkg['description'],
                pkg['version'],
                pkg['attribute'],
                timestamp
            ))
            
        conn.commit()
        conn.close()
        
        return len(packages)
        
    def learn_from_search(self, query: str, selected_package: Optional[str] = None):
        """Learn from user search behavior"""
        conn = sqlite3.connect(self.search_history_db)
        c = conn.cursor()
        
        # Record search
        c.execute('''
            INSERT INTO search_history (search_term, user_selected)
            VALUES (?, ?)
        ''', (query, selected_package))
        
        # Update search patterns
        words = query.lower().split()
        for word in words:
            c.execute('''
                INSERT OR REPLACE INTO search_patterns (pattern, frequency, last_seen)
                VALUES (
                    ?,
                    COALESCE((SELECT frequency FROM search_patterns WHERE pattern = ?), 0) + 1,
                    CURRENT_TIMESTAMP
                )
            ''', (word, word))
            
        conn.commit()
        conn.close()
        
        # If user selected a package, boost its search rank
        if selected_package:
            conn = sqlite3.connect(self.cache_db)
            c = conn.cursor()
            
            c.execute('''
                UPDATE package_cache 
                SET search_rank = search_rank + 1
                WHERE package_name = ?
            ''', (selected_package,))
            
            conn.commit()
            conn.close()
            
    def get_popular_packages(self) -> List[str]:
        """Get list of popular packages to pre-cache"""
        # Start with common packages
        popular = [
            'firefox', 'chromium', 'google-chrome',
            'vscode', 'vim', 'neovim', 'emacs',
            'git', 'docker', 'nodejs', 'python3',
            'rust', 'go', 'java', 'gcc',
            'htop', 'tmux', 'zsh', 'fish',
            'vlc', 'libreoffice', 'thunderbird',
            'gimp', 'inkscape', 'blender',
            'steam', 'discord', 'slack'
        ]
        
        # Add frequently searched patterns
        conn = sqlite3.connect(self.search_history_db)
        c = conn.cursor()
        
        frequent = c.execute('''
            SELECT pattern 
            FROM search_patterns 
            WHERE frequency >= ?
            ORDER BY frequency DESC
            LIMIT 20
        ''', (self.popular_threshold,)).fetchall()
        
        conn.close()
        
        popular.extend([f[0] for f in frequent])
        
        return list(set(popular))  # Remove duplicates
        
    def update_popular_packages_cache(self):
        """Update cache with popular packages"""
        popular = self.get_popular_packages()
        
        print(f"🔄 Updating cache for {len(popular)} popular packages...")
        
        for package in popular:
            try:
                # Run search with timeout
                result = subprocess.run(
                    ['nix', 'search', 'nixpkgs', package],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout:
                    count = self.update_cache_from_search(result.stdout)
                    print(f"  ✓ {package}: {count} packages cached")
                    
            except subprocess.TimeoutExpired:
                print(f"  ⏱️ {package}: Timeout, skipping")
            except Exception as e:
                print(f"  ❌ {package}: Error - {e}")
                
        print("✅ Cache update complete")
        
    def is_cache_stale(self) -> bool:
        """Check if cache needs updating"""
        conn = sqlite3.connect(self.cache_db)
        c = conn.cursor()
        
        # Check when cache was last updated
        result = c.execute('''
            SELECT MAX(last_updated) FROM package_cache
        ''').fetchone()
        
        conn.close()
        
        if not result or not result[0]:
            return True
            
        last_update = datetime.fromisoformat(result[0])
        return datetime.now() - last_update > self.cache_ttl
        
    def background_updater(self):
        """Background thread to keep cache fresh"""
        while True:
            try:
                if self.is_cache_stale():
                    print("🔄 Background cache update starting...")
                    self.update_popular_packages_cache()
                    
            except Exception as e:
                print(f"❌ Background update error: {e}")
                
            time.sleep(self.background_update_interval)
            
    def start_background_updater(self):
        """Start background cache updater thread"""
        thread = threading.Thread(target=self.background_updater, daemon=True)
        thread.start()
        
    def search_with_fallback(self, query: str, timeout: int = 5) -> Tuple[List[Dict], bool]:
        """
        Search with intelligent caching
        Returns: (results, from_cache)
        """
        # First, try cache
        cache_results = self.search_cache(query)
        
        if cache_results:
            # Learn from this search
            self.learn_from_search(query)
            return cache_results, True
            
        # Cache miss - try live search with short timeout
        print(f"🔍 Cache miss for '{query}', trying live search...")
        
        try:
            result = subprocess.run(
                ['nix', 'search', 'nixpkgs', query],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0 and result.stdout:
                # Update cache with results
                self.update_cache_from_search(result.stdout)
                
                # Search cache again with fresh data
                cache_results = self.search_cache(query)
                self.learn_from_search(query)
                
                return cache_results, False
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ Live search timeout for '{query}'")
            
        # If all else fails, suggest web search
        return [{
            'name': 'search-timeout',
            'description': f'Search is taking too long. Try searching online at search.nixos.org for "{query}"',
            'version': '',
            'attribute': '',
            'homepage': 'https://search.nixos.org'
        }], False
        
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        conn = sqlite3.connect(self.cache_db)
        c = conn.cursor()
        
        stats = {
            'total_packages': c.execute('SELECT COUNT(*) FROM package_cache').fetchone()[0],
            'popular_packages': c.execute('SELECT COUNT(*) FROM package_cache WHERE search_rank > 0').fetchone()[0],
            'cache_age': None
        }
        
        # Get cache age
        result = c.execute('SELECT MIN(last_updated) FROM package_cache').fetchone()
        if result and result[0]:
            oldest = datetime.fromisoformat(result[0])
            stats['cache_age'] = str(datetime.now() - oldest)
            
        conn.close()
        
        # Get search statistics
        conn = sqlite3.connect(self.search_history_db)
        c = conn.cursor()
        
        stats['total_searches'] = c.execute('SELECT COUNT(*) FROM search_history').fetchone()[0]
        stats['unique_terms'] = c.execute('SELECT COUNT(DISTINCT search_term) FROM search_history').fetchone()[0]
        
        conn.close()
        
        return stats


def main():
    """Test the intelligent cache"""
    cache = IntelligentPackageCache()
    
    print("🧠 Intelligent Package Cache Test\n")
    print("=" * 50)
    
    # Show cache stats
    stats = cache.get_cache_stats()
    print(f"📊 Cache Statistics:")
    print(f"   Total packages: {stats['total_packages']}")
    print(f"   Popular packages: {stats['popular_packages']}")
    print(f"   Cache age: {stats['cache_age'] or 'Empty'}")
    print(f"   Total searches: {stats['total_searches']}")
    print(f"   Unique terms: {stats['unique_terms']}")
    print("=" * 50)
    
    # Test searches
    test_queries = ['firefox', 'python', 'vim', 'docker', 'asdfqwerty']
    
    for query in test_queries:
        print(f"\n🔍 Searching for: {query}")
        start = time.time()
        
        results, from_cache = cache.search_with_fallback(query)
        
        elapsed = time.time() - start
        print(f"⏱️ Search took: {elapsed:.2f}s ({'from cache' if from_cache else 'live search'})")
        
        if results:
            print(f"📦 Found {len(results)} packages:")
            for r in results[:3]:  # Show top 3
                print(f"   - {r['name']}: {r['description'][:60]}...")
        else:
            print("   No results found")
            
    # Simulate user selecting a package
    cache.learn_from_search('firefox', 'firefox')
    print("\n✅ Learned from user selection!")


if __name__ == "__main__":
    main()