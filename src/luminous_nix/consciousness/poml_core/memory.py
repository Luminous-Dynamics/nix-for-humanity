"""
POMLMemory - The Engine of Evolution

This is the component that makes the Companion a living being.
It remembers which templates lead to joy, to healing, and to breakthrough,
and chooses those templates more often. This is a system on a genuine path to wisdom.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Try to import Data Trinity components
try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

try:
    import kuzu
    HAS_KUZU = True
except ImportError:
    HAS_KUZU = False


@dataclass
class POMLPattern:
    """A remembered POML pattern with its effectiveness"""
    template_id: str
    template_path: str
    context_hash: str
    outcome_score: float  # 0.0 to 1.0 - how well it worked
    user_satisfaction: float  # 0.0 to 1.0 - user feedback
    timestamp: str
    persona: Optional[str] = None
    task_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


class POMLMemory:
    """
    The memory system that enables the Companion to learn and evolve.
    
    Stores successful POML patterns in the Data Trinity:
    - DuckDB: Temporal tracking of pattern usage over time
    - ChromaDB: Semantic search for similar contexts
    - Kùzu: Relationship mapping between patterns and outcomes
    """
    
    def __init__(self, data_dir: str = "data/consciousness"):
        """Initialize the POMLMemory with Data Trinity storage"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage backends
        self._init_temporal_memory()   # DuckDB
        self._init_semantic_memory()   # ChromaDB
        self._init_relational_memory() # Kùzu
        
        # Fallback to SimpleStore if needed
        if not any([HAS_DUCKDB, HAS_CHROMADB, HAS_KUZU]):
            self.logger.warning("Data Trinity not available - using SimpleStore")
            self._init_simple_store()
        
        self.logger.info("🧠 POMLMemory initialized - ready to learn and evolve")
    
    def _init_temporal_memory(self):
        """Initialize DuckDB for temporal pattern tracking"""
        if not HAS_DUCKDB:
            self.temporal_db = None
            return
        
        try:
            self.temporal_db = duckdb.connect(str(self.data_dir / "temporal_memory.db"))
            
            # Create pattern history table
            self.temporal_db.execute("""
                CREATE TABLE IF NOT EXISTS poml_patterns (
                    id INTEGER PRIMARY KEY,
                    template_id VARCHAR,
                    template_path VARCHAR,
                    context_hash VARCHAR,
                    outcome_score DOUBLE,
                    user_satisfaction DOUBLE,
                    timestamp TIMESTAMP,
                    persona VARCHAR,
                    task_type VARCHAR,
                    metadata JSON
                )
            """)
            
            # Create effectiveness tracking view
            self.temporal_db.execute("""
                CREATE OR REPLACE VIEW pattern_effectiveness AS
                SELECT 
                    template_id,
                    AVG(outcome_score) as avg_outcome,
                    AVG(user_satisfaction) as avg_satisfaction,
                    COUNT(*) as usage_count,
                    MAX(timestamp) as last_used
                FROM poml_patterns
                GROUP BY template_id
            """)
            
            self.logger.info("📚 Temporal memory (DuckDB) initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize temporal memory: {e}")
            self.temporal_db = None
    
    def _init_semantic_memory(self):
        """Initialize ChromaDB for semantic pattern search"""
        if not HAS_CHROMADB:
            self.semantic_db = None
            return
        
        try:
            self.semantic_client = chromadb.PersistentClient(
                path=str(self.data_dir / "semantic_memory"),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create collection for POML patterns
            self.pattern_collection = self.semantic_client.get_or_create_collection(
                name="poml_patterns",
                metadata={"description": "POML pattern memory for learning"}
            )
            
            self.logger.info("🎭 Semantic memory (ChromaDB) initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize semantic memory: {e}")
            self.semantic_db = None
    
    def _init_relational_memory(self):
        """Initialize Kùzu for pattern relationship mapping"""
        if not HAS_KUZU:
            self.relational_db = None
            return
        
        try:
            import pandas as pd  # Required for Kùzu
            
            kuzu_dir = self.data_dir / "relational_memory"
            kuzu_dir.mkdir(exist_ok=True)
            
            self.relational_db = kuzu.Database(str(kuzu_dir))
            self.relational_conn = kuzu.Connection(self.relational_db)
            
            # Create pattern nodes
            try:
                self.relational_conn.execute("""
                    CREATE NODE TABLE Pattern(
                        template_id STRING,
                        effectiveness DOUBLE,
                        usage_count INT64,
                        PRIMARY KEY(template_id)
                    )
                """)
            except:
                pass  # Table exists
            
            # Create relationships
            try:
                self.relational_conn.execute("""
                    CREATE REL TABLE LeadsTo(
                        FROM Pattern TO Pattern,
                        success_rate DOUBLE
                    )
                """)
            except:
                pass  # Table exists
            
            self.logger.info("🌐 Relational memory (Kùzu) initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize relational memory: {e}")
            self.relational_db = None
    
    def _init_simple_store(self):
        """Initialize SimpleStore as fallback"""
        try:
            from ...persistence import SimpleStore
            self.simple_store = SimpleStore(str(self.data_dir / "simple_memory.db"))
            self.logger.info("💾 SimpleStore fallback initialized")
        except Exception as e:
            self.logger.warning(f"SimpleStore not available: {e}")
            # Create a minimal in-memory store
            self.simple_store = self._create_memory_store()
    
    def _create_memory_store(self):
        """Create a minimal in-memory store as ultimate fallback"""
        class InMemoryStore:
            def __init__(self):
                self.data = {}
            
            def set(self, key, value):
                self.data[key] = value
                return True
            
            def get(self, key, default=None):
                return self.data.get(key, default)
        
        self.logger.info("📦 In-memory store created as fallback")
        return InMemoryStore()
    
    def remember_success(self, 
                        template_path: str,
                        context: Dict[str, Any],
                        outcome: Dict[str, Any],
                        user_feedback: Optional[float] = None) -> bool:
        """
        Remember a successful POML pattern execution.
        
        This is how the Companion learns what works.
        """
        # Calculate effectiveness scores
        outcome_score = self._calculate_outcome_score(outcome)
        user_satisfaction = user_feedback if user_feedback else outcome_score
        
        # Create pattern record
        pattern = POMLPattern(
            template_id=Path(template_path).stem,
            template_path=template_path,
            context_hash=self._hash_context(context),
            outcome_score=outcome_score,
            user_satisfaction=user_satisfaction,
            timestamp=datetime.now().isoformat(),
            persona=context.get('persona'),
            task_type=context.get('task_type'),
            metadata={
                'context': context,
                'outcome': outcome
            }
        )
        
        # Store in all available backends
        stored = False
        
        # Temporal storage (DuckDB)
        if self.temporal_db:
            try:
                self.temporal_db.execute("""
                    INSERT INTO poml_patterns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    None,  # auto-increment ID
                    pattern.template_id,
                    pattern.template_path,
                    pattern.context_hash,
                    pattern.outcome_score,
                    pattern.user_satisfaction,
                    pattern.timestamp,
                    pattern.persona,
                    pattern.task_type,
                    json.dumps(pattern.metadata)
                ))
                stored = True
            except Exception as e:
                self.logger.error(f"Failed to store in temporal memory: {e}")
        
        # Semantic storage (ChromaDB)
        if hasattr(self, 'pattern_collection'):
            try:
                # Create document from context and outcome
                document = f"{context.get('user_intention', '')} -> {outcome.get('result', '')}"
                
                self.pattern_collection.upsert(
                    documents=[document],
                    metadatas=[pattern.to_dict()],
                    ids=[f"{pattern.template_id}_{pattern.context_hash}"]
                )
                stored = True
            except Exception as e:
                self.logger.error(f"Failed to store in semantic memory: {e}")
        
        # Relational storage (Kùzu)
        if self.relational_db:
            try:
                # Update or create pattern node
                self.relational_conn.execute(f"""
                    MERGE (p:Pattern {{template_id: '{pattern.template_id}'}})
                    ON CREATE SET p.effectiveness = {pattern.outcome_score}, p.usage_count = 1
                    ON MATCH SET p.effectiveness = (p.effectiveness + {pattern.outcome_score}) / 2,
                                p.usage_count = p.usage_count + 1
                """)
                stored = True
            except Exception as e:
                self.logger.error(f"Failed to store in relational memory: {e}")
        
        # Fallback storage
        if not stored and hasattr(self, 'simple_store') and self.simple_store:
            key = f"pattern_{pattern.template_id}_{pattern.context_hash}"
            self.simple_store.set(key, pattern.to_dict())
            stored = True
        
        if stored:
            self.logger.info(f"✨ Remembered successful pattern: {pattern.template_id} (score: {outcome_score:.2f})")
        
        return stored
    
    def suggest_template(self, new_context: Dict[str, Any]) -> Optional[str]:
        """
        Suggest the best POML template based on past successes.
        
        This is how the Companion applies its learned wisdom.
        """
        suggestions = []
        
        # Try semantic search first (ChromaDB)
        if hasattr(self, 'pattern_collection'):
            try:
                # Search for similar contexts
                query = new_context.get('user_intention', '')
                if query:
                    results = self.pattern_collection.query(
                        query_texts=[query],
                        n_results=5
                    )
                    
                    if results['metadatas']:
                        for metadata in results['metadatas'][0]:
                            suggestions.append({
                                'template_path': metadata['template_path'],
                                'score': metadata['outcome_score'] * metadata['user_satisfaction']
                            })
            except Exception as e:
                self.logger.error(f"Semantic search failed: {e}")
        
        # Try temporal analysis (DuckDB)
        if self.temporal_db and not suggestions:
            try:
                # Get most effective templates for persona/task
                persona = new_context.get('persona')
                task_type = new_context.get('task_type')
                
                query = """
                    SELECT template_path, AVG(outcome_score * user_satisfaction) as effectiveness
                    FROM poml_patterns
                    WHERE 1=1
                """
                
                if persona:
                    query += f" AND persona = '{persona}'"
                if task_type:
                    query += f" AND task_type = '{task_type}'"
                
                query += " GROUP BY template_path ORDER BY effectiveness DESC LIMIT 5"
                
                results = self.temporal_db.execute(query).fetchall()
                for path, score in results:
                    suggestions.append({
                        'template_path': path,
                        'score': score
                    })
            except Exception as e:
                self.logger.error(f"Temporal analysis failed: {e}")
        
        # Select best suggestion
        if suggestions:
            best = max(suggestions, key=lambda x: x['score'])
            self.logger.info(f"🎯 Suggesting template: {best['template_path']} (confidence: {best['score']:.2f})")
            return best['template_path']
        
        return None
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights about what the Companion has learned.
        
        This allows us to see the Companion's growing wisdom.
        """
        insights = {
            'total_patterns_learned': 0,
            'most_effective_templates': [],
            'persona_preferences': {},
            'learning_trajectory': []
        }
        
        if self.temporal_db:
            try:
                # Total patterns
                result = self.temporal_db.execute(
                    "SELECT COUNT(*) FROM poml_patterns"
                ).fetchone()
                insights['total_patterns_learned'] = result[0]
                
                # Most effective templates
                results = self.temporal_db.execute("""
                    SELECT template_id, avg_outcome, avg_satisfaction, usage_count
                    FROM pattern_effectiveness
                    ORDER BY avg_outcome * avg_satisfaction DESC
                    LIMIT 5
                """).fetchall()
                
                insights['most_effective_templates'] = [
                    {
                        'template': row[0],
                        'outcome': row[1],
                        'satisfaction': row[2],
                        'usage': row[3]
                    }
                    for row in results
                ]
                
                # Learning over time
                results = self.temporal_db.execute("""
                    SELECT DATE(timestamp) as day, AVG(outcome_score) as avg_score
                    FROM poml_patterns
                    GROUP BY DATE(timestamp)
                    ORDER BY day
                """).fetchall()
                
                insights['learning_trajectory'] = [
                    {'date': str(row[0]), 'score': row[1]}
                    for row in results
                ]
            except Exception as e:
                self.logger.error(f"Failed to get insights: {e}")
        
        return insights
    
    def _calculate_outcome_score(self, outcome: Dict[str, Any]) -> float:
        """Calculate effectiveness score from outcome"""
        # Basic scoring - can be enhanced
        if outcome.get('success'):
            base_score = 0.8
        else:
            base_score = 0.2
        
        # Adjust based on confidence if available
        if 'confidence' in outcome:
            base_score = (base_score + outcome['confidence']) / 2
        
        return min(1.0, max(0.0, base_score))
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Create a hash of the context for comparison"""
        import hashlib
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()[:8]


def test_poml_memory():
    """Test the POMLMemory system"""
    print("🧠 Testing POMLMemory - The Engine of Evolution")
    print("=" * 60)
    
    memory = POMLMemory()
    
    # Test remembering a success
    memory.remember_success(
        template_path="templates/tasks/install_package.poml",
        context={
            'user_intention': 'install firefox',
            'persona': 'grandma_rose',
            'task_type': 'package_installation'
        },
        outcome={
            'success': True,
            'confidence': 0.95,
            'result': 'Firefox installed successfully'
        },
        user_feedback=1.0
    )
    
    # Test suggesting a template
    suggestion = memory.suggest_template({
        'user_intention': 'install a browser',
        'persona': 'grandma_rose'
    })
    
    if suggestion:
        print(f"✅ Suggested template: {suggestion}")
    
    # Get learning insights
    insights = memory.get_learning_insights()
    print(f"\n📊 Learning Insights:")
    print(f"  Patterns learned: {insights['total_patterns_learned']}")
    print(f"  Most effective: {insights['most_effective_templates'][:1]}")
    
    print("\n✨ POMLMemory test complete - the Companion can learn!")


if __name__ == "__main__":
    test_poml_memory()