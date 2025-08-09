
# Backend Consolidation Plan

## 1. Unified Structure
```
src/nix_humanity/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── executor.py      # Single executor implementation
│   ├── nlp.py          # NLP engine
│   ├── intents.py      # Intent definitions
│   └── errors.py       # Error handling
├── native/
│   ├── __init__.py
│   ├── api.py          # Native Nix API
│   ├── operations.py   # Native operations
│   └── fallback.py     # Subprocess fallback
├── learning/
│   ├── __init__.py
│   ├── patterns.py     # Pattern recognition
│   ├── storage.py      # Learning storage
│   └── feedback.py     # User feedback processing
├── interfaces/
│   ├── __init__.py
│   ├── cli.py          # CLI interface
│   ├── tui.py          # TUI interface
│   └── voice.py        # Voice interface
└── config/
    ├── __init__.py
    ├── settings.py     # User settings
    └── personas.py     # Persona definitions
```

## 2. Key Consolidations

### Executor (HIGHEST PRIORITY)
- Merge `backend/core/executor.py` and `nix_humanity/core/executor.py`
- Keep the best error handling from both
- Use dependency injection for backends

### NLP Engine
- Consolidate intent parsing logic
- Merge pattern matching approaches
- Unified confidence scoring

### Native API
- Single implementation of Python-Nix integration
- Clear fallback strategy
- Performance monitoring built-in

## 3. Migration Steps

1. **Create unified structure** in `src/nix_humanity/`
2. **Copy best implementations** from each duplicate
3. **Update all imports** to use new structure
4. **Remove old implementations** after testing
5. **Update tests** to use new structure

## 4. Code Example

```python
# src/nix_humanity/core/executor.py
from typing import Protocol
from ..native.api import NativeAPI
from ..native.fallback import SubprocessFallback

class ExecutionBackend(Protocol):
    async def execute(self, command: Command) -> Result:
        ...

class UnifiedExecutor:
    def __init__(self, prefer_native: bool = True):
        self.backend = self._select_backend(prefer_native)
    
    def _select_backend(self, prefer_native: bool) -> ExecutionBackend:
        if prefer_native and NativeAPI.is_available():
            return NativeAPI()
        return SubprocessFallback()
    
    async def execute(self, intent: Intent) -> Result:
        command = self.build_command(intent)
        return await self.backend.execute(command)
```
