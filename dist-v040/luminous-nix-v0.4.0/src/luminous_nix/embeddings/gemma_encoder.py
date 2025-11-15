"""
EmbeddingGemma Integration for Luminous Nix
Provides semantic understanding for NixOS queries using Google's 308M parameter model
"""

import json
import logging
import time
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

# Optional imports - graceful degradation if not available
try:
    from sentence_transformers import SentenceTransformer
    import torch

    GEMMA_AVAILABLE = True
except ImportError:
    GEMMA_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Semantic features disabled.")

try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.info("FAISS not available. Using numpy for similarity search.")


class GemmaEncoder:
    """
    EmbeddingGemma encoder for semantic understanding of NixOS queries.

    Features:
    - 308M parameters, multilingual support (100+ languages)
    - Matryoshka embeddings (128-768 dimensions)
    - On-device processing (<200MB RAM)
    - Task-specific prompting for better performance
    """

    MODEL_NAME = "google/embeddinggemma-300m"
    DEFAULT_DIMENSION = 768
    CACHE_DIR = Path.home() / ".cache" / "luminous-nix" / "models"

    def __init__(self, dimension: int = DEFAULT_DIMENSION, use_gpu: bool = False):
        """
        Initialize the Gemma encoder.

        Args:
            dimension: Output embedding dimension (128, 256, 512, or 768)
            use_gpu: Whether to use GPU acceleration if available
        """
        self.dimension = dimension
        self.use_gpu = (
            use_gpu and torch.cuda.is_available() if GEMMA_AVAILABLE else False
        )
        self.model = None
        self.device = None

        # Performance tracking
        self._encoding_times = []

        if GEMMA_AVAILABLE:
            self._initialize_model()
        else:
            logger.warning("Using fallback mode without EmbeddingGemma")

    def _initialize_model(self):
        """Initialize the SentenceTransformer model"""
        try:
            # Ensure cache directory exists
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

            # Load model with caching
            logger.info(f"Loading EmbeddingGemma model: {self.MODEL_NAME}")
            self.model = SentenceTransformer(
                self.MODEL_NAME,
                cache_folder=str(self.CACHE_DIR),
                device="cuda" if self.use_gpu else "cpu",
            )
            self.device = self.model.device

            logger.info(f"Model loaded successfully on {self.device}")

            # Warm up the model
            self._warmup()

        except Exception as e:
            logger.error(f"Failed to load EmbeddingGemma: {e}")
            self.model = None

    def _warmup(self):
        """Warm up the model with a sample query"""
        if self.model:
            try:
                self.encode_query("test")
                logger.debug("Model warmup completed")
            except:
                pass

    def encode_query(
        self, text: str, dimension: Optional[int] = None
    ) -> Optional[np.ndarray]:
        """
        Encode a user query into a semantic embedding.

        Args:
            text: The query text to encode
            dimension: Override dimension for this encoding

        Returns:
            Numpy array of shape (dimension,) or None if encoding fails
        """
        if not GEMMA_AVAILABLE or not self.model:
            return self._fallback_encoding(text, dimension or self.dimension)

        try:
            start_time = time.time()

            # Add query prompt for better performance (as per Gemma docs)
            prompted_text = f"query: {text}"

            # Generate embedding
            embedding = self.model.encode(
                prompted_text, convert_to_numpy=True, normalize_embeddings=True
            )

            # Truncate to requested dimension (Matryoshka)
            target_dim = dimension or self.dimension
            if target_dim < len(embedding):
                embedding = embedding[:target_dim]

            # Track performance
            elapsed = (time.time() - start_time) * 1000
            self._encoding_times.append(elapsed)

            logger.debug(f"Encoded query in {elapsed:.1f}ms (dim={target_dim})")
            return embedding

        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            return self._fallback_encoding(text, dimension or self.dimension)

    def encode_documents(
        self, texts: List[str], dimension: Optional[int] = None
    ) -> Optional[np.ndarray]:
        """
        Batch encode multiple documents for indexing.

        Args:
            texts: List of document texts
            dimension: Override dimension for these encodings

        Returns:
            Numpy array of shape (n_texts, dimension) or None
        """
        if not texts:
            return None

        if not GEMMA_AVAILABLE or not self.model:
            return np.vstack(
                [
                    self._fallback_encoding(text, dimension or self.dimension)
                    for text in texts
                ]
            )

        try:
            start_time = time.time()

            # Add document prompt for better performance
            prompted_texts = [f"document: {text}" for text in texts]

            # Batch encode
            embeddings = self.model.encode(
                prompted_texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=32,
                show_progress_bar=len(texts) > 100,
            )

            # Truncate to requested dimension
            target_dim = dimension or self.dimension
            if target_dim < embeddings.shape[1]:
                embeddings = embeddings[:, :target_dim]

            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Encoded {len(texts)} documents in {elapsed:.1f}ms")

            return embeddings

        except Exception as e:
            logger.error(f"Batch encoding failed: {e}")
            return None

    def _fallback_encoding(self, text: str, dimension: int) -> np.ndarray:
        """
        Fallback encoding when Gemma is not available.
        Uses simple hashing for deterministic pseudo-embeddings.
        """
        # Create deterministic pseudo-embedding from text
        import hashlib

        # Hash the text
        text_hash = hashlib.sha256(text.encode()).digest()

        # Convert to normalized vector
        values = np.frombuffer(text_hash, dtype=np.uint8)

        # Repeat or truncate to match dimension
        if len(values) < dimension:
            values = np.tile(values, (dimension // len(values)) + 1)[:dimension]
        else:
            values = values[:dimension]

        # Normalize to [-1, 1]
        embedding = (values.astype(np.float32) / 127.5) - 1.0

        # L2 normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def compute_similarity(
        self, query_embedding: np.ndarray, document_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between query and documents.

        Args:
            query_embedding: Query embedding vector
            document_embeddings: Matrix of document embeddings

        Returns:
            Array of similarity scores
        """
        if query_embedding is None or document_embeddings is None:
            return np.array([])

        # Ensure 2D shape for documents
        if document_embeddings.ndim == 1:
            document_embeddings = document_embeddings.reshape(1, -1)

        # Compute cosine similarity (assuming normalized embeddings)
        similarities = np.dot(document_embeddings, query_embedding)

        return similarities

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self._encoding_times:
            return {"status": "no_data"}

        return {
            "model": self.MODEL_NAME if GEMMA_AVAILABLE else "fallback",
            "dimension": self.dimension,
            "device": str(self.device) if self.device else "cpu",
            "avg_encoding_time_ms": np.mean(self._encoding_times),
            "min_encoding_time_ms": np.min(self._encoding_times),
            "max_encoding_time_ms": np.max(self._encoding_times),
            "total_encodings": len(self._encoding_times),
        }

    def optimize_dimension(self, target_latency_ms: float = 10.0) -> int:
        """
        Find optimal embedding dimension for target latency.
        Leverages Matryoshka Representation Learning.

        Args:
            target_latency_ms: Target encoding latency in milliseconds

        Returns:
            Optimal dimension (128, 256, 512, or 768)
        """
        dimensions = [768, 512, 256, 128]
        test_text = "install firefox browser on nixos system"

        for dim in dimensions:
            start = time.time()
            embedding = self.encode_query(test_text, dimension=dim)
            latency = (time.time() - start) * 1000

            if latency <= target_latency_ms:
                logger.info(f"Optimized to {dim}D for {latency:.1f}ms latency")
                self.dimension = dim
                return dim

        # If even 128D is too slow, keep it anyway
        self.dimension = 128
        return 128


class SemanticIntentRecognizer:
    """
    Intent recognition using EmbeddingGemma semantic understanding.
    Maps natural language to NixOS operations with high accuracy.
    """

    # Intent templates for semantic matching
    INTENT_TEMPLATES = {
        "install": [
            "install package {}",
            "add {} to system",
            "setup {} on nixos",
            "get {} working",
            "I need {}",
        ],
        "search": [
            "find package {}",
            "search for {}",
            "what packages have {}",
            "looking for {}",
            "show me {} packages",
        ],
        "remove": ["uninstall {}", "remove package {}", "delete {}", "get rid of {}"],
        "update": [
            "update system",
            "upgrade packages",
            "update nixos",
            "upgrade everything",
            "refresh packages",
        ],
        "list": [
            "list installed packages",
            "show what's installed",
            "what packages do I have",
            "display installed software",
        ],
        "info": [
            "information about {}",
            "describe package {}",
            "what is {}",
            "tell me about {}",
        ],
        "configure": [
            "configure {}",
            "setup {} service",
            "enable {}",
            "create {} configuration",
        ],
        "generate": [
            "generate {} config",
            "create configuration for {}",
            "write {} setup",
            "make {} configuration",
        ],
    }

    def __init__(self, encoder: Optional[GemmaEncoder] = None):
        """Initialize with Gemma encoder"""
        self.encoder = encoder or GemmaEncoder()
        self.template_embeddings = None
        self.intent_labels = []

        self._build_template_index()

    def _build_template_index(self):
        """Pre-compute embeddings for all intent templates"""
        all_templates = []

        for intent, templates in self.INTENT_TEMPLATES.items():
            for template in templates:
                # Use placeholder for variety
                filled = template.replace("{}", "package")
                all_templates.append(filled)
                self.intent_labels.append(intent)

        # Encode all templates
        self.template_embeddings = self.encoder.encode_documents(all_templates)
        logger.info(f"Indexed {len(all_templates)} intent templates")

    def recognize(self, query: str, threshold: float = 0.7) -> Dict[str, Any]:
        """
        Recognize intent from natural language query.

        Args:
            query: User's natural language input
            threshold: Minimum similarity threshold

        Returns:
            Dict with intent type, confidence, and extracted entities
        """
        if not self.template_embeddings is not None:
            # Fallback to keyword matching
            return self._keyword_fallback(query)

        # Encode query
        query_embedding = self.encoder.encode_query(query)
        if query_embedding is None:
            return self._keyword_fallback(query)

        # Compute similarities
        similarities = self.encoder.compute_similarity(
            query_embedding, self.template_embeddings
        )

        # Find best match
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        best_intent = self.intent_labels[best_idx]

        if best_score < threshold:
            # Low confidence - might be complex query
            return {
                "type": "unknown",
                "confidence": float(best_score),
                "query": query,
                "suggestion": "Try rephrasing your request",
            }

        # Extract entities (simple for now)
        entities = self._extract_entities(query, best_intent)

        return {
            "type": best_intent,
            "confidence": float(best_score),
            "query": query,
            "entities": entities,
            "semantic": True,
        }

    def _extract_entities(self, query: str, intent: str) -> Dict[str, str]:
        """Extract entities from query based on intent"""
        entities = {}

        # Simple extraction - can be enhanced with NER
        if intent in ["install", "search", "remove", "info"]:
            # Remove common words
            words = query.lower().split()
            stopwords = {
                "install",
                "search",
                "remove",
                "find",
                "package",
                "for",
                "the",
                "a",
                "an",
                "on",
                "nixos",
                "system",
                "info",
                "about",
                "information",
                "tell",
                "me",
            }

            remaining = [w for w in words if w not in stopwords]
            if remaining:
                entities["package"] = " ".join(remaining)

        elif intent == "configure":
            # Extract service name
            if "service" in query:
                parts = query.split("service")
                if parts[0].strip():
                    service = parts[0].strip().split()[-1]
                    entities["service"] = service

        return entities

    def _keyword_fallback(self, query: str) -> Dict[str, Any]:
        """Fallback to keyword matching when embeddings unavailable"""
        query_lower = query.lower()

        for intent, templates in self.INTENT_TEMPLATES.items():
            for template in templates:
                # Check for intent keywords
                keywords = template.replace("{}", "").strip().split()
                if any(keyword in query_lower for keyword in keywords):
                    return {
                        "type": intent,
                        "confidence": 0.6,  # Lower confidence for keyword matching
                        "query": query,
                        "entities": self._extract_entities(query, intent),
                        "semantic": False,
                    }

        return {
            "type": "unknown",
            "confidence": 0.0,
            "query": query,
            "suggestion": "Could not understand request",
        }


def test_gemma_integration():
    """Test the EmbeddingGemma integration"""
    print("🧪 Testing EmbeddingGemma Integration")
    print("=" * 50)

    # Initialize encoder
    encoder = GemmaEncoder(dimension=768)
    recognizer = SemanticIntentRecognizer(encoder)

    # Test queries
    test_queries = [
        "install firefox",
        "add mozilla firefox browser",
        "instalar firefox",  # Spanish
        "search for text editor",
        "find vim or neovim",
        "update my system",
        "what packages are installed",
        "configure nginx web server",
        "generate python development environment",
    ]

    print("\n📝 Intent Recognition Tests:")
    for query in test_queries:
        result = recognizer.recognize(query)
        print(f"\nQuery: '{query}'")
        print(f"  Intent: {result['type']} (confidence: {result['confidence']:.2f})")
        if result.get("entities"):
            print(f"  Entities: {result['entities']}")
        if result.get("suggestion"):
            print(f"  Suggestion: {result['suggestion']}")

    # Test semantic similarity
    print("\n🔍 Semantic Similarity Test:")
    similar_queries = [
        "install firefox",
        "add firefox to my system",
        "get firefox browser",
        "firefox installation",
    ]

    embeddings = []
    for q in similar_queries:
        emb = encoder.encode_query(q)
        if emb is not None:
            embeddings.append(emb)

    if embeddings:
        embeddings = np.vstack(embeddings)
        similarities = np.dot(embeddings, embeddings.T)

        print("\nSimilarity Matrix:")
        for i, q1 in enumerate(similar_queries):
            scores = [f"{similarities[i,j]:.2f}" for j in range(len(similar_queries))]
            print(f"  {q1[:20]:20} | {' '.join(scores)}")

    # Performance stats
    print("\n📊 Performance Statistics:")
    stats = encoder.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Dimension optimization
    print("\n⚡ Dimension Optimization:")
    optimal = encoder.optimize_dimension(target_latency_ms=15.0)
    print(f"  Optimal dimension for 15ms target: {optimal}D")

    print("\n✅ EmbeddingGemma integration test complete!")


if __name__ == "__main__":
    test_gemma_integration()
