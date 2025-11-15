"""
Semantic Cache for EmbeddingGemma
High-performance vector similarity cache using FAISS/NumPy + SQLite
"""

import hashlib
import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Try to import FAISS for optimal performance
try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.info(
        "FAISS not available. Using NumPy for similarity search (slower but works)"
    )


@dataclass
class CachedResult:
    """Cached query result with metadata"""

    query: str
    query_hash: str
    embedding: Optional[np.ndarray]
    intent: str
    confidence: float
    response: dict[str, Any]
    timestamp: float
    access_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        d = asdict(self)
        # Convert numpy array to list for JSON serialization
        if self.embedding is not None:
            d["embedding"] = self.embedding.tolist()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CachedResult":
        """Reconstruct from dictionary"""
        # Convert list back to numpy array
        if d.get("embedding"):
            d["embedding"] = np.array(d["embedding"], dtype=np.float32)
        return cls(**d)


class SemanticCache:
    """
    High-performance semantic cache for NixOS queries.

    Features:
    - Exact match cache (hash-based)
    - Semantic similarity cache (vector search)
    - SQLite persistence
    - FAISS acceleration (optional)
    - LRU eviction policy
    """

    def __init__(
        self,
        encoder=None,
        cache_dir: Optional[Path] = None,
        max_cache_size: int = 10000,
        similarity_threshold: float = 0.9,
    ):
        """
        Initialize semantic cache.

        Args:
            encoder: GemmaEncoder instance for generating embeddings
            cache_dir: Directory for persistent cache
            max_cache_size: Maximum number of cached queries
            similarity_threshold: Minimum similarity for cache hit
        """
        self.encoder = encoder
        self.cache_dir = (
            cache_dir or Path.home() / ".cache" / "luminous-nix" / "semantic"
        )
        self.max_cache_size = max_cache_size
        self.similarity_threshold = similarity_threshold

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize caches
        self.exact_cache: dict[str, CachedResult] = {}  # Hash -> Result
        self.embeddings: list[np.ndarray] = []  # All embeddings
        self.results: list[CachedResult] = []  # Corresponding results

        # Initialize vector index
        self.index = None
        self.dimension = encoder.dimension if encoder else 768
        self._initialize_index()

        # Initialize SQLite for persistence
        self.db_path = self.cache_dir / "semantic_cache.db"
        self._initialize_db()

        # Load existing cache
        self._load_cache()

        # Performance tracking
        self.stats = {
            "exact_hits": 0,
            "semantic_hits": 0,
            "misses": 0,
            "total_queries": 0,
        }

    def _initialize_index(self):
        """Initialize the vector similarity index"""
        if FAISS_AVAILABLE:
            # Use FAISS for fast similarity search
            # L2 distance with normalization = cosine similarity
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine
            logger.info(f"Initialized FAISS index (dimension={self.dimension})")
        else:
            # Fallback to NumPy
            self.index = None
            logger.info("Using NumPy for similarity search")

    def _initialize_db(self):
        """Initialize SQLite database for persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                embedding BLOB,
                intent TEXT,
                confidence REAL,
                response TEXT,
                timestamp REAL,
                access_count INTEGER DEFAULT 0
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON cache(timestamp DESC)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_access_count
            ON cache(access_count DESC)
        """
        )

        conn.commit()
        conn.close()
        logger.info(f"Initialized cache database at {self.db_path}")

    def _load_cache(self):
        """Load cache from SQLite into memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Load most recently/frequently accessed entries
        cursor.execute(
            """
            SELECT * FROM cache
            ORDER BY access_count DESC, timestamp DESC
            LIMIT ?
        """,
            (self.max_cache_size,),
        )

        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            (
                query_hash,
                query,
                embedding_blob,
                intent,
                confidence,
                response_json,
                timestamp,
                access_count,
            ) = row

            # Reconstruct embedding
            embedding = None
            if embedding_blob:
                embedding = np.frombuffer(embedding_blob, dtype=np.float32)

            # Reconstruct result
            result = CachedResult(
                query=query,
                query_hash=query_hash,
                embedding=embedding,
                intent=intent,
                confidence=confidence,
                response=json.loads(response_json),
                timestamp=timestamp,
                access_count=access_count,
            )

            # Add to memory caches
            self.exact_cache[query_hash] = result
            if embedding is not None:
                self.embeddings.append(embedding)
                self.results.append(result)

        # Rebuild vector index
        if self.embeddings:
            self._rebuild_index()

        logger.info(f"Loaded {len(self.exact_cache)} entries from cache")

    def _rebuild_index(self):
        """Rebuild the vector similarity index"""
        if not self.embeddings:
            return

        embeddings_array = np.vstack(self.embeddings)

        if FAISS_AVAILABLE and self.index is not None:
            self.index.reset()
            self.index.add(embeddings_array)
        else:
            # NumPy doesn't need rebuilding
            pass

        logger.debug(f"Rebuilt index with {len(self.embeddings)} vectors")

    def get(self, query: str) -> Optional[CachedResult]:
        """
        Get cached result for query.

        First checks exact match, then semantic similarity.

        Args:
            query: The user query

        Returns:
            Cached result if found, None otherwise
        """
        self.stats["total_queries"] += 1

        # 1. Check exact match (fastest)
        query_hash = self._hash_query(query)
        if query_hash in self.exact_cache:
            result = self.exact_cache[query_hash]
            self._update_access(result)
            self.stats["exact_hits"] += 1
            logger.debug(f"Exact cache hit for: {query[:50]}...")
            return result

        # 2. Check semantic similarity (if encoder available)
        if self.encoder and self.embeddings:
            similar_result = self._find_similar(query)
            if similar_result:
                self._update_access(similar_result)
                self.stats["semantic_hits"] += 1
                logger.debug(f"Semantic cache hit for: {query[:50]}...")
                return similar_result

        # 3. Cache miss
        self.stats["misses"] += 1
        logger.debug(f"Cache miss for: {query[:50]}...")
        return None

    def _find_similar(self, query: str) -> Optional[CachedResult]:
        """Find semantically similar cached query"""
        if not self.encoder or not self.embeddings:
            return None

        # Generate query embedding
        query_embedding = self.encoder.encode_query(query)
        if query_embedding is None:
            return None

        # Normalize for cosine similarity
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        if FAISS_AVAILABLE and self.index is not None:
            # Use FAISS for fast search
            distances, indices = self.index.search(
                query_embedding.reshape(1, -1), k=min(5, len(self.embeddings))
            )

            if distances[0][0] >= self.similarity_threshold:
                return self.results[indices[0][0]]
        else:
            # NumPy fallback
            embeddings_array = np.vstack(self.embeddings)
            similarities = np.dot(embeddings_array, query_embedding)

            best_idx = np.argmax(similarities)
            if similarities[best_idx] >= self.similarity_threshold:
                return self.results[best_idx]

        return None

    def store(
        self, query: str, intent: str, confidence: float, response: dict[str, Any]
    ) -> CachedResult:
        """
        Store a query result in cache.

        Args:
            query: The original query
            intent: Recognized intent
            confidence: Confidence score
            response: The response to cache

        Returns:
            The cached result
        """
        query_hash = self._hash_query(query)

        # Generate embedding if encoder available
        embedding = None
        if self.encoder:
            embedding = self.encoder.encode_query(query)

        # Create cached result
        result = CachedResult(
            query=query,
            query_hash=query_hash,
            embedding=embedding,
            intent=intent,
            confidence=confidence,
            response=response,
            timestamp=time.time(),
            access_count=1,
        )

        # Add to memory caches
        self.exact_cache[query_hash] = result
        if embedding is not None:
            self.embeddings.append(embedding)
            self.results.append(result)

            # Update vector index
            if FAISS_AVAILABLE and self.index is not None:
                self.index.add(embedding.reshape(1, -1))

        # Persist to SQLite
        self._persist_result(result)

        # Evict if necessary
        if len(self.exact_cache) > self.max_cache_size:
            self._evict_lru()

        logger.debug(f"Cached result for: {query[:50]}...")
        return result

    def _persist_result(self, result: CachedResult):
        """Save result to SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        embedding_blob = None
        if result.embedding is not None:
            embedding_blob = result.embedding.tobytes()

        cursor.execute(
            """
            INSERT OR REPLACE INTO cache
            (query_hash, query, embedding, intent, confidence, response, timestamp, access_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                result.query_hash,
                result.query,
                embedding_blob,
                result.intent,
                result.confidence,
                json.dumps(result.response),
                result.timestamp,
                result.access_count,
            ),
        )

        conn.commit()
        conn.close()

    def _update_access(self, result: CachedResult):
        """Update access count and timestamp"""
        result.access_count += 1
        result.timestamp = time.time()

        # Update in SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE cache
            SET access_count = ?, timestamp = ?
            WHERE query_hash = ?
        """,
            (result.access_count, result.timestamp, result.query_hash),
        )

        conn.commit()
        conn.close()

    def _evict_lru(self):
        """Evict least recently used entries"""
        # Sort by access count and timestamp
        sorted_results = sorted(
            self.exact_cache.values(), key=lambda r: (r.access_count, r.timestamp)
        )

        # Evict bottom 10%
        evict_count = max(1, len(sorted_results) // 10)

        for result in sorted_results[:evict_count]:
            # Remove from memory
            del self.exact_cache[result.query_hash]

            # Remove from vector index
            if result.embedding is not None and result in self.results:
                idx = self.results.index(result)
                self.results.pop(idx)
                self.embeddings.pop(idx)

        # Rebuild vector index
        self._rebuild_index()

        logger.info(f"Evicted {evict_count} LRU entries")

    def _hash_query(self, query: str) -> str:
        """Generate hash for query"""
        # Normalize query for better matching
        normalized = query.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["total_queries"]
        if total == 0:
            hit_rate = 0
        else:
            hits = self.stats["exact_hits"] + self.stats["semantic_hits"]
            hit_rate = hits / total

        return {
            "cache_size": len(self.exact_cache),
            "vector_index_size": len(self.embeddings),
            "exact_hits": self.stats["exact_hits"],
            "semantic_hits": self.stats["semantic_hits"],
            "misses": self.stats["misses"],
            "total_queries": self.stats["total_queries"],
            "hit_rate": hit_rate,
            "similarity_threshold": self.similarity_threshold,
            "using_faiss": FAISS_AVAILABLE,
        }

    def clear(self):
        """Clear all caches"""
        self.exact_cache.clear()
        self.embeddings.clear()
        self.results.clear()

        if FAISS_AVAILABLE and self.index is not None:
            self.index.reset()

        # Clear database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache")
        conn.commit()
        conn.close()

        # Reset stats
        self.stats = {
            "exact_hits": 0,
            "semantic_hits": 0,
            "misses": 0,
            "total_queries": 0,
        }

        logger.info("Cache cleared")


def test_semantic_cache():
    """Test the semantic cache"""
    print("🧪 Testing Semantic Cache")
    print("=" * 50)

    # Import encoder
    from luminous_nix.embeddings.gemma_encoder import GemmaEncoder

    # Initialize
    encoder = GemmaEncoder(dimension=256)  # Smaller for speed
    cache = SemanticCache(encoder=encoder, similarity_threshold=0.85)

    # Test exact match
    print("\n1️⃣ Testing Exact Match:")
    response1 = {"packages": ["firefox"], "status": "success"}
    cache.store("install firefox", "install", 0.95, response1)

    result = cache.get("install firefox")
    print("  Query: 'install firefox'")
    print(f"  Hit: {result is not None}")
    print(f"  Access count: {result.access_count if result else 0}")

    # Test semantic match
    print("\n2️⃣ Testing Semantic Match:")
    result = cache.get("add firefox browser")
    print("  Query: 'add firefox browser'")
    print(f"  Hit: {result is not None}")
    if result:
        print(f"  Original query: '{result.query}'")
        print(f"  Intent: {result.intent}")

    # Test multiple similar queries
    print("\n3️⃣ Testing Multiple Similar Queries:")
    similar_queries = [
        "get firefox",
        "firefox installation",
        "setup firefox browser",
        "i want firefox",
    ]

    for q in similar_queries:
        result = cache.get(q)
        print(f"  '{q}' -> Hit: {result is not None}")

    # Test different intent
    print("\n4️⃣ Testing Different Intent:")
    response2 = {"packages": ["vim", "neovim"], "status": "success"}
    cache.store("search text editor", "search", 0.88, response2)

    result = cache.get("find text editor")
    print("  Query: 'find text editor'")
    print(f"  Hit: {result is not None}")
    if result:
        print(f"  Response: {result.response}")

    # Cache statistics
    print("\n📊 Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Performance test
    print("\n⚡ Performance Test:")
    import time

    # Exact match
    start = time.time()
    for _ in range(1000):
        cache.get("install firefox")
    exact_time = time.time() - start
    print(
        f"  1000 exact lookups: {exact_time*1000:.1f}ms ({exact_time/1000*1000:.3f}ms per lookup)"
    )

    # Semantic match
    start = time.time()
    for _ in range(100):
        cache.get("add firefox to my system")
    semantic_time = time.time() - start
    print(
        f"  100 semantic lookups: {semantic_time*1000:.1f}ms ({semantic_time/100*1000:.1f}ms per lookup)"
    )

    print("\n✅ Semantic cache test complete!")


if __name__ == "__main__":
    test_semantic_cache()
