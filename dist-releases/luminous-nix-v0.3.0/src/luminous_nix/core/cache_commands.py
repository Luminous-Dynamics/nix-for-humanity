"""
Cache Management Commands for Luminous Nix

Provides commands to manage the cache:
- cache status: Show cache statistics
- cache warm: Warm the cache with common queries
- cache clear: Clear the cache
- cache test: Test cache performance
"""

import time
from typing import Dict, Any
from pathlib import Path

from .enhanced_cache import get_enhanced_cache
from .intents import Intent, IntentType
from luminous_nix.api.schema import Response


class CacheCommands:
    """Handle cache management commands"""
    
    def __init__(self):
        """Initialize cache commands"""
        self.cache = get_enhanced_cache()
    
    def handle_cache_command(self, intent: Intent) -> Response:
        """
        Handle cache-related commands.
        
        Supports:
        - cache status / cache info
        - cache warm / cache build
        - cache clear / cache reset
        - cache test / cache benchmark
        """
        raw_text = intent.raw_text.lower()
        
        if any(word in raw_text for word in ["status", "info", "stats"]):
            return self._handle_cache_status()
        elif any(word in raw_text for word in ["warm", "build", "populate"]):
            return self._handle_cache_warm()
        elif any(word in raw_text for word in ["clear", "reset", "clean"]):
            return self._handle_cache_clear()
        elif any(word in raw_text for word in ["test", "benchmark", "perf"]):
            return self._handle_cache_test()
        else:
            return self._handle_cache_help()
    
    def _handle_cache_status(self) -> Response:
        """Show cache status and statistics"""
        info = self.cache.get_cache_info()
        
        message = "📊 Cache Status\n"
        message += "="*40 + "\n\n"
        
        # Basic info
        message += f"📦 Cached packages: {info['total_packages']}\n"
        message += f"🔍 Cached searches: {info['cached_searches']}\n"
        message += f"💾 Cache size: {info['cache_size_kb']:.1f} KB\n"
        
        # Statistics
        stats = info.get("stats", {})
        if stats.get("total_searches", 0) > 0:
            hit_rate = info.get("hit_rate", 0)
            fuzzy_rate = info.get("fuzzy_rate", 0)
            message += f"\n📈 Performance:\n"
            message += f"  • Total searches: {stats['total_searches']}\n"
            message += f"  • Cache hits: {stats['cache_hits']} ({hit_rate:.1f}%)\n"
            message += f"  • Fuzzy matches: {stats['fuzzy_matches']} ({fuzzy_rate:.1f}%)\n"
        
        # Cache locations
        message += f"\n📁 Locations:\n"
        message += f"  • User cache: {info['user_cache']}\n"
        if info.get("shared_cache"):
            message += f"  • Shared cache: {info['shared_cache']}\n"
        
        # Last warm
        if stats.get("last_warm"):
            message += f"\n🔥 Last warmed: {stats['last_warm']}\n"
        
        return Response(
            success=True,
            text=message.strip(),
            data=info
        )
    
    def _handle_cache_warm(self) -> Response:
        """Warm the cache with common queries"""
        message = "🔥 Warming cache...\n"
        message += "This will pre-cache common searches for 2-5 seconds results.\n\n"
        
        start_time = time.time()
        
        # Warm with subset of queries
        warm_queries = [
            "firefox", "chromium", "vim", "neovim", "emacs",
            "git", "docker", "python", "nodejs", "rust",
            "terminal", "editor", "browser", "database", "development"
        ]
        
        warmed = self.cache.warm_cache(warm_queries)
        elapsed = time.time() - start_time
        
        message += f"✅ Cache warming complete!\n"
        message += f"  • Warmed {warmed} new entries\n"
        message += f"  • Time taken: {elapsed:.1f} seconds\n"
        message += f"  • Total cached: {len(self.cache.cache.get('packages', {}))} packages\n"
        
        return Response(
            success=True,
            text=message.strip(),
            data={"warmed": warmed, "elapsed": elapsed}
        )
    
    def _handle_cache_clear(self) -> Response:
        """Clear the cache"""
        # Get stats before clearing
        info = self.cache.get_cache_info()
        old_searches = info['cached_searches']
        old_size = info['cache_size_kb']
        
        # Clear cache
        self.cache.clear_cache(searches_only=True)  # Keep common packages
        
        message = "🗑️ Cache cleared!\n\n"
        message += f"Removed:\n"
        message += f"  • {old_searches} cached searches\n"
        message += f"  • {old_size:.1f} KB freed\n"
        message += f"\nNote: Common packages kept for 2-5 seconds results.\n"
        message += "Use 'cache warm' to rebuild search cache."
        
        return Response(
            success=True,
            text=message.strip(),
            data={"cleared_searches": old_searches, "freed_kb": old_size}
        )
    
    def _handle_cache_test(self) -> Response:
        """Test cache performance"""
        message = "🧪 Testing cache performance...\n"
        message += "="*40 + "\n\n"
        
        test_queries = ["firefox", "vim", "editor", "asdfghjkl"]
        results = []
        
        for query in test_queries:
            # First search (might not be cached)
            start = time.time()
            res1, time1, cached1 = self.cache.fuzzy_search(query)
            
            # Second search (should be cached)
            res2, time2, cached2 = self.cache.fuzzy_search(query)
            
            speedup = time1 / time2 if time2 > 0 else 999
            
            results.append({
                "query": query,
                "first_ms": time1,
                "second_ms": time2,
                "speedup": speedup,
                "results": len(res1)
            })
            
            message += f"Query: '{query}'\n"
            message += f"  First:  {time1:>6.1f}ms (cached: {cached1})\n"
            message += f"  Second: {time2:>6.1f}ms (cached: {cached2})\n"
            message += f"  Speedup: {speedup:.1f}x\n"
            message += f"  Results: {len(res1)}\n\n"
        
        # Calculate averages
        avg_first = sum(r["first_ms"] for r in results) / len(results)
        avg_second = sum(r["second_ms"] for r in results) / len(results)
        avg_speedup = avg_first / avg_second if avg_second > 0 else 999
        
        message += "📊 Summary:\n"
        message += f"  Average first search:  {avg_first:.1f}ms\n"
        message += f"  Average cached search: {avg_second:.1f}ms\n"
        message += f"  Average speedup: {avg_speedup:.1f}x\n"
        
        return Response(
            success=True,
            text=message.strip(),
            data={"results": results}
        )
    
    def _handle_cache_help(self) -> Response:
        """Show cache command help"""
        message = """
🗄️ Cache Management Commands

Available commands:
  cache status   - Show cache statistics and info
  cache warm     - Pre-cache common searches
  cache clear    - Clear cached searches
  cache test     - Test cache performance

Examples:
  ask-nix "cache status"
  ask-nix "cache warm"
  ask-nix "cache clear"
  ask-nix "cache test"

The cache makes searches 2-5 seconds after the first lookup.
Common packages are always cached for immediate results.
        """
        
        return Response(
            success=True,
            text=message.strip()
        )


# Singleton instance
_cache_commands = None


def get_cache_commands() -> CacheCommands:
    """Get or create singleton cache commands"""
    global _cache_commands
    if _cache_commands is None:
        _cache_commands = CacheCommands()
    return _cache_commands