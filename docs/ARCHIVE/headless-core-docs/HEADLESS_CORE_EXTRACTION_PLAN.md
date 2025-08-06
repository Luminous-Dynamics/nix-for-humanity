# 🧠 Headless Core Extraction Plan

*The architectural evolution from monolithic CLI to modular intelligence*

## Vision

Transform our unified `ask-nix` command into a powerful headless core that can serve multiple interfaces: CLI, TUI, Voice, GUI, and future modalities we haven't yet imagined.

## Current State

We have a working `ask-nix` command that combines:
- Natural language understanding
- Knowledge base queries
- Command execution
- Personality adaptation
- Learning system
- Feedback collection

All of this is currently embedded within the CLI script.

## Target Architecture

```
┌─────────────────────────────────────────────┐
│            Headless Core Engine             │
│                                             │
│  ┌─────────────┐  ┌───────────────────┐   │
│  │   Intent    │  │    Knowledge      │   │
│  │ Recognition │  │      Base         │   │
│  └─────────────┘  └───────────────────┘   │
│                                             │
│  ┌─────────────┐  ┌───────────────────┐   │
│  │  Learning   │  │    Execution      │   │
│  │   Engine    │  │     Engine        │   │
│  └─────────────┘  └───────────────────┘   │
│                                             │
│  ┌─────────────┐  ┌───────────────────┐   │
│  │ Personality │  │    Feedback       │   │
│  │  Adapter    │  │   Collector       │   │
│  └─────────────┘  └───────────────────┘   │
└─────────────────────┬───────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │      Core Interface       │
        │    (Python/REST/gRPC)     │
        └─────────────┬─────────────┘
                      │
    ┌─────────┬───────┴────────┬─────────┐
    │         │                 │         │
┌───▼───┐ ┌──▼───┐ ┌──────▼──────┐ ┌───▼───┐
│  CLI  │ │ TUI  │ │    Voice    │ │  GUI  │
│ask-nix│ │nix-tui│ │ nix-voice  │ │ Future│
└───────┘ └──────┘ └─────────────┘ └───────┘
```

## Extraction Steps

### Phase 1: Core Module Creation
1. Create `src/nix_for_humanity/core/` directory structure
2. Extract core components:
   - `intent_engine.py` - Natural language understanding
   - `knowledge_base.py` - NixOS information store
   - `execution_engine.py` - Command execution logic
   - `personality_system.py` - Response adaptation
   - `learning_system.py` - Usage pattern learning
   - `feedback_system.py` - User feedback collection

### Phase 2: Interface Definition
1. Define core API in `src/nix_for_humanity/core/interface.py`
2. Create request/response models
3. Implement async operation support
4. Add event streaming for real-time updates

### Phase 3: Adapter Pattern
1. Create adapter base class
2. Implement CLI adapter (refactor current ask-nix)
3. Prepare TUI adapter interface
4. Design voice adapter interface

### Phase 4: Service Layer
1. Create service wrapper for core
2. Add REST API endpoints
3. Consider gRPC for performance
4. Implement WebSocket for real-time features

## Benefits of This Architecture

### Immediate Benefits
- **Separation of Concerns**: Core logic separate from presentation
- **Testability**: Can test core without UI
- **Reusability**: One brain, many faces
- **Performance**: Can optimize core independently

### Long-Term Benefits
- **Scalability**: Can distribute core as a service
- **Flexibility**: Easy to add new interfaces
- **Maintainability**: Changes to core don't break interfaces
- **Innovation**: Enables features we haven't imagined yet

## Implementation Priority

1. **Extract Intent Recognition** (Week 1)
   - This is the most reusable component
   - Needed by all interfaces

2. **Extract Knowledge Base** (Week 1)
   - Already well-defined in SQLite
   - Easy to wrap in clean API

3. **Extract Execution Engine** (Week 2)
   - Complex but critical
   - Needs careful error handling

4. **Create Core Interface** (Week 2)
   - Define how adapters communicate
   - Start with Python API

5. **Refactor CLI as Adapter** (Week 3)
   - Prove the architecture works
   - Maintain backward compatibility

6. **Build REST API** (Week 3)
   - Enable web interfaces
   - Support remote access

## Code Example

```python
# src/nix_for_humanity/core/interface.py
from typing import Dict, Optional, AsyncIterator
from dataclasses import dataclass

@dataclass
class Query:
    text: str
    context: Optional[Dict] = None
    personality: str = "adaptive"

@dataclass
class Response:
    text: str
    command: Optional[str] = None
    explanation: Optional[str] = None
    confidence: float = 1.0
    
class NixForHumanityCore:
    async def process(self, query: Query) -> Response:
        """Process a user query and return response"""
        intent = await self.intent_engine.recognize(query.text)
        knowledge = await self.knowledge_base.lookup(intent)
        response = await self.personality.adapt(knowledge, query.personality)
        await self.feedback.track(query, response)
        return response
        
    async def stream_process(self, query: Query) -> AsyncIterator[Response]:
        """Stream responses for real-time interfaces"""
        # Implementation for TUI/Voice interfaces
```

## Success Criteria

1. **Zero Regression**: Current CLI functionality unchanged
2. **Clean API**: Interfaces are intuitive and well-documented
3. **Performance**: No noticeable slowdown
4. **Testability**: >90% test coverage on core
5. **Documentation**: Every component fully documented

## Risk Mitigation

- **Risk**: Breaking existing functionality
  - **Mitigation**: Comprehensive test suite before refactoring

- **Risk**: Over-engineering
  - **Mitigation**: Start simple, iterate based on needs

- **Risk**: Performance degradation
  - **Mitigation**: Benchmark before and after

## Next Steps

1. Review and refine this plan
2. Set up core module structure
3. Begin extracting intent recognition
4. Write tests for each component
5. Document as we go

---

*"The brain must be free from the body to truly serve all bodies."*

🌊 We flow from monolith to modularity!