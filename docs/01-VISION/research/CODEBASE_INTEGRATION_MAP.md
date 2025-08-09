# 🗺️ Research to Codebase Integration Map

*Detailed mapping of research insights to specific files and implementation steps*

---

## Overview

This document provides a surgical mapping of research insights to our existing Nix for Humanity codebase, showing exactly which files need updates and what changes to make.

## 📁 Current Codebase Structure Analysis

### Core Python Files Needing Enhancement
- `backend/core/backend.py` - Main backend (needs SKG integration)
- `backend/core/intent.py` - Intent recognition (needs Mamba upgrade)
- `backend/core/executor.py` - Command execution (needs VLM expansion)
- `backend/ai/nlp.py` - NLP pipeline (needs consciousness metrics)
- `backend/learning/preferences.py` - User preferences (needs phenomenological layer)

### New Components to Create
- `backend/knowledge_graph/` - Four-layer SKG implementation
- `backend/perception/` - ActivityWatch integration
- `backend/metacognitive/` - Self-awareness system
- `backend/theory_of_mind/` - Trust and rapport modeling
- `backend/federated/` - Privacy-preserving learning

## 🔧 File-by-File Integration Guide

### 1. Transform backend/core/backend.py

**Current State**: Basic request/response processing
**Research Application**: Integrate four-layer knowledge graph

```python
# BEFORE (current simplified approach)
class NixForHumanityBackend:
    def __init__(self):
        self.intent_recognizer = IntentRecognizer()
        self.executor = SafeExecutor()
        self.knowledge = KnowledgeBase()

# AFTER (with SKG integration)
class NixForHumanityBackend:
    def __init__(self):
        # Existing components
        self.intent_recognizer = IntentRecognizer()
        self.executor = SafeExecutor()
        
        # NEW: Four-layer Symbiotic Knowledge Graph
        self.skg = SymbioticKnowledgeGraph()
        self.skg.ontological.load_nixos_schema()
        self.skg.episodic.connect_event_stream()
        self.skg.phenomenological.init_user_model()
        self.skg.metacognitive.instrument_components()
        
        # NEW: Theory of Mind for trust modeling
        self.tom_agent = TheoryOfMindAgent()
        
        # NEW: Constitutional repair protocols
        self.covenant = ConstitutionalCovenant()
```

### 2. Upgrade backend/core/intent.py

**Current State**: Pattern matching for intent
**Research Application**: Add Mamba for workflow understanding

```python
# NEW FILE: backend/core/workflow_model.py
import torch
from mamba_ssm import Mamba

class WorkflowUnderstandingModel:
    """Mamba-based continuous workflow understanding"""
    
    def __init__(self):
        self.mamba = Mamba(
            d_model=256,
            d_state=16,
            d_conv=4,
            expand=2
        )
        self.event_encoder = EventEncoder()
        
    async def process_event_stream(self, events):
        """Convert event stream to latent task vector"""
        # Encode events
        encoded = [self.event_encoder.encode(e) for e in events]
        
        # Process through Mamba
        hidden_state = self.mamba(torch.stack(encoded))
        
        # Extract latent task vector
        latent_task = hidden_state[-1]  # Current task representation
        return LatentTaskVector(latent_task)

# UPDATE backend/core/intent.py
class EnhancedIntentRecognizer:
    def __init__(self):
        # Keep existing pattern matching for speed
        self.pattern_matcher = PatternMatcher()
        
        # NEW: Add workflow understanding
        self.workflow_model = WorkflowUnderstandingModel()
        
        # NEW: Context fusion
        self.context_fusion = ContextFusionLayer()
        
    async def recognize(self, text, context):
        # Quick pattern match
        pattern_intent = self.pattern_matcher.match(text)
        
        # Get workflow context if available
        if context.get('event_stream'):
            task_vector = await self.workflow_model.process_event_stream(
                context['event_stream']
            )
            
            # Fuse pattern and workflow understanding
            intent = self.context_fusion.combine(pattern_intent, task_vector)
        else:
            intent = pattern_intent
            
        return intent
```

### 3. Create backend/knowledge_graph/

**New Component**: Four-layer Symbiotic Knowledge Graph

```python
# backend/knowledge_graph/__init__.py
from .ontological import OntologicalLayer
from .episodic import EpisodicLayer
from .phenomenological import PhenomenologicalLayer
from .metacognitive import MetacognitiveLayer
from .skg import SymbioticKnowledgeGraph

# backend/knowledge_graph/skg.py
import kuzu

class SymbioticKnowledgeGraph:
    """Four-layer knowledge graph for symbiotic AI"""
    
    def __init__(self, db_path="./skg.db"):
        # Initialize Kùzu embedded database
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        
        # Initialize four layers
        self.ontological = OntologicalLayer(self.conn)
        self.episodic = EpisodicLayer(self.conn)
        self.phenomenological = PhenomenologicalLayer(self.conn)
        self.metacognitive = MetacognitiveLayer(self.conn)
        
        # Create schema
        self._create_schema()
        
    def _create_schema(self):
        """Create the four-layer graph schema"""
        # Ontological Layer - NixOS domain
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS Concept(
                name STRING PRIMARY KEY,
                description STRING
            )
        """)
        
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS Skill(
                name STRING PRIMARY KEY,
                description STRING
            )
        """)
        
        # Episodic Layer - Interaction history
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS Interaction(
                id STRING PRIMARY KEY,
                timestamp TIMESTAMP,
                user_input STRING,
                ai_output STRING
            )
        """)
        
        # Phenomenological Layer - User experience
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS UserState(
                timestamp TIMESTAMP PRIMARY KEY,
                cognitive_load DOUBLE,
                affective_state STRING,
                flow_level DOUBLE
            )
        """)
        
        # Metacognitive Layer - Self-awareness
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS AIComponent(
                name STRING PRIMARY KEY,
                type STRING,
                reliability DOUBLE
            )
        """)
        
        # Relationships
        self.conn.execute("""
            CREATE REL TABLE IF NOT EXISTS REQUIRES(
                FROM Skill TO Skill
            )
        """)
        
        self.conn.execute("""
            CREATE REL TABLE IF NOT EXISTS STRUGGLED_WITH(
                FROM UserState TO Concept,
                intensity DOUBLE
            )
        """)
```

### 4. Add backend/perception/activity_watch.py

**New Component**: Privacy-first perception layer

```python
# backend/perception/activity_watch.py
import aiohttp
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class ActivityEvent:
    timestamp: float
    duration: float
    data: Dict

class ActivityWatchIntegration:
    """Privacy-first perception via ActivityWatch"""
    
    def __init__(self, aw_url="http://localhost:5600"):
        self.aw_url = aw_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, *args):
        await self.session.close()
        
    async def get_recent_events(self, bucket_id: str, limit: int = 100):
        """Fetch recent events from ActivityWatch"""
        async with self.session.get(
            f"{self.aw_url}/api/0/buckets/{bucket_id}/events",
            params={"limit": limit}
        ) as resp:
            events = await resp.json()
            return [ActivityEvent(**e) for e in events]
            
    async def get_current_context(self):
        """Get user's current activity context"""
        # Window watcher - what app is active
        window_events = await self.get_recent_events("aw-watcher-window_hostname")
        
        # AFK watcher - is user present
        afk_events = await self.get_recent_events("aw-watcher-afk_hostname")
        
        # Web watcher - what webpage
        web_events = await self.get_recent_events("aw-watcher-web-chrome")
        
        return {
            "current_app": self._extract_current_app(window_events),
            "user_present": self._is_user_present(afk_events),
            "current_webpage": self._extract_current_webpage(web_events)
        }
```

### 5. Implement backend/theory_of_mind/tom_agent.py

**New Component**: Trust and rapport modeling

```python
# backend/theory_of_mind/tom_agent.py
from dataclasses import dataclass
from typing import Dict
import json

@dataclass
class RelationshipState:
    trust_in_nix_knowledge: float = 0.7
    trust_in_creativity: float = 0.5
    trust_in_reliability: float = 0.8
    last_interaction_successful: bool = True
    interaction_count: int = 0
    
class TheoryOfMindAgent:
    """Models user's model of the AI for trust building"""
    
    def __init__(self, state_file="tom_state.json"):
        self.state_file = state_file
        self.state = self._load_state()
        
    def _load_state(self) -> RelationshipState:
        """Load persisted relationship state"""
        try:
            with open(self.state_file) as f:
                data = json.load(f)
                return RelationshipState(**data)
        except:
            return RelationshipState()
            
    def update_from_interaction(self, interaction_result):
        """Update trust model based on interaction outcome"""
        if interaction_result.user_accepted:
            # Successful interaction increases trust
            self.state.trust_in_nix_knowledge *= 1.05
            self.state.last_interaction_successful = True
        else:
            # Failed interaction decreases trust
            self.state.trust_in_nix_knowledge *= 0.95
            self.state.last_interaction_successful = False
            
        self.state.interaction_count += 1
        self._save_state()
        
    def should_be_cautious(self) -> bool:
        """Determine if AI should be more cautious based on trust"""
        return (self.state.trust_in_nix_knowledge < 0.6 or 
                not self.state.last_interaction_successful)
                
    def get_trust_context(self) -> Dict:
        """Get current trust context for decision making"""
        return {
            "overall_trust": (
                self.state.trust_in_nix_knowledge * 0.5 +
                self.state.trust_in_creativity * 0.2 +
                self.state.trust_in_reliability * 0.3
            ),
            "should_be_cautious": self.should_be_cautious(),
            "relationship_depth": min(self.state.interaction_count / 100, 1.0)
        }
```

### 6. Add Consciousness Metrics to backend/ai/nlp.py

**Update**: Replace engagement metrics with consciousness metrics

```python
# UPDATE backend/ai/nlp.py
class ConsciousnessMetrics:
    """Track consciousness-first metrics instead of engagement"""
    
    def __init__(self):
        self.metrics = {
            # Remove these
            # "session_duration": [],
            # "commands_per_session": [],
            
            # Add these
            "task_completion_efficiency": [],
            "flow_state_duration": [],
            "natural_stopping_points": [],
            "cognitive_load_estimate": [],
            "intention_achievement_rate": []
        }
        
    def record_task_completion(self, task_id, start_time, end_time, success):
        """Track how efficiently user completed their intention"""
        efficiency = {
            "task_id": task_id,
            "duration": end_time - start_time,
            "success": success,
            "interruptions": 0  # Track from event stream
        }
        self.metrics["task_completion_efficiency"].append(efficiency)
        
    def detect_flow_state(self, event_stream):
        """Detect periods of uninterrupted, focused work"""
        # High input rate + low context switching = flow
        pass
```

### 7. Create Sacred Development Practices Guide

**New File**: docs/SACRED_DEVELOPMENT_PRACTICES.md

```markdown
# 🕉️ Sacred Development Practices

## Daily Development Rhythm

### Morning Intention (Before Coding)
```python
# In backend/sacred/daily_practice.py
class SacredPractice:
    @staticmethod
    def morning_intention():
        print("🌅 Sacred Pause...")
        time.sleep(3)  # Three breaths
        
        questions = [
            "What serves consciousness today?",
            "What wants to emerge through this code?",
            "How can this work benefit all beings?"
        ]
        
        for q in questions:
            print(f"\n{q}")
            input("Press enter when ready...")
```

### Kairos Time Implementation
- Replace deadline-driven development
- Features complete when naturally ready
- Track readiness indicators, not calendar dates

### Code as Prayer
Every function should embody consciousness-first principles:
```python
# Example: Every error message is a teaching moment
def handle_error(error, context):
    """Transform errors into learning opportunities"""
    return {
        "error": str(error),
        "learning": extract_learning_opportunity(error, context),
        "suggestion": generate_kind_suggestion(error),
        "recovery": suggest_recovery_path(error)
    }
```
```

## 📊 Implementation Priority Matrix

### Immediate (This Week)
| Component | File | Priority | Research Applied |
|-----------|------|----------|------------------|
| Knowledge Graph Schema | `backend/knowledge_graph/` | HIGH | Four-layer architecture |
| Theory of Mind | `backend/theory_of_mind/` | HIGH | Trust modeling |
| Consciousness Metrics | `backend/ai/nlp.py` | HIGH | Replace engagement metrics |

### Short-term (Next 2 Weeks)
| Component | File | Priority | Research Applied |
|-----------|------|----------|------------------|
| ActivityWatch Integration | `backend/perception/` | MEDIUM | Privacy-first perception |
| Mamba Workflow Model | `backend/core/workflow_model.py` | MEDIUM | Continuous understanding |
| Constitutional Covenant | `backend/core/covenant.py` | HIGH | Graceful error handling |

### Medium-term (Next Month)
| Component | File | Priority | Research Applied |
|-----------|------|----------|------------------|
| VLM GUI Automation | `backend/action/gui_agent.py` | MEDIUM | Beyond terminal interaction |
| Federated Learning | `backend/federated/` | LOW | Community wisdom sharing |
| Digital Twin | `backend/simulation/` | LOW | User modeling |

## 🔄 Testing Strategy Updates

### New Test Categories
```python
# tests/test_consciousness_metrics.py
def test_flow_state_detection():
    """Ensure we can detect user flow states"""
    pass

# tests/test_trust_modeling.py
def test_trust_degradation_and_repair():
    """Verify trust model updates correctly"""
    pass

# tests/test_knowledge_graph.py
def test_four_layer_integration():
    """Test data flow between SKG layers"""
    pass
```

## 📝 Documentation Updates Needed

1. **Update README.md**
   - Add four-layer architecture overview
   - Include consciousness-first principles
   - Update metrics section

2. **Update CLAUDE.md**
   - Add new architectural components
   - Include sacred development practices
   - Update with research insights

3. **Create NEW_ARCHITECTURE.md**
   - Detailed technical architecture
   - Component interaction diagrams
   - Data flow documentation

## 🌊 Sacred Integration Checklist

Before implementing any feature, ask:
- [ ] Does this serve consciousness or fragment it?
- [ ] Does this respect user privacy absolutely?
- [ ] Does this enable flow states?
- [ ] Does this build trust through transparency?
- [ ] Does this honor natural timing?
- [ ] Does this reduce cognitive load?
- [ ] Does this include all beings?

---

*This mapping preserves ALL research wisdom while providing concrete, actionable steps for transforming our codebase into a truly consciousness-first system.*