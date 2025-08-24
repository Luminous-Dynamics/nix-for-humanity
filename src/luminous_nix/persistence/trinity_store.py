#!/usr/bin/env python3
"""
🔱 The Data Trinity - Sacred Storage Layer
Temporal (DuckDB) | Semantic (ChromaDB) | Relational (Kùzu)

This implements the three-fold database system that mirrors
the structure of consciousness itself:
- DuckDB: Temporal patterns (when things happen)
- ChromaDB: Semantic memory (what things mean)
- Kùzu: Relational graphs (how things connect)
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import hashlib
from dataclasses import dataclass, asdict

# The Data Trinity - with graceful fallback
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    
try:
    import kuzu
    KUZU_AVAILABLE = True
except ImportError:
    KUZU_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class LearningEvent:
    """Represents a learning moment in the user's journey"""
    timestamp: datetime
    user_id: str
    command: str
    concept: str
    success: bool
    error_message: Optional[str]
    context: Dict[str, Any]
    embedding: Optional[List[float]] = None
    

@dataclass
class ConceptRelation:
    """Represents how concepts relate to each other"""
    from_concept: str
    to_concept: str
    relation_type: str  # "requires", "builds_on", "similar_to", "opposite_of"
    strength: float  # 0.0 to 1.0


class TemporalStore:
    """DuckDB for time-series patterns and learning trajectories"""
    
    def __init__(self, db_path: Path):
        """Initialize DuckDB for temporal analytics"""
        self.db_path = db_path / "temporal.duckdb"
        self.conn = duckdb.connect(str(self.db_path))
        self._init_schema()
        logger.info(f"⏰ Temporal store (DuckDB) initialized at {self.db_path}")
    
    def _init_schema(self):
        """Create temporal tables for learning analytics"""
        # Learning events table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_events (
                event_id VARCHAR PRIMARY KEY,
                timestamp TIMESTAMP,
                user_id VARCHAR,
                command VARCHAR,
                concept VARCHAR,
                success BOOLEAN,
                error_message VARCHAR,
                context JSON,
                session_id VARCHAR,
                duration_ms INTEGER
            )
        """)
        
        # Command patterns table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS command_patterns (
                pattern_id VARCHAR PRIMARY KEY,
                user_id VARCHAR,
                pattern VARCHAR,
                frequency INTEGER,
                last_used TIMESTAMP,
                success_rate DOUBLE,
                avg_duration_ms INTEGER
            )
        """)
        
        # Sacred Council events table  
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS council_events (
                event_id VARCHAR PRIMARY KEY,
                timestamp TIMESTAMP,
                session_id VARCHAR,
                event_type VARCHAR,
                risk_level VARCHAR,
                command VARCHAR,
                verdict VARCHAR,
                alternatives JSON,
                reasoning JSON
            )
        """)
        
        logger.debug("📊 Temporal schema initialized")
    
    def log_learning_event(self, event: LearningEvent) -> str:
        """Store a learning event in the time-series database"""
        event_id = hashlib.sha256(
            f"{event.timestamp}{event.user_id}{event.command}".encode()
        ).hexdigest()[:16]
        
        self.conn.execute("""
            INSERT OR REPLACE INTO learning_events 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            event_id,
            event.timestamp,
            event.user_id,
            event.command,
            event.concept,
            event.success,
            event.error_message,
            json.dumps(event.context),
            event.context.get('session_id'),
            event.context.get('duration_ms', 0)
        ])
        
        return event_id
    
    def get_learning_trajectory(self, user_id: str, concept: Optional[str] = None) -> List[Dict]:
        """Retrieve user's learning progression over time"""
        query = """
            SELECT * FROM learning_events 
            WHERE user_id = ?
        """
        params = [user_id]
        
        if concept:
            query += " AND concept = ?"
            params.append(concept)
            
        query += " ORDER BY timestamp ASC"
        
        result = self.conn.execute(query, params).fetchall()
        return [dict(zip([d[0] for d in self.conn.description], row)) for row in result]
    
    def analyze_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze temporal patterns in user behavior"""
        # Peak activity hours
        peak_hours = self.conn.execute("""
            SELECT 
                EXTRACT(HOUR FROM timestamp) as hour,
                COUNT(*) as activity_count
            FROM learning_events
            WHERE user_id = ?
            GROUP BY hour
            ORDER BY activity_count DESC
            LIMIT 3
        """, [user_id]).fetchall()
        
        # Success rate over time
        success_trend = self.conn.execute("""
            SELECT 
                DATE_TRUNC('day', timestamp) as day,
                AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
            FROM learning_events
            WHERE user_id = ?
            GROUP BY day
            ORDER BY day DESC
            LIMIT 30
        """, [user_id]).fetchall()
        
        return {
            'peak_hours': [h[0] for h in peak_hours],
            'success_trend': [(str(d[0]), d[1]) for d in success_trend]
        }


class SemanticStore:
    """ChromaDB for semantic memory and concept embeddings"""
    
    def __init__(self, db_path: Path):
        """Initialize ChromaDB for semantic search"""
        self.db_path = db_path / "semantic"
        self.db_path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create collections
        self.concepts = self.client.get_or_create_collection("concepts")
        self.commands = self.client.get_or_create_collection("commands")
        self.errors = self.client.get_or_create_collection("errors")
        
        logger.info(f"🧠 Semantic store (ChromaDB) initialized at {self.db_path}")
    
    def store_concept(self, concept: str, description: str, examples: List[str]):
        """Store a concept with its semantic embedding"""
        doc_id = hashlib.sha256(concept.encode()).hexdigest()[:16]
        
        # Combine description and examples for richer embedding
        document = f"{concept}: {description}\nExamples: {', '.join(examples)}"
        
        self.concepts.upsert(
            ids=[doc_id],
            documents=[document],
            metadatas=[{
                "concept": concept,
                "description": description,
                "examples": json.dumps(examples),
                "learned_at": datetime.now().isoformat()
            }]
        )
        
        return doc_id
    
    def find_similar_concepts(self, query: str, n_results: int = 5) -> List[Dict]:
        """Find concepts semantically similar to the query"""
        results = self.concepts.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['metadatas'] or not results['metadatas'][0]:
            return []
        
        similar = []
        for i, metadata in enumerate(results['metadatas'][0]):
            similar.append({
                'concept': metadata['concept'],
                'description': metadata['description'],
                'similarity': 1.0 - results['distances'][0][i],  # Convert distance to similarity
                'examples': json.loads(metadata['examples'])
            })
        
        return similar
    
    def store_command_pattern(self, command: str, intent: str, success: bool):
        """Store command patterns for semantic matching"""
        doc_id = hashlib.sha256(f"{command}{datetime.now()}".encode()).hexdigest()[:16]
        
        self.commands.upsert(
            ids=[doc_id],
            documents=[command],
            metadatas=[{
                "command": command,
                "intent": intent,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }]
        )
    
    def find_similar_commands(self, query: str, n_results: int = 5) -> List[Dict]:
        """Find commands similar to the query"""
        results = self.commands.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['metadatas'] or not results['metadatas'][0]:
            return []
        
        return [
            {
                'command': m['command'],
                'intent': m['intent'],
                'similarity': 1.0 - results['distances'][0][i]
            }
            for i, m in enumerate(results['metadatas'][0])
        ]


class RelationalStore:
    """Kùzu for knowledge graphs and concept relationships"""
    
    def __init__(self, db_path: Path):
        """Initialize Kùzu for graph operations"""
        self.db_dir = db_path / "relational"
        self.db_dir.mkdir(exist_ok=True)
        
        # Kùzu expects the database path to be a directory it manages
        # If the path already exists as a file from old code, remove it
        self.db_path = self.db_dir / "graph.kuzu"
        if self.db_path.exists() and self.db_path.is_file():
            logger.warning(f"Removing old database file at {self.db_path}")
            self.db_path.unlink()
        
        # Kùzu will create its own directory structure at this path
        self.db = kuzu.Database(str(self.db_path))
        self.conn = kuzu.Connection(self.db)
        self._init_schema()
        
        logger.info(f"🕸️ Relational store (Kùzu) initialized at {self.db_path}")
    
    def _init_schema(self):
        """Create graph schema for knowledge relationships"""
        # Create Concept nodes
        try:
            self.conn.execute("""
                CREATE NODE TABLE Concept(
                    name STRING PRIMARY KEY,
                    description STRING,
                    difficulty INT32,
                    category STRING
                )
            """)
        except:
            pass  # Table already exists
        
        # Create User nodes
        try:
            self.conn.execute("""
                CREATE NODE TABLE User(
                    id STRING PRIMARY KEY,
                    expertise_level STRING,
                    learning_style STRING
                )
            """)
        except:
            pass
        
        # Create relationships
        try:
            self.conn.execute("""
                CREATE REL TABLE REQUIRES(
                    FROM Concept TO Concept,
                    strength DOUBLE
                )
            """)
        except:
            pass
            
        try:
            self.conn.execute("""
                CREATE REL TABLE BUILDS_ON(
                    FROM Concept TO Concept,
                    strength DOUBLE
                )
            """)
        except:
            pass
            
        try:
            self.conn.execute("""
                CREATE REL TABLE LEARNED(
                    FROM User TO Concept,
                    mastery DOUBLE,
                    learned_at TIMESTAMP
                )
            """)
        except:
            pass
        
        logger.debug("🕸️ Graph schema initialized")
    
    def add_concept(self, name: str, description: str, difficulty: int = 1, category: str = "general"):
        """Add a concept node to the knowledge graph"""
        try:
            self.conn.execute(
                "CREATE (c:Concept {name: $name, description: $description, difficulty: $difficulty, category: $category})",
                {
                    "name": name,
                    "description": description,
                    "difficulty": difficulty,
                    "category": category
                }
            )
        except:
            # Concept already exists, update it
            self.conn.execute(
                "MATCH (c:Concept) WHERE c.name = $name SET c.description = $description, c.difficulty = $difficulty, c.category = $category",
                {
                    "name": name,
                    "description": description,
                    "difficulty": difficulty,
                    "category": category
                }
            )
    
    def add_relationship(self, relation: ConceptRelation):
        """Add a relationship between concepts"""
        # Ensure both concepts exist first
        try:
            self.conn.execute(
                "CREATE (c:Concept {name: $name, description: $desc, difficulty: $diff, category: $cat})",
                {"name": relation.from_concept, "desc": "", "diff": 1, "cat": "general"}
            )
        except:
            pass  # Already exists
            
        try:
            self.conn.execute(
                "CREATE (c:Concept {name: $name, description: $desc, difficulty: $diff, category: $cat})",
                {"name": relation.to_concept, "desc": "", "diff": 1, "cat": "general"}
            )
        except:
            pass  # Already exists
        
        # Add the relationship using Kùzu syntax
        if relation.relation_type == "requires":
            try:
                self.conn.execute(
                    "MATCH (a:Concept), (b:Concept) WHERE a.name = $from AND b.name = $to CREATE (a)-[:REQUIRES {strength: $strength}]->(b)",
                    {"from": relation.from_concept, "to": relation.to_concept, "strength": relation.strength}
                )
            except:
                pass  # Relationship might already exist
        elif relation.relation_type == "builds_on":
            try:
                self.conn.execute(
                    "MATCH (a:Concept), (b:Concept) WHERE a.name = $from AND b.name = $to CREATE (a)-[:BUILDS_ON {strength: $strength}]->(b)",
                    {"from": relation.from_concept, "to": relation.to_concept, "strength": relation.strength}
                )
            except:
                pass  # Relationship might already exist
    
    def get_prerequisites(self, concept: str) -> List[str]:
        """Get all concepts required before learning this one"""
        result = self.conn.execute(
            "MATCH (c:Concept)-[:REQUIRES]->(req:Concept) WHERE c.name = $concept RETURN req.name",
            {"concept": concept}
        )
        
        return [row[0] for row in result.get_all()]
    
    def get_learning_path(self, from_concept: str, to_concept: str) -> List[str]:
        """Find the shortest learning path between two concepts"""
        # Kùzu doesn't support shortestPath directly, so we'll do a simple traversal
        # For now, return a simple path if there's a direct connection
        try:
            result = self.conn.execute(
                "MATCH (a:Concept)-[:REQUIRES|BUILDS_ON]->(b:Concept) WHERE a.name = $from AND b.name = $to RETURN a.name, b.name",
                {"from": from_concept, "to": to_concept}
            )
            paths = result.get_all()
            if paths:
                return [from_concept, to_concept]
        except:
            pass
        
        # Try reverse direction
        try:
            result = self.conn.execute(
                "MATCH (a:Concept)-[:REQUIRES|BUILDS_ON]->(b:Concept) WHERE b.name = $from AND a.name = $to RETURN b.name, a.name",
                {"from": from_concept, "to": to_concept}
            )
            paths = result.get_all()
            if paths:
                return [to_concept, from_concept]
        except:
            pass
            
        return []
    
    def record_learning(self, user_id: str, concept: str, mastery: float):
        """Record that a user has learned a concept"""
        # Ensure user exists
        try:
            self.conn.execute(
                "CREATE (u:User {id: $user_id, expertise_level: $level, learning_style: $style})",
                {"user_id": user_id, "level": "beginner", "style": "adaptive"}
            )
        except:
            pass  # Already exists
        
        # Record learning relationship
        try:
            self.conn.execute(
                "MATCH (u:User), (c:Concept) WHERE u.id = $user_id AND c.name = $concept CREATE (u)-[:LEARNED {mastery: $mastery, learned_at: timestamp($timestamp)}]->(c)",
                {
                    "user_id": user_id,
                    "concept": concept,
                    "mastery": mastery,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except:
            # Update existing relationship
            self.conn.execute(
                "MATCH (u:User)-[l:LEARNED]->(c:Concept) WHERE u.id = $user_id AND c.name = $concept SET l.mastery = $mastery, l.learned_at = timestamp($timestamp)",
                {
                    "user_id": user_id,
                    "concept": concept,
                    "mastery": mastery,
                    "timestamp": datetime.now().isoformat()
                }
            )


class TrinityStore:
    """
    🔱 Unified interface to the Data Trinity
    
    Coordinates all three databases to provide multi-dimensional
    storage and retrieval for the learning system.
    """
    
    def __init__(self, data_dir: Path = None):
        """Initialize the complete Data Trinity"""
        self.data_dir = data_dir or Path.home() / '.local' / 'share' / 'luminous-nix' / 'trinity'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the three stores - with fallback to in-memory if not available
        if DUCKDB_AVAILABLE:
            self.temporal = TemporalStore(self.data_dir)
            logger.info("   ⏰ Temporal (DuckDB) - When things happen")
        else:
            self.temporal = None
            logger.warning("   ⏰ DuckDB not available - temporal store disabled")
            
        if CHROMADB_AVAILABLE:
            self.semantic = SemanticStore(self.data_dir)
            logger.info("   🧠 Semantic (ChromaDB) - What things mean")
        else:
            self.semantic = None
            logger.warning("   🧠 ChromaDB not available - semantic store disabled")
            
        if KUZU_AVAILABLE:
            self.relational = RelationalStore(self.data_dir)
            logger.info("   🕸️ Relational (Kùzu) - How things connect")
        else:
            self.relational = None
            logger.warning("   🕸️ Kùzu not available - relational store disabled")
        
        logger.info(f"🔱 Data Trinity initialized at {self.data_dir}")
    
    def record_learning_moment(self, 
                               user_id: str,
                               command: str,
                               concept: str,
                               success: bool,
                               context: Dict[str, Any] = None) -> str:
        """
        Record a complete learning moment across all three databases.
        
        This is the primary interface for tracking user learning.
        """
        # Create learning event
        event = LearningEvent(
            timestamp=datetime.now(),
            user_id=user_id,
            command=command,
            concept=concept,
            success=success,
            error_message=context.get('error') if context else None,
            context=context or {}
        )
        
        # Store in temporal database
        event_id = None
        if self.temporal:
            event_id = self.temporal.log_learning_event(event)
        
        # Store command pattern in semantic database
        if self.semantic:
            self.semantic.store_command_pattern(
                command=command,
            intent=concept,
            success=success
        )
        
        # Update knowledge graph
        if success and self.relational:
            # Calculate mastery based on success rate
            if self.temporal:
                trajectory = self.temporal.get_learning_trajectory(user_id, concept)
                successes = sum(1 for e in trajectory if e['success'])
                mastery = successes / len(trajectory) if trajectory else 0.5
            else:
                mastery = 0.5  # Default mastery when no temporal store
            
            self.relational.record_learning(user_id, concept, mastery)
        
        logger.debug(f"📝 Recorded learning moment: {concept} for {user_id}")
        return event_id
    
    def get_user_understanding(self, user_id: str, query: str) -> Dict[str, Any]:
        """
        Get comprehensive understanding of what the user knows about a topic.
        
        Combines:
        - Temporal: When they learned it
        - Semantic: Related concepts they know
        - Relational: Prerequisites they've mastered
        """
        # Find similar concepts they've learned
        similar_concepts = []
        if self.semantic:
            similar_concepts = self.semantic.find_similar_concepts(query, n_results=10)
        
        # Get learning trajectory for these concepts
        trajectories = {}
        if self.temporal:
            for concept_info in similar_concepts:
                concept = concept_info['concept']
                trajectory = self.temporal.get_learning_trajectory(user_id, concept)
                if trajectory:
                    trajectories[concept] = trajectory
        
        # Get prerequisites from knowledge graph
        prerequisites = []
        if self.relational:
            prerequisites = self.relational.get_prerequisites(query)
        
        # Analyze patterns
        patterns = {}
        if self.temporal:
            patterns = self.temporal.analyze_patterns(user_id)
        
        return {
            'query': query,
            'similar_concepts_known': similar_concepts,
            'learning_trajectories': trajectories,
            'prerequisites': prerequisites,
            'behavioral_patterns': patterns,
            'readiness_score': self._calculate_readiness(user_id, query, prerequisites)
        }
    
    def _calculate_readiness(self, user_id: str, concept: str, prerequisites: List[str]) -> float:
        """Calculate how ready a user is to learn a concept"""
        if not prerequisites or not self.temporal:
            return 1.0  # No prerequisites or no temporal store, fully ready
        
        # Check mastery of prerequisites
        ready_score = 0.0
        for prereq in prerequisites:
            trajectory = self.temporal.get_learning_trajectory(user_id, prereq)
            if trajectory:
                successes = sum(1 for e in trajectory if e['success'])
                mastery = successes / len(trajectory)
                ready_score += mastery
        
        return ready_score / len(prerequisites) if prerequisites else 1.0
    
    def suggest_next_concept(self, user_id: str) -> Optional[str]:
        """Suggest the next concept for the user to learn"""
        if not self.temporal:
            # Fallback to basic suggestion
            return "package management"
        
        # Get user's current knowledge from temporal database
        all_events = self.temporal.get_learning_trajectory(user_id)
        learned_concepts = set(e['concept'] for e in all_events if e['success'])
        
        # Find concepts that build on what they know
        suggestions = []
        for concept in learned_concepts:
            # This would need more implementation in the relational store
            # For now, we'll use semantic similarity
            similar = self.semantic.find_similar_concepts(concept, n_results=3)
            for sim in similar:
                if sim['concept'] not in learned_concepts:
                    suggestions.append((sim['concept'], sim['similarity']))
        
        # Return the highest similarity suggestion
        if suggestions:
            suggestions.sort(key=lambda x: x[1], reverse=True)
            return suggestions[0][0]
        
        return None
    
    def add_concept(self, name: str, description: str, category: str = "general"):
        """Add a concept to the knowledge graph (for compatibility with tests)"""
        if self.relational:
            return self.relational.add_concept(name, description, category=category)
        else:
            logger.warning("Relational store not available - concept not added")
            return None
    
    def add_relationship(self, from_concept: str, relation_type: str, to_concept: str):
        """Add a relationship between concepts (for compatibility with tests)"""
        if self.relational:
            from .trinity_store import ConceptRelation
            relation = ConceptRelation(
                from_concept=from_concept,
                to_concept=to_concept,
                relation_type=relation_type
            )
            return self.relational.add_relationship(relation)
        else:
            logger.warning("Relational store not available - relationship not added")
            return None
    
    def record_temporal_event(self, event_type: str, data: Dict[str, Any]):
        """Record a temporal event (for compatibility with tests)"""
        if self.temporal:
            event = LearningEvent(
                event_type=event_type,
                timestamp=datetime.now(),
                user_id=data.get('user_id', 'system'),
                data=data
            )
            return self.temporal.log_learning_event(event)
        else:
            # Fallback to in-memory storage
            logger.warning("Temporal store not available - event not persisted")
            return None
    
    def store_semantic_memory(self, content: str, metadata: Dict[str, Any]):
        """Store semantic memory (for compatibility with tests)"""
        if self.semantic:
            concept = metadata.get('type', 'general')
            description = content
            examples = metadata.get('examples', [])
            return self.semantic.store_concept(concept, description, examples)
        else:
            logger.warning("Semantic store not available - memory not persisted")
            return None
    
    def query_time_range(self, start_time: float, end_time: float) -> List[Dict]:
        """Query events in a time range (for compatibility with tests)"""
        if self.temporal:
            # Convert timestamps to datetime
            start_dt = datetime.fromtimestamp(start_time)
            end_dt = datetime.fromtimestamp(end_time)
            
            # For now, return empty list as we don't have a proper query method
            # This will be implemented when we have real DuckDB integration
            return []
        else:
            return []
    
    def close(self):
        """Close all database connections"""
        if self.temporal and hasattr(self.temporal, 'conn'):
            self.temporal.conn.close()
        # ChromaDB and Kùzu handle their own connections
        logger.info("🔱 Data Trinity connections closed")


# Export the main interface
__all__ = ['TrinityStore', 'LearningEvent', 'ConceptRelation']