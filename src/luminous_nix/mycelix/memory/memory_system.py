"""
Multi-Level Memory System
Enables context continuity across sessions with short-term, working, and long-term memory

Memory Tiers:
1. Short-term: Current session (seconds to minutes) - In-memory, fast
2. Working: Recent context (hours to days) - LRU cache with persistence
3. Long-term: Permanent knowledge (forever) - SQLite database

Memory Types:
- Episodic: "Remember when we installed X?"
- Semantic: "I know that Y is for Z"
- Procedural: "I learned that doing A before B works better"
- User: "This user prefers detailed explanations"
"""

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """A single memory item"""
    id: str  # Unique ID (hash of content)
    content: str  # The actual memory content
    memory_type: str  # episodic, semantic, procedural, user
    importance: float  # 0-1, how important is this?
    context: Dict[str, Any]  # Additional context
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryItem':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)


class ShortTermMemory:
    """
    Short-term memory: Current session

    Fast, in-memory storage for immediate context
    Capacity: ~100 items
    Lifespan: Current session only
    """

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.memories: OrderedDict[str, MemoryItem] = OrderedDict()

    def add(self, item: MemoryItem):
        """Add item to short-term memory"""
        # If at capacity, remove oldest
        if len(self.memories) >= self.capacity:
            self.memories.popitem(last=False)

        self.memories[item.id] = item
        self.memories.move_to_end(item.id)  # Most recent

    def get(self, item_id: str) -> Optional[MemoryItem]:
        """Get item by ID"""
        item = self.memories.get(item_id)
        if item:
            item.access_count += 1
            item.last_accessed = datetime.now()
            self.memories.move_to_end(item_id)  # Mark as recently used
        return item

    def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search short-term memory"""
        query_lower = query.lower()

        results = []
        for item in reversed(self.memories.values()):  # Most recent first
            if query_lower in item.content.lower():
                results.append(item)
                if len(results) >= limit:
                    break

        return results

    def get_recent(self, n: int = 10) -> List[MemoryItem]:
        """Get n most recent memories"""
        return list(reversed(list(self.memories.values())[-n:]))

    def clear(self):
        """Clear all short-term memory"""
        self.memories.clear()

    def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            'capacity': self.capacity,
            'count': len(self.memories),
            'utilization': len(self.memories) / self.capacity,
            'oldest': list(self.memories.values())[0].created_at if self.memories else None,
            'newest': list(self.memories.values())[-1].created_at if self.memories else None
        }


class WorkingMemory:
    """
    Working memory: Recent context

    LRU cache with persistence for recent important memories
    Capacity: ~1000 items
    Lifespan: Hours to days
    """

    def __init__(self, capacity: int = 1000, persistence_path: Optional[Path] = None):
        self.capacity = capacity
        self.memories: OrderedDict[str, MemoryItem] = OrderedDict()
        self.persistence_path = persistence_path

        # Load from disk if exists
        if persistence_path and persistence_path.exists():
            self._load_from_disk()

    def add(self, item: MemoryItem):
        """Add item to working memory"""
        # If at capacity, remove least recently used
        if len(self.memories) >= self.capacity:
            # But keep high-importance items
            lru_candidates = [
                (k, v) for k, v in self.memories.items()
                if v.importance < 0.8  # Don't evict important items
            ]

            if lru_candidates:
                # Remove least recently accessed, lowest importance
                to_remove = min(
                    lru_candidates,
                    key=lambda x: (x[1].last_accessed, x[1].importance)
                )
                del self.memories[to_remove[0]]
            else:
                # All important, remove oldest
                self.memories.popitem(last=False)

        self.memories[item.id] = item
        self.memories.move_to_end(item.id)

        # Persist to disk
        if self.persistence_path:
            self._save_to_disk()

    def get(self, item_id: str) -> Optional[MemoryItem]:
        """Get item by ID"""
        item = self.memories.get(item_id)
        if item:
            item.access_count += 1
            item.last_accessed = datetime.now()
            self.memories.move_to_end(item_id)
        return item

    def search(self, query: str, limit: int = 20) -> List[MemoryItem]:
        """Search working memory"""
        query_lower = query.lower()

        # Score items by relevance
        scored_items = []
        for item in self.memories.values():
            score = 0.0

            # Text match
            if query_lower in item.content.lower():
                score += 1.0

            # Tag match
            for tag in item.tags:
                if query_lower in tag.lower():
                    score += 0.5

            # Recency bonus
            age_days = (datetime.now() - item.last_accessed).days
            recency_score = 1.0 / (1 + age_days)
            score += recency_score * 0.2

            # Importance bonus
            score += item.importance * 0.3

            if score > 0:
                scored_items.append((score, item))

        # Sort by score
        scored_items.sort(reverse=True, key=lambda x: x[0])

        return [item for score, item in scored_items[:limit]]

    def _save_to_disk(self):
        """Save working memory to disk"""
        if not self.persistence_path:
            return

        try:
            data = [item.to_dict() for item in self.memories.values()]

            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save working memory: {e}")

    def _load_from_disk(self):
        """Load working memory from disk"""
        try:
            with open(self.persistence_path, 'r') as f:
                data = json.load(f)

            for item_dict in data:
                item = MemoryItem.from_dict(item_dict)
                self.memories[item.id] = item

            logger.info(f"Loaded {len(self.memories)} items from working memory")
        except Exception as e:
            logger.error(f"Failed to load working memory: {e}")

    def get_stats(self) -> Dict:
        """Get statistics"""
        if not self.memories:
            return {
                'count': 0,
                'capacity': self.capacity
            }

        return {
            'capacity': self.capacity,
            'count': len(self.memories),
            'utilization': len(self.memories) / self.capacity,
            'avg_importance': sum(m.importance for m in self.memories.values()) / len(self.memories),
            'avg_access_count': sum(m.access_count for m in self.memories.values()) / len(self.memories),
        }


class LongTermMemory:
    """
    Long-term memory: Permanent knowledge

    SQLite database for persistent storage
    Capacity: Unlimited
    Lifespan: Forever
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                importance REAL NOT NULL,
                context TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                tags TEXT
            )
        ''')

        # Index for fast search
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_content_fts
            ON memories(content)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_memory_type
            ON memories(memory_type)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_importance
            ON memories(importance)
        ''')

        conn.commit()
        conn.close()

    async def add(self, item: MemoryItem):
        """Add item to long-term memory"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO memories
                (id, content, memory_type, importance, context, created_at, last_accessed, access_count, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.id,
                item.content,
                item.memory_type,
                item.importance,
                json.dumps(item.context),
                item.created_at.isoformat(),
                item.last_accessed.isoformat(),
                item.access_count,
                json.dumps(item.tags)
            ))

            conn.commit()
        finally:
            conn.close()

    async def get(self, item_id: str) -> Optional[MemoryItem]:
        """Get item by ID"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT * FROM memories WHERE id = ?
            ''', (item_id,))

            row = cursor.fetchone()

            if row:
                # Update access count
                cursor.execute('''
                    UPDATE memories
                    SET access_count = access_count + 1,
                        last_accessed = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), item_id))
                conn.commit()

                return self._row_to_item(row)
        finally:
            conn.close()

        return None

    async def search(self, query: str, limit: int = 50) -> List[MemoryItem]:
        """Search long-term memory"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            # Simple text search (could be enhanced with FTS5)
            cursor.execute('''
                SELECT * FROM memories
                WHERE content LIKE ?
                ORDER BY importance DESC, last_accessed DESC
                LIMIT ?
            ''', (f'%{query}%', limit))

            rows = cursor.fetchall()

            return [self._row_to_item(row) for row in rows]
        finally:
            conn.close()

    def _row_to_item(self, row: tuple) -> MemoryItem:
        """Convert database row to MemoryItem"""
        return MemoryItem(
            id=row[0],
            content=row[1],
            memory_type=row[2],
            importance=row[3],
            context=json.loads(row[4]),
            created_at=datetime.fromisoformat(row[5]),
            last_accessed=datetime.fromisoformat(row[6]),
            access_count=row[7],
            tags=json.loads(row[8]) if row[8] else []
        )

    async def get_stats(self) -> Dict:
        """Get statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT COUNT(*) FROM memories')
            total = cursor.fetchone()[0]

            cursor.execute('SELECT AVG(importance) FROM memories')
            avg_importance = cursor.fetchone()[0] or 0

            cursor.execute('SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type')
            type_distribution = dict(cursor.fetchall())

            return {
                'total': total,
                'avg_importance': avg_importance,
                'type_distribution': type_distribution,
                'database_size_mb': self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
            }
        finally:
            conn.close()


class MemorySystem:
    """
    Complete three-tier memory system

    Automatically manages memories across tiers based on importance and recency
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize memory system"""
        if storage_dir is None:
            storage_dir = Path.home() / '.luminous-nix' / 'memory'

        storage_dir.mkdir(parents=True, exist_ok=True)

        # Initialize tiers
        self.short_term = ShortTermMemory(capacity=100)

        self.working = WorkingMemory(
            capacity=1000,
            persistence_path=storage_dir / 'working_memory.json'
        )

        self.long_term = LongTermMemory(
            db_path=storage_dir / 'long_term_memory.db'
        )

        logger.info(f"✅ Memory system initialized")
        logger.info(f"   Storage: {storage_dir}")

    async def remember(self, item: MemoryItem):
        """
        Store memory with automatic tier management

        Importance levels:
        - < 0.5: Short-term only
        - 0.5-0.7: Short-term + working
        - 0.7-0.9: All tiers
        - > 0.9: Permanent (long-term emphasis)
        """

        # Generate ID if not set
        if not item.id:
            content_hash = hashlib.sha256(item.content.encode()).hexdigest()
            item.id = content_hash[:16]

        # Always to short-term
        self.short_term.add(item)

        # Important items to working memory
        if item.importance >= 0.5:
            self.working.add(item)

        # Very important to long-term
        if item.importance >= 0.7:
            await self.long_term.add(item)

    async def recall(self, query: str, context: Optional[Dict] = None) -> List[MemoryItem]:
        """
        Retrieve relevant memories from all tiers

        Searches all tiers in parallel and merges results
        """

        # Search all tiers in parallel
        short_term_task = asyncio.create_task(
            asyncio.to_thread(self.short_term.search, query)
        )

        working_task = asyncio.create_task(
            asyncio.to_thread(self.working.search, query)
        )

        long_term_task = asyncio.create_task(
            self.long_term.search(query)
        )

        # Wait for all searches
        short_results, working_results, long_results = await asyncio.gather(
            short_term_task, working_task, long_term_task
        )

        # Merge and deduplicate
        seen_ids = set()
        merged_results = []

        # Priority: Short-term (most recent) → Working → Long-term
        for result_set in [short_results, working_results, long_results]:
            for item in result_set:
                if item.id not in seen_ids:
                    seen_ids.add(item.id)
                    merged_results.append(item)

        # Sort by relevance (combination of importance, recency, access count)
        merged_results.sort(
            key=lambda x: (
                x.importance * 0.5 +
                (1.0 / (1 + (datetime.now() - x.last_accessed).days)) * 0.3 +
                min(x.access_count / 10, 1.0) * 0.2
            ),
            reverse=True
        )

        return merged_results

    async def forget(self, item_id: str):
        """Remove memory from all tiers"""
        # Remove from short-term
        if item_id in self.short_term.memories:
            del self.short_term.memories[item_id]

        # Remove from working
        if item_id in self.working.memories:
            del self.working.memories[item_id]
            if self.working.persistence_path:
                self.working._save_to_disk()

        # Remove from long-term
        conn = sqlite3.connect(str(self.long_term.db_path))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM memories WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()

    async def get_stats(self) -> Dict:
        """Get complete memory system statistics"""
        long_term_stats = await self.long_term.get_stats()

        return {
            'short_term': self.short_term.get_stats(),
            'working': self.working.get_stats(),
            'long_term': long_term_stats,
            'total_memories': (
                self.short_term.get_stats()['count'] +
                self.working.get_stats()['count'] +
                long_term_stats['total']
            )
        }


# Example usage
async def example_memory_usage():
    """Example of using memory system"""

    memory = MemorySystem()

    # Remember episodic memory
    await memory.remember(MemoryItem(
        id="",
        content="User installed firefox successfully",
        memory_type="episodic",
        importance=0.8,
        context={'package': 'firefox', 'success': True},
        tags=['install', 'firefox']
    ))

    # Remember semantic knowledge
    await memory.remember(MemoryItem(
        id="",
        content="Firefox is a web browser package in nixpkgs",
        memory_type="semantic",
        importance=0.9,
        context={'package': 'firefox', 'category': 'browser'},
        tags=['firefox', 'browser', 'knowledge']
    ))

    # Recall memories
    results = await memory.recall("firefox")

    print(f"Found {len(results)} memories about firefox:")
    for result in results:
        print(f"  - {result.content} (importance: {result.importance})")

    # Get stats
    stats = await memory.get_stats()
    print(f"\nMemory statistics:")
    print(json.dumps(stats, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(example_memory_usage())
