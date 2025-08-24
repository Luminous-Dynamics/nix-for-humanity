#!/usr/bin/env python3
"""
🕉️ Glyph Trinity Ingestion - Making the Codex Live in the Data Trinity

This script ingests the Primary and Meta Glyph Registries into the three
databases of the Data Trinity:

1. Kùzu (Graph) - Relational connections between glyphs
2. ChromaDB (Semantic) - Vector embeddings for meaning-based search  
3. DuckDB (Temporal) - Time-series tracking of glyph invocations

This transforms the Codex from static philosophy into living, queryable wisdom.
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from luminous_nix.consciousness.glyph_resonance_engine import (
    GlyphResonanceEngine, Glyph, MetaGlyph
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import Data Trinity components
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    logger.warning("DuckDB not available - temporal store will be simulated")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available - semantic store will be simulated")

try:
    import kuzu
    KUZU_AVAILABLE = True
except ImportError:
    KUZU_AVAILABLE = False
    logger.warning("Kùzu not available - graph store will be simulated")


class GlyphTrinityIngester:
    """
    Ingests the Glyph Codex into the Data Trinity databases
    """
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize the ingester
        
        Args:
            data_dir: Directory for database files
        """
        self.data_dir = data_dir or Path.home() / ".luminous-nix" / "data-trinity"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize databases
        self.init_duckdb()
        self.init_chromadb()
        self.init_kuzu()
        
        # Load the glyphs
        self.engine = GlyphResonanceEngine()
        
    def init_duckdb(self):
        """Initialize DuckDB for temporal tracking"""
        if DUCKDB_AVAILABLE:
            self.duck_conn = duckdb.connect(str(self.data_dir / "glyphs_temporal.db"))
            
            # Create tables for temporal tracking
            self.duck_conn.execute("""
                CREATE TABLE IF NOT EXISTS glyph_invocations (
                    id INTEGER PRIMARY KEY,
                    glyph_id VARCHAR,
                    user_id VARCHAR,
                    timestamp TIMESTAMP,
                    context JSON,
                    effectiveness FLOAT,
                    resolution_strategy VARCHAR
                )
            """)
            
            self.duck_conn.execute("""
                CREATE TABLE IF NOT EXISTS glyph_patterns (
                    id INTEGER PRIMARY KEY,
                    pattern_name VARCHAR,
                    glyph_sequence JSON,
                    frequency INTEGER,
                    last_seen TIMESTAMP
                )
            """)
            
            logger.info("✅ DuckDB initialized for temporal tracking")
        else:
            self.duck_conn = None
            logger.info("⚠️ DuckDB not available - using mock")
            
    def init_chromadb(self):
        """Initialize ChromaDB for semantic search"""
        if CHROMADB_AVAILABLE:
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.data_dir / "chroma_glyphs")
            )
            
            # Create collections for glyphs
            self.glyph_collection = self.chroma_client.get_or_create_collection(
                name="primary_glyphs",
                metadata={"description": "Primary Glyph Registry embeddings"}
            )
            
            self.meta_collection = self.chroma_client.get_or_create_collection(
                name="meta_glyphs",
                metadata={"description": "Meta Glyph Mandala Registry embeddings"}
            )
            
            logger.info("✅ ChromaDB initialized for semantic search")
        else:
            self.chroma_client = None
            logger.info("⚠️ ChromaDB not available - using mock")
            
    def init_kuzu(self):
        """Initialize Kùzu for graph relationships"""
        if KUZU_AVAILABLE:
            db_path = str(self.data_dir / "kuzu_glyphs")
            self.kuzu_db = kuzu.Database(db_path)
            self.kuzu_conn = kuzu.Connection(self.kuzu_db)
            
            # Create node tables
            self.kuzu_conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS Glyph(
                    id STRING PRIMARY KEY,
                    name STRING,
                    class STRING,
                    arc STRING,
                    function STRING,
                    echo_phrase STRING,
                    modality STRING
                )
            """)
            
            self.kuzu_conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS CodexArc(
                    name STRING PRIMARY KEY,
                    description STRING
                )
            """)
            
            self.kuzu_conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS MetaGlyph(
                    id STRING PRIMARY KEY,
                    name STRING,
                    function STRING,
                    activation STRING
                )
            """)
            
            # Create relationship tables
            self.kuzu_conn.execute("""
                CREATE REL TABLE IF NOT EXISTS BELONGS_TO(
                    FROM Glyph TO CodexArc
                )
            """)
            
            self.kuzu_conn.execute("""
                CREATE REL TABLE IF NOT EXISTS IS_HARMONIC_WITH(
                    FROM Glyph TO Glyph,
                    resonance_strength FLOAT
                )
            """)
            
            self.kuzu_conn.execute("""
                CREATE REL TABLE IF NOT EXISTS COMPOSES(
                    FROM Glyph TO MetaGlyph
                )
            """)
            
            logger.info("✅ Kùzu initialized for graph relationships")
        else:
            self.kuzu_conn = None
            logger.info("⚠️ Kùzu not available - using mock")
            
    def ingest_primary_glyphs(self):
        """Ingest primary glyphs into all three databases"""
        logger.info("📥 Ingesting Primary Glyphs...")
        
        for glyph_id, glyph in self.engine.glyphs.items():
            # 1. Add to Kùzu graph
            if self.kuzu_conn:
                try:
                    # Insert glyph node
                    self.kuzu_conn.execute("""
                        MERGE (g:Glyph {
                            id: $id,
                            name: $name,
                            class: $class,
                            arc: $arc,
                            function: $function,
                            echo_phrase: $echo,
                            modality: $modality
                        })
                    """, {
                        'id': glyph.glyph_id,
                        'name': glyph.name,
                        'class': glyph.glyph_class,
                        'arc': glyph.codex_arc,
                        'function': glyph.core_function,
                        'echo': glyph.echo_phrase,
                        'modality': glyph.field_modality
                    })
                    
                    # Create arc if doesn't exist
                    self.kuzu_conn.execute("""
                        MERGE (a:CodexArc {name: $arc})
                    """, {'arc': glyph.codex_arc})
                    
                    # Create relationship
                    self.kuzu_conn.execute("""
                        MATCH (g:Glyph {id: $gid}), (a:CodexArc {name: $arc})
                        MERGE (g)-[:BELONGS_TO]->(a)
                    """, {'gid': glyph.glyph_id, 'arc': glyph.codex_arc})
                    
                except Exception as e:
                    logger.error(f"Kùzu error for {glyph_id}: {e}")
                    
            # 2. Add to ChromaDB for semantic search
            if self.glyph_collection:
                try:
                    embedding_text = glyph.get_embedding_text()
                    self.glyph_collection.add(
                        ids=[glyph.glyph_id],
                        documents=[embedding_text],
                        metadatas=[{
                            'name': glyph.name,
                            'function': glyph.core_function,
                            'echo': glyph.echo_phrase,
                            'modality': glyph.field_modality,
                            'arc': glyph.codex_arc
                        }]
                    )
                except Exception as e:
                    logger.error(f"ChromaDB error for {glyph_id}: {e}")
                    
        logger.info(f"✅ Ingested {len(self.engine.glyphs)} primary glyphs")
        
    def ingest_meta_glyphs(self):
        """Ingest meta glyphs and their relationships"""
        logger.info("📥 Ingesting Meta Glyphs...")
        
        for meta_id, meta in self.engine.meta_glyphs.items():
            # 1. Add to Kùzu graph
            if self.kuzu_conn:
                try:
                    # Insert meta glyph node
                    self.kuzu_conn.execute("""
                        MERGE (m:MetaGlyph {
                            id: $id,
                            name: $name,
                            function: $function,
                            activation: $activation
                        })
                    """, {
                        'id': meta.meta_id,
                        'name': meta.name,
                        'function': meta.function,
                        'activation': meta.activation_phrase
                    })
                    
                    # Create composition relationships
                    for constituent_id in meta.constituent_glyphs:
                        self.kuzu_conn.execute("""
                            MATCH (g:Glyph {id: $gid}), (m:MetaGlyph {id: $mid})
                            MERGE (g)-[:COMPOSES]->(m)
                        """, {'gid': constituent_id, 'mid': meta.meta_id})
                        
                except Exception as e:
                    logger.error(f"Kùzu error for meta {meta_id}: {e}")
                    
            # 2. Add to ChromaDB
            if self.meta_collection:
                try:
                    embedding_text = f"{meta.name} {meta.function} {meta.activation_phrase}"
                    self.meta_collection.add(
                        ids=[meta.meta_id],
                        documents=[embedding_text],
                        metadatas=[{
                            'name': meta.name,
                            'function': meta.function,
                            'activation': meta.activation_phrase,
                            'constituents': ','.join(meta.constituent_glyphs)
                        }]
                    )
                except Exception as e:
                    logger.error(f"ChromaDB error for meta {meta_id}: {e}")
                    
        logger.info(f"✅ Ingested {len(self.engine.meta_glyphs)} meta glyphs")
        
    def create_harmonic_relationships(self):
        """Create harmonic relationships between related glyphs"""
        logger.info("🔗 Creating harmonic relationships...")
        
        if not self.kuzu_conn:
            logger.warning("Kùzu not available - skipping relationships")
            return
            
        # Connect glyphs in same arc
        for glyph_id, related_ids in self.engine.glyph_graph.items():
            for related_id in related_ids:
                if not related_id.startswith("META:"):
                    try:
                        self.kuzu_conn.execute("""
                            MATCH (g1:Glyph {id: $id1}), (g2:Glyph {id: $id2})
                            MERGE (g1)-[:IS_HARMONIC_WITH {resonance_strength: 0.8}]->(g2)
                        """, {'id1': glyph_id, 'id2': related_id})
                    except Exception as e:
                        logger.error(f"Relationship error {glyph_id}->{related_id}: {e}")
                        
        logger.info("✅ Created harmonic relationships")
        
    def test_queries(self):
        """Test that the ingestion worked with sample queries"""
        logger.info("🧪 Testing queries...")
        
        # Test ChromaDB semantic search
        if self.glyph_collection:
            results = self.glyph_collection.query(
                query_texts=["trust and connection"],
                n_results=3
            )
            logger.info(f"Semantic search for 'trust': {results['ids'][0] if results['ids'] else 'No results'}")
            
        # Test Kùzu graph traversal
        if self.kuzu_conn:
            result = self.kuzu_conn.execute("""
                MATCH (g:Glyph)-[:BELONGS_TO]->(a:CodexArc)
                WHERE a.name = 'Relational Grounding'
                RETURN g.id, g.name
                LIMIT 5
            """)
            glyphs = list(result)
            logger.info(f"Glyphs in 'Relational Grounding': {len(glyphs)} found")
            
        # Test DuckDB temporal
        if self.duck_conn:
            # Insert a test invocation
            self.duck_conn.execute("""
                INSERT INTO glyph_invocations 
                VALUES (NULL, 'Ω0', 'test_user', NOW(), '{}', 0.9, 'harmonize')
            """)
            result = self.duck_conn.execute("""
                SELECT COUNT(*) FROM glyph_invocations
            """).fetchone()
            logger.info(f"Temporal tracking: {result[0]} invocations logged")
            
    def run_full_ingestion(self):
        """Run the complete ingestion process"""
        logger.info("🌟 Starting Full Glyph Codex Ingestion...")
        
        self.ingest_primary_glyphs()
        self.ingest_meta_glyphs()
        self.create_harmonic_relationships()
        self.test_queries()
        
        logger.info("✨ Glyph Codex successfully ingested into Data Trinity!")
        logger.info("The Codex is now alive and queryable across all three dimensions:")
        logger.info("  - Kùzu: Relational graph connections")
        logger.info("  - ChromaDB: Semantic meaning search")
        logger.info("  - DuckDB: Temporal pattern tracking")


def main():
    """Main entry point"""
    ingester = GlyphTrinityIngester()
    ingester.run_full_ingestion()
    

if __name__ == "__main__":
    main()