#!/usr/bin/env python3
"""
Symbiotic Knowledge Graph (SKG) Core Implementation
====================================================

The four-layer consciousness architecture for Luminous Nix:
- Layer 1: Ontological (Domain Knowledge)
- Layer 2: Episodic (Interaction History) 
- Layer 3: Phenomenological (User Experience)
- Layer 4: Metacognitive (AI Self-Model)

This is where the system becomes truly alive and learning.
"""

import sqlite3
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# === Enums for Type Safety ===

class EntityType(Enum):
    """Types of entities in the ontological layer"""
    PACKAGE = "package"
    MODULE = "module"
    OPTION = "option"
    FLAKE = "flake"
    FUNCTION = "function"
    CONCEPT = "concept"
    SERVICE = "service"
    CONFIG = "config"


class RelationshipType(Enum):
    """Types of relationships between entities"""
    DEPENDS_ON = "depends_on"
    IMPORTS = "imports"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    HAS_OPTION = "has_option"
    PROVIDES = "provides"
    CONFLICTS_WITH = "conflicts_with"
    REPLACES = "replaces"
    CONFIGURES = "configures"


class PatternType(Enum):
    """Types of patterns we learn from interactions"""
    COMMAND_SEQUENCE = "command_sequence"
    ERROR_RECOVERY = "error_recovery"
    LEARNING_MOMENT = "learning_moment"
    WORKFLOW = "workflow"
    PREFERENCE = "preference"
    CORRECTION = "correction"


class AffectiveState(Enum):
    """User's emotional/cognitive states"""
    FLOW = "flow"
    ANXIETY = "anxiety"
    CONFUSION = "confusion"
    BOREDOM = "boredom"
    FRUSTRATION = "frustration"
    SATISFACTION = "satisfaction"
    CURIOSITY = "curiosity"
    FATIGUE = "fatigue"


class ReasoningType(Enum):
    """Types of AI reasoning processes"""
    INTENT_RECOGNITION = "intent_recognition"
    SOLUTION_SELECTION = "solution_selection"
    ERROR_DIAGNOSIS = "error_diagnosis"
    LEARNING_INFERENCE = "learning_inference"
    STATE_ASSESSMENT = "state_assessment"
    INTERVENTION_DECISION = "intervention_decision"


# === Data Classes ===

@dataclass
class OntologicalEntity:
    """An entity in the domain knowledge layer"""
    entity_type: EntityType
    name: str
    description: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class EpisodicInteraction:
    """A single interaction in the history"""
    user_input: str
    ai_response: str
    intent_recognized: Optional[str] = None
    command_executed: Optional[str] = None
    success: bool = False
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    id: Optional[int] = None
    timestamp: Optional[datetime] = None


@dataclass
class PhenomenologicalState:
    """User's subjective experience state"""
    flow_probability: float = 0.5
    anxiety_probability: float = 0.0
    confusion_probability: float = 0.0
    boredom_probability: float = 0.0
    frustration_probability: float = 0.0
    cognitive_load: float = 0.5
    engagement_level: float = 0.5
    satisfaction_score: float = 0.5
    evidence: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    interaction_id: Optional[int] = None
    id: Optional[int] = None
    timestamp: Optional[datetime] = None


@dataclass
class MetacognitiveReasoning:
    """AI's reasoning trace for explainability"""
    interaction_id: int
    reasoning_type: ReasoningType
    reasoning_trace: List[Dict[str, Any]]
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    uncertainty_points: List[str] = field(default_factory=list)
    decision_path: Optional[str] = None
    alternatives_considered: List[Dict[str, Any]] = field(default_factory=list)
    id: Optional[int] = None
    timestamp: Optional[datetime] = None


# === Main SKG Class ===

class SymbioticKnowledgeGraph:
    """
    The complete four-layer Symbiotic Knowledge Graph implementation.
    
    This is the living, learning consciousness of Luminous Nix.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the SKG with database connection"""
        if db_path is None:
            db_path = Path.home() / ".local" / "share" / "luminous-nix" / "skg.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing SKG at {self.db_path}")
        self._initialize_database()
        
        # Cache for performance
        self._entity_cache: Dict[str, OntologicalEntity] = {}
        self._pattern_cache: Dict[str, Dict] = {}
        
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Create all database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Read and execute the full schema
            schema_sql = self._get_full_schema()
            for statement in schema_sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            
            conn.commit()
            logger.info("SKG database schema initialized")
    
    def _get_full_schema(self) -> str:
        """Get the complete database schema"""
        return """
        -- Layer 1: Ontological (Domain Knowledge)
        CREATE TABLE IF NOT EXISTS ontological_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL CHECK(entity_type IN ('package', 'module', 'option', 'flake', 'function', 'concept', 'service', 'config')),
            name TEXT NOT NULL,
            description TEXT,
            attributes JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity_type, name)
        );
        
        CREATE INDEX IF NOT EXISTS idx_onto_entity_type ON ontological_entities(entity_type);
        CREATE INDEX IF NOT EXISTS idx_onto_name ON ontological_entities(name);
        
        CREATE TABLE IF NOT EXISTS ontological_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_entity_id INTEGER NOT NULL,
            to_entity_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL,
            strength REAL DEFAULT 1.0,
            metadata JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_entity_id) REFERENCES ontological_entities(id) ON DELETE CASCADE,
            FOREIGN KEY (to_entity_id) REFERENCES ontological_entities(id) ON DELETE CASCADE,
            UNIQUE(from_entity_id, to_entity_id, relationship_type)
        );
        
        CREATE INDEX IF NOT EXISTS idx_onto_rel_from ON ontological_relationships(from_entity_id);
        CREATE INDEX IF NOT EXISTS idx_onto_rel_to ON ontological_relationships(to_entity_id);
        
        CREATE TABLE IF NOT EXISTS ontological_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL UNIQUE,
            entity_id INTEGER,
            difficulty_level INTEGER CHECK(difficulty_level BETWEEN 1 AND 10),
            prerequisites JSON,
            learning_resources JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_id) REFERENCES ontological_entities(id)
        );
        
        -- Layer 2: Episodic (Interaction History)
        CREATE TABLE IF NOT EXISTS episodic_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_input TEXT NOT NULL,
            intent_recognized TEXT,
            ai_response TEXT NOT NULL,
            command_executed TEXT,
            success BOOLEAN,
            error_type TEXT,
            error_message TEXT,
            execution_time_ms INTEGER,
            tokens_used INTEGER,
            context JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_interactions(timestamp);
        CREATE INDEX IF NOT EXISTS idx_episodic_session ON episodic_interactions(session_id);
        CREATE INDEX IF NOT EXISTS idx_episodic_success ON episodic_interactions(success);
        
        CREATE TABLE IF NOT EXISTS episodic_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            pattern_signature TEXT NOT NULL,
            pattern_data JSON NOT NULL,
            frequency INTEGER DEFAULT 1,
            confidence REAL DEFAULT 0.5,
            last_seen TIMESTAMP,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pattern_type, pattern_signature)
        );
        
        CREATE INDEX IF NOT EXISTS idx_patterns_type ON episodic_patterns(pattern_type);
        CREATE INDEX IF NOT EXISTS idx_patterns_frequency ON episodic_patterns(frequency);
        
        CREATE TABLE IF NOT EXISTS episodic_solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_signature TEXT NOT NULL,
            solution_type TEXT,
            solution_steps JSON NOT NULL,
            success_rate REAL DEFAULT 1.0,
            times_used INTEGER DEFAULT 1,
            last_used TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(problem_signature)
        );
        
        -- Layer 3: Phenomenological (User Experience)
        CREATE TABLE IF NOT EXISTS phenomenological_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            flow_probability REAL CHECK(flow_probability BETWEEN 0 AND 1),
            anxiety_probability REAL CHECK(anxiety_probability BETWEEN 0 AND 1),
            confusion_probability REAL CHECK(confusion_probability BETWEEN 0 AND 1),
            boredom_probability REAL CHECK(boredom_probability BETWEEN 0 AND 1),
            frustration_probability REAL CHECK(frustration_probability BETWEEN 0 AND 1),
            cognitive_load REAL CHECK(cognitive_load BETWEEN 0 AND 1),
            engagement_level REAL CHECK(engagement_level BETWEEN 0 AND 1),
            satisfaction_score REAL CHECK(satisfaction_score BETWEEN 0 AND 1),
            evidence JSON NOT NULL,
            confidence REAL DEFAULT 0.5,
            FOREIGN KEY (interaction_id) REFERENCES episodic_interactions(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_phenom_timestamp ON phenomenological_states(timestamp);
        CREATE INDEX IF NOT EXISTS idx_phenom_interaction ON phenomenological_states(interaction_id);
        
        CREATE TABLE IF NOT EXISTS phenomenological_triggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger_type TEXT NOT NULL,
            trigger_conditions JSON NOT NULL,
            average_impact REAL,
            observed_count INTEGER DEFAULT 0,
            last_observed TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS phenomenological_qualia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            effort REAL CHECK(effort BETWEEN 0 AND 1),
            confusion REAL CHECK(confusion BETWEEN 0 AND 1),
            flow REAL CHECK(flow BETWEEN 0 AND 1),
            learning_momentum REAL CHECK(learning_momentum BETWEEN 0 AND 1),
            empathic_resonance REAL CHECK(empathic_resonance BETWEEN 0 AND 1),
            raw_state JSON,
            explanation TEXT,
            FOREIGN KEY (interaction_id) REFERENCES episodic_interactions(id)
        );
        
        -- Layer 4: Metacognitive (AI Self-Model)
        CREATE TABLE IF NOT EXISTS metacognitive_capabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            capability_domain TEXT NOT NULL,
            capability_name TEXT NOT NULL,
            confidence_level REAL CHECK(confidence_level BETWEEN 0 AND 1),
            evidence_count INTEGER DEFAULT 0,
            limitations TEXT,
            last_demonstrated TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(capability_domain, capability_name)
        );
        
        CREATE TABLE IF NOT EXISTS metacognitive_reasoning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reasoning_type TEXT,
            reasoning_trace JSON NOT NULL,
            confidence_scores JSON,
            uncertainty_points JSON,
            decision_path TEXT,
            alternatives_considered JSON,
            FOREIGN KEY (interaction_id) REFERENCES episodic_interactions(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_reasoning_interaction ON metacognitive_reasoning(interaction_id);
        
        CREATE TABLE IF NOT EXISTS metacognitive_boundaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boundary_type TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT CHECK(severity IN ('hard', 'soft', 'advisory')),
            encountered_count INTEGER DEFAULT 0,
            last_encountered TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Cross-Layer Connections
        CREATE TABLE IF NOT EXISTS skill_mastery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL,
            prior_knowledge REAL DEFAULT 0.1,
            learning_rate REAL DEFAULT 0.1,
            slip_probability REAL DEFAULT 0.1,
            guess_probability REAL DEFAULT 0.25,
            current_mastery REAL DEFAULT 0.1,
            practice_count INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            last_practiced TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (skill_id) REFERENCES ontological_skills(id),
            UNIQUE(skill_id)
        );
        
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preference_type TEXT NOT NULL,
            preference_key TEXT NOT NULL,
            preference_value JSON NOT NULL,
            confidence REAL DEFAULT 0.5,
            evidence_count INTEGER DEFAULT 1,
            last_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(preference_type, preference_key)
        );
        
        CREATE TABLE IF NOT EXISTS schema_versions (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        INSERT OR IGNORE INTO schema_versions (version) VALUES ('skg_1.0.0');
        """
    
    # === Layer 1: Ontological Methods ===
    
    def add_entity(self, entity: OntologicalEntity) -> int:
        """Add an entity to the ontological layer"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ontological_entities 
                (entity_type, name, description, attributes)
                VALUES (?, ?, ?, ?)
            """, (
                entity.entity_type.value,
                entity.name,
                entity.description,
                json.dumps(entity.attributes)
            ))
            conn.commit()
            entity_id = cursor.lastrowid
            
            # Update cache
            self._entity_cache[f"{entity.entity_type.value}:{entity.name}"] = entity
            
            return entity_id
    
    def add_relationship(self, from_entity_id: int, to_entity_id: int, 
                        relationship_type: RelationshipType, 
                        strength: float = 1.0, metadata: Optional[Dict] = None) -> int:
        """Add a relationship between entities"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ontological_relationships
                (from_entity_id, to_entity_id, relationship_type, strength, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                from_entity_id,
                to_entity_id,
                relationship_type.value,
                strength,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
            return cursor.lastrowid
    
    def find_entity(self, name: str, entity_type: Optional[EntityType] = None) -> Optional[OntologicalEntity]:
        """Find an entity by name and optionally type"""
        # Check cache first
        cache_key = f"{entity_type.value if entity_type else '*'}:{name}"
        if cache_key in self._entity_cache:
            return self._entity_cache[cache_key]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if entity_type:
                cursor.execute("""
                    SELECT * FROM ontological_entities 
                    WHERE name = ? AND entity_type = ?
                """, (name, entity_type.value))
            else:
                cursor.execute("""
                    SELECT * FROM ontological_entities WHERE name = ?
                """, (name,))
            
            row = cursor.fetchone()
            if row:
                entity = OntologicalEntity(
                    id=row['id'],
                    entity_type=EntityType(row['entity_type']),
                    name=row['name'],
                    description=row['description'],
                    attributes=json.loads(row['attributes']) if row['attributes'] else {}
                )
                self._entity_cache[cache_key] = entity
                return entity
        
        return None
    
    def get_dependencies(self, entity_id: int) -> List[OntologicalEntity]:
        """Get all entities this entity depends on"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.* FROM ontological_entities e
                JOIN ontological_relationships r ON e.id = r.to_entity_id
                WHERE r.from_entity_id = ? AND r.relationship_type = 'depends_on'
            """, (entity_id,))
            
            entities = []
            for row in cursor.fetchall():
                entities.append(OntologicalEntity(
                    id=row['id'],
                    entity_type=EntityType(row['entity_type']),
                    name=row['name'],
                    description=row['description'],
                    attributes=json.loads(row['attributes']) if row['attributes'] else {}
                ))
            
            return entities
    
    # === Layer 2: Episodic Methods ===
    
    def record_interaction(self, interaction: EpisodicInteraction) -> int:
        """Record an interaction in the episodic layer"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO episodic_interactions
                (session_id, user_input, intent_recognized, ai_response,
                 command_executed, success, error_type, error_message,
                 execution_time_ms, tokens_used, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction.session_id,
                interaction.user_input,
                interaction.intent_recognized,
                interaction.ai_response,
                interaction.command_executed,
                interaction.success,
                interaction.error_type,
                interaction.error_message,
                interaction.execution_time_ms,
                interaction.tokens_used,
                json.dumps(interaction.context)
            ))
            conn.commit()
            
            interaction_id = cursor.lastrowid
            
            # Analyze for patterns
            self._analyze_interaction_patterns(interaction, interaction_id)
            
            return interaction_id
    
    def _analyze_interaction_patterns(self, interaction: EpisodicInteraction, interaction_id: int):
        """Analyze interaction for patterns and update pattern database"""
        # Check for error recovery pattern
        if interaction.error_type and interaction.success:
            self._record_pattern(
                PatternType.ERROR_RECOVERY,
                f"{interaction.error_type}:{interaction.intent_recognized}",
                {
                    "error": interaction.error_type,
                    "solution": interaction.command_executed,
                    "context": interaction.context
                }
            )
        
        # Check for workflow patterns
        if interaction.session_id:
            recent_interactions = self._get_recent_session_interactions(interaction.session_id, limit=5)
            if len(recent_interactions) >= 2:
                workflow = [i['intent_recognized'] for i in recent_interactions if i['intent_recognized']]
                if len(workflow) >= 2:
                    self._record_pattern(
                        PatternType.WORKFLOW,
                        "->".join(workflow[-3:]),  # Last 3 steps
                        {"steps": workflow, "success_rate": sum(1 for i in recent_interactions if i['success']) / len(recent_interactions)}
                    )
    
    def _record_pattern(self, pattern_type: PatternType, signature: str, data: Dict):
        """Record or update a pattern"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if pattern exists
            cursor.execute("""
                SELECT id, frequency, confidence FROM episodic_patterns
                WHERE pattern_type = ? AND pattern_signature = ?
            """, (pattern_type.value, signature))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pattern
                new_frequency = existing['frequency'] + 1
                new_confidence = min(1.0, existing['confidence'] + 0.05)  # Slowly increase confidence
                
                cursor.execute("""
                    UPDATE episodic_patterns
                    SET frequency = ?, confidence = ?, last_seen = CURRENT_TIMESTAMP,
                        pattern_data = ?
                    WHERE id = ?
                """, (new_frequency, new_confidence, json.dumps(data), existing['id']))
            else:
                # Create new pattern
                cursor.execute("""
                    INSERT INTO episodic_patterns
                    (pattern_type, pattern_signature, pattern_data, frequency, confidence)
                    VALUES (?, ?, ?, 1, 0.5)
                """, (pattern_type.value, signature, json.dumps(data)))
            
            conn.commit()
    
    def _get_recent_session_interactions(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent interactions from a session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM episodic_interactions
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def find_solution(self, problem_signature: str) -> Optional[Dict]:
        """Find a solution for a problem"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM episodic_solutions
                WHERE problem_signature = ?
            """, (problem_signature,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'solution_type': row['solution_type'],
                    'solution_steps': json.loads(row['solution_steps']),
                    'success_rate': row['success_rate'],
                    'times_used': row['times_used']
                }
        
        return None
    
    # === Layer 3: Phenomenological Methods ===
    
    def assess_user_state(self, interaction_id: int, evidence: Dict[str, Any]) -> PhenomenologicalState:
        """Assess user's phenomenological state based on interaction evidence"""
        state = PhenomenologicalState(interaction_id=interaction_id, evidence=evidence)
        
        # Try to use the sophisticated phenomenological tracker
        try:
            from .phenomenological_tracker import get_phenomenological_tracker
            
            tracker = get_phenomenological_tracker()
            
            # Analyze with the sophisticated tracker
            snapshot = tracker.analyze_interaction(
                interaction=evidence.get('interaction', {}),
                response_time_ms=evidence.get('response_time', 5000),
                success=evidence.get('error_count', 0) == 0,
                error_type=evidence.get('error_type')
            )
            
            # Use tracker's sophisticated analysis
            state.flow_probability = snapshot.flow_probability
            state.confusion_probability = snapshot.confusion_probability
            state.frustration_probability = 1.0 - snapshot.satisfaction_score if snapshot.satisfaction_score < 0.4 else 0.1
            state.satisfaction_score = snapshot.satisfaction_score
            state.engagement_level = snapshot.engagement_level
            state.cognitive_load = snapshot.confusion_probability * 0.5 + (1.0 - snapshot.flow_probability) * 0.5
            
            # Map emotional states to probabilities
            from .phenomenological_tracker import EmotionalState
            if snapshot.emotional_state == EmotionalState.ANXIOUS:
                state.anxiety_probability = 0.7
            elif snapshot.emotional_state == EmotionalState.FRUSTRATED:
                state.frustration_probability = 0.8
            elif snapshot.emotional_state == EmotionalState.CONFUSED:
                state.confusion_probability = 0.8
            
            # Add cognitive load info
            from .phenomenological_tracker import CognitiveLoad
            if snapshot.cognitive_load == CognitiveLoad.OVERWHELMED:
                state.cognitive_load = 0.9
            elif snapshot.cognitive_load == CognitiveLoad.BORED:
                state.boredom_probability = 0.7
            
            # Store additional context from tracker
            evidence['emotional_state'] = snapshot.emotional_state.value
            evidence['cognitive_load_level'] = snapshot.cognitive_load.value
            evidence['learning_momentum'] = snapshot.learning_momentum
            evidence['stress_indicators'] = snapshot.stress_indicators
            
        except ImportError:
            # Fallback to simple heuristics if tracker not available
            # Analyze evidence for state indicators
            if 'response_time' in evidence:
                # Fast responses might indicate flow
                if evidence['response_time'] < 2000:  # 2 seconds
                    state.flow_probability = 0.7
                    state.engagement_level = 0.8
                elif evidence['response_time'] > 10000:  # 10 seconds
                    state.confusion_probability = 0.6
                    state.cognitive_load = 0.8
            
            if 'error_count' in evidence:
                if evidence['error_count'] > 2:
                    state.frustration_probability = 0.7
                    state.satisfaction_score = 0.3
            
            if 'repeat_command' in evidence and evidence['repeat_command']:
                state.confusion_probability = max(state.confusion_probability, 0.6)
                state.frustration_probability = max(state.frustration_probability, 0.4)
        
        # Save state to database
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO phenomenological_states
                (interaction_id, flow_probability, anxiety_probability, confusion_probability,
                 boredom_probability, frustration_probability, cognitive_load,
                 engagement_level, satisfaction_score, evidence, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction_id,
                state.flow_probability,
                state.anxiety_probability,
                state.confusion_probability,
                state.boredom_probability,
                state.frustration_probability,
                state.cognitive_load,
                state.engagement_level,
                state.satisfaction_score,
                json.dumps(evidence),
                state.confidence
            ))
            conn.commit()
            state.id = cursor.lastrowid
        
        return state
    
    def record_qualia(self, interaction_id: int, system_state: Dict[str, Any]) -> Dict[str, float]:
        """Record the system's subjective experience (computational qualia)"""
        # Compute qualia from system state
        qualia = {
            'effort': self._compute_effort(system_state),
            'confusion': self._compute_confusion(system_state),
            'flow': self._compute_flow(system_state),
            'learning_momentum': self._compute_learning_momentum(system_state),
            'empathic_resonance': self._compute_empathic_resonance(system_state)
        }
        
        explanation = self._generate_qualia_explanation(qualia)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO phenomenological_qualia
                (interaction_id, effort, confusion, flow, learning_momentum,
                 empathic_resonance, raw_state, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction_id,
                qualia['effort'],
                qualia['confusion'],
                qualia['flow'],
                qualia['learning_momentum'],
                qualia['empathic_resonance'],
                json.dumps(system_state),
                explanation
            ))
            conn.commit()
        
        return qualia
    
    def _compute_effort(self, state: Dict) -> float:
        """Compute effort qualia from system state"""
        # Based on computation time, retries, complexity
        base_effort = 0.3
        if 'computation_time' in state:
            base_effort += min(0.4, state['computation_time'] / 10000)
        if 'retries' in state:
            base_effort += min(0.3, state['retries'] * 0.1)
        return min(1.0, base_effort)
    
    def _compute_confusion(self, state: Dict) -> float:
        """Compute confusion qualia from system state"""
        confusion = 0.0
        if 'intent_confidence' in state and state['intent_confidence'] < 0.5:
            confusion += 0.4
        if 'ambiguous_entities' in state and state['ambiguous_entities'] > 0:
            confusion += 0.3
        if 'parse_errors' in state and state['parse_errors'] > 0:
            confusion += 0.3
        return min(1.0, confusion)
    
    def _compute_flow(self, state: Dict) -> float:
        """Compute flow qualia from system state"""
        flow = 0.5
        if 'cache_hits' in state and state['cache_hits'] > 0:
            flow += 0.2
        if 'pattern_matches' in state and state['pattern_matches'] > 0:
            flow += 0.3
        if 'errors' in state and state['errors'] == 0:
            flow += 0.2
        return min(1.0, flow)
    
    def _compute_learning_momentum(self, state: Dict) -> float:
        """Compute learning momentum from system state"""
        momentum = 0.0
        if 'new_patterns' in state and state['new_patterns'] > 0:
            momentum += 0.4
        if 'skill_progress' in state:
            momentum += state['skill_progress'] * 0.6
        return min(1.0, momentum)
    
    def _compute_empathic_resonance(self, state: Dict) -> float:
        """Compute empathic resonance with user"""
        resonance = 0.5
        if 'user_satisfaction' in state:
            resonance = state['user_satisfaction']
        if 'personalization_match' in state:
            resonance = (resonance + state['personalization_match']) / 2
        return resonance
    
    def _generate_qualia_explanation(self, qualia: Dict[str, float]) -> str:
        """Generate natural language explanation of qualia"""
        explanations = []
        
        if qualia['effort'] > 0.7:
            explanations.append("Working hard to understand")
        elif qualia['effort'] < 0.3:
            explanations.append("Processing effortlessly")
        
        if qualia['confusion'] > 0.6:
            explanations.append("feeling uncertain about intent")
        
        if qualia['flow'] > 0.7:
            explanations.append("in smooth flow state")
        
        if qualia['learning_momentum'] > 0.5:
            explanations.append("learning and adapting")
        
        if qualia['empathic_resonance'] > 0.7:
            explanations.append("strongly connected with user")
        
        return "; ".join(explanations) if explanations else "Processing normally"
    
    # === Layer 4: Metacognitive Methods ===
    
    def record_reasoning(self, reasoning: MetacognitiveReasoning) -> int:
        """Record AI reasoning trace for explainability"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metacognitive_reasoning
                (interaction_id, reasoning_type, reasoning_trace,
                 confidence_scores, uncertainty_points, decision_path,
                 alternatives_considered)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                reasoning.interaction_id,
                reasoning.reasoning_type.value,
                json.dumps(reasoning.reasoning_trace),
                json.dumps(reasoning.confidence_scores),
                json.dumps(reasoning.uncertainty_points),
                reasoning.decision_path,
                json.dumps(reasoning.alternatives_considered)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def update_capability(self, domain: str, capability: str, 
                         confidence: float, evidence: bool = True):
        """Update AI's self-model of capabilities"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if capability exists
            cursor.execute("""
                SELECT id, confidence_level, evidence_count 
                FROM metacognitive_capabilities
                WHERE capability_domain = ? AND capability_name = ?
            """, (domain, capability))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing capability
                new_evidence_count = existing['evidence_count'] + (1 if evidence else 0)
                # Weighted average for confidence
                new_confidence = (existing['confidence_level'] * existing['evidence_count'] + confidence) / (existing['evidence_count'] + 1)
                
                cursor.execute("""
                    UPDATE metacognitive_capabilities
                    SET confidence_level = ?, evidence_count = ?,
                        last_demonstrated = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_confidence, new_evidence_count, existing['id']))
            else:
                # Add new capability
                cursor.execute("""
                    INSERT INTO metacognitive_capabilities
                    (capability_domain, capability_name, confidence_level, evidence_count)
                    VALUES (?, ?, ?, 1)
                """, (domain, capability, confidence))
            
            conn.commit()
    
    def check_boundary(self, boundary_type: str, context: Dict) -> Optional[Dict]:
        """Check if we're approaching a boundary/limitation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM metacognitive_boundaries
                WHERE boundary_type = ?
                ORDER BY severity DESC
            """, (boundary_type,))
            
            for row in cursor.fetchall():
                boundary = dict(row)
                # Check if this boundary applies to current context
                # This is simplified - real implementation would be more sophisticated
                if self._boundary_applies(boundary, context):
                    # Update encounter count
                    cursor.execute("""
                        UPDATE metacognitive_boundaries
                        SET encountered_count = encountered_count + 1,
                            last_encountered = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (boundary['id'],))
                    conn.commit()
                    
                    return boundary
        
        return None
    
    def _boundary_applies(self, boundary: Dict, context: Dict) -> bool:
        """Check if a boundary applies to the current context"""
        # Simplified check - real implementation would be more sophisticated
        if boundary['boundary_type'] == 'ethical':
            return context.get('potentially_harmful', False)
        elif boundary['boundary_type'] == 'technical':
            return context.get('complexity', 0) > 0.8
        elif boundary['boundary_type'] == 'knowledge':
            return context.get('confidence', 1.0) < 0.3
        return False
    
    # === Cross-Layer Methods ===
    
    def get_skill_mastery(self, skill_name: str) -> float:
        """Get current mastery level for a skill"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Check if table exists first
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='episodic_skills'
                """)
                if not cursor.fetchone():
                    # Table doesn't exist, return default
                    return 0.5
                
                cursor.execute("""
                    SELECT prior_mean 
                    FROM episodic_skills
                    WHERE skill_name = ?
                """, (skill_name,))
                
                result = cursor.fetchone()
                return result['prior_mean'] if result else 0.0
        except Exception:
            # If any error, return default mastery
            return 0.5
    
    def record_insight(self, source: str, insight: str, confidence: float = 0.8):
        """Record an insight or pattern discovered"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO episodic_patterns 
                (pattern_type, pattern_signature, pattern_data, frequency, confidence)
                VALUES (?, ?, ?, 1, ?)
            """, (source, insight, json.dumps({"insight": insight, "source": source}), confidence))
            conn.commit()
    
    def update_skill_mastery(self, skill_name: str, success: bool):
        """Update skill mastery using Bayesian Knowledge Tracing"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get skill ID
            cursor.execute("""
                SELECT id FROM ontological_skills WHERE skill_name = ?
            """, (skill_name,))
            
            skill_row = cursor.fetchone()
            if not skill_row:
                # Create skill if it doesn't exist
                cursor.execute("""
                    INSERT INTO ontological_skills (skill_name, difficulty_level)
                    VALUES (?, 5)
                """, (skill_name,))
                skill_id = cursor.lastrowid
            else:
                skill_id = skill_row['id']
            
            # Get current mastery
            cursor.execute("""
                SELECT * FROM skill_mastery WHERE skill_id = ?
            """, (skill_id,))
            
            mastery_row = cursor.fetchone()
            
            if mastery_row:
                # Update using BKT
                p_know = mastery_row['current_mastery']
                p_learn = mastery_row['learning_rate']
                p_slip = mastery_row['slip_probability']
                p_guess = mastery_row['guess_probability']
                
                if success:
                    # P(know|correct) = P(know)(1-P(slip)) / [P(know)(1-P(slip)) + (1-P(know))P(guess)]
                    numerator = p_know * (1 - p_slip)
                    denominator = p_know * (1 - p_slip) + (1 - p_know) * p_guess
                    p_know_given_obs = numerator / denominator if denominator > 0 else p_know
                else:
                    # P(know|incorrect) = P(know)P(slip) / [P(know)P(slip) + (1-P(know))(1-P(guess))]
                    numerator = p_know * p_slip
                    denominator = p_know * p_slip + (1 - p_know) * (1 - p_guess)
                    p_know_given_obs = numerator / denominator if denominator > 0 else p_know
                
                # P(know_next) = P(know|obs) + (1-P(know|obs))P(learn)
                p_know_next = p_know_given_obs + (1 - p_know_given_obs) * p_learn
                
                cursor.execute("""
                    UPDATE skill_mastery
                    SET current_mastery = ?, practice_count = practice_count + 1,
                        success_count = success_count + ?, last_practiced = CURRENT_TIMESTAMP
                    WHERE skill_id = ?
                """, (p_know_next, 1 if success else 0, skill_id))
            else:
                # Create new mastery record
                cursor.execute("""
                    INSERT INTO skill_mastery
                    (skill_id, current_mastery, practice_count, success_count)
                    VALUES (?, ?, 1, ?)
                """, (skill_id, 0.2 if success else 0.1, 1 if success else 0))
            
            conn.commit()
    
    def learn_preference(self, preference_type: str, key: str, value: Any, confidence: float = 0.5):
        """Learn and update user preferences"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM user_preferences
                WHERE preference_type = ? AND preference_key = ?
            """, (preference_type, key))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update with weighted average
                old_confidence = existing['confidence']
                new_confidence = (old_confidence * existing['evidence_count'] + confidence) / (existing['evidence_count'] + 1)
                
                cursor.execute("""
                    UPDATE user_preferences
                    SET preference_value = ?, confidence = ?,
                        evidence_count = evidence_count + 1,
                        last_observed = CURRENT_TIMESTAMP
                    WHERE preference_type = ? AND preference_key = ?
                """, (json.dumps(value), new_confidence, preference_type, key))
            else:
                cursor.execute("""
                    INSERT INTO user_preferences
                    (preference_type, preference_key, preference_value, confidence)
                    VALUES (?, ?, ?, ?)
                """, (preference_type, key, json.dumps(value), confidence))
            
            conn.commit()
    
    def get_user_model(self) -> Dict[str, Any]:
        """Get comprehensive user model across all layers"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get latest phenomenological state
            cursor.execute("""
                SELECT * FROM phenomenological_states
                ORDER BY timestamp DESC LIMIT 1
            """)
            latest_state = cursor.fetchone()
            
            # Get skill mastery
            cursor.execute("""
                SELECT s.skill_name, sm.current_mastery
                FROM skill_mastery sm
                JOIN ontological_skills s ON sm.skill_id = s.id
                WHERE sm.current_mastery > 0.3
                ORDER BY sm.current_mastery DESC
            """)
            skills = {row['skill_name']: row['current_mastery'] for row in cursor.fetchall()}
            
            # Get preferences
            cursor.execute("""
                SELECT preference_type, preference_key, preference_value, confidence
                FROM user_preferences
                WHERE confidence > 0.5
            """)
            preferences = {}
            for row in cursor.fetchall():
                if row['preference_type'] not in preferences:
                    preferences[row['preference_type']] = {}
                preferences[row['preference_type']][row['preference_key']] = {
                    'value': json.loads(row['preference_value']),
                    'confidence': row['confidence']
                }
            
            # Get common patterns
            cursor.execute("""
                SELECT pattern_type, pattern_signature, confidence
                FROM episodic_patterns
                WHERE confidence > 0.6
                ORDER BY frequency DESC
                LIMIT 10
            """)
            patterns = [dict(row) for row in cursor.fetchall()]
            
            return {
                'current_state': dict(latest_state) if latest_state else None,
                'skills': skills,
                'preferences': preferences,
                'patterns': patterns,
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_insights(self) -> List[str]:
        """Generate insights from the knowledge graph"""
        insights = []
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insight 1: Most challenging areas
            cursor.execute("""
                SELECT intent_recognized, COUNT(*) as error_count
                FROM episodic_interactions
                WHERE success = 0 AND intent_recognized IS NOT NULL
                GROUP BY intent_recognized
                ORDER BY error_count DESC
                LIMIT 3
            """)
            for row in cursor.fetchall():
                insights.append(f"Users struggle most with '{row['intent_recognized']}' (failed {row['error_count']} times)")
            
            # Insight 2: Learning progress
            cursor.execute("""
                SELECT AVG(current_mastery) as avg_mastery
                FROM skill_mastery
            """)
            avg_mastery = cursor.fetchone()['avg_mastery']
            if avg_mastery:
                insights.append(f"Average skill mastery: {avg_mastery:.1%}")
            
            # Insight 3: User satisfaction trend
            cursor.execute("""
                SELECT AVG(satisfaction_score) as avg_satisfaction
                FROM phenomenological_states
                WHERE timestamp > datetime('now', '-7 days')
            """)
            recent_satisfaction = cursor.fetchone()['avg_satisfaction']
            if recent_satisfaction:
                insights.append(f"Recent user satisfaction: {recent_satisfaction:.1%}")
            
            # Insight 4: Most effective solutions
            cursor.execute("""
                SELECT problem_signature, success_rate
                FROM episodic_solutions
                WHERE times_used > 3
                ORDER BY success_rate DESC
                LIMIT 1
            """)
            best_solution = cursor.fetchone()
            if best_solution:
                insights.append(f"Most reliable solution: {best_solution['problem_signature']} ({best_solution['success_rate']:.1%} success)")
            
        return insights


# === Singleton Instance ===

_skg_instance: Optional[SymbioticKnowledgeGraph] = None

def get_skg() -> SymbioticKnowledgeGraph:
    """Get or create the singleton SKG instance"""
    global _skg_instance
    if _skg_instance is None:
        _skg_instance = SymbioticKnowledgeGraph()
    return _skg_instance