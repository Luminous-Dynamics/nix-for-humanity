# 🧬 Research Components Integration

*Implementing symbiotic intelligence through research-based components*

---

💡 **Quick Context**: How cutting-edge research is integrated into Nix for Humanity  
📍 **You are here**: Architecture → Research Integration  
🔗 **Related**: [System Architecture](./01-SYSTEM-ARCHITECTURE.md) | [Learning System](./09-LEARNING-SYSTEM.md) | [Dynamic User Modeling](./03-DYNAMIC-USER-MODELING.md)  
⏱️ **Read time**: 10 minutes  
📊 **Mastery Level**: 🌿 Intermediate-Advanced

---

## Overview

The research integration brings five major components from our symbiotic intelligence research directly into the Nix for Humanity codebase:

1. **Symbiotic Knowledge Graph (SKG)** - Four-layer knowledge representation
2. **Theory of Mind Trust Engine** - CASA-based trust building
3. **Consciousness-First Metrics** - Wellbeing over engagement
4. **Privacy-First Perception** - ActivityWatch integration
5. **Sacred Development Patterns** - Consciousness-aware code

## Architecture Integration

```
┌─────────────────────────────────────────────────────────┐
│                   User Interfaces                         │
│         (CLI, TUI, Voice, API)                           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              NixForHumanityBackend                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │          Research Components Layer               │    │
│  │  ┌─────────────┐  ┌──────────────┐             │    │
│  │  │     SKG     │  │ Trust Engine │             │    │
│  │  │ ┌─────────┐ │  │              │             │    │
│  │  │ │Ontology │ │  │  ┌────────┐  │             │    │
│  │  │ │Episodic │ │  │  │  ToM   │  │             │    │
│  │  │ │Phenom.  │ │  │  │ Model  │  │             │    │
│  │  │ │Metacog. │ │  │  └────────┘  │             │    │
│  │  │ └─────────┘ │  └──────────────┘             │    │
│  │  └─────────────┘                                │    │
│  │                                                 │    │
│  │  ┌──────────────┐  ┌─────────────┐            │    │
│  │  │ Consciousness│  │  Activity   │            │    │
│  │  │   Metrics    │  │  Monitor    │            │    │
│  │  └──────────────┘  └─────────────┘            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Traditional Components                 │    │
│  │  (Intent Recognition, Executor, Knowledge Base) │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Symbiotic Knowledge Graph (SKG)

**Location**: `backend/knowledge_graph/`

The SKG provides four layers of knowledge representation:

```python
# Ontological Layer - What exists
skg.ontological.add_concept("firefox", "package", {
    "category": "browser",
    "declarative_install": True
})

# Episodic Layer - What happened
interaction_id = skg.episodic.record_interaction(
    user_input="install firefox",
    timestamp=time.time()
)

# Phenomenological Layer - What was experienced
skg.phenomenological.record_experience({
    'type': 'user_satisfaction',
    'rating': 0.9,
    'context': 'smooth_install'
})

# Metacognitive Layer - What we learned
skg.metacognitive.record_meta_learning({
    'pattern': 'browser_preference',
    'insight': 'user prefers open source'
})
```

### 2. Trust Engine with Theory of Mind

**Location**: `backend/trust_modeling/`

Implements CASA (Computers as Social Actors) paradigm:

```python
# Process each interaction for trust dynamics
trust_update = trust_engine.process_interaction(
    interaction_id="int_123",
    user_input="that didn't work",
    ai_response="I apologize. Let me try a different approach..."
)

# Returns trust actions
{
    'trust_delta': -0.1,
    'repair_needed': True,
    'repair_type': 'acknowledge_failure',
    'vulnerability_action': None,
    'new_trust_level': 'companion'
}
```

### 3. Consciousness-First Metrics

**Location**: `backend/consciousness_metrics/`

Tracks wellbeing instead of engagement:

```python
metrics = metrics_collector.collect_current_metrics({
    'session_start': session_start_time,
    'interruptions': 5,
    'breaks_taken': 2,
    'focus_duration': 2400  # 40 minutes
})

# Returns consciousness state
{
    'wellbeing_score': 0.75,
    'attention_state': 'focused',
    'flow_state': True,
    'interruption_appropriate': False
}
```

### 4. Privacy-First Activity Monitoring

**Location**: `backend/perception/`

Optional ActivityWatch integration:

```python
# Only enabled with explicit consent
if os.getenv('NIX_HUMANITY_ACTIVITY_TRACKING') == 'true':
    monitor = ActivityMonitor(skg, privacy_mode='aggregate')
    context = monitor.get_current_context()
    # Returns behavioral patterns without content
```

### 5. Sacred Development Patterns

**Location**: `backend/sacred_development/`

Consciousness-aware coding patterns:

```python
# Sacred function decorator
@sacred_function(intention="Process with full awareness")
async def process_request(request):
    # Function automatically tracks wisdom
    pass

# Consciousness guard
with consciousness_guard.sacred_context("Handle user request"):
    # Code executes with intention
    response = await process()
```

## Configuration

### Environment Variables

```bash
# Enable/disable research components
export NIX_HUMANITY_DISABLE_RESEARCH=false

# SKG database location
export NIX_HUMANITY_SKG_PATH=./data/skg.db

# Activity tracking (opt-in only)
export NIX_HUMANITY_ACTIVITY_TRACKING=false

# Privacy mode: strict, aggregate, full
export NIX_HUMANITY_PRIVACY_MODE=aggregate
```

### Research Configuration

```python
from backend.config import ResearchConfig

config = ResearchConfig(
    # SKG settings
    skg_enabled=True,
    skg_db_path="./data/skg.db",
    
    # Trust modeling
    trust_modeling_enabled=True,
    trust_initial_level="acquaintance",
    vulnerability_frequency=0.1,  # 10% of interactions
    
    # Consciousness metrics
    consciousness_metrics_enabled=True,
    wellbeing_tracking=True,
    flow_state_detection=True,
    
    # Sacred patterns
    sacred_patterns_enabled=True,
    consciousness_guard_enabled=True
)
```

## Usage Examples

### Basic Integration

```python
from backend.core.backend import NixForHumanityBackend

# Backend automatically initializes research components
backend = NixForHumanityBackend()

# Process request with full awareness
response = await backend.process_request(request)

# Response includes research enhancements
if response.data.get('consciousness_metrics'):
    print(f"Wellbeing: {response.data['consciousness_metrics']['wellbeing_score']}")
    
if response.data.get('trust_building'):
    print(f"Trust action: {response.data['trust_building']}")
```

### Direct Component Access

```python
# Access SKG for queries
if backend.skg:
    # Find related concepts
    concepts = backend.skg.ontological.get_related_concepts(
        "firefox", 
        relation_type="alternative_to"
    )
    
    # Get user's history
    history = backend.skg.episodic.get_user_history(
        user_id="default",
        limit=10
    )
```

### Trust-Aware Responses

```python
# Trust engine automatically enhances responses
response = await backend.process_request(request)

# May include vulnerability disclosure
if response.data.get('vulnerability_disclosure'):
    # "I'm still learning about this. Your feedback helps me improve!"
    print(response.data['vulnerability_disclosure'])
```

## Testing Research Components

```bash
# Run integration tests
python test_research_integration.py

# Output shows initialized components
✓ SKG Available: True
✓ Trust Engine: True  
✓ Metrics Collector: True
✓ Consciousness Guard: True
```

## Performance Considerations

1. **Lazy Loading**: Components only initialize when needed
2. **Async Operations**: SKG updates happen asynchronously
3. **Timeouts**: Research components have 5-second timeout
4. **Graceful Degradation**: System works without research components

## Privacy & Ethics

1. **Local-First**: All data stays on user's machine
2. **Opt-In Tracking**: Activity monitoring requires explicit consent
3. **Transparent Data**: Users can inspect all stored data
4. **Right to Deletion**: Complete data removal supported

## Future Enhancements

1. **Federated Learning**: Share patterns, not data
2. **Advanced ToM**: Deeper mental state modeling
3. **Collective Intelligence**: Community wisdom aggregation
4. **Embodied Perception**: Richer context awareness

---

*"Through research integration, we transform academic insights into lived technological experience, creating genuine human-AI partnership."*

**Status**: Research components fully integrated 🧬  
**Impact**: Consciousness-first AI that truly serves users 🌊