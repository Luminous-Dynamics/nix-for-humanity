# System Architecture - Nix for Humanity

*One brain, many faces: The technical blueprint for symbiotic human-AI partnership*

## Overview

Nix for Humanity implements a headless architecture where one intelligent Python backend serves multiple frontend interfaces. This enables natural language NixOS interaction through CLI, TUI, voice, or API - all powered by the same AI brain.

```
┌─────────────────────────────────┐          ┌─────────────────────────────────┐
│      Frontend Interfaces        │    ←→    │       Headless Core Engine      │
├─────────────────────────────────┤          ├─────────────────────────────────┤
│ • CLI (ask-nix)                 │          │ • NLP Engine (hybrid)           │
│ • TUI (Textual)                 │          │ • Intent Recognition            │
│ • Voice (pipecat)               │          │ • Command Execution             │
│ • API (REST)                    │          │ • Learning System               │
└─────────────────────────────────┘          │ • Knowledge Graph (SKG)         │
            ↕ JSON-RPC                       │ • Trust Engine                  │
┌─────────────────────────────────┐          │ • Metrics Collector             │
│    NixOS Integration Layer      │          └─────────────────────────────────┘
├─────────────────────────────────┤                         ↕
│ • Native Python API (25.11+)    │          ┌─────────────────────────────────┐
│ • Subprocess fallback           │          │        Data Storage             │
│ • Safe execution sandbox        │          ├─────────────────────────────────┤
└─────────────────────────────────┘          │ • SQLite (current)              │
                                             │ • LanceDB (vectors - planned)   │
                                             │ • DuckDB (analytics - future)   │
                                             └─────────────────────────────────┘
```

## Core Components

### 1. Natural Language Processing (NLP) Engine

**Hybrid approach for optimal performance:**
- **Rule-based**: Fast pattern matching for common commands
- **Statistical**: Fuzzy matching and typo correction
- **Neural**: Deep understanding for complex queries

```python
# Example: Intent recognition flow
user_input = "install firefox"
→ Tokenize & normalize
→ Check rule patterns (instant)
→ Fuzzy match if needed (fast)
→ Neural fallback for complex (slower)
→ Intent(type=INSTALL, package="firefox", confidence=0.95)
```

### 2. Command Execution & Safety

**Multi-layer security architecture:**
1. Input validation (prevent injection)
2. Intent verification (confirm understanding)
3. Permission checking (sudo only when needed)
4. Sandboxed execution (limited scope)
5. Rollback capability (undo on failure)

### 3. Knowledge Systems

**Symbiotic Knowledge Graph (SKG):**
- **Ontological Layer**: NixOS concepts and relationships
- **Episodic Layer**: User interaction history
- **Phenomenological Layer**: User states and preferences
- **Metacognitive Layer**: System self-awareness

**Current Implementation**: SQLite with 5 core tables
**Future Enhancement**: LanceDB for vector search + DuckDB for analytics

### 4. Learning & Adaptation

**Four-dimensional learning:**
- **WHO**: User modeling (preferences, skill level)
- **WHAT**: Command patterns and success rates
- **HOW**: Preferred interaction styles
- **WHEN**: Timing and context awareness

### 5. Multi-Modal Interfaces

All interfaces share the same backend intelligence:

**CLI (`ask-nix`)**: Terminal command-line tool
**TUI (Textual)**: Rich terminal UI with panels
**Voice (pipecat)**: Speech-to-text and text-to-speech
**API (REST)**: For third-party integrations

## Request Flow

```
1. User Input → "install firefox"
   ↓
2. Frontend → Validates & forwards to backend
   ↓
3. NLP → Extracts intent & entities
   ↓
4. Validator → Checks safety & permissions
   ↓
5. Executor → Runs Nix commands
   ↓
6. Monitor → Tracks progress & results
   ↓
7. Learning → Updates patterns & preferences
   ↓
8. Response → Natural language + command result
```

## Performance Architecture

### Current State
- Response time: 2-5 seconds (subprocess overhead)
- Memory usage: 200-400MB
- CPU usage: Minimal except during NLP

### Target with Native Python-Nix API
- Response time: <0.1 seconds for most operations
- Memory usage: <300MB with all features
- CPU usage: Negligible for common tasks

### Performance Optimizations
1. **Caching**: Package metadata, common queries
2. **Lazy Loading**: Neural models only when needed
3. **Native API**: Direct Python-Nix integration (10x-1500x faster)
4. **Progressive Enhancement**: Start fast, add intelligence as needed

## Security & Privacy

### Local-First Principles
- All processing happens on user's machine
- No cloud dependencies or data uploads
- User owns and controls all data
- Learning data never leaves the system

### Security Boundaries
```
User Space          Privileged Space
┌─────────┐         ┌──────────────┐
│   NLP   │   →     │  Validation  │
│ Engine  │         │    Layer     │
└─────────┘         └──────┬───────┘
                            ↓
┌─────────┐         ┌──────────────┐
│ Learning│         │   Sandbox    │
│ System  │   ←     │  Execution   │
└─────────┘         └──────────────┘
```

## Data Architecture

### Current (SQLite)
- Simple, reliable, single-file database
- Good for: Structured data, relationships
- Limited for: Vector search, analytics

### Planned Enhancement (Hybrid)
```python
class HybridDataLayer:
    def __init__(self):
        self.graph = SQLite()      # Relationships
        self.vectors = LanceDB()   # Semantic search
        self.analytics = DuckDB()  # Pattern analysis
```

## Development Patterns

### Sacred Trinity Model
- **Human**: Vision, user empathy, validation
- **Claude Code Max**: Architecture, implementation
- **Local LLM**: NixOS expertise, best practices

### Code Organization
```
backend/
├── core/           # Shared logic
├── nlp/            # Language processing
├── execution/      # Command runners
├── learning/       # AI components
└── api/            # Frontend interfaces

frontends/
├── cli/            # Terminal interface
├── tui/            # Textual UI
├── voice/          # Speech interface
└── web/            # REST API
```

## Extensibility

### Plugin Architecture (Future)
```python
class NixHumanityPlugin:
    def on_intent(self, intent: Intent) -> Optional[Response]:
        """Handle custom intents"""
        
    def on_learn(self, interaction: Interaction) -> None:
        """Learn from interactions"""
```

### Custom Personas
Users can define their own interaction styles beyond the default 10 personas.

## Deployment

### Development
```bash
nix develop         # Enter dev environment
pytest             # Run tests
./bin/ask-nix      # Test CLI
```

### Production (Future)
```nix
services.nixForHumantiy = {
  enable = true;
  voiceEnabled = true;
  learningEnabled = true;
};
```

## Next Steps

### Immediate Priorities
1. **Native Python-Nix API**: Eliminate subprocess overhead
2. **Fix Basic Commands**: 100% reliability for install/remove/update
3. **Connect TUI**: Wire up the Textual interface

### Medium Term
1. **Vector Search**: Add LanceDB for semantic queries
2. **Voice Interface**: Complete pipecat integration
3. **Learning Loop**: Implement basic RLHF

### Long Term
1. **Federated Learning**: Privacy-preserving collective intelligence
2. **Multi-Modal**: Seamless switching between interfaces
3. **Invisible Excellence**: Technology that disappears through perfection

---

*This architecture enables genuine human-AI partnership while keeping everything local, private, and lightning fast.*