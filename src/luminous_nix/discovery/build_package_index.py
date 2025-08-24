#!/usr/bin/env python3
"""
Build comprehensive package index for Luminous Nix.

This script builds a searchable index of all nixpkgs packages with
enhanced metadata for intelligent discovery.

Run weekly via CI/CD to keep index fresh.
"""

import json
import subprocess
import sqlite3
import lzma
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import asyncio
import aiohttp
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedPackageInfo:
    """Enhanced package information with metadata."""
    # Core info from nixpkgs
    name: str
    pname: str
    version: str
    description: str
    
    # Enhanced metadata
    categories: List[str]
    tags: List[str]
    keywords: List[str]
    alternatives: List[str]
    commonly_with: List[str]
    depends_on: List[str]
    
    # Metrics
    popularity_score: float  # 0-1
    github_stars: Optional[int]
    download_count: Optional[int]
    last_updated: str
    
    # System info
    platforms: List[str]
    size_mb: Optional[float]
    homepage: Optional[str]
    license: Optional[str]
    maintainers: List[str]


class PackageIndexBuilder:
    """
    Builds comprehensive package index from nixpkgs.
    """
    
    def __init__(self, output_path: Path = None):
        self.output_path = output_path or Path("package_index.db")
        self.packages = {}
        self.categories = self._init_categories()
        self.stats = {
            "total_packages": 0,
            "categorized": 0,
            "with_alternatives": 0,
            "with_metadata": 0,
        }
    
    def _init_categories(self) -> Dict[str, List[str]]:
        """Initialize category definitions."""
        return {
            "browsers": ["browser", "web", "internet", "firefox", "chrome", "chromium"],
            "editors": ["editor", "vim", "emacs", "vscode", "ide", "text"],
            "development": ["compiler", "language", "build", "debug", "git", "docker"],
            "media": ["video", "audio", "player", "music", "movie", "streaming"],
            "graphics": ["image", "photo", "draw", "paint", "design", "gimp"],
            "office": ["document", "spreadsheet", "word", "excel", "libreoffice"],
            "security": ["password", "encryption", "vpn", "firewall", "security"],
            "system": ["monitor", "process", "hardware", "cpu", "memory", "disk"],
            "network": ["network", "wifi", "ethernet", "vpn", "proxy", "firewall"],
            "communication": ["chat", "message", "email", "irc", "discord", "slack"],
            "games": ["game", "gaming", "steam", "minecraft", "emulator"],
            "science": ["science", "math", "calculation", "analysis", "data"],
            "database": ["database", "sql", "postgres", "mysql", "mongodb", "redis"],
            "terminal": ["terminal", "console", "shell", "tmux", "screen"],
        }
    
    async def build_index(self):
        """Build the complete package index."""
        logger.info("🚀 Starting package index build...")
        
        # Step 1: Fetch all packages
        logger.info("📦 Fetching all packages from nixpkgs...")
        await self.fetch_all_packages()
        
        # Step 2: Enrich with metadata
        logger.info("✨ Enriching package metadata...")
        await self.enrich_metadata()
        
        # Step 3: Calculate relationships
        logger.info("🔗 Calculating package relationships...")
        self.calculate_relationships()
        
        # Step 4: Build search indices
        logger.info("🔍 Building search indices...")
        self.build_indices()
        
        # Step 5: Save to database
        logger.info("💾 Saving to database...")
        self.save_to_database()
        
        # Step 6: Create compressed archive
        logger.info("📦 Creating compressed archive...")
        self.create_compressed_archive()
        
        logger.info(f"✅ Index build complete! Stats: {self.stats}")
    
    async def fetch_all_packages(self):
        """Fetch all packages from nixpkgs."""
        try:
            # Use nix search to get all packages
            # Note: In production, might want to use nix eval for more control
            result = subprocess.run(
                ["nix", "search", "nixpkgs", "^", "--json"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0 and result.stdout:
                raw_packages = json.loads(result.stdout)
                
                for path, info in raw_packages.items():
                    # Extract package name from path
                    parts = path.split(".")
                    name = parts[-1] if parts else "unknown"
                    
                    self.packages[name] = EnhancedPackageInfo(
                        name=name,
                        pname=info.get("pname", name),
                        version=info.get("version", "unknown"),
                        description=info.get("description", ""),
                        categories=[],
                        tags=[],
                        keywords=[],
                        alternatives=[],
                        commonly_with=[],
                        depends_on=[],
                        popularity_score=0.5,
                        github_stars=None,
                        download_count=None,
                        last_updated=datetime.now().isoformat(),
                        platforms=["x86_64-linux"],  # Default, would need to check properly
                        size_mb=None,
                        homepage=None,
                        license=None,
                        maintainers=[]
                    )
                
                self.stats["total_packages"] = len(self.packages)
                logger.info(f"  Found {len(self.packages)} packages")
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout fetching packages")
        except Exception as e:
            logger.error(f"Error fetching packages: {e}")
    
    async def enrich_metadata(self):
        """Enrich packages with additional metadata."""
        for name, pkg in self.packages.items():
            # Categorize based on name and description
            pkg.categories = self.categorize_package(pkg)
            if pkg.categories:
                self.stats["categorized"] += 1
            
            # Extract keywords from description
            pkg.keywords = self.extract_keywords(pkg.description)
            
            # Generate tags
            pkg.tags = self.generate_tags(pkg)
            
            # Calculate popularity (simplified - would use real metrics)
            pkg.popularity_score = self.calculate_popularity(pkg)
            
            # Find alternatives (simplified)
            pkg.alternatives = self.find_alternatives(name)
            if pkg.alternatives:
                self.stats["with_alternatives"] += 1
            
            # Common combinations (would use real data)
            pkg.commonly_with = self.find_commonly_installed(name)
            
            self.stats["with_metadata"] += 1
    
    def categorize_package(self, pkg: EnhancedPackageInfo) -> List[str]:
        """Categorize package based on name and description."""
        categories = []
        text = f"{pkg.name} {pkg.description}".lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        # Limit to top 3 categories
        return categories[:3] if categories else ["uncategorized"]
    
    def extract_keywords(self, description: str) -> List[str]:
        """Extract keywords from description."""
        # Simple keyword extraction - in production, use NLP
        words = re.findall(r'\b[a-z]+\b', description.lower())
        
        # Filter common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", 
                    "to", "for", "of", "with", "by", "from", "as", "is", "was"}
        
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        
        # Return top 10 most common
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, _ in word_counts.most_common(10)]
    
    def generate_tags(self, pkg: EnhancedPackageInfo) -> List[str]:
        """Generate tags for package."""
        tags = []
        
        # Add category tags
        tags.extend(pkg.categories)
        
        # Add version tags
        if "beta" in pkg.version:
            tags.append("beta")
        if "dev" in pkg.version or "git" in pkg.version:
            tags.append("development")
        
        # Add common tags based on patterns
        if "lib" in pkg.name:
            tags.append("library")
        if "python" in pkg.name:
            tags.append("python")
        if "node" in pkg.name:
            tags.append("nodejs")
        
        return list(set(tags))[:10]
    
    def calculate_popularity(self, pkg: EnhancedPackageInfo) -> float:
        """Calculate popularity score (0-1)."""
        score = 0.5  # Base score
        
        # Boost for common packages
        common_packages = ["firefox", "chrome", "vim", "emacs", "git", "docker",
                          "python", "nodejs", "gcc", "vscode", "thunderbird"]
        
        if pkg.name in common_packages:
            score = 0.9
        elif any(common in pkg.name for common in common_packages):
            score = 0.7
        
        # Boost for good descriptions
        if len(pkg.description) > 50:
            score += 0.1
        
        return min(score, 1.0)
    
    def find_alternatives(self, package: str) -> List[str]:
        """Find alternative packages."""
        alternatives_map = {
            "firefox": ["chromium", "brave", "librewolf"],
            "chromium": ["firefox", "brave", "ungoogled-chromium"],
            "vim": ["neovim", "emacs", "vscode"],
            "docker": ["podman", "lxc"],
            # Add more...
        }
        
        return alternatives_map.get(package, [])
    
    def find_commonly_installed(self, package: str) -> List[str]:
        """Find commonly installed together packages."""
        common_map = {
            "firefox": ["thunderbird"],
            "vim": ["tmux", "git"],
            "python3": ["python3-pip"],
            "nodejs": ["yarn", "npm"],
            # Add more...
        }
        
        return common_map.get(package, [])
    
    def calculate_relationships(self):
        """Calculate package relationships."""
        logger.info("  Calculating alternative relationships...")
        
        # Build bidirectional alternatives
        for name, pkg in self.packages.items():
            for alt in pkg.alternatives:
                if alt in self.packages:
                    if name not in self.packages[alt].alternatives:
                        self.packages[alt].alternatives.append(name)
    
    def build_indices(self):
        """Build search indices for fast lookup."""
        # This would create various indices
        # For now, we'll rely on SQLite's built-in indexing
        pass
    
    def save_to_database(self):
        """Save index to SQLite database."""
        conn = sqlite3.connect(self.output_path)
        cursor = conn.cursor()
        
        # Create main table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                name TEXT PRIMARY KEY,
                pname TEXT,
                version TEXT,
                description TEXT,
                categories TEXT,
                tags TEXT,
                keywords TEXT,
                alternatives TEXT,
                commonly_with TEXT,
                depends_on TEXT,
                popularity_score REAL,
                github_stars INTEGER,
                download_count INTEGER,
                last_updated TEXT,
                platforms TEXT,
                size_mb REAL,
                homepage TEXT,
                license TEXT,
                maintainers TEXT
            )
        """)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_popularity ON packages(popularity_score DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories ON packages(categories)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_description ON packages(description)")
        
        # Insert packages
        for pkg in self.packages.values():
            cursor.execute("""
                INSERT OR REPLACE INTO packages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pkg.name,
                pkg.pname,
                pkg.version,
                pkg.description,
                json.dumps(pkg.categories),
                json.dumps(pkg.tags),
                json.dumps(pkg.keywords),
                json.dumps(pkg.alternatives),
                json.dumps(pkg.commonly_with),
                json.dumps(pkg.depends_on),
                pkg.popularity_score,
                pkg.github_stars,
                pkg.download_count,
                pkg.last_updated,
                json.dumps(pkg.platforms),
                pkg.size_mb,
                pkg.homepage,
                pkg.license,
                json.dumps(pkg.maintainers)
            ))
        
        # Create full-text search table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS packages_fts USING fts5(
                name, description, categories, tags, keywords,
                content=packages
            )
        """)
        
        # Populate FTS
        cursor.execute("""
            INSERT INTO packages_fts (name, description, categories, tags, keywords)
            SELECT name, description, categories, tags, keywords FROM packages
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"  Saved {len(self.packages)} packages to {self.output_path}")
    
    def create_compressed_archive(self):
        """Create compressed archive for distribution."""
        compressed_path = self.output_path.with_suffix('.xz')
        
        with open(self.output_path, 'rb') as f_in:
            with lzma.open(compressed_path, 'wb', preset=9) as f_out:
                f_out.write(f_in.read())
        
        original_size = self.output_path.stat().st_size / (1024 * 1024)
        compressed_size = compressed_path.stat().st_size / (1024 * 1024)
        
        logger.info(f"  Compressed {original_size:.1f}MB -> {compressed_size:.1f}MB")
        logger.info(f"  Archive saved to {compressed_path}")


async def main():
    """Build the package index."""
    builder = PackageIndexBuilder(Path("luminous_package_index.db"))
    await builder.build_index()
    
    # Show some statistics
    print("\n📊 Index Statistics:")
    print(f"  Total packages: {builder.stats['total_packages']}")
    print(f"  Categorized: {builder.stats['categorized']}")
    print(f"  With alternatives: {builder.stats['with_alternatives']}")
    print(f"  With metadata: {builder.stats['with_metadata']}")
    
    # Test the index
    print("\n🔍 Testing index...")
    conn = sqlite3.connect("luminous_package_index.db")
    cursor = conn.cursor()
    
    # Test search
    cursor.execute("""
        SELECT name, description, popularity_score 
        FROM packages 
        WHERE description LIKE '%browser%' 
        ORDER BY popularity_score DESC 
        LIMIT 5
    """)
    
    print("  Top browsers:")
    for name, desc, score in cursor.fetchall():
        print(f"    {name} ({score:.2f}): {desc[:50]}...")
    
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())