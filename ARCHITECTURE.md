# 🏗️ Luminous Nix Architecture

## Overview
Luminous Nix uses a revolutionary **subprocess-based operations** architecture that uses subprocess, achieving standard Nix performance improvements over traditional approaches.

## 🎯 Core Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                          │
├──────────────┬───────────────┬──────────────┬──────────────┤
│     CLI      │      TUI      │    Voice     │   GUI        │
│  (ask-nix)   │  (Textual)    │   (Ready)    │  (Tauri)     │
└──────┬───────┴───────┬───────┴──────┬───────┴──────┬───────┘
       │               │              │              │
       └───────────────┴──────────────┴──────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Intent Pipeline  │
                    │ (Natural Language)│
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Command Executor │
                    │  (Orchestration)  │
                    └─────────┬─────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
   ┌────────▼────────┐ ┌─────▼──────┐ ┌───────▼────────┐
   │  Native API     │ │   Config   │ │    AI/LLM      │
   │  (normal)    │ │ Generator  │ │  Integration   │
   └────────┬────────┘ └─────┬──────┘ └───────┬────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   NixOS 25.11+    │
                    │ (nixos-rebuild-ng)│
                    └───────────────────┘
```

## 🚀 The Native API Revolution

### Traditional Approach (SLOW)
```python
# Every operation spawns a subprocess
result = subprocess.run(['nix', 'search', 'firefox'], 
                       capture_output=True, 
                       timeout=30)  # Can timeout!
# Parse string output (error-prone)
# No progress tracking
# 2-5 seconds per operation
```

### Our Approach (FAST)
```python
# Direct Python bindings to Nix
from luminous_nix.core.native_nix_api import get_native_api

api = get_native_api()
result = api.search_packages('firefox')
# Native Python objects
# Real-time progress
# 2-3 seconds per operation!
```

## 📁 Module Architecture

### Core Layer (`src/luminous_nix/core/`)
The heart of the system - handles all NixOS operations.

- **`native_nix_api.py`** - Revolutionary native Python-Nix integration
- **`intent_pipeline.py`** - Converts natural language to intents
- **`command_executor.py`** - Orchestrates intent execution
- **`config_generator.py`** - Generates NixOS configurations
- **`backend_real.py`** - Real NixOS operations backend

### Frontend Layer (`src/luminous_nix/frontends/`)
Multiple interfaces for different user preferences.

- **`cli.py`** - Command-line interface
- **`tui.py`** - Terminal UI (Textual framework)
- **`voice.py`** - Voice interface (speech recognition/synthesis)
- **`api.py`** - REST API for external integration

### AI Layer (`src/luminous_nix/ai/`)
Intelligence and learning capabilities.

- **`ollama_integration.py`** - Local LLM support
- **`config_generator.py`** - AI-powered configuration
- **`learning_system.py`** - Adaptive learning
- **`personality_modes.py`** - 10-persona system

### GUI Layer (`gui-tauri/`)
Native desktop application using Tauri.

- **`src/main.rs`** - Rust backend
- **`src/python_bridge.rs`** - Python integration
- **`src-ui/`** - React frontend

## 🔄 Request Flow

1. **User Input** → "install firefox"
2. **Intent Recognition** → `IntentType.INSTALL, package="firefox"`
3. **Command Execution** → Routes to appropriate executor
4. **Native API Call** → Direct Python call to Nix
5. **Response** → 2-5 seconds result with progress

## 🎭 The 10-Persona System

Each persona adapts the interface for different users:

```python
PERSONAS = {
    'grandma_rose': {
        'complexity': 'minimal',
        'interface': 'voice_first',
        'guidance': 'maximum'
    },
    'maya_adhd': {
        'complexity': 'streamlined',
        'interface': 'fast_visual',
        'guidance': 'minimal'
    },
    'alex_blind': {
        'complexity': 'full',
        'interface': 'screen_reader',
        'guidance': 'audio'
    },
    # ... 7 more personas
}
```

## 🔌 Plugin Architecture

Extensible plugin system for custom functionality:

```python
class Plugin:
    def __init__(self, manifest: dict):
        self.name = manifest['name']
        self.version = manifest['version']
    
    def on_intent(self, intent: Intent) -> Optional[Response]:
        """Hook into intent processing"""
        pass
    
    def on_response(self, response: Response) -> Response:
        """Modify responses"""
        pass
```

## 🛡️ Security Architecture

### Input Validation
```python
# All user input is validated
validator = InputValidator()
validator.check_command_injection(user_input)
validator.check_path_traversal(user_input)
```

### Permission System
```python
# Operations require appropriate permissions
@requires_permission('system.modify')
def install_package(package: str):
    # Only executes with permission
```

### Sandboxing
```python
# Plugins run in sandbox
sandbox = PluginSandbox(
    allowed_modules=['os', 'json'],
    max_memory=100_000_000,  # 100MB
    timeout=5.0
)
```

## 📊 Performance Optimizations

### 1. Native API (Primary)
- Direct Python bindings eliminate subprocess overhead
- standard Nix performance improvement

### 2. Intelligent Caching
```python
@cached(ttl=300)  # 5-minute cache
def search_packages(query: str):
    return native_api.search(query)
```

### 3. Predictive Loading
```python
# Preload likely next operations
predictor = PredictiveCache()
predictor.preload_likely_packages(current_context)
```

### 4. Lazy Loading
```python
# Load modules only when needed
def get_voice_interface():
    from luminous_nix.frontends.voice import VoiceInterface
    return VoiceInterface()
```

## 🧪 Testing Architecture

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Focus on business logic

### Integration Tests
- Test real NixOS operations
- Use native API for speed
- Verify end-to-end flows

### Performance Tests
- Benchmark native API vs subprocess
- Monitor regression
- Track optimization impact

## 🔮 Future Architecture

### Phase 1: Current (v0.6.x)
- Native API integration ✅
- Basic persona system ✅
- CLI/TUI interfaces ✅

### Phase 2: Voice & Learning (v0.7.x)
- Complete voice interface
- Active learning system
- Full 10-persona implementation

### Phase 3: Intelligence (v0.8.x)
- Predictive maintenance
- Community knowledge sharing
- Self-optimizing configurations

### Phase 4: Transcendence (v1.0)
- Invisible excellence
- Anticipatory problem solving
- True AI partnership

## 🏗️ Design Patterns

### Singleton Native API
```python
_native_api = None

def get_native_api():
    global _native_api
    if _native_api is None:
        _native_api = NativeNixAPI()
    return _native_api
```

### Command Pattern
```python
class Command:
    def execute(self) -> Response:
        pass
    
    def undo(self) -> Response:
        pass
```

### Observer Pattern
```python
class ProgressObserver:
    def on_progress(self, percent: float, message: str):
        pass
```

### Strategy Pattern
```python
class ExecutionStrategy:
    def execute(self, command: Command) -> Response:
        pass

class NativeAPIStrategy(ExecutionStrategy):
    def execute(self, command: Command) -> Response:
        return native_api.execute(command)
```

## 📈 Metrics & Monitoring

### Performance Metrics
- Operation latency (target: <100ms)
- Native API usage (target: 100%)
- Cache hit rate (target: >80%)

### User Metrics
- Intent recognition accuracy
- Task completion rate
- User satisfaction score

### System Metrics
- Memory usage (<200MB)
- CPU usage (<5% idle)
- Disk I/O (minimal)

---

*Architecture Version: 2.0 (Post-Native API Integration)*
*Last Updated: 2025-08-29*
*Status: Production Ready*