# 🎯 Technical Decisions Based on Research

*Concrete architectural choices derived from our research findings*

## Core Architecture Decision

**Decision**: Build Nix for Humanity as a **Unified Python Backend** with **Pluggable Frontend Adapters**

**Rationale**:
- Leverages NixOS 25.11's Python-first approach
- Enables deep system integration via nixos-rebuild-ng
- Supports multiple interaction modalities
- Maintains single source of truth for business logic

## Detailed Technical Decisions

### 1. Backend Language & Framework

**Decision**: Python 3.11+ with asyncio

**Implementation**:
```python
# Core backend structure
class NixForHumanityBackend:
    def __init__(self):
        self.nix_api = NixOSPythonAPI()  # Direct nixos-rebuild-ng
        self.ai_engine = MultiModelAI()   # Specialized models
        self.knowledge = KnowledgeBase()  # SQLite + LanceDB
        self.learner = PreferenceLearner()  # DPO/LoRA
```

**Rationale**:
- Native integration with nixos-rebuild-ng
- Rich AI/ML ecosystem
- Excellent async support
- NixOS standard for system tools

### 2. AI Model Architecture

**Decision**: Multi-Model Pyramid, Not Monolithic LLM

**Implementation Stack**:
```yaml
Speech Layer:
  STT: Whisper (whisper.cpp)
  TTS: Piper
  Fallback: Vosk + eSpeak-NG

NLP Layer:
  Intent: SentenceTransformers
  NER: spaCy
  Preprocessing: NLTK
  Syntax: Tree-sitter

ML Layer:
  Patterns: Scikit-learn
  Embeddings: sentence-transformers
  Future: Local GGUF via llama.cpp
```

**Rationale**:
- 10-100x faster than LLMs for specific tasks
- Runs on modest hardware
- Fully local and private
- Explainable results

### 3. Data Architecture

**Decision**: Tiered Storage Strategy

**Implementation**:
```python
# Tier 1: Hot data (Redis/In-memory)
cache = {
    "recent_commands": LRUCache(1000),
    "active_sessions": {},
    "intent_cache": TTLCache(300)  # 5 min
}

# Tier 2: Warm data (SQLite)
knowledge_db = SQLiteDB("nix_knowledge.db")
user_prefs = SQLiteDB("preferences.db")

# Tier 3: Embeddings (LanceDB)
vector_store = lancedb.connect("./nix_vectors")
```

**Rationale**:
- Instant responses for common queries
- Rich relational queries for knowledge
- Semantic search via embeddings
- All data remains local

### 4. Frontend Architecture

**Decision**: Thin Adapters, Not Fat Clients

**Implementation Pattern**:
```python
# Each frontend is ~200 lines
class CLIAdapter:
    def __init__(self, backend: NixForHumanityBackend):
        self.backend = backend
    
    async def run(self, args):
        # Parse CLI args
        # Call backend
        # Format output
        
class TUIAdapter:
    def __init__(self, backend: NixForHumanityBackend):
        self.backend = backend
        self.app = TextualApp()
```

**Rationale**:
- Consistent behavior across interfaces
- Easy to add new frontends
- Centralized business logic
- Simplified testing

### 5. Communication Protocol

**Decision**: Structured Internal API

**Schema**:
```python
@dataclass
class Request:
    text: str
    context: Dict[str, Any]
    frontend: Literal["cli", "tui", "voice", "api"]
    session_id: str
    
@dataclass
class Response:
    intent: Intent
    explanation: str
    commands: List[Command]
    confidence: float
    suggestions: List[str]
```

**Rationale**:
- Type safety with dataclasses
- Clear contracts between layers
- Easy to extend
- Self-documenting

### 6. Learning System

**Decision**: Local-First Preference Learning

**Implementation**:
```python
class PreferenceLearner:
    def __init__(self):
        self.feedback_db = SQLiteDB("feedback.db")
        self.model = None  # Lazy load
    
    async def learn_from_interaction(
        self,
        request: Request,
        response: Response,
        feedback: Feedback
    ):
        # Store locally
        await self.feedback_db.store(request, response, feedback)
        
        # Update model if enough data
        if self.should_retrain():
            self.model = self.train_local_adapter()
```

**Rationale**:
- Privacy preserved
- No cloud dependencies
- Learns user preferences
- Can share anonymized patterns

### 7. Execution Strategy

**Decision**: Staged Execution with Rollback

**Implementation**:
```python
class SafeExecutor:
    async def execute(self, commands: List[Command]):
        # Stage 1: Validate
        validation = await self.validate_all(commands)
        if not validation.safe:
            return validation.errors
            
        # Stage 2: Snapshot
        snapshot = await self.create_snapshot()
        
        # Stage 3: Execute
        try:
            results = []
            for cmd in commands:
                result = await self.execute_with_timeout(cmd)
                results.append(result)
                if result.failed:
                    await self.rollback(snapshot)
                    break
            return results
            
        except Exception as e:
            await self.rollback(snapshot)
            raise
```

**Rationale**:
- Safety first
- Always recoverable
- Clear error attribution
- User confidence

### 8. Configuration Management

**Decision**: Managed Nix Generation

**Approach**:
```python
class NixConfigGenerator:
    def generate_config(self, spec: ConfigSpec) -> str:
        """Generate Nix config from high-level spec"""
        template = self.get_template(spec.type)
        config = self.render_template(template, spec)
        return self.validate_nix_syntax(config)
```

**Not This**:
- Direct file editing
- String manipulation
- Regex-based updates

**Rationale**:
- Syntax-safe by construction
- Rollback-friendly
- Composable configurations
- Version control friendly

### 9. Performance Optimization

**Decision**: Lazy Loading + Predictive Caching

**Implementation**:
```python
class OptimizedBackend:
    def __init__(self):
        self._models = {}  # Lazy load
        self._cache = PredictiveCache()
    
    @property
    def whisper(self):
        if 'whisper' not in self._models:
            self._models['whisper'] = load_whisper()
        return self._models['whisper']
    
    async def process(self, request):
        # Check cache first
        if cached := self._cache.get(request):
            return cached
            
        # Predict next likely request
        self._cache.preload(self.predict_next(request))
```

**Rationale**:
- Fast startup
- Low memory baseline
- Instant common operations
- Scales with usage

### 10. Error Handling

**Decision**: Educational Error Messages

**Example**:
```python
class EducationalError(Exception):
    def __init__(self, message: str, suggestion: str, learn_more: str):
        self.message = message
        self.suggestion = suggestion
        self.learn_more = learn_more
        
    def format_for_user(self, frontend: str) -> str:
        if frontend == "cli":
            return f"""
❌ {self.message}

💡 Suggestion: {self.suggestion}

📚 Learn more: {self.learn_more}
"""
```

**Rationale**:
- Errors as learning opportunities
- Reduce user frustration
- Build NixOS knowledge
- Encourage exploration

## Technical Principles

Based on research, we adopt these principles:

1. **Local-First**: Everything runs on user's machine
2. **Privacy-Preserving**: No data leaves system
3. **Fail-Safe**: Always have rollback path
4. **Progressive**: Start simple, enhance over time
5. **Explainable**: User understands what happens
6. **Efficient**: Optimize for common cases
7. **Extensible**: Easy to add capabilities
8. **Accessible**: Works for all users

## Anti-Patterns to Avoid

Based on research, we explicitly avoid:

❌ **Monolithic LLM dependency**
❌ **Cloud-required features**
❌ **Subprocess command chains**
❌ **String-based config manipulation**
❌ **Fat client architectures**
❌ **Synchronous blocking operations**
❌ **Opaque ML decisions**
❌ **English-only interfaces**

## Migration Path

For existing codebase:

1. **Week 1**: Refactor to unified backend
2. **Week 2**: Migrate frontends to adapters
3. **Week 3**: Integrate AI models
4. **Week 4**: Add learning system

---

*"Good architecture is not about making the right decision, but making decisions that are easy to change."*