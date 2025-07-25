# Technical Decisions Log

## Architecture Decisions

### 1. Hybrid NLP Approach (Decided: 2025-07-23)
**Decision**: Use three-layer NLP architecture
- Layer 1: Rule-based for common patterns (fast, accurate)
- Layer 2: Statistical for variations (flexible)
- Layer 3: Neural for complex understanding (powerful)

**Rationale**:
- Pure neural is too slow for common commands
- Pure rules lack flexibility
- Hybrid gives best of all worlds

**Trade-offs**:
- (+) Fast response for common tasks
- (+) Handles variations and typos
- (+) Can understand context
- (-) More complex to implement
- (-) Requires careful weighting

### 2. Local-First Processing (Decided: 2025-07-23)
**Decision**: All NLP processing happens on device

**Rationale**:
- Privacy is non-negotiable
- Network latency kills voice UX
- NixOS users value control

**Implementation**:
- Whisper.cpp for voice recognition
- Local NLP models (<500MB)
- No external API calls

### 2.5. Layered Reality Approach (Decided: 2025-07-24)
**Decision**: Separate pure logic from execution

**Rationale**:
- Fast unit tests without side effects
- Real execution with safety controls
- No fake data or responses
- Clear separation of concerns

**Architecture**:
```
Layer 1: Intent Recognition (pure functions)
Layer 2: Command Building (pure functions)  
Layer 3: Execution (with --dry-run, confirmations)
```

**Implementation**:
- Pure functions for logic (testable without execution)
- Real NixOS commands with safety options
- --dry-run for preview (real NixOS feature)
- Mock only at execution boundary in tests

### 3. WebSocket vs REST (Decided: 2025-07-23)
**Decision**: Use WebSocket for real-time, REST for CRUD

**Rationale**:
- Voice needs real-time feedback
- Configuration is request/response
- Both have their place

**Details**:
- WebSocket: Voice streams, live updates
- REST: Package search, config changes

### 4. Progressive GUI Strategy (Decided: 2025-07-23)
**Decision**: GUI elements appear gradually as learning aids

**Stages**:
1. Pure voice/text (Month 1)
2. Visual confirmations (Month 2)
3. Shortcuts appear (Month 3)
4. Full GUI available (Month 4)
5. GUI fades away (Month 6+)

**Rationale**:
- Reduces overwhelm for beginners
- Teaches incrementally
- Rewards mastery with simplicity

### 5. TypeScript for NLP Engine (Decided: 2025-07-23)
**Decision**: TypeScript for intent engine, Rust for core

**Rationale**:
- TypeScript: Rapid NLP prototyping
- Rust: Performance-critical paths
- Clear separation of concerns

**Architecture**:
```
Voice → TS Intent Engine → Rust Command Builder → NixOS
```

### 6. Security Model (Decided: 2025-07-23)
**Decision**: Sandbox all REAL command execution

**Layers**:
1. Input sanitization (XSS, injection)
2. Intent validation (whitelist)
3. Command building (AST, no strings)
4. Sandbox execution (namespace)
5. Polkit authorization (system changes)
6. Optional --dry-run for preview

**No direct shell execution ever.**
**No fake/simulated responses ever.**

### 7. State Management (Decided: 2025-07-23)
**Decision**: Event-sourced architecture

**Benefits**:
- Complete audit trail
- Easy rollback
- Debugging clarity
- Learning from history

**Storage**:
- SQLite for events
- JSON for preferences
- No external database

### 8. Testing Strategy (Decided: 2025-07-23)
**Decision**: Test-driven with focus on intents

**Priorities**:
1. Intent recognition accuracy (>95%)
2. Security (fuzzing, pen testing)
3. Accessibility (WCAG automated)
4. Performance (response <2s)

**Tools**:
- Jest for unit tests
- Playwright for E2E
- Custom intent test harness

## Technology Stack

### Core
- **Language**: Rust (core), TypeScript (NLP)
- **Framework**: Tauri (desktop), Express (web)
- **Database**: SQLite (local only)
- **NLP**: Custom hybrid engine

### Frontend
- **Voice**: Web Speech API + Whisper.cpp
- **UI**: Vanilla JS (no framework)
- **Styling**: CSS with variables
- **Build**: Vite (fast, simple)

### Development
- **Package Manager**: npm (not yarn/pnpm)
- **Testing**: Jest + Playwright
- **Linting**: ESLint + Prettier
- **Security**: npm audit + custom checks

## Rejected Alternatives

### ❌ Cloud NLP Services (for core functionality)
- **Options**: Google Cloud Speech, AWS Transcribe
- **Rejected because**: Privacy, latency, cost for basic operations
- **Decision**: Local-first processing with optional cloud enhancement

### ✅ Cloud AI Services (as optional enhancement)
- **Reconsidered**: Optional cloud AI for advanced capabilities
- **Approved Providers**: Claude, Gemini, ChatGPT, Ollama (self-hosted)
- **Rationale**: User choice, enhanced capabilities, maintains privacy
- **Implementation**: Plugin-based, opt-in only, sanitized data

### ❌ Heavy Frontend Framework
- **Options**: React, Vue, Angular
- **Rejected because**: Unnecessary complexity
- **Decision**: Vanilla JS with Web Components

### ❌ Electron
- **Options**: Electron for desktop
- **Rejected because**: Resource usage
- **Decision**: Tauri (Rust + WebView)

### ❌ GraphQL
- **Options**: GraphQL for API
- **Rejected because**: Overkill for our needs
- **Decision**: Simple REST + WebSocket

## Performance Targets

### Response Times
- Voice recognition: <500ms
- Intent parsing: <100ms  
- Command generation: <50ms
- Total response: <2000ms

### Resource Usage
- RAM: <400MB (with voice)
- CPU: <10% idle
- Disk: <500MB total
- Network: 0 (local only)

### Scalability
- Single user: Perfect
- Family (5 users): Good
- Team (20 users): Acceptable
- Enterprise: Out of scope

## Future Considerations

### Planned
- Federated learning (privacy-preserving)
- Plugin architecture
- Multi-language support
- Gesture input

### Not Planned
- Cloud services
- User accounts
- Analytics
- Ads/monetization

## Review Schedule
- Weekly: During active development
- Monthly: During beta
- Quarterly: After launch

---

*Every decision should serve the user, not the technology.*