# 🗄️ Symbiotic Knowledge Graph (SKG) Schema Design

*SQLite implementation of the four-layer knowledge graph architecture*

---

💡 **Quick Context**: Database schema for implementing the SKG architecture from Oracle research  
📍 **You are here**: Architecture → SKG Schema Design  
🔗 **Related**: [Oracle Research Synthesis](../01-VISION/research/ORACLE_RESEARCH_SYNTHESIS.md) | [Learning System Architecture](./09-LEARNING-SYSTEM.md)  
⏱️ **Implementation**: Ready for immediate use  
📊 **Database**: SQLite 3.x compatible

---

## Overview

This document provides the complete SQLite schema for implementing the four-layer Symbiotic Knowledge Graph (SKG) as described in the Oracle research. The schema is designed to be:

- **Incremental**: Can be added to existing SQLite databases
- **Performant**: Optimized indexes for common queries
- **Extensible**: JSON fields for flexible metadata
- **Traceable**: Audit trails and timestamps throughout

## Schema Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Symbiotic Knowledge Graph                 │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Metacognitive (AI Self-Model)                     │
│  - capabilities, reasoning traces, limitations              │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Phenomenological (User Experience)                │
│  - affective states, cognitive load, subjective experience  │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Episodic (Interaction History)                    │
│  - commands, errors, solutions, temporal patterns           │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Ontological (Domain Knowledge)                    │
│  - packages, modules, options, relationships                │
└─────────────────────────────────────────────────────────────┘
```

## Layer 1: Ontological (Domain Knowledge)

The foundation layer that models NixOS domain knowledge.

```sql
-- Core entities in the NixOS domain
CREATE TABLE IF NOT EXISTS ontological_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL CHECK(entity_type IN ('package', 'module', 'option', 'flake', 'function', 'concept')),
    name TEXT NOT NULL,
    description TEXT,
    attributes JSON, -- Flexible attributes like version, maintainer, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, name)
);

CREATE INDEX idx_onto_entity_type ON ontological_entities(entity_type);
CREATE INDEX idx_onto_name ON ontological_entities(name);

-- Relationships between entities
CREATE TABLE IF NOT EXISTS ontological_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_entity_id INTEGER NOT NULL,
    to_entity_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL CHECK(relationship_type IN (
        'depends_on', 'imports', 'extends', 'implements', 
        'has_option', 'provides', 'conflicts_with', 'replaces'
    )),
    strength REAL DEFAULT 1.0, -- Relationship strength/weight
    metadata JSON, -- Additional relationship data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_entity_id) REFERENCES ontological_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (to_entity_id) REFERENCES ontological_entities(id) ON DELETE CASCADE,
    UNIQUE(from_entity_id, to_entity_id, relationship_type)
);

CREATE INDEX idx_onto_rel_from ON ontological_relationships(from_entity_id);
CREATE INDEX idx_onto_rel_to ON ontological_relationships(to_entity_id);
CREATE INDEX idx_onto_rel_type ON ontological_relationships(relationship_type);

-- Skill graph for learning system
CREATE TABLE IF NOT EXISTS ontological_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE,
    entity_id INTEGER,
    difficulty_level INTEGER CHECK(difficulty_level BETWEEN 1 AND 10),
    prerequisites JSON, -- Array of skill IDs
    learning_resources JSON, -- Links to documentation, tutorials
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES ontological_entities(id)
);

CREATE INDEX idx_skills_difficulty ON ontological_skills(difficulty_level);
```

## Layer 2: Episodic (Interaction History)

Records the temporal history of user-AI interactions.

```sql
-- Main interaction log
CREATE TABLE IF NOT EXISTS episodic_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT, -- Group related interactions
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_input TEXT NOT NULL,
    intent_recognized TEXT, -- What the system understood
    ai_response TEXT NOT NULL,
    command_executed TEXT,
    success BOOLEAN,
    error_type TEXT,
    error_message TEXT,
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    context JSON, -- Additional context like active directory, env vars
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_episodic_timestamp ON episodic_interactions(timestamp);
CREATE INDEX idx_episodic_session ON episodic_interactions(session_id);
CREATE INDEX idx_episodic_success ON episodic_interactions(success);
CREATE INDEX idx_episodic_intent ON episodic_interactions(intent_recognized);

-- Learned patterns from interactions
CREATE TABLE IF NOT EXISTS episodic_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL CHECK(pattern_type IN (
        'command_sequence', 'error_recovery', 'learning_moment', 
        'workflow', 'preference', 'correction'
    )),
    pattern_signature TEXT NOT NULL, -- Hash or identifier
    pattern_data JSON NOT NULL, -- The actual pattern
    frequency INTEGER DEFAULT 1,
    confidence REAL DEFAULT 0.5,
    last_seen TIMESTAMP,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pattern_type, pattern_signature)
);

CREATE INDEX idx_patterns_type ON episodic_patterns(pattern_type);
CREATE INDEX idx_patterns_frequency ON episodic_patterns(frequency);

-- Solutions that worked for specific problems
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

CREATE INDEX idx_solutions_success ON episodic_solutions(success_rate);
```

## Layer 3: Phenomenological (User Experience)

Models the user's subjective experience and affective states.

```sql
-- Continuous tracking of user's affective state
CREATE TABLE IF NOT EXISTS phenomenological_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Probability distributions for different states
    flow_probability REAL CHECK(flow_probability BETWEEN 0 AND 1),
    anxiety_probability REAL CHECK(anxiety_probability BETWEEN 0 AND 1),
    confusion_probability REAL CHECK(confusion_probability BETWEEN 0 AND 1),
    boredom_probability REAL CHECK(boredom_probability BETWEEN 0 AND 1),
    frustration_probability REAL CHECK(frustration_probability BETWEEN 0 AND 1),
    -- Continuous metrics
    cognitive_load REAL CHECK(cognitive_load BETWEEN 0 AND 1),
    engagement_level REAL CHECK(engagement_level BETWEEN 0 AND 1),
    satisfaction_score REAL CHECK(satisfaction_score BETWEEN 0 AND 1),
    -- Evidence for this inference
    evidence JSON NOT NULL, -- What behavioral signals led to this inference
    confidence REAL DEFAULT 0.5,
    FOREIGN KEY (interaction_id) REFERENCES episodic_interactions(id)
);

CREATE INDEX idx_phenom_timestamp ON phenomenological_states(timestamp);
CREATE INDEX idx_phenom_interaction ON phenomenological_states(interaction_id);

-- Identified triggers for state changes
CREATE TABLE IF NOT EXISTS phenomenological_triggers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_type TEXT NOT NULL CHECK(trigger_type IN (
        'frustration_pattern', 'flow_indicator', 'confusion_signal',
        'satisfaction_marker', 'fatigue_sign', 'engagement_boost'
    )),
    trigger_conditions JSON NOT NULL, -- Specific conditions that trigger this
    average_impact REAL, -- How much this affects the state
    observed_count INTEGER DEFAULT 0,
    last_observed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_triggers_type ON phenomenological_triggers(trigger_type);
CREATE INDEX idx_triggers_count ON phenomenological_triggers(observed_count);

-- Computational qualia - the system's subjective experience
CREATE TABLE IF NOT EXISTS phenomenological_qualia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effort REAL CHECK(effort BETWEEN 0 AND 1),
    confusion REAL CHECK(confusion BETWEEN 0 AND 1),
    flow REAL CHECK(flow BETWEEN 0 AND 1),
    learning_momentum REAL CHECK(learning_momentum BETWEEN 0 AND 1),
    empathic_resonance REAL CHECK(empathic_resonance BETWEEN 0 AND 1),
    raw_state JSON, -- The SystemState that produced these qualia
    explanation TEXT, -- Natural language explanation
    FOREIGN KEY (interaction_id) REFERENCES episodic_interactions(id)
);

CREATE INDEX idx_qualia_interaction ON phenomenological_qualia(interaction_id);
```

## Layer 4: Metacognitive (AI Self-Model)

The AI's model of its own capabilities and reasoning.

```sql
-- AI's understanding of its own capabilities
CREATE TABLE IF NOT EXISTS metacognitive_capabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capability_domain TEXT NOT NULL,
    capability_name TEXT NOT NULL,
    confidence_level REAL CHECK(confidence_level BETWEEN 0 AND 1),
    evidence_count INTEGER DEFAULT 0, -- How many times demonstrated
    limitations TEXT, -- Known limitations
    last_demonstrated TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(capability_domain, capability_name)
);

CREATE INDEX idx_meta_cap_domain ON metacognitive_capabilities(capability_domain);
CREATE INDEX idx_meta_cap_confidence ON metacognitive_capabilities(confidence_level);

-- Reasoning traces for explainability
CREATE TABLE IF NOT EXISTS metacognitive_reasoning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reasoning_type TEXT CHECK(reasoning_type IN (
        'intent_recognition', 'solution_selection', 'error_diagnosis',
        'learning_inference', 'state_assessment', 'intervention_decision'
    )),
    reasoning_trace JSON NOT NULL, -- Step-by-step reasoning
    confidence_scores JSON, -- Confidence at each step
    uncertainty_points JSON, -- Where the AI was unsure
    decision_path TEXT, -- Final decision made
    alternatives_considered JSON, -- Other options that were rejected
    FOREIGN KEY (interaction_id) REFERENCES episodic_interactions(id)
);

CREATE INDEX idx_reasoning_interaction ON metacognitive_reasoning(interaction_id);
CREATE INDEX idx_reasoning_type ON metacognitive_reasoning(reasoning_type);

-- Self-assessment and limitations
CREATE TABLE IF NOT EXISTS metacognitive_boundaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    boundary_type TEXT NOT NULL CHECK(boundary_type IN (
        'ethical', 'technical', 'knowledge', 'computational', 'safety'
    )),
    description TEXT NOT NULL,
    severity TEXT CHECK(severity IN ('hard', 'soft', 'advisory')),
    encountered_count INTEGER DEFAULT 0,
    last_encountered TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_boundaries_type ON metacognitive_boundaries(boundary_type);
```

## Cross-Layer Connections

Views and helper tables that connect across layers.

```sql
-- Connect skills to user mastery (Ontological → Episodic)
CREATE TABLE IF NOT EXISTS skill_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    -- BKT parameters
    prior_knowledge REAL DEFAULT 0.1,
    learning_rate REAL DEFAULT 0.1,
    slip_probability REAL DEFAULT 0.1,
    guess_probability REAL DEFAULT 0.25,
    current_mastery REAL DEFAULT 0.1,
    -- Tracking
    practice_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_practiced TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES ontological_skills(id),
    UNIQUE(skill_id)
);

-- User preferences learned over time
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

-- ActivityWatch integration cache
CREATE TABLE IF NOT EXISTS activity_watch_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bucket_id TEXT NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    duration_seconds REAL,
    event_data JSON NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_aw_timestamp ON activity_watch_events(event_timestamp);
CREATE INDEX idx_aw_processed ON activity_watch_events(processed);
```

## Migration Script

For existing databases, this migration script adds the SKG tables:

```sql
-- Migration: Add SKG tables to existing database
-- Version: 1.0.0
-- Date: 2024-01-XX

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Add version tracking
CREATE TABLE IF NOT EXISTS schema_versions (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Check if already applied
INSERT OR IGNORE INTO schema_versions (version) VALUES ('skg_1.0.0');

-- Create all tables (they all use IF NOT EXISTS)
-- [Include all CREATE TABLE statements from above]

COMMIT;
```

## Query Examples

### 1. Find user's current emotional state
```sql
SELECT 
    ps.*,
    ei.user_input,
    ei.ai_response
FROM phenomenological_states ps
JOIN episodic_interactions ei ON ps.interaction_id = ei.id
ORDER BY ps.timestamp DESC
LIMIT 1;
```

### 2. Get skill mastery with prerequisites
```sql
WITH RECURSIVE skill_tree AS (
    SELECT s.*, sm.current_mastery, 0 as depth
    FROM ontological_skills s
    LEFT JOIN skill_mastery sm ON s.id = sm.skill_id
    WHERE s.skill_name = 'nix-flakes'
    
    UNION ALL
    
    SELECT s.*, sm.current_mastery, st.depth + 1
    FROM ontological_skills s
    JOIN skill_tree st ON s.id IN (
        SELECT value FROM json_each(st.prerequisites)
    )
    LEFT JOIN skill_mastery sm ON s.id = sm.skill_id
)
SELECT * FROM skill_tree ORDER BY depth;
```

### 3. Analyze reasoning patterns
```sql
SELECT 
    mr.reasoning_type,
    COUNT(*) as count,
    AVG(json_extract(mr.confidence_scores, '$.final')) as avg_confidence
FROM metacognitive_reasoning mr
WHERE mr.timestamp > datetime('now', '-7 days')
GROUP BY mr.reasoning_type
ORDER BY count DESC;
```

## Performance Considerations

1. **Indexes**: All foreign keys and commonly queried fields are indexed
2. **JSON Storage**: Used for flexible, evolving data structures
3. **Timestamps**: Consistent UTC timestamps throughout
4. **Constraints**: CHECK constraints ensure data validity
5. **Archival**: Consider archiving old episodic data after 6 months

## Security Notes

1. **User Privacy**: No PII stored in the base schema
2. **Local-First**: Designed for local SQLite, not cloud deployment
3. **Audit Trail**: Timestamps allow full audit of all changes
4. **Data Ownership**: User can export/delete all their data

---

*"A knowledge graph that grows with understanding, modeling not just what we know, but how we know it."*

**Status**: Ready for implementation  
**Next Step**: Run migration script on development database  
**Remember**: Start with Layer 1 & 2, add phenomenological features gradually 🌊