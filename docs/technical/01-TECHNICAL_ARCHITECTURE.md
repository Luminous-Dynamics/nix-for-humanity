# Nix for Humanity - Technical Architecture Document

## System Overview

Nix for Humanity transforms NixOS management from command-line expertise to natural conversation. The architecture prioritizes local-first operation, privacy, and progressive enhancement.

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface Layer                   │
│                                                         │
│  ┌─────────┐     ┌─────────┐     ┌──────────────┐    │
│  │  Voice  │     │  Text   │     │Visual (Min)  │    │
│  │ (WebRTC)│     │ (Input) │     │   (HTML)     │    │
│  └────┬────┘     └────┬────┘     └──────┬───────┘    │
│       └──────────────┬┴─────────────────┘             │
├───────────────────────┴─────────────────────────────────┤
│                  Intent Engine (JS/WASM)                 │
│  ┌────────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ Pattern Match  │  │ Context     │  │ Confidence │  │
│  │ (Regex+FSM)    │  │ Awareness   │  │ Scoring    │  │
│  └────────────────┘  └─────────────┘  └────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    Nix Core (Rust)                       │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐ │
│  │   AST   │  │  Safety  │  │  State  │  │Learning │ │
│  │ Builder │  │ Validator│  │ Manager │  │ Engine  │ │
│  └─────────┘  └──────────┘  └─────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────┤
│                   Integration Layer                      │
│  ┌──────────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │ Nix Command  │  │  Config  │  │ System Monitor  │  │
│  │   Wrapper    │  │  Editor  │  │   (Metrics)     │  │
│  └──────────────┘  └──────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    Storage Layer                         │
│  ┌──────────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │Pattern Store │  │  State   │  │  User Prefs    │  │
│  │  (SQLite)    │  │  Cache   │  │   (JSON)       │  │
│  └──────────────┘  └──────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. User Interface Layer

#### Voice Interface
- **Technology**: WebRTC Speech Recognition API
- **Fallback**: Local whisper.cpp integration (optional)
- **Features**:
  - Wake word detection ("Hey Nix")
  - Continuous listening mode
  - Multi-language support preparation
  - Noise cancellation

#### Execution Safety Levels
- **Preview**: All commands run with --dry-run flag
- **Cautious**: Destructive commands require confirmation
- **Normal**: Safe queries execute immediately
- **Expert**: Reduced safety checks for power users

#### Testing Strategy (Layered)
- **Unit Tests**: Test pure functions (intent, command building)
- **Integration Tests**: Test with --dry-run in containers
- **E2E Tests**: Real NixOS with safety flags
- **No Fake Data**: Never simulate command outputs

#### Text Interface
- **Single input field**: Universal command/query box
- **Auto-complete**: Based on learned patterns
- **Natural language**: No syntax requirements
- **Accessibility**: Full ARIA support

#### Visual Interface
- **Minimal by default**: Black screen, white text
- **Progressive disclosure**: Show only what's needed
- **Responsive**: Adapts to any screen size
- **Animation**: Subtle, can be disabled

### 2. Intent Engine

#### Pattern Matching Core
```javascript
// Enhanced pattern matching with context
const IntentPatterns = {
  install: {
    patterns: [
      /^(install|add|get|i need|i want)\s+(.+)$/i,
      /^(.+)\s+(is missing|not installed)$/i
    ],
    extractor: (match) => ({
      action: 'install',
      target: extractPackageName(match),
      confidence: calculateConfidence(match)
    })
  },
  
  fix: {
    patterns: [
      /^(fix|repair|troubleshoot)\s+(.+)$/i,
      /^(.+)\s+(is broken|not working|won't start)$/i
    ],
    extractor: (match) => ({
      action: 'diagnose',
      target: extractServiceName(match),
      symptoms: extractSymptoms(match)
    })
  }
}
```

#### Context Awareness
- **Session memory**: Remember recent actions
- **User patterns**: Learn preferences over time
- **Environmental**: Time of day, system state
- **Predictive**: Suggest likely next actions

#### Confidence Scoring
- **0-100 scale**: How sure are we of intent?
- **Threshold**: 80+ auto-execute, 50-79 confirm, <50 clarify
- **Learning**: Adjust based on user corrections
- **Transparency**: Always show confidence level

### 3. Nix Core Engine (Rust)

#### AST Builder
```rust
pub struct NixAST {
    configuration: ConfigNode,
    packages: Vec<PackageNode>,
    services: Vec<ServiceNode>,
    options: HashMap<String, Value>,
}

impl NixAST {
    pub fn add_package(&mut self, pkg: &str) -> Result<()> {
        // Validate package exists
        let pkg_info = nix_search(pkg)?;
        
        // Check dependencies
        let deps = resolve_dependencies(pkg)?;
        
        // Add to AST
        self.packages.push(PackageNode {
            name: pkg.to_string(),
            version: pkg_info.version,
            dependencies: deps,
        });
        
        Ok(())
    }
}
```

#### Safety Validator
- **Syntax checking**: Valid Nix expressions
- **Dependency resolution**: No conflicts
- **Resource limits**: Prevent system overload
- **Rollback safety**: Ensure we can revert
- **User confirmation**: For system-level changes

#### State Manager
- **Current configuration**: Parsed from files
- **Pending changes**: Queued modifications
- **History tracking**: What changed when
- **Diff generation**: Show exact changes
- **Generation management**: List/switch/rollback

#### Learning Engine
- **Pattern recognition**: Common user workflows
- **Anomaly detection**: Unusual requests
- **Preference learning**: User-specific adaptations
- **Collective intelligence**: Anonymous pattern sharing
- **Privacy preserving**: All learning is local

##### Machine Learning Model Progression
```
Phase 1: Simple Statistical Models
- Frequency counting for common patterns
- Confidence scoring via logistic regression
- Time-series analysis for usage patterns

Phase 2: Advanced Pattern Recognition
- Neural networks for intent classification
- Sequence modeling for multi-step workflows
- Clustering for user segmentation

Phase 3: Adaptive Intelligence
- Reinforcement learning from user feedback
- Transfer learning from community patterns
- Federated learning for collective intelligence
```

### 4. Integration Layer

#### Nix Command Wrapper (Layered Approach)
```rust
pub struct NixWrapper {
    executor: CommandExecutor,
    parser: OutputParser,
}

// Layer 1: Pure command building (no execution)
impl NixWrapper {
    pub fn build_search_command(query: &str) -> Command {
        Command::new("nix")
            .args(&["search", "nixpkgs", query])
    }
    
    pub fn build_install_command(package: &str, dry_run: bool) -> Command {
        let mut args = vec!["-iA", &format!("nixpkgs.{}", package)];
        if dry_run {
            args.push("--dry-run");
        }
        Command::new("nix-env").args(&args)
    }
}

// Layer 2: Execution with options
impl NixWrapper {
    pub async fn execute(&self, cmd: Command, opts: ExecutionOptions) -> Result<Output> {
        // Safety checks before execution
        if opts.require_confirmation && !self.confirm_with_user(&cmd).await? {
            return Err(ExecutionError::Cancelled);
        }
        
        // Real execution with timeout and sandboxing
        self.executor.run_sandboxed(cmd, opts.timeout).await
    }
}
```

#### Configuration Editor
- **Safe editing**: Never corrupt configuration.nix
- **Atomic updates**: All or nothing changes
- **Formatting**: Maintain consistent style
- **Comments**: Preserve user annotations
- **Validation**: Check before writing

#### System Monitor
- **Resource usage**: CPU, RAM, disk
- **Service health**: Running/stopped/failed
- **Network status**: Connectivity checks
- **Package updates**: Available upgrades
- **System logs**: Filtered for relevance

### 5. Storage Layer

#### Pattern Store (SQLite)
```sql
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY,
    user_input TEXT NOT NULL,
    interpreted_intent TEXT NOT NULL,
    confidence REAL NOT NULL,
    outcome TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    success BOOLEAN NOT NULL
);

CREATE TABLE adaptations (
    id INTEGER PRIMARY KEY,
    pattern_id INTEGER REFERENCES patterns(id),
    ui_element TEXT NOT NULL,
    adaptation_type TEXT NOT NULL,
    value TEXT,
    active BOOLEAN DEFAULT true
);
```

#### State Cache
- **Current config**: Parsed representation
- **Package cache**: Available packages
- **Service status**: Running services
- **Search index**: Fast package lookup
- **Update frequency**: Configurable refresh

#### User Preferences
```json
{
  "theme": "dark",
  "voice": {
    "enabled": true,
    "language": "en-US",
    "speed": 1.0
  },
  "privacy": {
    "telemetry": false,
    "pattern_learning": true,
    "collective_learning": false
  },
  "accessibility": {
    "high_contrast": false,
    "reduce_motion": true,
    "screen_reader_mode": false
  }
}
```

## Security Architecture

### Privilege Separation
```
┌─────────────────┐
│   Web UI (User) │
└────────┬────────┘
         │ JSON-RPC
┌────────▼────────┐
│ Nix Core (User) │
└────────┬────────┘
         │ Unix Socket
┌────────▼────────┐
│ Helper (Root)   │
└─────────────────┘
```

### Security Measures
1. **Input sanitization**: All user input validated
2. **Command injection prevention**: No shell execution
3. **File system isolation**: Chroot/namespace
4. **Network isolation**: Local-only by default
5. **Audit logging**: All system changes logged

## Performance Targets

### Response Times
- **Voice recognition start**: <500ms
- **Intent parsing**: <50ms
- **Package search**: <1s (cached: <100ms)
- **Configuration validation**: <2s
- **System rebuild**: (Depends on changes)

### Resource Usage
- **Base memory**: <50MB
- **With learning**: <200MB
- **CPU usage**: <5% idle, <25% active
- **Storage**: <100MB + patterns
- **Network**: Minimal, only for updates

## Scalability Design

### Horizontal Scaling
- **Multi-device sync**: Optional cloud bridge
- **Federated learning**: Share patterns anonymously
- **Plugin architecture**: Community extensions
- **Language packs**: Downloadable modules

### Vertical Scaling
- **Progressive enhancement**: Use available resources
- **Graceful degradation**: Work on minimal hardware
- **Caching strategies**: Multi-level caches
- **Background processing**: Non-blocking operations

## Data Flow

### Typical User Interactions

#### Install Flow
```
User: "I need to edit documents"
         │
         ▼
┌─────────────────┐
│ Voice → Text    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Intent: Install │
│ Target: Editor  │
│ Confidence: 95% │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Search Packages │
│ "libreoffice"   │
│ "vscode"        │
│ "vim"           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User Confirms   │
│ "LibreOffice"   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update Config   │
│ Add Package     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rebuild System  │
│ Show Progress   │
└────────┬────────┘
         │
         ▼
"LibreOffice is ready to use!"
```

#### Fix Flow
```
User: "My wifi isn't working"
         │
         ▼
┌─────────────────┐
│ Voice → Text    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Intent: Fix     │
│ Target: Network │
│ Confidence: 88% │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Diagnostic Run  │
│ - Check service │
│ - Test hardware │
│ - Verify config │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Issue Found     │
│ "NetworkManager │
│  not running"   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Suggest Fix     │
│ "Start service?"│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Apply Fix       │
│ Start NM Service│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verify Success  │
│ Test Connection │
└────────┬────────┘
         │
         ▼
"WiFi is working now! Connected to your network."
```

## Error Handling

### Error Categories
1. **User errors**: Unclear intent → Ask for clarification
2. **System errors**: Command failed → Explain simply
3. **Network errors**: Can't download → Offer offline alternatives
4. **Permission errors**: Need sudo → Request elevation
5. **Unknown errors**: Log and gracefully recover

### Recovery Strategies
- **Automatic rollback**: On critical failures
- **Checkpoint system**: Save state before changes
- **Undo functionality**: Reverse recent actions
- **Help suggestions**: Proactive assistance
- **Fallback modes**: CLI access if needed

## Testing Strategy

### Unit Tests
- Pattern matching accuracy
- AST generation correctness
- Safety validation rules
- State management consistency

### Integration Tests
- End-to-end workflows
- Multi-component interaction
- Error propagation
- Performance benchmarks

### User Tests
- Accessibility compliance
- Voice recognition accuracy
- Intent interpretation rates
- Task completion times

## Future Architecture Extensions

### Phase 2: Enhanced NLP
- Transformer-based intent parsing
- Context-aware conversations
- Multi-turn interactions
- Sentiment analysis

### Phase 3: Collective Intelligence
- Anonymous pattern sharing
- Community-driven improvements
- Federated learning models
- Cross-distribution support

### Phase 4: Ecosystem Integration
- Home automation bridges
- Cloud service management
- Container orchestration
- Development environment setup

## Architecture Principles

1. **Local First**: Full functionality without internet
2. **Privacy Sacred**: No data leaves device without permission
3. **Progressive Enhancement**: Better experience with more resources
4. **Graceful Degradation**: Always functional on minimal hardware
5. **User Sovereignty**: User owns all data and controls all features
6. **Modular Design**: Components can be replaced/upgraded
7. **Open Standards**: Use existing protocols where possible
8. **Future Proof**: Design for 10 years of evolution

---

This architecture enables Nix for Humanity to serve everyone from command-line experts to complete beginners, while maintaining the security and reliability NixOS users expect.