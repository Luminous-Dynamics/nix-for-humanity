"""
Cache management commands for Luminous Nix
"""

import click
from luminous_nix.core.search_cache import SearchCache

@click.group()
def cache():
    """Manage search cache for better performance"""
    pass

@cache.command()
def build():
    """Build local package database for instant searches"""
    click.echo("🔨 Building package cache...")
    
    try:
        cache = SearchCache()
        
        # Build package database
        cache.build_package_database()
        
        # Pre-cache common searches
        cache.pre_cache_common_searches()
        
        click.echo("✅ Cache built successfully!")
        click.echo("🚀 Searches will now be instant!")
        
    except Exception as e:
        click.echo(f"❌ Failed to build cache: {e}")
        return 1
    
    return 0

@cache.command()
def clear():
    """Clear all cached data"""
    click.echo("🗑️ Clearing cache...")
    
    try:
        cache = SearchCache()
        cache.clear_cache()
        click.echo("✅ Cache cleared")
        
    except Exception as e:
        click.echo(f"❌ Failed to clear cache: {e}")
        return 1
    
    return 0

@cache.command()
def status():
    """Show cache status and statistics"""
    from pathlib import Path
    import json
    from datetime import datetime
    
    cache_dir = Path.home() / ".cache/luminous-nix"
    
    click.echo("📊 Cache Status")
    click.echo("=" * 40)
    
    # Check search cache
    search_cache = cache_dir / "search_cache.json"
    if search_cache.exists():
        try:
            data = json.loads(search_cache.read_text())
            click.echo(f"✓ Search cache: {len(data)} cached searches")
            
            # Show recent searches
            recent = []
            for key, entry in data.items():
                if 'term' in entry and 'timestamp' in entry:
                    recent.append((entry['term'], entry['timestamp']))
            
            recent.sort(key=lambda x: x[1], reverse=True)
            if recent:
                click.echo("\nRecent searches:")
                for term, timestamp in recent[:5]:
                    dt = datetime.fromisoformat(timestamp)
                    age = datetime.now() - dt
                    click.echo(f"  • {term} ({age.total_seconds()//60:.0f} minutes ago)")
                    
        except Exception as e:
            click.echo(f"⚠️ Search cache exists but couldn't read: {e}")
    else:
        click.echo("✗ No search cache")
    
    # Check package database
    package_db = cache_dir / "package_db.json"
    if package_db.exists():
        try:
            data = json.loads(package_db.read_text())
            count = data.get('count', 0)
            timestamp = data.get('timestamp')
            
            click.echo(f"\n✓ Package database: {count} packages")
            
            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                age = datetime.now() - dt
                click.echo(f"  Last updated: {age.days} days ago")
                
        except Exception as e:
            click.echo(f"⚠️ Package database exists but couldn't read: {e}")
    else:
        click.echo("\n✗ No package database")
        click.echo("  Run 'ask-nix cache build' to create one")
    
    # Show cache size
    total_size = 0
    for file in cache_dir.glob("*.json"):
        total_size += file.stat().st_size
    
    click.echo(f"\n💾 Total cache size: {total_size / 1024:.1f} KB")

@cache.command()
def warm():
    """Warm up cache with common searches"""
    click.echo("🔥 Warming up cache...")
    
    try:
        cache = SearchCache()
        cache.pre_cache_common_searches()
        click.echo("✅ Cache warmed up!")
        
    except Exception as e:
        click.echo(f"❌ Failed to warm cache: {e}")
        return 1
    
    return 0