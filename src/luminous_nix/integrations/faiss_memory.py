"""
FAISS Vector Memory for Semantic Search and Learning
Facebook AI Similarity Search for ultra-fast vector operations
"""

import numpy as np
import json
import pickle
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    logger.warning("FAISS not available. Install with: pip install faiss-cpu or faiss-gpu")

@dataclass
class Memory:
    """A single memory in the vector store"""
    id: str
    text: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0
    access_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding embedding)"""
        data = asdict(self)
        data.pop('embedding', None)  # Don't serialize embeddings
        data['timestamp'] = self.timestamp.isoformat()
        return data
        

class FAISSMemoryStore:
    """High-performance semantic memory using FAISS"""
    
    def __init__(
        self,
        dimension: int = 768,  # Default for sentence-transformers
        index_type: str = "IVF",  # IVF, Flat, HNSW
        memory_path: Optional[Path] = None
    ):
        if not HAS_FAISS:
            raise ImportError("FAISS is required but not installed")
            
        self.dimension = dimension
        self.index_type = index_type
        self.memory_path = memory_path or Path.home() / ".luminous-nix" / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        self._init_index()
        
        # Memory storage
        self.memories: Dict[str, Memory] = {}
        self.id_to_idx: Dict[str, int] = {}  # Map memory ID to FAISS index
        self.idx_to_id: Dict[int, str] = {}  # Map FAISS index to memory ID
        
        # Load existing memories if available
        self.load()
        
    def _init_index(self):
        """Initialize FAISS index based on type"""
        if self.index_type == "Flat":
            # Exact search - slower but precise
            self.index = faiss.IndexFlatL2(self.dimension)
            
        elif self.index_type == "IVF":
            # Inverted file index - fast approximate search
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            self.index.nprobe = 10  # Number of clusters to search
            
        elif self.index_type == "HNSW":
            # Hierarchical Navigable Small World - very fast
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            
        else:
            # Default to flat index
            self.index = faiss.IndexFlatL2(self.dimension)
            
        logger.info(f"Initialized FAISS {self.index_type} index with dimension {self.dimension}")
        
    def _generate_id(self, text: str) -> str:
        """Generate unique ID for memory"""
        return hashlib.md5(f"{text}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
    def add_memory(
        self,
        text: str,
        embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a memory to the store"""
        
        # Validate embedding dimension
        if embedding.shape[0] != self.dimension:
            raise ValueError(f"Embedding dimension {embedding.shape[0]} doesn't match index dimension {self.dimension}")
            
        # Create memory
        memory_id = self._generate_id(text)
        memory = Memory(
            id=memory_id,
            text=text,
            embedding=embedding,
            metadata=metadata or {}
        )
        
        # Add to FAISS index
        idx = len(self.memories)
        self.index.add(embedding.reshape(1, -1))
        
        # Store mappings
        self.memories[memory_id] = memory
        self.id_to_idx[memory_id] = idx
        self.idx_to_id[idx] = memory_id
        
        logger.debug(f"Added memory {memory_id}: {text[:50]}...")
        return memory_id
        
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Tuple[Memory, float]]:
        """Search for similar memories"""
        
        if len(self.memories) == 0:
            return []
            
        # Search in FAISS
        distances, indices = self.index.search(query_embedding.reshape(1, -1), min(k, len(self.memories)))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
                
            memory_id = self.idx_to_id.get(idx)
            if memory_id:
                memory = self.memories[memory_id]
                
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + dist)
                
                # Apply threshold if specified
                if threshold is None or similarity >= threshold:
                    # Update access count
                    memory.access_count += 1
                    results.append((memory, similarity))
                    
        return results
        
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get a specific memory by ID"""
        return self.memories.get(memory_id)
        
    def update_relevance(self, memory_id: str, delta: float):
        """Update relevance score based on user feedback"""
        if memory_id in self.memories:
            self.memories[memory_id].relevance_score += delta
            self.memories[memory_id].relevance_score = max(0.0, min(1.0, self.memories[memory_id].relevance_score))
            
    def forget(self, memory_id: str) -> bool:
        """Remove a memory from the store"""
        if memory_id not in self.memories:
            return False
            
        # Note: FAISS doesn't support deletion, so we mark as deleted
        # In production, periodically rebuild index without deleted items
        self.memories[memory_id].relevance_score = -1.0  # Mark as deleted
        return True
        
    def save(self):
        """Save memory store to disk"""
        # Save FAISS index
        index_path = self.memory_path / "faiss.index"
        faiss.write_index(self.index, str(index_path))
        
        # Save memories and mappings
        data = {
            "memories": {k: v.to_dict() for k, v in self.memories.items()},
            "id_to_idx": self.id_to_idx,
            "idx_to_id": self.idx_to_id,
            "dimension": self.dimension,
            "index_type": self.index_type,
        }
        
        data_path = self.memory_path / "memories.json"
        with open(data_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Saved {len(self.memories)} memories to {self.memory_path}")
        
    def load(self):
        """Load memory store from disk"""
        index_path = self.memory_path / "faiss.index"
        data_path = self.memory_path / "memories.json"
        
        if not index_path.exists() or not data_path.exists():
            logger.info("No existing memory store found")
            return
            
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_path))
            
            # Load memories and mappings
            with open(data_path) as f:
                data = json.load(f)
                
            # Reconstruct memories
            self.memories = {}
            for memory_id, memory_data in data["memories"].items():
                memory = Memory(
                    id=memory_data["id"],
                    text=memory_data["text"],
                    metadata=memory_data.get("metadata", {}),
                    timestamp=datetime.fromisoformat(memory_data["timestamp"]),
                    relevance_score=memory_data.get("relevance_score", 1.0),
                    access_count=memory_data.get("access_count", 0)
                )
                self.memories[memory_id] = memory
                
            self.id_to_idx = data["id_to_idx"]
            self.idx_to_id = {int(k): v for k, v in data["idx_to_id"].items()}
            
            logger.info(f"Loaded {len(self.memories)} memories from {self.memory_path}")
            
        except Exception as e:
            logger.error(f"Failed to load memory store: {e}")
            

class SemanticLearningSystem:
    """Learn from user interactions using semantic memory"""
    
    def __init__(self, memory_store: FAISSMemoryStore):
        self.memory = memory_store
        self.embedding_cache: Dict[str, np.ndarray] = {}
        
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text (cached)"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
            
        # In production, use sentence-transformers or OpenAI embeddings
        # For now, create random embedding for demonstration
        embedding = np.random.randn(self.memory.dimension).astype('float32')
        embedding = embedding / np.linalg.norm(embedding)  # Normalize
        
        self.embedding_cache[text] = embedding
        return embedding
        
    def learn_from_interaction(
        self,
        user_query: str,
        system_response: str,
        was_helpful: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Learn from a user interaction"""
        
        # Create memory text
        memory_text = f"Q: {user_query}\nA: {system_response}"
        
        # Get embedding
        embedding = self._get_embedding(memory_text)
        
        # Add metadata
        meta = metadata or {}
        meta.update({
            "query": user_query,
            "response": system_response,
            "helpful": was_helpful,
            "type": "interaction"
        })
        
        # Store memory
        memory_id = self.memory.add_memory(memory_text, embedding, meta)
        
        # Adjust relevance based on feedback
        if not was_helpful:
            self.memory.update_relevance(memory_id, -0.2)
            
        logger.info(f"Learned from interaction: {memory_id}")
        
    def find_similar_interactions(
        self,
        query: str,
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """Find similar past interactions"""
        
        query_embedding = self._get_embedding(query)
        results = self.memory.search(query_embedding, k)
        
        similar = []
        for memory, similarity in results:
            if memory.metadata.get("type") == "interaction":
                similar.append({
                    "query": memory.metadata.get("query"),
                    "response": memory.metadata.get("response"),
                    "similarity": similarity,
                    "helpful": memory.metadata.get("helpful"),
                    "access_count": memory.access_count
                })
                
        return similar
        
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about learned patterns"""
        
        total_memories = len(self.memory.memories)
        helpful_count = sum(1 for m in self.memory.memories.values() 
                          if m.metadata.get("helpful"))
        
        most_accessed = sorted(
            self.memory.memories.values(),
            key=lambda m: m.access_count,
            reverse=True
        )[:5]
        
        return {
            "total_memories": total_memories,
            "helpful_ratio": helpful_count / max(1, total_memories),
            "most_accessed": [
                {
                    "text": m.text[:100],
                    "access_count": m.access_count,
                    "relevance": m.relevance_score
                }
                for m in most_accessed
            ]
        }


# Integration with Luminous Nix
class NixOSKnowledgeBase:
    """Semantic knowledge base for NixOS information"""
    
    def __init__(self):
        self.memory = FAISSMemoryStore(dimension=384)  # all-MiniLM-L6-v2 dimension
        self.learning = SemanticLearningSystem(self.memory)
        self._preload_knowledge()
        
    def _preload_knowledge(self):
        """Preload NixOS knowledge"""
        knowledge_items = [
            ("Install Firefox", "nix-env -iA nixos.firefox", {"category": "installation"}),
            ("Update system", "sudo nixos-rebuild switch", {"category": "system"}),
            ("Search packages", "nix search nixpkgs <package>", {"category": "search"}),
            ("List generations", "nix-env --list-generations", {"category": "management"}),
            ("Rollback", "nixos-rebuild switch --rollback", {"category": "recovery"}),
        ]
        
        for query, answer, metadata in knowledge_items:
            text = f"Q: {query}\nA: {answer}"
            embedding = np.random.randn(self.memory.dimension).astype('float32')
            embedding = embedding / np.linalg.norm(embedding)
            self.memory.add_memory(text, embedding, metadata)
            
    def find_answer(self, question: str) -> Optional[str]:
        """Find answer to a NixOS question"""
        similar = self.learning.find_similar_interactions(question, k=1)
        
        if similar and similar[0]["similarity"] > 0.7:
            return similar[0]["response"]
        return None