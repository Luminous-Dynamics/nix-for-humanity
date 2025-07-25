# 🏗️ System Architecture Diagram - Nix for Humanity

## High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        Voice[Voice Input]
        Text[Text Input]
        GUI[Learning GUI]
    end

    subgraph "Natural Language Processing"
        STT[Speech to Text<br/>Whisper.cpp]
        NLP[Hybrid NLP Engine]
        Intent[Intent Recognition]
        Entity[Entity Extraction]
        Context[Context Manager]
    end

    subgraph "Command Generation"
        Safety[Safety Validator]
        Builder[Command Builder]
        Preview[Preview Generator]
    end

    subgraph "NixOS Integration"
        Polkit[Polkit Auth]
        Nix[Nix Commands]
        Config[configuration.nix]
        Rollback[Rollback System]
    end

    subgraph "Data Layer"
        Learning[Learning DB<br/>SQLite]
        Cache[Cache<br/>Local]
        Audit[Audit Log]
    end

    Voice --> STT
    Text --> Intent
    STT --> Intent
    Intent --> NLP
    NLP --> Entity
    Entity --> Context
    Context --> Safety
    Safety --> Builder
    Builder --> Preview
    Preview --> GUI
    
    Builder --> Polkit
    Polkit --> Nix
    Nix --> Config
    Config --> Rollback
    
    Context --> Learning
    Builder --> Cache
    Nix --> Audit
    
    GUI -.->|Feedback| Learning
```

## Component Details

### 1. User Interface Layer
- **Voice Input**: Web Speech API + Whisper.cpp fallback
- **Text Input**: Natural language text box
- **Learning GUI**: Progressive interface (appears/fades based on mastery)

### 2. NLP Pipeline
```mermaid
graph LR
    Input[User Input] --> Token[Tokenization]
    Token --> Rules[Rule-Based<br/>Matcher<br/>95% accuracy]
    Rules --> Stats[Statistical<br/>CRF Model<br/>Handles variations]
    Stats --> Neural[Neural<br/>Transformer<br/>Complex understanding]
    Neural --> Fusion[Score Fusion]
    Fusion --> Intent[Final Intent]
```

### 3. Three-Layer NLP Architecture

#### Layer 1: Rule-Based (Fast Path)
```yaml
Common Commands:
  - Pattern: "install {package}"
  - Response Time: <10ms
  - Accuracy: 95%
  - Examples: 50+ patterns
```

#### Layer 2: Statistical (Variation Handler)
```yaml
Handles:
  - Typos: "instal fierfix"
  - Variations: "get me firefox"
  - Context: Pronouns, references
  - Response Time: <50ms
```

#### Layer 3: Neural (Complex Understanding)
```yaml
For:
  - Complex queries
  - Multi-step operations
  - Ambiguous requests
  - Response Time: <200ms
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant V as Voice/Text
    participant N as NLP Engine
    participant S as Safety Check
    participant B as Command Builder
    participant P as Polkit
    participant X as NixOS
    participant G as GUI

    U->>V: "Install Firefox"
    V->>N: Tokenized input
    N->>N: Intent: install_package
    N->>N: Entity: firefox
    N->>S: Validate intent
    S->>B: Build command
    B->>G: Show preview
    G->>U: "Installing Firefox..."
    B->>P: Request auth
    P->>X: Execute command
    X->>G: Progress updates
    G->>U: "Firefox installed!"
```

## Security Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        Input[User Input]
        Sanitize[Input Sanitization]
    end

    subgraph "Validation Layer"
        Whitelist[Intent Whitelist]
        Validate[Parameter Validation]
        AST[AST Builder<br/>No String Concat]
    end

    subgraph "Execution Layer"
        Sandbox[Namespace Isolation]
        Polkit[Polkit Authorization]
        Audit[Audit Logging]
    end

    Input --> Sanitize
    Sanitize --> Whitelist
    Whitelist --> Validate
    Validate --> AST
    AST --> Sandbox
    Sandbox --> Polkit
    Polkit --> Audit
```

## Deployment Architecture

```mermaid
graph LR
    subgraph "Local Machine"
        Browser[Web Browser<br/>Port 3456]
        API[NLP API<br/>Port 3456]
        WS[WebSocket<br/>Port 3457]
        GUI[Learning GUI<br/>Port 3458]
        
        Browser <--> API
        Browser <--> WS
        Browser <--> GUI
    end

    subgraph "System Integration"
        Polkit[Polkit Helper]
        Nix[Nix Commands]
        
        API --> Polkit
        Polkit --> Nix
    end
```

## State Management

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Listening: Voice activated
    Idle --> Processing: Text input
    
    Listening --> Processing: Speech recognized
    Processing --> Confirming: Intent recognized
    Confirming --> Executing: User approved
    Confirming --> Idle: User cancelled
    
    Executing --> Success: Command completed
    Executing --> Error: Command failed
    
    Success --> Idle
    Error --> Recovery
    Recovery --> Idle
```

## Performance Architecture

### Response Time Targets
```
Voice Input → Response: <2s total
├── Speech Recognition: 500ms
├── NLP Processing: 100ms
├── Command Building: 50ms
├── UI Update: 50ms
└── Buffer: 300ms
```

### Resource Usage
```
Memory Usage: <400MB
├── NLP Models: 200MB
├── Voice Models: 140MB
├── Application: 50MB
└── Buffer: 10MB

CPU Usage: <25% average
├── Idle: <5%
├── Processing: 15-25%
└── Peak: 40%
```

## Scalability Considerations

### Current Scope (v1.0)
- Single user
- Local machine only
- 50+ intents
- English only

### Future Expansion (v2.0+)
- Multi-user (family)
- Network service option
- 200+ intents
- Multi-language

---

*Architecture designed for simplicity, security, and user sovereignty.*