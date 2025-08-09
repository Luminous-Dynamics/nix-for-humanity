# Architecture - Nix for Humanity v1.0

Simple, focused architecture for two hero capabilities.

## Overview

```
User Input → Intent Recognition → Native Nix API → Learning Loop → Response
```

## Core Components

### 1. CLI Interface (`bin/ask-nix`)
- Accepts natural language input
- Routes to backend
- Displays responses

### 2. Intent Recognition (`backend/core/nlp.py`)
- Pattern matching for common commands
- ~70% accuracy currently
- Target: 95% for top 20 commands

### 3. Native Nix API (`backend/core/executor.py`)
- Direct Python integration with nixos-rebuild
- Eliminates subprocess timeouts
- Target: <0.5s for all operations

### 4. Learning Loop (`backend/core/learning.py`)
- Tracks command patterns
- Builds user profile
- Suggests based on history

## Data Flow

```python
# 1. User types command
"install firefox"

# 2. Intent recognition
Intent(action="install", package="firefox", confidence=0.92)

# 3. Native API execution
nix_api.install_package("firefox")  # <0.5s

# 4. Learning system
learning.record_success("install", "firefox", context)
learning.update_suggestions()

# 5. Response with learning
"✓ Installed firefox
💡 You often install browsers. Try 'brave' or 'chromium'?"
```

## File Structure (Simplified)

```
nix-for-humanity/
├── bin/
│   └── ask-nix          # CLI entry point
├── backend/
│   └── core/
│       ├── nlp.py       # Intent recognition
│       ├── executor.py  # Native Nix API
│       └── learning.py  # Pattern learning
├── data/
│   └── learning.db      # SQLite for patterns
└── tests/
    └── integration/     # Real command tests
```

## Key Design Decisions

### Why Native Python-Nix API?
- Subprocess calls timeout (2+ minutes for rebuilds)
- Python API gives real-time progress
- 10x-100x performance improvement
- Better error handling

### Why Simple Learning?
- No complex AI models needed
- Pattern matching is sufficient
- Fast and predictable
- Privacy-preserving (all local)

### Why SQLite?
- Simple and reliable
- No external dependencies
- Good enough for v1.0
- Easy to backup/migrate

## Performance Targets

| Operation | Current | v1.0 Target |
|-----------|---------|-------------|
| Install package | 5-10s | <0.5s |
| Search packages | 2-5s | <0.2s |
| System update | Times out | <5s with progress |
| Intent recognition | 100ms | 50ms |
| Learning update | N/A | <10ms |

## Security Model

1. **Input Validation**: Sanitize all user input
2. **Command Verification**: Confirm before system changes
3. **No Shell Execution**: Direct API calls only
4. **Local Only**: No network requests
5. **User Consent**: Explicit approval for operations

## Error Handling

```python
try:
    result = nix_api.install(package)
except NixError as e:
    # Transform cryptic error
    user_message = explain_error(e)
    suggestion = suggest_fix(e)
    return f"❌ {user_message}\n💡 Try: {suggestion}"
```

## Future Architecture (Post-v1.0)

### v1.1 Additions
- TUI Interface (Textual)
- Advanced pattern recognition
- Command chaining

### v2.0 Vision
- Voice interface
- Plugin system
- Community features

## Development Principles

1. **Simplicity First**: No premature optimization
2. **User Feedback**: Learn from real usage
3. **Incremental**: Ship working features early
4. **Testable**: Integration tests for everything
5. **Maintainable**: Clear code over clever code

---

This architecture prioritizes delivering two features exceptionally well rather than building a complex system that does many things poorly.