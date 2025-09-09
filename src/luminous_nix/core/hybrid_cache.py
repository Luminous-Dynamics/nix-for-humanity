"""
Hybrid cache that combines ultra-fast static cache with real Nix data
Maintains <100ms performance while providing real, up-to-date information
"""

import json
import subprocess
import threading
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import pickle

class HybridCache:
    """
    Hybrid caching system that provides:
    1. Instant (<1ms) responses from memory cache
    2. Background updates from real Nix database
    3. Progressive loading with immediate feedback
    4. Smart invalidation based on system changes
    """
    
    def __init__(self):
        """Initialize hybrid cache with static data and real connection"""
        # Layer 1: Ultra-fast in-memory cache (same as before)
        self.l1_cache = self._init_static_cache()
        
        # Layer 2: Recently accessed real data
        self.l2_cache = OrderedDict()  # LRU cache
        self.l2_max_size = 1000
        
        # Layer 3: Persistent disk cache
        self.cache_dir = Path.home() / ".cache" / "luminous-nix"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.l3_cache_file = self.cache_dir / "packages.pkl"
        self.l3_cache = self._load_disk_cache()
        
        # Cache metadata
        self.cache_stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "misses": 0,
            "updates": 0
        }
        
        # Background refresh thread
        self.refresh_thread = None
        self.stop_refresh = threading.Event()
        self.last_refresh = 0
        self.refresh_interval = 300  # 5 minutes
        
        # Start background refresh
        self._start_background_refresh()
        
        # Track system state for invalidation
        self.system_state = self._get_system_state()
    
    def _init_static_cache(self) -> Dict:
        """Initialize with common packages for instant response"""
        # Same as UltraFastCache but will be updated with real data
        return {
            "firefox": {"name": "firefox", "version": "128.0", "description": "Mozilla Firefox web browser"},
            "vim": {"name": "vim", "version": "9.1.0707", "description": "Vi IMproved - enhanced vi editor"},
            "git": {"name": "git", "version": "2.47.1", "description": "Distributed version control system"},
            "python3": {"name": "python3", "version": "3.13.1", "description": "Python 3 interpreter"},
            "nodejs": {"name": "nodejs", "version": "22.12.0", "description": "JavaScript runtime"},
            # ... more common packages
        }
    
    def search_hybrid(self, query: str) -> Tuple[List[Dict], float, str]:
        """
        Hybrid search with progressive loading
        Returns: (results, elapsed_ms, source)
        """
        start = time.time()
        
        # Phase 1: Check L1 cache (instant, <1ms)
        l1_results = self._search_l1(query)
        if l1_results:
            self.cache_stats["l1_hits"] += 1
            elapsed = (time.time() - start) * 1000
            return (l1_results, elapsed, "memory")
        
        # Phase 2: Check L2 cache (recent, <10ms)
        l2_results = self._search_l2(query)
        if l2_results:
            self.cache_stats["l2_hits"] += 1
            elapsed = (time.time() - start) * 1000
            return (l2_results, elapsed, "recent")
        
        # Phase 3: Check L3 disk cache (<50ms)
        l3_results = self._search_l3(query)
        if l3_results:
            self.cache_stats["l3_hits"] += 1
            # Promote to L2 for faster access
            self._promote_to_l2(query, l3_results)
            elapsed = (time.time() - start) * 1000
            return (l3_results, elapsed, "disk")
        
        # Phase 4: Real Nix query (>100ms but necessary)
        # Do this in background and return best guess
        self.cache_stats["misses"] += 1
        
        # Start async fetch
        threading.Thread(
            target=self._fetch_and_cache,
            args=(query,),
            daemon=True
        ).start()
        
        # Return approximate results immediately
        approx_results = self._get_approximate_results(query)
        elapsed = (time.time() - start) * 1000
        return (approx_results, elapsed, "approximate")
    
    def _search_l1(self, query: str) -> List[Dict]:
        """Search in ultra-fast memory cache"""
        query_lower = query.lower()
        results = []
        
        for name, info in self.l1_cache.items():
            # Skip None or invalid entries
            if not info or not isinstance(info, dict):
                continue
            
            # Search in name and description
            desc = info.get("description", "") if isinstance(info, dict) else ""
            if query_lower in name.lower() or query_lower in desc.lower():
                results.append(info)
                if len(results) >= 10:
                    break
        
        return results
    
    def _search_l2(self, query: str) -> List[Dict]:
        """Search in recent cache"""
        cache_key = f"search:{query}"
        if cache_key in self.l2_cache:
            # Move to end (most recently used)
            self.l2_cache.move_to_end(cache_key)
            return self.l2_cache[cache_key]
        return []
    
    def _search_l3(self, query: str) -> List[Dict]:
        """Search in disk cache"""
        cache_key = hashlib.md5(f"search:{query}".encode()).hexdigest()
        if cache_key in self.l3_cache:
            return self.l3_cache[cache_key]
        return []
    
    def _promote_to_l2(self, query: str, results: List[Dict]):
        """Promote results to L2 cache"""
        cache_key = f"search:{query}"
        self.l2_cache[cache_key] = results
        
        # Enforce LRU size limit
        if len(self.l2_cache) > self.l2_max_size:
            self.l2_cache.popitem(last=False)
    
    def _fetch_and_cache(self, query: str):
        """Fetch real data from Nix and update caches"""
        try:
            # Real Nix query
            cmd = ["nix", "search", "nixpkgs", query, "--json"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                packages = json.loads(result.stdout)
                results = []
                
                for name, info in packages.items():
                    pkg_name = name.split(".")[-1]
                    pkg_info = {
                        "name": pkg_name,
                        "version": info.get("version", ""),
                        "description": info.get("description", "")
                    }
                    results.append(pkg_info)
                    
                    # Update L1 cache if it's a common package
                    if len(self.l1_cache) < 100:  # Keep L1 small
                        self.l1_cache[pkg_name] = pkg_info
                
                # Update L2 cache
                self._promote_to_l2(query, results[:10])
                
                # Update L3 cache
                cache_key = hashlib.md5(f"search:{query}".encode()).hexdigest()
                self.l3_cache[cache_key] = results[:20]
                
                # Save to disk periodically
                self.cache_stats["updates"] += 1
                if self.cache_stats["updates"] % 10 == 0:
                    self._save_disk_cache()
                
        except Exception as e:
            # Silent fail - we already returned approximate results
            pass
    
    def _get_approximate_results(self, query: str) -> List[Dict]:
        """Get approximate results based on query analysis"""
        # Smart guessing based on common patterns
        if "browser" in query.lower():
            return [
                {"name": "firefox", "version": "latest", "description": "Mozilla Firefox (loading exact version...)"},
                {"name": "chromium", "version": "latest", "description": "Open source browser (loading...)"}
            ]
        elif "editor" in query.lower():
            return [
                {"name": "vim", "version": "latest", "description": "Vi IMproved (loading exact version...)"},
                {"name": "neovim", "version": "latest", "description": "Modern Vim (loading...)"},
                {"name": "emacs", "version": "latest", "description": "Extensible editor (loading...)"}
            ]
        elif "python" in query.lower():
            return [
                {"name": "python3", "version": "3.x", "description": "Python interpreter (loading exact version...)"},
                {"name": "python311", "version": "3.11.x", "description": "Python 3.11 (loading...)"}
            ]
        else:
            # Return empty with message
            return [{
                "name": f"Searching for '{query}'...",
                "version": "",
                "description": "Real results loading in background. Try again in a moment for exact matches."
            }]
    
    def _start_background_refresh(self):
        """Start background thread to refresh cache"""
        def refresh_worker():
            while not self.stop_refresh.is_set():
                try:
                    # Wait for interval or stop signal
                    if self.stop_refresh.wait(self.refresh_interval):
                        break
                    
                    # Check if system changed
                    new_state = self._get_system_state()
                    if new_state != self.system_state:
                        self._invalidate_changed_packages()
                        self.system_state = new_state
                    
                    # Refresh popular packages
                    self._refresh_popular_packages()
                    
                except Exception:
                    pass  # Silent fail in background
        
        self.refresh_thread = threading.Thread(target=refresh_worker, daemon=True)
        self.refresh_thread.start()
    
    def _get_system_state(self) -> str:
        """Get system state hash for change detection"""
        try:
            # Check nixos generation
            result = subprocess.run(
                ["nixos-version", "--json"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                return hashlib.md5(result.stdout.encode()).hexdigest()
        except:
            pass
        
        return str(time.time())
    
    def _invalidate_changed_packages(self):
        """Invalidate cache entries that might have changed"""
        # Clear L2 cache (recent items)
        self.l2_cache.clear()
        
        # Mark L3 cache as stale (but don't delete)
        self.l3_cache["_stale"] = True
    
    def _refresh_popular_packages(self):
        """Refresh the most popular packages in background"""
        popular = ["firefox", "vim", "git", "python3", "nodejs", "docker", "vscode"]
        
        for pkg in popular:
            try:
                cmd = ["nix", "eval", f"nixpkgs#{pkg}.meta", "--json"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if result.returncode == 0 and result.stdout:
                    meta = json.loads(result.stdout)
                    # Update L1 cache with real data
                    self.l1_cache[pkg] = {
                        "name": pkg,
                        "version": meta.get("version", "unknown"),
                        "description": meta.get("description", "")[:200]
                    }
            except:
                pass  # Silent fail
            
            # Don't hammer the system
            time.sleep(0.1)
    
    def _load_disk_cache(self) -> Dict:
        """Load cache from disk"""
        if self.l3_cache_file.exists():
            try:
                with open(self.l3_cache_file, "rb") as f:
                    cache = pickle.load(f)
                    # Check if cache is recent (< 1 day old)
                    if cache.get("_timestamp", 0) > time.time() - 86400:
                        return cache
            except:
                pass
        return {}
    
    def _save_disk_cache(self):
        """Save cache to disk"""
        try:
            self.l3_cache["_timestamp"] = time.time()
            with open(self.l3_cache_file, "wb") as f:
                pickle.dump(self.l3_cache, f)
        except:
            pass
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_hits = (
            self.cache_stats["l1_hits"] +
            self.cache_stats["l2_hits"] +
            self.cache_stats["l3_hits"]
        )
        total_requests = total_hits + self.cache_stats["misses"]
        
        return {
            "hit_rate": (total_hits / total_requests * 100) if total_requests > 0 else 0,
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "l3_size": len(self.l3_cache),
            **self.cache_stats
        }
    
    def shutdown(self):
        """Clean shutdown"""
        self.stop_refresh.set()
        if self.refresh_thread:
            self.refresh_thread.join(timeout=1)
        self._save_disk_cache()

# Singleton
_hybrid_cache = None

def get_hybrid_cache() -> HybridCache:
    """Get or create hybrid cache singleton"""
    global _hybrid_cache
    if _hybrid_cache is None:
        _hybrid_cache = HybridCache()
    return _hybrid_cache