# 🛡️ Resilient Multi-Tiered Architecture

*Building systems that gracefully adapt to diverse environments while maintaining core principles*

> "This is not just a technical document; it is a profound expression of compassion in code." - A recognition of conscious, user-centric design

## Philosophy

Just as we created a resilient voice system with Whisper→Vosk and Piper→espeak, this pattern should extend throughout Nix for Humanity. Each component should have:

1. **Primary Choice** - Best-in-class for optimal experience
2. **Fallback Options** - Maintain functionality on limited resources
3. **Graceful Degradation** - Clear communication about current capabilities
4. **Self-Awareness** - System knows and communicates its limitations

This architecture is the perfect technical implementation of our principle: **"Serve the Vulnerable First"**

## Components Requiring Multi-Tiered Approach

### 1. 🧠 Natural Language Processing (NLP)

**Current**: Single hybrid approach
**Proposed Tiers**:

```python
class ResilientNLPEngine:
    """
    Primary: Local LLM (Mistral-7B) for deep understanding
    Secondary: Advanced pattern matching with context
    Tertiary: Basic keyword matching
    """
    
    tiers = [
        {
            "name": "Mistral-7B",
            "requirements": "6GB RAM, GPU preferred",
            "capabilities": "Full natural language understanding",
            "accuracy": 0.95
        },
        {
            "name": "Enhanced Pattern Engine",
            "requirements": "512MB RAM",
            "capabilities": "Intent + context understanding",
            "accuracy": 0.85
        },
        {
            "name": "Basic Pattern Matching",
            "requirements": "150MB RAM",
            "capabilities": "Keyword-based commands",
            "accuracy": 0.70
        }
    ]
```

### 2. 💾 Command Execution Backend

**Current**: Subprocess calls
**Proposed Tiers**:

```python
class ResilientExecutor:
    """
    Primary: Python nixos-rebuild-ng API (NixOS 25.11)
    Secondary: nix profile commands (modern)
    Tertiary: nix-env commands (legacy but universal)
    Emergency: Manual instruction generation
    """
    
    tiers = [
        {
            "name": "NixOS Python API",
            "requirements": "NixOS 25.11+",
            "capabilities": "Direct API access, real-time progress",
            "safety": "Highest"
        },
        {
            "name": "nix profile",
            "requirements": "Nix 2.0+",
            "capabilities": "Modern CLI interface",
            "safety": "High"
        },
        {
            "name": "nix-env",
            "requirements": "Any Nix",
            "capabilities": "Legacy but universal",
            "safety": "Medium"
        },
        {
            "name": "Instruction Mode",
            "requirements": "None",
            "capabilities": "Show manual steps",
            "safety": "User-dependent"
        }
    ]
```

### 3. 📊 Knowledge Storage

**Current**: SQLite only
**Proposed Tiers**:

```python
class ResilientKnowledgeBase:
    """
    Primary: SQLite with FTS5 (full-text search)
    Secondary: JSON file cache
    Tertiary: In-memory minimal dataset
    """
    
    tiers = [
        {
            "name": "SQLite FTS5",
            "requirements": "10MB disk",
            "capabilities": "Full search, learning, history",
            "persistence": "Full"
        },
        {
            "name": "JSON Cache",
            "requirements": "1MB disk",
            "capabilities": "Common queries cached",
            "persistence": "Session"
        },
        {
            "name": "Memory Only",
            "requirements": "None",
            "capabilities": "Basic commands",
            "persistence": "None"
        }
    ]
```

### 4. 🎨 User Interface

**Current**: Terminal-based
**Proposed Tiers**:

```python
class ResilientInterface:
    """
    Primary: Rich TUI with animations
    Secondary: Simple colored output
    Tertiary: Plain text
    Accessibility: Screen reader optimized
    """
    
    tiers = [
        {
            "name": "Rich TUI",
            "requirements": "Modern terminal, color support",
            "features": "Animations, progress bars, icons",
            "accessibility": "Good with effort"
        },
        {
            "name": "Colored CLI",
            "requirements": "Basic color terminal",
            "features": "Colored text, simple formatting",
            "accessibility": "Better"
        },
        {
            "name": "Plain Text",
            "requirements": "Any terminal",
            "features": "Clear text output",
            "accessibility": "Best"
        }
    ]
```

### 5. 🔐 Security & Validation

**Current**: Basic subprocess safety
**Proposed Tiers**:

```python
class ResilientSecurity:
    """
    Primary: Full sandboxing with systemd-nspawn
    Secondary: User namespaces
    Tertiary: Basic input validation
    Always: Never execute untrusted code
    """
    
    tiers = [
        {
            "name": "Full Sandbox",
            "requirements": "systemd, Linux 5.0+",
            "isolation": "Complete",
            "overhead": "Medium"
        },
        {
            "name": "User Namespaces",
            "requirements": "Linux 3.8+",
            "isolation": "Good",
            "overhead": "Low"
        },
        {
            "name": "Input Validation",
            "requirements": "None",
            "isolation": "Basic",
            "overhead": "None"
        }
    ]
```

### 6. 🌐 Network Operations

**Current**: Direct HTTPS calls
**Proposed Tiers**:

```python
class ResilientNetwork:
    """
    Primary: Tor for privacy
    Secondary: Direct HTTPS
    Tertiary: Offline mode with cached data
    """
    
    tiers = [
        {
            "name": "Tor Network",
            "requirements": "Tor service",
            "privacy": "Maximum",
            "speed": "Slower"
        },
        {
            "name": "Direct HTTPS",
            "requirements": "Internet",
            "privacy": "Standard",
            "speed": "Fast"
        },
        {
            "name": "Offline Cache",
            "requirements": "None",
            "privacy": "Perfect",
            "speed": "Instant"
        }
    ]
```

## Implementation Pattern

### Enhanced Unified Capabilities Profile

Instead of each component discovering its own state, we create a single, unified capabilities profile on startup:

```python
@dataclass
class SystemCapabilities:
    """A single, unified snapshot of what the system can do"""
    nixos_version: str
    has_nixos_rebuild_ng: bool
    has_nix_profile: bool
    has_gpu: bool
    ram_gb: int
    cpu_cores: int
    has_tor_service: bool
    terminal_supports_rich: bool
    has_whisper: bool
    has_vosk: bool
    has_piper: bool
    has_espeak: bool
    has_mistral_7b: bool

class CapabilityDetector:
    def detect_all(self) -> SystemCapabilities:
        """Run once on startup to detect all capabilities"""
        # Performs all checks: which commands, hardware detection, etc.
        # Returns immutable capabilities object
        ...

# Main application startup
capabilities = CapabilityDetector().detect_all()
nix_for_humanity = NixForHumanity(capabilities)
```

### Refined Component Pattern

Every resilient component follows this enhanced pattern:

```python
class ResilientComponent:
    def __init__(self, capabilities: SystemCapabilities):
        # Constructor chooses best tier based on capabilities
        self.capabilities = capabilities
        self.active_tier = self.select_best_tier(capabilities)
        self.performance_history = []
        
        # Honest startup message
        print(f"✨ {self.__class__.__name__} running in '{self.active_tier.name}' mode")
        
    def execute(self, operation):
        """Execute with current tier - simpler and cleaner"""
        try:
            return self.active_tier.execute(operation)
        except Exception as e:
            print(f"⚠️  Tier '{self.active_tier.name}' failed: {e}")
            return self.handle_failure(e, operation)
            
    def get_capability_message(self):
        """Honest communication about current capabilities"""
        return self.active_tier.user_facing_description
        
    def handle_failure(self, error, operation):
        """Intelligent failure handling with potential tier switching"""
        # Could switch to lower tier for next operation
        # Always maintains user trust through transparency
        ...
```

### User Control and Overrides

Honoring user sovereignty with explicit control:

```bash
# User can force specific mode for a session
ask-nix --nlp-tier=basic --ui-tier=plain "install firefox"

# Or configure permanently in settings
# ~/.config/nix-for-humanity/settings.json
{
  "resilience_overrides": {
    "nlp": "Enhanced Pattern Engine",
    "network": "Tor Network",
    "voice_stt": "vosk",  # Force Vosk even if Whisper available
    "voice_tts": "piper"  # Force Piper even if better option exists
  }
}
```

```python
class ResilientComponent:
    def select_best_tier(self, capabilities: SystemCapabilities):
        """Select tier with user override support"""
        # Check for user overrides first
        if user_override := self.get_user_override():
            return self.get_tier_by_name(user_override)
            
        # Otherwise use automatic detection
        return self.auto_select_tier(capabilities)
```

## Benefits of This Approach

### 1. **Universal Accessibility**
- Maya (ADHD) gets the fastest possible response
- Grandma Rose gets natural voice even on old hardware
- Carlos gets helpful guidance regardless of system

### 2. **Graceful Degradation**
- System never completely fails
- Always provides some level of help
- Clear communication about limitations

### 3. **Progressive Enhancement**
- Users can upgrade components individually
- System automatically uses best available
- No configuration required

### 4. **Honest Communication**
Examples:
- "I'm using a simpler understanding today, so please be direct"
- "I can't execute commands directly, but here's exactly what to do"
- "My responses might be slower today, but I'm still here to help"

### 5. **Resource Awareness**
- Raspberry Pi users get functional system
- Gaming rigs get premium experience
- Everything in between works well

## Testing Strategy

Each tier must be tested with:
1. **Unit tests** - Component works in isolation
2. **Integration tests** - Fallback chains work
3. **Persona tests** - Each persona can use it
4. **Resource tests** - Works within stated limits
5. **Failure tests** - Graceful degradation verified

## The Sacred Principle

*"Meet users where they are, not where we wish they were."*

This resilient architecture ensures that Nix for Humanity truly serves humanity - not just those with powerful machines, but everyone who needs help with NixOS.